"""
ashenmoor.net.websocket
───────────────────────
WebSocket transport for browser-based clients.

Drop-in alongside the existing TCP/telnet stack.  A WebSocketClient
implements the same MudClient ABC as NetworkClient, so the entire game
loop, login, tick system, and MCCP2 support work without modification.

Architecture
────────────
  Browser  ←→  WS frame  ←→  WebSocketClient._raw_send / _raw_readline
                                        ↓
                                  diku_to_ansi()    (same as telnet)
                                        ↓
                              GameState.handle()    (unchanged)

MCCP2 note
──────────
  The `websockets` library supports the permessage-deflate extension
  natively.  When the browser negotiates it, every frame is compressed
  transparently — no application-level zlib needed.  This gives you
  equivalent bandwidth savings to MCCP2 without any extra code.

  If you specifically need MCCP2-inside-WS-frames for a non-browser
  client that understands both, wrap CompressingWriter around the send
  path exactly as NetworkClient does; the framing is orthogonal.

Telnet IAC stripping
────────────────────
  Browser clients don't send telnet IAC sequences, so TelnetParser is
  NOT used here.  The raw text from the frame goes straight to the game.

Usage — in main.py
──────────────────
  from ashenmoor.net.websocket import WebSocketServer

  ws_server = WebSocketServer(state, host="0.0.0.0", port=4001)
  # run alongside MudServer inside async_main:
  await asyncio.gather(
      mud_server.start(serve=True, console=True, ...),
      ws_server.start(start_room=START_ROOM, races=RACES, db_path=DB_PATH),
  )

nginx config (snippet)
──────────────────────
  location /ws {
      proxy_pass         http://127.0.0.1:4001;
      proxy_http_version 1.1;
      proxy_set_header   Upgrade    $http_upgrade;
      proxy_set_header   Connection "upgrade";
      proxy_set_header   Host       $host;
      proxy_buffering    off;
      proxy_read_timeout 3600s;
  }
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

try:
    import websockets                              # pip install websockets
    from websockets.server import ServerConnection as _WsConn
except ImportError:
    websockets = None                              # type: ignore
    _WsConn    = None                              # type: ignore

from .client import MudClient, TICK_INTERVAL

if TYPE_CHECKING:
    from ..engine.game import GameState

log = logging.getLogger(__name__)


# ── WebSocketClient ───────────────────────────────────────────────────────────

class WebSocketClient(MudClient):
    """
    One connected browser session.

    Wraps a `websockets` connection as an async line-oriented stream.
    Partial lines (browser sent text without a newline, which never
    actually happens from our web client) are buffered and returned
    only when a newline or carriage-return is seen.

    Text encoding: UTF-8 throughout.  The web client sends plain text
    commands; the server sends ANSI-colored UTF-8 strings.

    Each send() call becomes one WebSocket text frame — the browser's
    terminal splits on \\r\\n just like it would with raw telnet.
    """

    def __init__(self, state: "GameState", websocket: "_WsConn"):
        super().__init__(state)
        self._ws      = websocket
        self._linebuf = ""          # partial-line accumulator
        # asyncio.Queue so tick output can be delivered between readline calls
        self._recv_queue: asyncio.Queue[str | None] = asyncio.Queue()
        self._recv_task: asyncio.Task | None = None

    # ── Internal reader task ──────────────────────────────────────────────────

    def _start_recv_task(self) -> None:
        """
        Pump incoming WebSocket messages into self._recv_queue.

        Runs as a background task so _raw_readline() can be cancelled
        by asyncio.wait_for() without killing the underlying socket.
        """
        loop = asyncio.get_event_loop()
        self._recv_task = loop.create_task(self._recv_loop(), name="ws-recv")

    async def _recv_loop(self) -> None:
        try:
            async for message in self._ws:
                if isinstance(message, bytes):
                    message = message.decode("utf-8", errors="replace")
                await self._recv_queue.put(message)
        except Exception:
            pass
        finally:
            await self._recv_queue.put(None)   # EOF sentinel

    # ── MudClient interface ───────────────────────────────────────────────────

    async def _raw_send(self, text: str) -> None:
        """
        Send text to the browser as a single WebSocket frame.

        Normalises line endings to \\r\\n so the terminal renderer
        in mud-client.html sees clean lines regardless of what the
        game engine produces.
        """
        normalised = (
            text.replace("\r\n", "\n")
                .replace("\r",   "\n")
                .replace("\n",   "\r\n")
        )
        try:
            await self._ws.send(normalised)
        except Exception as exc:
            log.debug("WebSocket send error: %s", exc)
            self._closed = True

    async def _raw_readline(self) -> str:
        """
        Return one complete line from the browser, stripping the terminator.

        Blocks until a complete line arrives or the connection closes.
        Never raises TimeoutError — polls internally with a short timeout
        to stay cancellable without blocking the event loop forever.
        Raises EOFError only when the WebSocket is genuinely closed.
        """
        while True:
            # Return immediately if the buffer already has a complete line
            for sep in ("\r\n", "\n", "\r"):
                if sep in self._linebuf:
                    line, _, self._linebuf = self._linebuf.partition(sep)
                    return line.strip()

            # Poll with a short timeout so we remain cancellable while
            # waiting for a slow typist.  Timeout is NOT an error here.
            try:
                chunk = await asyncio.wait_for(
                    self._recv_queue.get(), timeout=0.5
                )
            except (asyncio.TimeoutError, TimeoutError):
                continue   # no data yet — loop back and wait again

            if chunk is None:
                raise EOFError("WebSocket closed")

            self._linebuf += chunk

    async def close(self) -> None:
        self._closed = True
        if self._recv_task and not self._recv_task.done():
            self._recv_task.cancel()
        try:
            await self._ws.close()
        except Exception:
            pass


# ── WebSocketServer ───────────────────────────────────────────────────────────

class WebSocketServer:
    """
    Listens for WebSocket connections and runs a full MudClient session
    for each one, integrated with the existing MudServer tick loop.

    Parameters
    ----------
    state      : GameState   shared with the TCP MudServer
    mud_server : MudServer   the existing server — we register clients
                             in its _clients dict so they receive ticks
    host       : str         bind address (default 0.0.0.0)
    port       : int         WebSocket port (default 4001)
    """

    def __init__(
        self,
        state:      "GameState",
        mud_server,                 # MudServer — avoids circular import
        host:       str = "0.0.0.0",
        port:       int = 4001,
    ):
        if websockets is None:
            raise RuntimeError(
                "websockets package not found.\n"
                "Install it with:  pip install websockets"
            )
        self._state      = state
        self._mud_server = mud_server
        self._host       = host
        self._port       = port

    async def _handle(
        self,
        websocket: "_WsConn",
        start_room: int,
        races:      dict,
        db_path:    str,
    ) -> None:
        addr = websocket.remote_address
        print(f"[ws] connection from {addr[0]}:{addr[1]}", flush=True)

        client = WebSocketClient(self._state, websocket)
        client._start_recv_task()

        try:
            ok = await client.run_login(start_room, races, db_path)
            if ok:
                # Register with the mud_server tick loop so combat ticks,
                # rest ticks, mob aggro, and HP regen all reach this client.
                name = client._player_name
                if name:
                    self._mud_server._clients[name] = client

                await client.run_game()
        except Exception as exc:
            log.exception("WebSocket session error: %s", exc)
        finally:
            name = client._player_name
            if name:
                self._mud_server._clients.pop(name, None)
                self._state.characters.pop(name, None)
                self._state.locations.pop(name,  None)
                self._state.fighting.pop(name,   None)
                self._state._resting.pop(name,   None)
            await client.close()
            print(f"[ws] {addr[0]}:{addr[1]} disconnected", flush=True)

    async def start(
        self,
        start_room: int  = 1,
        races:      dict | None = None,
        db_path:    str  = "ashenmoor.db",
    ) -> None:
        if races is None:
            from ..core import RACES
            races = RACES

        async def handler(ws):
            await self._handle(ws, start_room, races, db_path)

        print(f"[ws] listening on {self._host}:{self._port}", flush=True)
        async with websockets.serve(
            handler,
            self._host,
            self._port,
            # permessage-deflate: browser-transparent compression
            # equivalent to MCCP2 without any application-level zlib
            compression="deflate",
            # Generous ping/pong to keep connections alive through nginx
            ping_interval=30,
            ping_timeout=10,
            # Allow large messages (zone descriptions can be verbose)
            max_size=2**20,
        ):
            await asyncio.Future()   # run forever until task is cancelled
