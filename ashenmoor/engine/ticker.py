"""
ashenmoor.engine.ticker
───────────────────────
Auto-combat REPL.

Uses select() on stdin so the combat tick fires every TICK_INTERVAL
seconds regardless of whether the player is typing.

Prompt behaviour
────────────────
  The prompt is only (re)printed when there is actually something to
  show the player:
    • The player typed a command  → show result, then prompt.
    • Combat tick produced output → show output, then prompt.
    • Idle timeout, no combat     → do nothing, no extra prompt printed.

This prevents the cursor line from being spammed with prompts while the
player is just standing around.
"""

import sys
import time
import select

from ..color import diku_to_ansi, cprint

TICK_INTERVAL = 4.0   # seconds between auto-attack rounds


def auto_crepl(
    state,
    prompt:    str   = "&g> &N",
    quit_cmds: tuple = ("quit", "exit", "q"),
    banner:    str   = "",
    farewell:  str   = "",
) -> None:
    """
    Drop-in replacement for crepl() with automatic combat ticks.

    While state.fighting is set:
      • An auto-attack round fires every TICK_INTERVAL seconds.
      • Powers fire immediately when typed, subject to their cooldown.
      • Movement is blocked (use 'flee' to escape).

    Outside combat the loop behaves like a normal REPL with no extra output.
    """
    if banner:
        cprint(banner)

    base_prompt = diku_to_ansi(prompt)

    def _build_prompt() -> str:
        """Show HP in the prompt while in combat."""
        if state.fighting:
            char = state.characters.get(state.player)
            if char:
                hp  = getattr(char, "hp",     "?")
                mhp = getattr(char, "max_hp",  "?")
                return diku_to_ansi(f"&w[&W{hp}&w/&W{mhp}&whp] &g>&N ")
        return base_prompt

    last_tick = time.monotonic()

    # Show the initial prompt once.
    sys.stdout.write(_build_prompt())
    sys.stdout.flush()

    while True:
        now          = time.monotonic()
        time_to_tick = max(0.05, TICK_INTERVAL - (now - last_tick))

        # Wait for input up to time_to_tick seconds.
        try:
            ready, _, _ = select.select([sys.stdin], [], [], time_to_tick)
        except (KeyboardInterrupt, EOFError):
            break

        # Track whether we have anything to show so we know whether to
        # reprint the prompt at the bottom of this iteration.
        need_prompt = False

        # ── Player typed something ────────────────────────────────────────
        if ready:
            try:
                raw = sys.stdin.readline()
            except (KeyboardInterrupt, EOFError):
                break

            if not raw:   # EOF — Ctrl-D
                break

            raw = raw.strip()

            if raw:
                if raw.lower() in quit_cmds:
                    break

                result = state.handle(raw)

                if result == "quit":
                    break

                sys.stdout.write("\n")
                if result:
                    cprint(result)
            else:
                # Player pressed Enter on a blank line — just drop to a
                # new line and give them a fresh prompt.
                sys.stdout.write("\n")

            # Always show a prompt after the player types something.
            need_prompt = True

        # ── Tick check ────────────────────────────────────────────────────
        now = time.monotonic()
        if (now - last_tick) >= TICK_INTERVAL:
            last_tick += TICK_INTERVAL   # advance by one interval, no drift

            if state.fighting:
                # Clear the current input line so output prints cleanly.
                sys.stdout.write("\r\033[K")
                output = state.combat_tick()
                if output:
                    cprint(output)
                    # Show a fresh prompt after combat output.
                    need_prompt = True

        # ── Reprint prompt only when needed ──────────────────────────────
        if need_prompt:
            sys.stdout.write(_build_prompt())
            sys.stdout.flush()

    if farewell:
        cprint(farewell)
