"""
ashenmoor.net.client
────────────────────
Abstract MudClient base class and the async per-client game loop.

The subclass selection flow is handled via the shared
ashenmoor.engine.subclass module, keeping local and network
paths identical — only the send/recv primitives differ.
"""

from __future__ import annotations
import asyncio
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..engine.game import GameState

TICK_INTERVAL = 4.0


class MudClient(ABC):

    def __init__(self, state: "GameState"):
        self._state       = state
        self._player_name = ""
        self._outbox: asyncio.Queue[str] = asyncio.Queue()
        self._closed      = False

    @abstractmethod
    async def _raw_send(self, text: str) -> None: ...

    @abstractmethod
    async def _raw_readline(self) -> str: ...

    @abstractmethod
    async def close(self) -> None: ...

    async def send(self, text: str) -> None:
        await self._outbox.put(text)

    # ── Prompt builder ────────────────────────────────────────────────────────

    def _build_prompt(self) -> str:
        """
        Full prompt showing HP (with temp_hp in magenta), movement, and
        all active resource pools.

        Format:
          [<hp>/<maxhp>hp <mv>/<maxmv>mv | SW:2/2 AS:1/1 IND:2/2 SD:4d8 RIP:armed] >

        The > is red in combat, green out of combat.
        """
        from ..color import diku_to_ansi

        state = self._state
        name  = self._player_name
        char  = state.characters.get(name)

        if not char:
            return diku_to_ansi("&g> &N")

        hp   = getattr(char, "hp",        0)
        mhp  = getattr(char, "max_hp",    1)
        temp = getattr(char, "temp_hp",   0)
        mv   = getattr(char, "moves",     0)
        mmv  = getattr(char, "max_moves", 1)

        # HP colour and display value
        if temp > 0:
            hp_color   = "&M"
            hp_display = hp + temp
        else:
            pct      = hp / max(1, mhp)
            hp_color = "&+G" if pct > 0.66 else ("&+Y" if pct > 0.33 else "&+R")
            hp_display = hp

        # Resource pools
        dnd       = getattr(char, "dnd", {}) or {}
        resources = []

        sw  = dnd.get("second_wind_uses", 0)
        swm = dnd.get("second_wind_max",  0)
        if swm:
            resources.append(f"SW:{sw}/{swm}")

        as_ = dnd.get("action_surge_uses", 0)
        asm = dnd.get("action_surge_max",  0)
        if asm:
            resources.append(f"AS:{as_}/{asm}")

        ind  = dnd.get("indomitable_uses", 0)
        indm = dnd.get("indomitable_max",  0)
        if indm:
            resources.append(f"IND:{ind}/{indm}")

        sd  = dnd.get("superiority_dice",     0)
        sdm = dnd.get("superiority_dice_max", 0)
        sds = dnd.get("superiority_die_size", 8)
        if sdm:
            if sd > 0:
                rip_state = "&Garmed&N" if dnd.get("riposte_armed") else "ready"
            else:
                rip_state = "&R0&N"
            resources.append(f"SD:{sd}d{sds} RIP:{rip_state}")

        res_str  = " ".join(resources)
        chevron  = "&R>&N" if name in state.fighting else "&g>&N"
        res_part = f" | {res_str}" if res_str else ""

        raw = (
            f"&w[{hp_color}{hp_display}&w/{mhp}hp "
            f"&W{mv}&w/{mmv}mv{res_part}&w] {chevron} &N"
        )
        return diku_to_ansi(raw)

    async def _send_prompt(self) -> None:
        await self._raw_send(self._build_prompt())

    async def _flush_outbox(self) -> None:
        from ..color import diku_to_ansi
        while not self._outbox.empty():
            text = self._outbox.get_nowait()
            await self._raw_send(diku_to_ansi(text) + "\r\n")

    # ── Login ─────────────────────────────────────────────────────────────────

    async def run_login(self, start_room: int, races: dict,
                        db_path: str = "ashenmoor.db") -> bool:
        from ..engine.persist import open_db, save_character, load_character
        from ..core.character import Character
        from ..dnd.classes.fighter import new_fighter_dnd, FIGHTER_POWERS

        conn = open_db(db_path)

        await self._raw_send("\r\n")
        await self._raw_send("\033[1;37m╔══════════════════════════════╗\033[0m\r\n")
        await self._raw_send("\033[1;37m║      W e l c o m e  t o      ║\033[0m\r\n")
        await self._raw_send("\033[1;37m║      R i v e r m o o r       ║\033[0m\r\n")
        await self._raw_send("\033[1;37m╚══════════════════════════════╝\033[0m\r\n\r\n")

        while True:
            await self._raw_send("Who would you like to be known as? ")
            try:
                raw = await self._raw_readline()
            except (EOFError, ConnectionResetError):
                return False

            if not raw.strip():
                continue

            if raw.strip().lower() in ("quit", "exit", "q"):
                await self._raw_send("Farewell!\r\n")
                return False

            name = raw.strip()[0].upper() + raw.strip()[1:].lower()

            row = conn.execute(
                "SELECT race, class, level, hp FROM characters WHERE name = ?",
                (name,),
            ).fetchone()

            if row is None:
                # ── New character ─────────────────────────────────────────
                await self._raw_send(
                    f"\r\n\033[1;37mCharacter {name} does not exist.\033[0m\r\n"
                    f"Would you like to create {name} now? (yes/no) "
                )
                try:
                    answer = await self._raw_readline()
                except (EOFError, ConnectionResetError):
                    return False
                if answer.strip().lower() not in ("yes", "y"):
                    await self._raw_send("Very well. Enter another name.\r\n\r\n")
                    continue

                # Sex selection
                sex = "male"
                while True:
                    await self._raw_send("Are you Male or Female (M/F)? ")
                    try:
                        sex_raw = await self._raw_readline()
                    except (EOFError, ConnectionResetError):
                        return False
                    s = sex_raw.strip().lower()
                    if s in ("m", "male"):
                        sex = "male"; break
                    elif s in ("f", "female"):
                        sex = "female"; break
                    else:
                        await self._raw_send("Please enter M or F.\r\n")

                char = Character({
                    "name":      name,
                    "race":      "Human",
                    "class":     "Fighter",
                    "level":     1,
                    "stats":     [90, 90, 90, 70, 70, 70],
                    "dnd":       new_fighter_dnd(level=1, fighting_style="dueling"),
                    "powers":    list(FIGHTER_POWERS),
                    "alignment": "True Neutral",
                    "position":  "standing",
                    "sex":       sex,
                }, races=races)

                save_character(conn, char, location=start_room, include_hp=True)
                self._state.characters[name] = char
                self._state.locations[name]  = start_room
                self._player_name            = name

                await self._raw_send(
                    f"\r\n\033[1;37mCharacter {name} has been created!\033[0m\r\n"
                    f"You are a level 1 Human Fighter.\r\n"
                    f"(STR 90 / DEX 90 / CON 90 / INT 70 / WIS 70 / CHA 70)\r\n\r\n"
                )
                break

            else:
                # ── Existing character ────────────────────────────────────
                cclass = row["class"]
                level  = row["level"]

                # Migrate Warrior → Fighter in the shell dict
                display_class = "Fighter" if cclass.lower() == "warrior" else cclass

                d = {
                    "name":  name,
                    "race":  row["race"],
                    "class": display_class,
                    "level": level,
                    "stats": [75] * 6,
                }
                if display_class.lower() in ("fighter", "warrior"):
                    d["dnd"]    = new_fighter_dnd(level=level)
                    d["powers"] = list(FIGHTER_POWERS)

                char      = Character(d, races=races)
                saved_loc = load_character(conn, name, char)
                room_vnum = saved_loc if saved_loc else start_room

                self._state.characters[name] = char
                self._state.locations[name]  = room_vnum
                self._player_name            = name

                await self._raw_send(
                    f"\r\n\033[1;37mWelcome back, {name}!\033[0m\r\n"
                    f"(Level {char.level} {char.race} {char.cclass})\r\n\r\n"
                )
                break

        if self._state._db is None:
            self._state._db = conn

        # ── Subclass selection (blocks before room look) ──────────────────
        from ..engine.subclass import needs_subclass, run_subclass_selection

        if needs_subclass(char):
            await run_subclass_selection(
                char,
                send = self._async_send,
                recv = self._raw_readline,
            )
            # Save immediately so the choice persists
            from ..engine.persist import save_character as _save
            _save(conn, char, self._state.locations.get(name, start_room))

        return True

    async def _async_send(self, text: str) -> None:
        """Adapter so run_subclass_selection can await send(text)."""
        from ..color import diku_to_ansi
        await self._raw_send(diku_to_ansi(text) + "\r\n")

    # ── Game loop ─────────────────────────────────────────────────────────────

    async def run_game(self) -> None:
        from ..color import diku_to_ansi
        from ..engine.subclass import needs_subclass, run_subclass_selection

        name  = self._player_name
        state = self._state

        _srv = getattr(state, '_server', None)
        if _srv is not None and name:
            _srv._clients[name] = self

        char = state.characters.get(name)

        if char:
            await self._raw_send(
                f"\033[0mYou are \033[1;37m{char.name}\033[0m, a level "
                f"\033[1;37m{char.level}\033[0m {char.race} {char.cclass}.\r\n"
                f"Type \033[1;37mscore\033[0m, \033[1;37matt\033[0m, "
                f"\033[1;37mlook\033[0m, \033[1;37mkill <mob>\033[0m, "
                f"\033[1;37mhelp\033[0m, or \033[1;37mquit\033[0m.\r\n\r\n"
            )
            result = state.handle("look", player_name=name)
            if result:
                await self._raw_send(diku_to_ansi(result) + "\r\n")

        need_prompt = True

        while not self._closed:
            await self._flush_outbox()

            if need_prompt:
                await self._send_prompt()
                need_prompt = False

            try:
                raw = await asyncio.wait_for(
                    self._raw_readline(),
                    timeout=0.5,
                )
            except asyncio.TimeoutError:
                if not self._outbox.empty():
                    await self._raw_send("\r\n")
                    await self._flush_outbox()
                    need_prompt = True
                continue
            except (EOFError, ConnectionResetError, BrokenPipeError):
                break

            raw = raw.strip()
            if not raw:
                need_prompt = True
                continue

            # ── Subclass selection intercept ──────────────────────────────
            # Triggers when a level-up just set subclass_pending.
            char = state.characters.get(name)
            if char and needs_subclass(char):
                await run_subclass_selection(
                    char,
                    send = self._async_send,
                    recv = self._raw_readline,
                )
                if state._db:
                    from ..engine.persist import save_character as _save
                    _save(state._db, char, state.locations.get(name, 0))
                need_prompt = True
                continue

            result = state.handle(raw, player_name=name)

            if result == "quit":
                await self._raw_send("\r\nGoodbye! Your progress has been saved.\r\n")
                break

            if result:
                await self._flush_outbox()
                await self._raw_send(diku_to_ansi(result) + "\r\n")

            need_prompt = True

        self._closed = True
        state.fighting.pop(name, None)
        state.characters.pop(name, None)
        state.locations.pop(name, None)

    async def run(self, start_room: int, races: dict,
                  db_path: str = "ashenmoor.db") -> None:
        try:
            ok = await self.run_login(start_room, races, db_path)
            if ok:
                await self.run_game()
        except Exception:
            import traceback
            traceback.print_exc()
        finally:
            await self.close()
