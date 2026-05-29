"""
ashenmoor.net.client
────────────────────
Abstract MudClient base class and the async per-client game loop.
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

    def _build_prompt(self) -> str:
        """
        Always shows HP and movement points.
        Combat:     [23/23hp 100/100mv] > (red chevron)
        Peaceful:   [23/23hp 100/100mv] > (green chevron)
        """
        state = self._state
        name  = self._player_name
        char  = state.characters.get(name)
        if char:
            hp  = getattr(char, "hp",        0)
            mhp = getattr(char, "max_hp",     1)
            mv  = getattr(char, "moves",      0)
            mmv = getattr(char, "max_moves",  1)
            if name in state.fighting:
                return f"&w[&W{hp}&w/&W{mhp}&whp &R{mv}&w/&W{mmv}&wmv] &R>&N "
            return f"&w[&W{hp}&w/&W{mhp}&whp &W{mv}&w/&W{mmv}&wmv] &g>&N "
        return "&g> &N"

    async def _send_prompt(self) -> None:
        from ..color import diku_to_ansi
        await self._raw_send(diku_to_ansi(self._build_prompt()))

    async def _flush_outbox(self) -> None:
        from ..color import diku_to_ansi
        while not self._outbox.empty():
            text = self._outbox.get_nowait()
            await self._raw_send(diku_to_ansi(text) + "\r\n")

    async def run_login(self, start_room: int, races: dict,
                        db_path: str = "ashenmoor.db") -> bool:
        from ..engine.persist import open_db, save_character, load_character
        from ..core.character import Character
        from ..dnd.classes.warrior import new_warrior_dnd, WARRIOR_POWERS

        conn = open_db(db_path)

        await self._raw_send("\r\n")
        await self._raw_send("\033[1;37m╔══════════════════════════════╗\033[0m\r\n")
        await self._raw_send("\033[1;37m║      W e l c o m e  t o      ║\033[0m\r\n")
        await self._raw_send("\033[1;37m║      A s h e n m o o r       ║\033[0m\r\n")
        await self._raw_send("\033[1;37m╚══════════════════════════════╝\033[0m\r\n\r\n")

        while True:
            await self._raw_send("Who would you like to be known as? ")
            try:
                raw = await self._raw_readline()
            except (EOFError, ConnectionResetError):
                return False

            if not raw.strip():
                continue

            name = raw.strip()[0].upper() + raw.strip()[1:].lower()

            row = conn.execute(
                "SELECT race, class, level, hp FROM characters WHERE name = ?",
                (name,),
            ).fetchone()

            if row is None:
                await self._raw_send(f"\r\nThat character does not exist.\r\n")
                await self._raw_send(f"Would you like to create {name} now? (yes/no) ")
                try:
                    answer = await self._raw_readline()
                except (EOFError, ConnectionResetError):
                    return False

                if answer.strip().lower() not in ("yes", "y"):
                    await self._raw_send("Very well. Enter another name.\r\n\r\n")
                    continue

                char = Character({
                    "name":      name,
                    "race":      "Human",
                    "class":     "Warrior",
                    "level":     1,
                    "stats":     [90, 90, 90, 70, 70, 70],
                    "dnd":       new_warrior_dnd(level=1, fighting_style="dueling"),
                    "powers":    WARRIOR_POWERS,
                    "alignment": "True Neutral",
                    "position":  "standing",
                }, races=races)

                save_character(conn, char, location=start_room, include_hp=True)
                self._state.characters[name] = char
                self._state.locations[name]  = start_room
                self._player_name            = name

                await self._raw_send(
                    f"\r\n\033[1;37mCharacter {name} has been created!\033[0m\r\n"
                    f"You are a level 1 Human Warrior.\r\n"
                    f"(STR 90 / DEX 90 / CON 90 / INT 70 / WIS 70 / CHA 70)\r\n\r\n"
                )
                break

            else:
                cclass = row["class"]
                level  = row["level"]
                d      = {
                    "name":  name,
                    "race":  row["race"],
                    "class": cclass,
                    "level": level,
                    "stats": [75] * 6,
                }
                if cclass.lower() in ("warrior", "fighter"):
                    d["dnd"]    = new_warrior_dnd(level=level)
                    d["powers"] = WARRIOR_POWERS

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

        return True

    async def run_game(self) -> None:
        from ..color import diku_to_ansi

        name  = self._player_name
        state = self._state

        # Register with the server's tick loop
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
