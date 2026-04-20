"""
diku_color.py
─────────────
Converts Diku/ROM/SMAUG-style color codes to ANSI escape sequences,
with a Colab-aware HTML renderer that matches the classic xterm 16-color
dark-terminal palette exactly.

Usage:
    cprint("&+cAshenmoor&N -- &Rwarning&N!")

    In a real terminal  → ANSI escape codes
    In Colab / Jupyter  → HTML with CSS colors on a black background,
                          matching xterm/PuTTY dark-terminal colors

Color codes:
    &N / &n   reset
    &r / &R   dark red      / bright red
    &g / &G   dark green    / bright green
    &b / &B   dark blue     / bright blue
    &c / &C   dark cyan     / bright cyan
    &y / &Y   dark yellow   / bright yellow
    &m / &M   dark magenta  / bright magenta
    &w / &W   dark grey     / bright white
    &x / &X   black         / dark grey
    &+X       same as uppercase (explicit bright-bit prefix)
    &&        literal ampersand
"""

import re

# ── ANSI escape helpers ───────────────────────────────────────────────────────

RESET = "\033[0m"

def _ansi(code: int, bold: bool = False) -> str:
    return f"\033[1;{code}m" if bold else f"\033[{code}m"

_BARE = {
    "x": (30, False),  "X": (30, True),
    "r": (31, False),  "R": (31, True),
    "g": (32, False),  "G": (32, True),
    "y": (33, False),  "Y": (33, True),
    "b": (34, False),  "B": (34, True),
    "m": (35, False),  "M": (35, True),
    "c": (36, False),  "C": (36, True),
    "w": (37, False),  "W": (37, True),
}
_PLUS = {ch.lower(): (code, True) for ch, (code, _) in _BARE.items()}
_PLUS.update({ch.upper(): (code, True) for ch, (code, _) in _BARE.items()})


# ── Classic xterm 16-color palette (dark background) ─────────────────────────
#
# These are the standard hex values used by xterm, PuTTY, and most
# Linux terminal emulators. They're what players would have seen on a
# real Diku MUD in the 90s. Colab dark mode background is very close
# to #0d1117 so these read almost identically to a real terminal.
#
#   Index  ANSI  Color            Normal      Bright
#     0    30    black            #000000     #555555
#     1    31    red              #AA0000     #FF5555
#     2    32    green            #00AA00     #55FF55
#     3    33    yellow           #AA5500     #FFFF55
#     4    34    blue             #0000AA     #5555FF
#     5    35    magenta          #AA00AA     #FF55FF
#     6    36    cyan             #00AAAA     #55FFFF
#     7    37    white            #AAAAAA     #FFFFFF

_XTERM_PALETTE = {
    #        (ansi_code, bold)  ->  hex color
    (30, False): "#000000",   # black
    (30, True):  "#555555",   # dark grey
    (31, False): "#AA0000",   # dark red
    (31, True):  "#FF5555",   # bright red
    (32, False): "#00AA00",   # dark green
    (32, True):  "#55FF55",   # bright green
    (33, False): "#AA5500",   # dark yellow / olive
    (33, True):  "#FFFF55",   # bright yellow
    (34, False): "#0000AA",   # dark blue
    (34, True):  "#5555FF",   # bright blue
    (35, False): "#AA00AA",   # dark magenta
    (35, True):  "#FF55FF",   # bright magenta
    (36, False): "#00AAAA",   # dark cyan
    (36, True):  "#55FFFF",   # bright cyan
    (37, False): "#AAAAAA",   # dark white / grey
    (37, True):  "#FFFFFF",   # bright white
}


# ── Token parser (shared by both renderers) ───────────────────────────────────

def _tokenize(text: str):
    """
    Yield (kind, value) tuples:
        ("text",   str)
        ("color",  (ansi_code, bold))
        ("reset",  None)
    """
    i = 0
    n = len(text)
    while i < n:
        if text[i] != "&":
            # collect a run of plain characters
            j = i + 1
            while j < n and text[j] != "&":
                j += 1
            yield ("text", text[i:j])
            i = j
            continue

        if i + 1 >= n:
            yield ("text", "&"); i += 1; continue

        ch = text[i + 1]

        if ch == "&":
            yield ("text", "&"); i += 2; continue

        if ch in ("N", "n"):
            yield ("reset", None); i += 2; continue

        if ch == "+" and i + 2 < n:
            entry = _PLUS.get(text[i + 2])
            if entry:
                yield ("color", entry); i += 3; continue
            yield ("text", "&"); i += 1; continue

        entry = _BARE.get(ch)
        if entry:
            yield ("color", entry); i += 2; continue

        yield ("text", "&"); i += 1


# ── ANSI renderer ─────────────────────────────────────────────────────────────

def diku_to_ansi(text: str) -> str:
    """Replace Diku color codes with ANSI escape sequences."""
    parts = []
    for kind, value in _tokenize(text):
        if kind == "text":
            parts.append(value)
        elif kind == "color":
            parts.append(_ansi(*value))
        elif kind == "reset":
            parts.append(RESET)
    return "".join(parts)


# ── HTML renderer (Colab / Jupyter) ──────────────────────────────────────────

def _html_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def diku_to_html(text: str, bg: str = "#0d0d0d") -> str:
    """
    Convert Diku color codes to an HTML snippet styled to match a classic
    dark-background terminal using the standard xterm 16-color palette.

    bg defaults to near-black (#0d0d0d), matching Colab dark mode.
    Pass bg=None to omit the wrapper div (embed in your own container).
    """
    DEFAULT_FG = "#AAAAAA"   # grey — same as a bare terminal prompt

    parts = []
    current_color = None    # None means "use default fg"

    def open_span(color_hex):
        return f'<span style="color:{color_hex}">'

    for kind, value in _tokenize(text):
        if kind == "text":
            txt = _html_escape(value).replace("\n", "<br>")
            if txt:
                if current_color:
                    parts.append(open_span(current_color))
                    parts.append(txt)
                    parts.append("</span>")
                else:
                    parts.append(f'<span style="color:{DEFAULT_FG}">{txt}</span>')

        elif kind == "color":
            current_color = _XTERM_PALETTE.get(value, DEFAULT_FG)

        elif kind == "reset":
            current_color = None

    inner = "".join(parts)

    if bg is None:
        return inner

    return (
        f'<div style="background:{bg}; font-family:\'Courier New\',monospace; '
        f'font-size:14px; padding:8px 12px; border-radius:4px; '
        f'line-height:1.5; white-space:pre-wrap;">'
        f'{inner}</div>'
    )


# ── cprint: auto-detects Colab vs real terminal ───────────────────────────────

def _in_notebook() -> bool:
    """True when running inside Jupyter / Colab."""
    try:
        from IPython import get_ipython
        return get_ipython() is not None
    except ImportError:
        return False


def cprint(*args, sep: str = " ", end: str = "\n") -> None:
    """
    Drop-in replacement for print() that colorizes Diku codes.

    Accepts any objects, exactly like print() — each argument is converted
    to a string via str(), joined with sep, then colorized for the current
    environment:

        Terminal   : ANSI escape codes
        Colab/Jupyter : HTML rendered via IPython.display

    This means __repr__ / __str__ methods can return raw Diku-coded strings
    and cprint() will handle the colorization automatically:

        class Room:
            def __str__(self):
                return "&+WTHE RUSTY FLAGON&N\\nSmoky and warm."

        cprint(room)          # works — no color() call needed inside __str__
        cprint(room, player)  # works — stringifies both, joins, colorizes
        cprint("&Rhp:&N", 42) # works — mixed types fine
    """
    text = sep.join(str(a) for a in args)
    if _in_notebook():
        from IPython.display import display, HTML
        display(HTML(diku_to_html(text)))
    else:
        print(diku_to_ansi(text) + RESET, end=end)


def cstrip(text: str) -> str:
    """Remove all Diku color codes, returning plain text."""
    return re.sub(r"&&|&[Nn]|&\+?[a-zA-Z]",
                  lambda m: "&" if m.group() == "&&" else "",
                  text)

def color(text: str) -> str:
  return diku_to_ansi(text) + RESET

class ColorString(str):
    """
    A str subclass returned by color(..., "html").

    Behaves exactly like a regular string in every context — concatenation,
    slicing, len(), storing in a variable — but adds two extras:

      _repr_html_()   Colab/Jupyter calls this automatically when the object
                      is the last expression in a cell, so it renders as
                      colored HTML without you doing anything special.

      .display()      Explicitly push the HTML to the Colab output cell.
                      Use this when the color() call is NOT the last
                      expression, e.g. inside a loop or function.

    Never pass to print() — print() always writes the raw string, bypassing
    the HTML renderer.  Use cprint() or .display() instead.
    """
    def _repr_html_(self):
        return str(self)

    def display(self):
        """Render this HTML string in the current Colab / Jupyter output cell."""
        from IPython.display import display as _display, HTML
        _display(HTML(str(self)))


def color(text: str, mode: str = "ansi") -> str:
    """
    Convert a Diku-colored string and return the result.

    Parameters
    ----------
    text : str
        String containing Diku color codes (&+c, &R, &N, etc.)
    mode : str
        "ansi"  (default)
            Returns a plain str with ANSI escape sequences.
            Correct output when passed to print() in a real terminal.

        "html"
            Returns a ColorString (str subclass) containing an HTML
            snippet with inline CSS colors on a dark background.

            DO NOT pass to print() — print() always writes raw text.
            Instead use one of:
              color(s, "html").display()        explicit render
              cprint(s)                         auto-detects env, always right
            Or let it be the last expression in a Colab cell and Colab
            renders it automatically via _repr_html_().

    Returns
    -------
    str or ColorString
        "ansi" mode  ->  plain str  (ANSI escapes inside)
        "html" mode  ->  ColorString  (HTML that auto-renders in Colab)

    Examples
    --------
        # terminal
        print(color("&+cHello&N world"))

        # Colab — three equivalent ways
        cprint("&+cHello&N world")                    # easiest, always correct
        color("&+cHello&N world", "html").display()   # explicit render
        color("&+cHello&N world", "html")             # last expression in cell
    """
    if mode == "html":
        return ColorString(diku_to_html(text))
    return diku_to_ansi(text) + RESET


def cinput(prompt: str = "") -> str:
    """
    Colorized input(). Displays a Diku-coded prompt then reads a line.

    Terminal  : passes the ANSI-converted prompt directly to input(), so
                the prompt and cursor appear on the same line as normal.
    Colab     : cprints the prompt (rendered HTML), then calls input("")
                so the text box appears on the line below the prompt.

    Returns the raw string the user typed, stripped of leading/trailing
    whitespace. Never returns color codes — input is always plain text.

    Examples
    --------
        name = cinput("&+WEnter your name:&N ")
        cmd  = cinput("&Y>&N ")
    """
    if _in_notebook():
        cprint(prompt, end="")
        return input("").strip()
    else:
        return input(diku_to_ansi(prompt) + RESET).strip()

def crepl(
    handler,
    prompt:    str = "&g> &N ",
    banner:    str = "",
    farewell:  str = "",
) -> None:

    if banner:
        cprint(banner)
    
    cprint(rooms[locations['Moted']])
    while True:
        try:
            raw = cinput(prompt)
        except (EOFError, KeyboardInterrupt):
            break
        if not raw:
            continue
        result = handler(raw)
        if result == 'quit':
            break
        if result is not None and result != "":
            cprint(result)

    if farewell:
        cprint(farewell)
