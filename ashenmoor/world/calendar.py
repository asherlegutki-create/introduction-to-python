"""
ashenmoor.world.calendar
------------------------
Faerun Calendar of Harptos.

Time scale:
    1 real second  = 1 game minute
    60 real seconds = 1 game hour
    24 real minutes = 1 game day
    ~12 real hours  = 1 game month  (30 days)
    ~6 real days    = 1 game year   (365 days)

Epoch: 1 Flamerule 867 DR, 06:00
"""

from __future__ import annotations

# -- Year structure: (period_name, days, is_festival) -------------------------

YEAR_STRUCTURE: list[tuple[str, int, bool]] = [
    ("Hammer",            30, False),
    ("Midwinter",          1, True),
    ("Alturiak",          30, False),
    ("Ches",              30, False),
    ("Tarsakh",           30, False),
    ("Greengrass",         1, True),
    ("Mirtul",            30, False),
    ("Kythorn",           30, False),
    ("Flamerule",         30, False),
    ("Midsummer",          1, True),
    ("Eleasis",           30, False),
    ("Eleint",            30, False),
    ("Highharvestide",     1, True),
    ("Marpenoth",         30, False),
    ("Uktar",             30, False),
    ("Feast of the Moon",  1, True),
    ("Nightal",           30, False),
]

DAYS_PER_YEAR = sum(d for _, d, _ in YEAR_STRUCTURE)   # 365

# Season by month name
SEASONS: dict[str, str] = {
    "Hammer":    "Deepwinter",
    "Alturiak":  "The Claw of Winter",
    "Ches":      "The Claw of Sunsets",
    "Tarsakh":   "The Claw of Storms",
    "Mirtul":    "The Melting",
    "Kythorn":   "The Time of Flowers",
    "Flamerule": "Summertide",
    "Eleasis":   "Highsun",
    "Eleint":    "The Fading",
    "Marpenoth": "Leaffall",
    "Uktar":     "The Rotting",
    "Nightal":   "The Drawing Down",
}

# Moon phases keyed by day-of-month (1-30); festivals use day 1
MOON_PHASES: list[tuple[range, str, str]] = [
    (range(1,  3),  "new moon",         "&x(O)&N"),
    (range(3,  8),  "waxing crescent",  "&w(@)&N"),
    (range(8,  12), "first quarter",    "&W( )&N"),
    (range(12, 16), "waxing gibbous",   "&W(@)&N"),
    (range(16, 21), "full moon",        "&W(O)&N"),
    (range(21, 25), "waning gibbous",   "&w(@)&N"),
    (range(25, 29), "last quarter",     "&w( )&N"),
    (range(29, 31), "waning crescent",  "&x(@)&N"),
]

# Epoch constants
EPOCH_YEAR      = 867
EPOCH_HOUR      = 6         # 06:00 at start
MINUTES_PER_DAY = 24 * 60   # 1440

# 0-indexed day-of-year for 1 Flamerule (day 183 = index 182)
_EPOCH_DOY0 = sum(d for _, d, _ in YEAR_STRUCTURE[:8])   # 182

# Announcements keyed by hour (0-23) -- sent to all players with toggle on
HOUR_ANNOUNCES: dict[int, str] = {
    0:  "&cThe witching hour falls across Faerun. Midnight.&N",
    6:  "&YThe sun rises on the horizon, golden light spreading across the land.&N",
    19: "&YThe sun dips below the horizon, long shadows falling across the land.&N",
}


# -- GameTime -----------------------------------------------------------------

class GameTime:
    """
    Tracks Faerun game time as total minutes elapsed since the epoch.

    Epoch = 1 Flamerule 867 DR, 06:00.
    total_minutes starts at 0 and is incremented by 1 each real second.
    """

    def __init__(self, total_minutes: int = 0) -> None:
        self.total_minutes = total_minutes

    # -- Internal helpers -----------------------------------------------------

    @property
    def _abs_day0(self) -> int:
        """0-indexed absolute day since year 0 day 0, accounting for epoch."""
        epoch_days = _EPOCH_DOY0 + EPOCH_YEAR * DAYS_PER_YEAR
        mins       = self.total_minutes + EPOCH_HOUR * 60 + epoch_days * MINUTES_PER_DAY
        return mins // MINUTES_PER_DAY

    @property
    def _minute_of_day(self) -> int:
        mins = self.total_minutes + EPOCH_HOUR * 60
        return mins % MINUTES_PER_DAY

    # -- Time components ------------------------------------------------------

    @property
    def hour(self) -> int:
        return self._minute_of_day // 60

    @property
    def minute(self) -> int:
        return self._minute_of_day % 60

    @property
    def year(self) -> int:
        return self._abs_day0 // DAYS_PER_YEAR

    @property
    def day_of_year(self) -> int:
        """1-indexed day of year (1-365)."""
        return (self._abs_day0 % DAYS_PER_YEAR) + 1

    def _period(self) -> tuple[str, int, bool]:
        """Return (period_name, day_within_period, is_festival)."""
        remaining = self.day_of_year - 1  # 0-indexed
        for name, days, is_fest in YEAR_STRUCTURE:
            if remaining < days:
                return name, remaining + 1, is_fest
            remaining -= days
        return "Nightal", 30, False

    @property
    def month_name(self) -> str:
        return self._period()[0]

    @property
    def day(self) -> int:
        return self._period()[1]

    @property
    def is_festival(self) -> bool:
        return self._period()[2]

    @property
    def season(self) -> str:
        name = self.month_name
        if self.is_festival:
            return name   # festival name IS the season descriptor
        return SEASONS.get(name, name)

    # -- Moon phase -----------------------------------------------------------

    @property
    def moon_phase(self) -> tuple[str, str]:
        """Returns (phase_name, symbol_str)."""
        day = self.day   # 1-30 for months, 1 for festival
        for r, name, sym in MOON_PHASES:
            if day in r:
                return name, sym
        return "new moon", "&x(O)&N"

    # -- Time of day ----------------------------------------------------------

    @property
    def time_of_day(self) -> str:
        h = self.hour
        if h < 6:              return "night"
        elif h < 9:            return "dawn"
        elif h < 12:           return "morning"
        elif h < 14:           return "midday"
        elif h < 19:           return "afternoon"
        elif h < 22:           return "dusk"
        else:                  return "night"

    @property
    def sky_description(self) -> str:
        h = self.hour
        if h == 0:             return "The night is at its darkest."
        elif h < 4:            return "Stars blanket the sky above."
        elif h < 6:            return "The eastern horizon begins to pale."
        elif h < 8:            return "The sun rises, painting the sky in gold."
        elif h < 12:           return "The morning sun climbs steadily."
        elif h < 14:           return "The sun stands at its zenith overhead."
        elif h < 17:           return "The afternoon sun warms the land."
        elif h < 19:           return "The sun descends toward the horizon."
        elif h < 20:           return "Dusk paints the sky in shades of crimson."
        elif h < 22:           return "The last light fades from the sky."
        else:                  return "Darkness has fallen across the land."

    # -- Display --------------------------------------------------------------

    def ordinal(self, n: int) -> str:
        if 11 <= n <= 13:
            return f"{n}th"
        return f"{n}{['th','st','nd','rd','th'][min(n % 10, 4)]}"

    def time_str(self) -> str:
        """e.g.  06:30"""
        return f"{self.hour:02d}:{self.minute:02d}"

    def date_str(self) -> str:
        """e.g.  the 1st day of Flamerule, 867 DR"""
        if self.is_festival:
            return f"the festival of {self.month_name}, {self.year} DR"
        return (
            f"the {self.ordinal(self.day)} day of "
            f"{self.month_name}, {self.year} DR"
        )

    def full_display(self) -> str:
        """Multi-line time display for the 'time' command."""
        phase_name, phase_sym = self.moon_phase
        lines = [
            f"&wIt is {self.time_str()} on {self.date_str()}.&N",
            f"&w{self.sky_description}&N",
            f"&wSeason: &c{self.season}&N",
            f"&wSelune: &W{phase_sym} &w{phase_name.title()}&N",
        ]
        return "\n".join(lines)

    def advance(self, minutes: int = 1) -> None:
        self.total_minutes += minutes
