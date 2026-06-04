"""
ashenmoor.net.telnet — from document index 28, WILL ECHO removed
"""

import zlib
from typing import Callable

IAC  = 255
SE   = 240
NOP  = 241
GA   = 249
SB   = 250
WILL = 251
WONT = 252
DO   = 253
DONT = 254

OPT_ECHO     = 1
OPT_SGA      = 3
OPT_TTYPE    = 24
OPT_NAWS     = 31
OPT_LINEMODE = 34
OPT_MCCP2    = 86

MCCP2_START = bytes([IAC, SB, OPT_MCCP2, IAC, SE])

_S_NORMAL  = 0
_S_IAC     = 1
_S_VERB    = 2
_S_SB      = 3
_S_SB_IAC  = 4


class TelnetParser:
    def __init__(
        self,
        raw_write: Callable[[bytes], None],
        on_compress_start: Callable[[], None] | None = None,
    ):
        self._write             = raw_write
        self._on_compress_start = on_compress_start
        self._state             = _S_NORMAL
        self._verb: int | None  = None
        self._sb_opt: int | None = None
        self._sb_buf             = bytearray()

    def offer_options(self) -> None:
        """
        Send initial negotiations on connect.
        WILL ECHO is intentionally omitted — the client (e.g. TinTin++)
        handles local echo in split mode. Server-side character echo
        causes characters to appear in the output pane instead of the
        input pane.
        """
        self._write(bytes([
            IAC, WILL, OPT_SGA,
            IAC, DO,   OPT_SGA,
            IAC, WILL, OPT_MCCP2,
        ]))

    def offer_mccp2(self) -> None:
        self.offer_options()

    def feed(self, data: bytes) -> bytes:
        out = bytearray()
        for b in data:
            if   self._state == _S_NORMAL:  self._normal(b, out)
            elif self._state == _S_IAC:     self._iac(b, out)
            elif self._state == _S_VERB:    self._verb_byte(b)
            elif self._state == _S_SB:      self._sb(b)
            elif self._state == _S_SB_IAC:  self._sb_iac(b)
        return bytes(out)

    def _normal(self, b: int, out: bytearray) -> None:
        if b == IAC:
            self._state = _S_IAC
        else:
            out.append(b)

    def _iac(self, b: int, out: bytearray) -> None:
        if b == IAC:
            out.append(IAC)
            self._state = _S_NORMAL
        elif b in (WILL, WONT, DO, DONT):
            self._verb  = b
            self._state = _S_VERB
        elif b == SB:
            self._sb_opt = None
            self._sb_buf.clear()
            self._state  = _S_SB
        else:
            self._state = _S_NORMAL

    def _verb_byte(self, opt: int) -> None:
        self._respond(self._verb, opt)
        self._state = _S_NORMAL

    def _sb(self, b: int) -> None:
        if b == IAC:
            self._state = _S_SB_IAC
        elif self._sb_opt is None:
            self._sb_opt = b
        else:
            self._sb_buf.append(b)

    def _sb_iac(self, b: int) -> None:
        if b == SE:
            self._handle_sb(self._sb_opt, bytes(self._sb_buf))
            self._state = _S_NORMAL
        else:
            self._sb_buf.append(b)
            self._state = _S_SB

    def _respond(self, verb: int, opt: int) -> None:
        if verb == DO:
            if opt == OPT_MCCP2:
                self._write(MCCP2_START)
                if self._on_compress_start:
                    self._on_compress_start()
            elif opt in (OPT_SGA,):
                pass
            else:
                self._write(bytes([IAC, WONT, opt]))

        elif verb == WILL:
            if opt in (OPT_TTYPE, OPT_NAWS, OPT_SGA):
                self._write(bytes([IAC, DO, opt]))
            elif opt == OPT_LINEMODE:
                self._write(bytes([IAC, DONT, OPT_LINEMODE]))
            else:
                self._write(bytes([IAC, DONT, opt]))

        elif verb == DONT:
            pass

        elif verb == WONT:
            pass

    def _handle_sb(self, opt: int | None, data: bytes) -> None:
        pass


class CompressingWriter:
    def __init__(self, writer):
        self._writer     = writer
        self._compressor = None

    def start_compression(self) -> None:
        self._compressor = zlib.compressobj(zlib.Z_DEFAULT_COMPRESSION)

    @property
    def compressing(self) -> bool:
        return self._compressor is not None

    def write(self, data: bytes) -> None:
        if self._compressor:
            chunk  = self._compressor.compress(data)
            chunk += self._compressor.flush(zlib.Z_SYNC_FLUSH)
            self._writer.write(chunk)
        else:
            self._writer.write(data)

    async def drain(self) -> None:
        await self._writer.drain()

    def close(self) -> None:
        self._writer.close()

    async def wait_closed(self) -> None:
        await self._writer.wait_closed()

    @property
    def transport(self):
        return self._writer.transport
