"""
ashenmoor.net.server
────────────────────
Concrete client implementations and the TCP server.

LocalConsoleClient uses a daemon thread to read stdin so the terminal
stays in normal cooked mode (Enter sends \\n, backspace works, no ^M).
Lines are shuttled into an asyncio.Queue; the game loop awaits on that.
When asyncio.wait_for cancels the Queue.get() during idle periods, no
data is ever lost — the queue itself is unaffected.

NetworkClient uses asyncio StreamReader + telnet IAC parser + MCCP2.

Two async loops run independently:
  _tick_loop      — every 4 seconds: combat, mob aggro, rest ability restore
  _hp_regen_loop  — every 1 second:  silent out-of-combat HP regeneration
"""

from __future__ import annotations
import asyncio
import sys
import threading
from typing import TYPE_CHECKING

from .client  import MudClient, TICK_INTERVAL
from .telnet  import TelnetParser, CompressingWriter

if TYPE_CHECKING:
    from ..engine.game import GameState


# ── Local console client ──────────────────────────────────────────────────────

class LocalConsoleClient(MudClient):
    """
    stdin / stdout shell — no telnet negotiation.

    A daemon thread reads from stdin using the normal blocking readline,
    keeping the terminal in cooked mode.  This means:
      - Enter sends \\n  (not \\r / ^M)
      - Backspace works normally
      - Ctrl-C / Ctrl-D are handled by the OS as expected

    Lines are placed into an asyncio.Queue via call_soon_threadsafe.
    The async game loop awaits Queue.get() with a short timeout so it
    can flush tick output between keystrokes.  Cancelling Queue.get()
    while the queue is empty is safe — no data is consumed or lost.
    """

    def __init__(self, state: "GameState"):
        super().__init__(state)
        self._line_queue: asyncio.Queue[str | None] = asyncio.Queue()
        self._reader_started = False

    def _start_stdin_reader(self) -> None:
        """
        Spawn a single daemon thread that reads stdin lines forever.
        Puts each stripped line into the queue; puts None on EOF.
        Called lazily on the first _raw_readline() so the event loop
        is already running when we call get_event_loop().
        """
        loop = asyncio.get_event_loop()

        def _read_loop() -> None:
            while True:
                try:
                    raw = sys.stdin.readline()
                except Exception:
                    raw = ""
                line: str | None = raw.rstrip("\r\n") if raw else None
                loop.call_soon_threadsafe(self._line_queue.put_nowait, line)
                if line is None:
                    break   # EOF — stop the thread

        t = threading.Thread(target=_read_loop, daemon=True, name="stdin-reader")
        t.start()
        self._reader_started = True

    async def _raw_send(self, text: str) -> None:
        sys.stdout.write(text)
        sys.stdout.flush()

    async def _raw_readline(self) -> str:
        if not self._reader_started:
            self._start_stdin_reader()
        line = await self._line_queue.get()
        if line is None:
            raise EOFError("stdin closed")
        return line

    async def close(self) -> None:
        self._closed = True


# ── Network client ─────────────────────────────────────────────────────────────

class NetworkClient(MudClient):
    """
    Remote player over TCP with server-side echo and MCCP2 support.
    """

    def __init__(self, state: "GameState",
                 reader: asyncio.StreamReader,
                 writer: asyncio.StreamWriter):
        super().__init__(state)
        self._reader  = reader
        self._cwriter = CompressingWriter(writer)
        self._parser  = TelnetParser(
            raw_write         = writer.write,
            on_compress_start = self._cwriter.start_compression,
        )
        self._linebuf = bytearray()

    async def _raw_send(self, text: str) -> None:
        normalized = text.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\r\n")
        data = normalized.encode("utf-8", errors="replace")
        self._cwriter.write(data)
        await self._cwriter.drain()

    async def _raw_readline(self) -> str:
        while True:
            try:
                chunk = await self._reader.read(512)
            except (ConnectionResetError, asyncio.IncompleteReadError):
                raise EOFError("disconnected")

            if not chunk:
                raise EOFError("disconnected")

            clean = self._parser.feed(chunk)

            for byte in clean:
                if byte == 0x0d:
                    line = self._linebuf.decode("utf-8", errors="replace").strip()
                    self._linebuf.clear()
                    self._cwriter.write(b"\r\n")
                    await self._cwriter.drain()
                    if line:
                        return line
                elif byte == 0x0a:
                    continue
                elif byte in (0x7f, 0x08):
                    if self._linebuf:
                        self._linebuf.pop()
                        self._cwriter.write(b"\x08 \x08")
                        await self._cwriter.drain()
                elif 0x20 <= byte < 0x7f:
                    self._linebuf.append(byte)
                    self._cwriter.write(bytes([byte]))
                    await self._cwriter.drain()

    async def close(self) -> None:
        self._closed = True
        try:
            self._cwriter.close()
            await self._cwriter.wait_closed()
        except Exception:
            pass


# ── MudServer ──────────────────────────────────────────────────────────────────

class MudServer:

    def __init__(
        self,
        state: "GameState",
        host:  str = "0.0.0.0",
        port:  int = 4000,
    ):
        self._state   = state
        self._host    = host
        self._port    = port
        self._clients: dict[str, MudClient] = {}

    # ── 4-second tick: combat / rest / aggro ──────────────────────────────────

    async def _tick_loop(self) -> None:
        while True:
            await asyncio.sleep(TICK_INTERVAL)
            for name, client in list(self._clients.items()):
                if client._closed:
                    self._clients.pop(name, None)
                    continue

                state = self._state
                char  = state.characters.get(name)
                wimpy = getattr(char, "wimpy", None) if char else None

                # Status effects tick every 4 seconds regardless of combat state
                effect_out = state.effect_tick(player_name=name)
                if effect_out:
                    await client.send(effect_out)

                if name in state.fighting:
                    if wimpy and char and char.hp <= wimpy:
                        flee_out = state.handle("flee", player_name=name)
                        if flee_out and flee_out != "quit":
                            await client.send(flee_out)
                        continue
                    output = state.combat_tick(player_name=name)
                    if output:
                        await client.send(output)
                else:
                    rest_out = state.rest_tick(player_name=name)
                    if rest_out:
                        await client.send(rest_out)
                    aggro_out = state.mob_aggro_tick(player_name=name)
                    if aggro_out:
                        await client.send(aggro_out)

    # ── 1-second tick: HP regeneration ────────────────────────────────────────

    async def _hp_regen_loop(self) -> None:
        """HP regen and game clock tick every 4 seconds."""
        from ..world.calendar import HOUR_ANNOUNCES
        from ..engine.persist import save_world_time

        while True:
            await asyncio.sleep(TICK_INTERVAL)

            # -- Advance game clock ------------------------------------------
            gt       = self._state.game_time
            prev_hr  = gt.hour
            gt.advance(4)          # 4 real seconds = 4 game minutes
            new_hr   = gt.hour

            # Save time to DB every real minute (15 ticks)
            if gt.total_minutes % 15 == 0 and self._state._db is not None:
                try:
                    save_world_time(self._state._db, gt.total_minutes)
                except Exception:
                    pass

            # -- Broadcast hour announcements --------------------------------
            announce = HOUR_ANNOUNCES.get(new_hr) if new_hr != prev_hr else None

            # -- HP regen for all connected players --------------------------
            for name in list(self._clients):
                client = self._clients.get(name)
                if client is None or client._closed:
                    continue
                self._state.hp_regen_tick(player_name=name)

                # Send time announcement if the hour changed and toggle is on
                if announce:
                    char    = self._state.characters.get(name)
                    toggles = getattr(char, "toggles", {}) if char else {}
                    if toggles.get("time_announce", True):
                        await client.send(announce)

    # ── Per-client wrapper ────────────────────────────────────────────────────

    async def _run_client(self, client: MudClient, start_room: int,
                          races: dict, db_path: str) -> None:
        await client.run(start_room, races, db_path)
        name = client._player_name
        if name:
            self._clients.pop(name, None)
            self._state.characters.pop(name, None)
            self._state.locations.pop(name,  None)
            self._state.fighting.pop(name,   None)
            self._state._resting.pop(name,   None)

    async def _on_connect(self, reader: asyncio.StreamReader,
                          writer: asyncio.StreamWriter,
                          start_room: int, races: dict,
                          db_path: str) -> None:
        addr = writer.get_extra_info("peername", ("?", 0))
        print(f"[net] connection from {addr[0]}:{addr[1]}", flush=True)
        client = NetworkClient(self._state, reader, writer)
        client._parser.offer_options()
        await self._run_client(client, start_room, races, db_path)
        print(f"[net] {addr[0]}:{addr[1]} disconnected", flush=True)

    # ── Entry point ────────────────────────────────────────────────────────────

    async def start(
        self,
        serve:      bool      = False,
        console:    bool      = True,
        start_room: int       = 1,
        races:      dict|None = None,
        db_path:    str       = "ashenmoor.db",
    ) -> None:
        if races is None:
            from ..core import RACES
            races = RACES

        tasks = []

        # Pre-load world clock from DB if available
        try:
            from ..engine.persist import open_db, load_world_time
            _tmp_conn = open_db(db_path)
            self._state.game_time.total_minutes = load_world_time(_tmp_conn)
            if self._state._db is None:
                self._state._db = _tmp_conn
        except Exception:
            pass  # fresh DB or unavailable -- stays at epoch

        tick_task           = asyncio.create_task(self._tick_loop())
        regen_task          = asyncio.create_task(self._hp_regen_loop())
        self._state._server = self

        tcp_server = None
        if serve:
            tcp_server = await asyncio.start_server(
                lambda r, w: self._on_connect(r, w, start_room, races, db_path),
                host=self._host,
                port=self._port,
            )
            addr = tcp_server.sockets[0].getsockname()
            print(f"[net] listening on {addr[0]}:{addr[1]}", flush=True)
            tasks.append(asyncio.create_task(tcp_server.serve_forever()))

        if console:
            console_client = LocalConsoleClient(self._state)
            console_task   = asyncio.create_task(
                self._run_client(console_client, start_room, races, db_path)
            )
            tasks.append(console_task)

            async def _watch_console() -> None:
                await console_task
                n = console_client._player_name
                if n:
                    self._clients.pop(n, None)
                if not serve:
                    tick_task.cancel()
                    regen_task.cancel()

            tasks.append(asyncio.create_task(_watch_console()))

        if not tasks:
            print("[net] nothing to do — no --serve and no console", flush=True)
            tick_task.cancel()
            regen_task.cancel()
            return

        try:
            if serve and not console:
                await asyncio.gather(*tasks, return_exceptions=True)
            else:
                done, pending = await asyncio.wait(
                    tasks, return_when=asyncio.FIRST_COMPLETED
                )
                for t in pending:
                    t.cancel()
        finally:
            tick_task.cancel()
            regen_task.cancel()
            if tcp_server:
                tcp_server.close()
                await tcp_server.wait_closed()
