"""
main.py  —  Ashenmoor MUD entry point

Usage
─────
  python main.py                  Local shell only (offline, stdin/stdout)
  python main.py -s               Local shell + network server on :4000
  python main.py -s -nc           Network server only (no local shell)
  python main.py -s --port 4001   Custom port

Options
───────
  -s  / --serve       Also accept network connections (TCP/telnet/MCCP2)
  -nc / --no-console  Suppress the local stdin/stdout shell
  -p  / --port        TCP port to listen on (default: 4000)
"""

import sys
import os
import asyncio
import argparse

sys.path.insert(0, os.path.dirname(__file__))

from ashenmoor.core                import RACES
from ashenmoor.engine              import GameState
from ashenmoor.net.server          import MudServer
from ashenmoor.net.websocket       import WebSocketServer

from zones.the_void  import ZONE as THE_VOID
from zones.archer    import ZONE as ARCHER
from zones.asher     import ZONE as ASHER
from zones.charlotte import ZONE as CHARLOTTE
from zones.damien    import ZONE as DAMIEN
from zones.drew      import ZONE as DREW
from zones.eva       import ZONE as EVA
from zones.gabe      import ZONE as GABE
from zones.isaac     import ZONE as ISAAC
from zones.jordan    import ZONE as JORDAN
from zones.joshua    import ZONE as JOSHUA
from zones.lindi     import ZONE as LINDI
from zones.new_zone  import ZONE as NEW_ZONE
from zones.reese     import ZONE as REESE
from zones.timothy   import ZONE as TIMOTHY
from zones.wilson    import ZONE as WILSON
from zones.wyatt     import ZONE as WYATT
from zones.abyss     import ZONE as ABYSS

DB_PATH    = "ashenmoor.db"
START_ROOM = 99001   # Hub room in new_zone — where new characters spawn


# ── Argument parsing ───────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog        = "main.py",
        description = "Ashenmoor MUD server",
        formatter_class = argparse.RawDescriptionHelpFormatter,
        epilog = (
            "examples:\n"
            "  python main.py               # offline single-player shell\n"
            "  python main.py -s            # shell + network server\n"
            "  python main.py -s -nc        # network server only\n"
            "  python main.py -s -p 5000    # custom port\n"
        ),
    )
    parser.add_argument(
        "--serve", "-s",
        action  = "store_true",
        default = False,
        help    = "accept network connections (TCP telnet, port 4000)",
    )
    parser.add_argument(
        "--no-console", "-nc",
        dest    = "no_console",
        action  = "store_true",
        default = False,
        help    = "suppress local stdin/stdout shell",
    )
    parser.add_argument(
        "--port", "-p",
        type    = int,
        default = 4000,
        metavar = "PORT",
        help    = "TCP port to listen on (default: 4000, requires --serve)",
    )
    parser.add_argument(
        "--host",
        default = "0.0.0.0",
        metavar = "HOST",
        help    = "bind address for TCP server (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--ws-port",
        type    = int,
        default = 4001,
        metavar = "PORT",
        help    = "WebSocket port for browser clients (default: 4001)",
    )
    parser.add_argument(
        "--no-ws",
        action  = "store_true",
        default = False,
        help    = "disable the WebSocket server",
    )
    return parser.parse_args()


# ── World loading ──────────────────────────────────────────────────────────────

def load_world() -> GameState:
    state = GameState()
    state.load_world({}, {}, {})

    for zone in (
        THE_VOID, ARCHER, ASHER, CHARLOTTE, DAMIEN,
        DREW, EVA, GABE, ISAAC, JORDAN, JOSHUA,
        LINDI, NEW_ZONE, REESE, TIMOTHY, WILSON, WYATT, ABYSS
    ):
        state.load_zone(zone)

    print(f"[world] {len(state.rooms)} rooms loaded.", flush=True)
    return state


# ── Async main ─────────────────────────────────────────────────────────────────

async def async_main(args: argparse.Namespace) -> None:
    state      = load_world()
    mud_server = MudServer(state, host=args.host, port=args.port)
    ws_server  = WebSocketServer(
        state      = state,
        mud_server = mud_server,
        host       = "127.0.0.1",
        port       = args.ws_port,
    )
 
    serve   = args.serve
    console = not args.no_console
    run_ws  = serve and not args.no_ws   # WS only makes sense alongside --serve
 
    if not serve and not console:
        print(
            "error: --no-console requires --serve",
            file=sys.stderr,
        )
        sys.exit(1)
 
    mode_parts = []
    if console:  mode_parts.append("local console")
    if serve:    mode_parts.append(f"TCP:{args.port}")
    if run_ws:   mode_parts.append(f"WS:{args.ws_port}")
    print(f"[ashenmoor] starting: {' + '.join(mode_parts)}", flush=True)
 
    tasks = [
        mud_server.start(
            serve      = serve,
            console    = console,
            start_room = START_ROOM,
            races      = RACES,
            db_path    = DB_PATH,
        ),
    ]
 
    if run_ws:
        tasks.append(
            ws_server.start(
                start_room = START_ROOM,
                races      = RACES,
                db_path    = DB_PATH,
            )
        )
 
    await asyncio.gather(*tasks)


#async def async_main(args: argparse.Namespace) -> None:
#    state  = load_world()
#    server = MudServer(state, host=args.host, port=args.port)
#
#    serve   = args.serve
#    console = not args.no_console
#
#    if not serve and not console:
#        print(
#            "error: --no-console requires --serve  "
#            "(nothing to do without at least one client source)",
#            file=sys.stderr,
#        )
#        sys.exit(1)
#
#    if args.no_console and not args.serve:
#        print(
#            "warning: --no-console has no effect without --serve",
#            file=sys.stderr,
#        )
#
#    mode_parts = []
#    if console: mode_parts.append("local console")
#    if serve:   mode_parts.append(f"TCP server on {args.host}:{args.port}")
#    print(f"[ashenmoor] starting: {' + '.join(mode_parts)}", flush=True)
#
#    await server.start(
#        serve      = serve,
#        console    = console,
#        start_room = START_ROOM,
#        races      = RACES,
#        db_path    = DB_PATH,
#    )


# ── Entry point ────────────────────────────────────────────────────────────────

def main() -> None:
    args = parse_args()
    try:
        asyncio.run(async_main(args))
    except KeyboardInterrupt:
        print("\n[ashenmoor] shutting down.", flush=True)


if __name__ == "__main__":
    main()
