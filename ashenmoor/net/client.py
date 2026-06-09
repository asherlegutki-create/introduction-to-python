"""
ashenmoor.net.client
────────────────────
Abstract MudClient base class and the async per-client game loop.
Login flow is handled by ashenmoor.engine.login (shared with ticker.py).
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
        self._account_id  = 0
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

    # ── Prompt ────────────────────────────────────────────────────────────────

    def _build_prompt(self) -> str:
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

        if temp > 0:
            hp_color   = "&M"
            hp_display = hp + temp
        else:
            pct      = hp / max(1, mhp)
            hp_color = "&+G" if pct > 0.66 else ("&+Y" if pct > 0.33 else "&+R")
            hp_display = hp

        dnd       = getattr(char, "dnd", {}) or {}
        resources = []

        sw  = dnd.get("second_wind_uses", 0)
        swm = dnd.get("second_wind_max",  0)
        if swm: resources.append(f"SW:{sw}/{swm}")

        as_ = dnd.get("action_surge_uses", 0)
        asm = dnd.get("action_surge_max",  0)
        if asm: resources.append(f"AS:{as_}/{asm}")

        ind  = dnd.get("indomitable_uses", 0)
        indm = dnd.get("indomitable_max",  0)
        if indm: resources.append(f"IND:{ind}/{indm}")

        sd  = dnd.get("superiority_dice",     0)
        sdm = dnd.get("superiority_dice_max", 0)
        sds = dnd.get("superiority_die_size", 8)
        if sdm:
            rip_state = "&Garmed&N" if dnd.get("riposte_armed") else "ready"
            if sd == 0: rip_state = "&R0&N"
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

    # ── Send adapter (plain text, no diku conversion) ─────────────────────────

    async def _plain_send(self, text: str) -> None:
        from ..color import diku_to_ansi
        await self._raw_send(diku_to_ansi(text))

    # ── Login ─────────────────────────────────────────────────────────────────

    async def run_login(self, start_room: int, races: dict,
                        db_path: str = "ashenmoor.db") -> bool:
        from ..engine.persist import open_db
        from ..engine.login   import run_login_flow

        conn = open_db(db_path)

        result = await run_login_flow(
            state      = self._state,
            conn       = conn,
            send       = self._plain_send,
            recv       = self._raw_readline,
            start_room = start_room,
            races      = races,
        )

        if result is None:
            return False

        char, account_id, room_vnum = result
        self._player_name = char.name
        self._account_id  = account_id

        if self._state._db is None:
            self._state._db = conn

        # Store account_id on state for wiz commands and save calls
        self._state._account_ids = getattr(self._state, "_account_ids", {})
        self._state._account_ids[char.name] = account_id

        # Subclass selection if needed
        from ..engine.subclass import needs_subclass, run_subclass_selection
        if needs_subclass(char):
            await run_subclass_selection(
                char, send=self._async_send, recv=self._raw_readline,
            )
            from ..engine.persist import save_character
            save_character(conn, char, room_vnum,
                           account_id=account_id)

        return True

    async def _async_send(self, text: str) -> None:
        from ..color import diku_to_ansi
        await self._raw_send(diku_to_ansi(text) + "\r\n")

    # ── Game loop ─────────────────────────────────────────────────────────────

    async def run_game(self) -> None:
        from ..color import diku_to_ansi
        from ..engine.subclass import needs_subclass, run_subclass_selection

        name  = self._player_name
        state = self._state

        _srv = getattr(state, "_server", None)
        if _srv is not None and name:
            _srv._clients[name] = self

        char = state.characters.get(name)

        if char:
            await self._raw_send(
                f"\033[0mYou are \033[1;37m{char.name}\033[0m, a level "
                f"\033[1;37m{char.level}\033[0m {char.race} {char.cclass}.\r\n"
                f"Type \033[1;37mscore\033[0m, \033[1;37matt\033[0m, "
                f"\033[1;37mlook\033[0m, \033[1;37mkill <mob>\033[0m, "
                f"or \033[1;37mquit\033[0m.\r\n\r\n"
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
                    self._raw_readline(), timeout=0.5,
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

            # Subclass selection intercept
            char = state.characters.get(name)
            if char and needs_subclass(char):
                await run_subclass_selection(
                    char, send=self._async_send, recv=self._raw_readline,
                )
                if state._db:
                    from ..engine.persist import save_character
                    account_id = getattr(state, "_account_ids", {}).get(name, 0)
                    save_character(state._db, char,
                                   state.locations.get(name, 0),
                                   account_id=account_id)
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
