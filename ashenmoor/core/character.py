"""
ashenmoor.core.character
────────────────────────
Base Character class.

Three stat layers
─────────────────
  1. base_stat      rolled 1-100 at character creation; never changes except
                    through levelling or permanent events
  2. displayed_stat min(base + equipment_bonus, 100)
                    this is what the player SEES — always 1-100 for every race
  3. computed_stat  int(displayed × racial_multiplier)
                    this is what EVERYTHING IN THE BACKEND uses
                    (modifiers, AC, attack rolls, saving throws, etc.)

Why the split?
──────────────
  An Ogre and a Human both see "STR: 100" at the cap.
  The same +10 STR ring benefits both identically on the display screen.
  But in combat:
    Human : effective STR 100 × 1.0 = 100 → modifier +5
    Ogre  : effective STR 100 × 1.5 = 150 → modifier +15

  Racial identity lives in the multiplier, not the display.
"""

from __future__ import annotations
from typing import TYPE_CHECKING
from .stats import Stats

if TYPE_CHECKING:
    from .race import Race

# Hard display cap — every race reads 1-100 on the character sheet
_DISPLAY_CAP = 100


class Character:
    def __init__(self, d: dict, races: dict | None = None):
        self.name:      str  = d.get("name",     "Unknown")
        self.stats:     list = d.get("stats",    [80]*6)
        self.race:      str  = d.get("race",     "Human")
        self.level:     int  = d.get("level",    1)
        self.position:  str  = d.get("position", "standing")
        self.cclass:    str  = d.get("class",    "Warrior")
        self.powers:    list = d.get("powers",   [])
        self.inventory: list = list(d.get("inventory", []))
        self.equipment: dict = dict(d.get("equipment", {}))
        self.xp:        int  = d.get("xp", 0)

        # D&D class state (charges, fighting style, hit dice …)
        # Does NOT hold ability scores — those come from self.stats + gear.
        self.dnd: dict | None = d.get("dnd", None)

        # ── Movement points ───────────────────────────────────────────────────
        dex_base        = self.stats[Stats.DEXTERITY.value] if len(self.stats) > 1 else 75
        default_moves   = max(50, dex_base)
        self.max_moves: int  = d.get("max_moves", default_moves)
        self.moves:     int  = d.get("moves",     self.max_moves)

        # ── Currency (gold / silver / copper) ─────────────────────────────────
        self.coins:      dict = d.get("coins",      {"gold": 0, "silver": 0, "copper": 0})
        self.bank_coins: dict = d.get("bank_coins", {"gold": 0, "silver": 0, "copper": 0})

        # ── Character title (e.g. "the Archmage") ─────────────────────────────
        self.title: str = d.get("title", "")

        # ── Active status flags (populated by spells/abilities/items) ─────────
        self.detect_flags:  list[str] = list(d.get("detect_flags",  []))
        self.protect_flags: list[str] = list(d.get("protect_flags", []))
        self.enchant_flags: list[str] = list(d.get("enchant_flags", []))

        # ── Accumulated play time (seconds, persisted across sessions) ─────────
        self.play_time_seconds: int = d.get("play_time_seconds", 0)

        con         = self.stats[Stats.CONSTITUTION.value] if len(self.stats) > Stats.CONSTITUTION.value else 75
        default_max = max(10, (con // 5) * max(1, self.level) + max(1, self.level) * 5)
        self.max_hp: int = d.get("max_hp", default_max)
        self.hp:     int = d.get("hp",     self.max_hp)

        # Alignment: one of the classic 9 (Lawful/Neutral/Chaotic × Good/Neutral/Evil)
        self.alignment: str      = d.get("alignment", "True Neutral")
        # Wimpy: auto-flee when HP drops to or below this value. None = disabled.
        self.wimpy:     int|None = d.get("wimpy", None)

        if races is None:
            from .race import RACES
            races = RACES
        self._races = races

    # ── Internal helper ───────────────────────────────────────────────────────

    @staticmethod
    def _stat_key(stat) -> str:
        if isinstance(stat, Stats): return stat.abv
        if isinstance(stat, int):   return list(Stats)[stat].abv
        return str(stat).lower()

    # ── Stat accessors ────────────────────────────────────────────────────────

    def get_stat(self, stat) -> int:
        """Raw base stat (1-100, no gear, no racial scaling)."""
        if isinstance(stat, int):   return self.stats[stat]
        if isinstance(stat, Stats): return self.stats[stat.value]
        if isinstance(stat, str):
            for s in Stats:
                if stat.lower() == s.abv: return self.stats[s.value]
        raise ValueError(f"Unknown stat: {stat!r}")

    def _equipment_stat_bonus(self, stat_key: str) -> int:
        """
        Sum of stat_mods[stat_key] across equipped items.
        These push toward the 100 display cap (capped there).
        """
        total = 0
        for item in self.equipment.values():
            if item is not None:
                total += getattr(item, "stat_mods", {}).get(stat_key, 0)
        return total

    def _equipment_max_stat_bonus(self, stat_key: str) -> int:
        """
        Sum of stat_mods["max_<stat>"] across equipped items.
        These extend the displayed stat BEYOND the 100 cap.
        e.g. stat_mods={"max_int": 56} on a tome lets INT show as 156.
        """
        total = 0
        max_key = f"max_{stat_key}"
        for item in self.equipment.values():
            if item is not None:
                total += getattr(item, "stat_mods", {}).get(max_key, 0)
        return total

    def displayed_stat(self, stat) -> int:
        """
        Stat as shown on the att page.

        Two tiers of gear bonus:
          stat_mods     — regular gear, pushes toward 100 (capped there)
          max_stat_mods — extends the ceiling above 100 (no cap)

        displayed = min(base + regular_gear, 100) + max_extending_gear

        Examples:
          INT 80,  +20 ring,  +56 max_int item  → min(100,100) + 56 = 156
          INT 80,  no ring,   +56 max_int item  → min(80, 100) + 56 = 136
          INT 100, +20 ring,  no max item       → min(120,100) + 0  = 100
        """
        key       = self._stat_key(stat)
        base      = self.get_stat(key)
        regular   = self._equipment_stat_bonus(key)
        above_cap = self._equipment_max_stat_bonus(key)
        return min(_DISPLAY_CAP, base + regular) + above_cap

    def computed_stat(self, stat) -> int:
        """
        Effective stat used by all backend systems (modifiers, AC, attacks).

        computed = int(displayed × racial_multiplier)

        Ogre  displayed STR 100 × 1.5 → 150 → modifier +15
        Human displayed STR 100 × 1.0 → 100 → modifier +5
        """
        key  = self._stat_key(stat)
        disp = self.displayed_stat(key)
        race = self._races.get(self.race)
        mult = race.get_multiplier(key) if race else 1.0
        return int(disp * mult)

    # ── Position helpers ──────────────────────────────────────────────────────────

    def position_str(self) -> str:
        """Short description of character position for room look lists."""
        pos = self.position
        if pos == "standing":  return "is standing here."
        if pos == "sitting":   return "is sitting here."
        if pos == "resting":   return "is here, resting."
        if pos == "kneeling":  return "is here, kneeling."
        if pos == "reclined":  return "is here, lying down."
        return "is here."

    def position_label(self) -> str:
        """Capitalised one-word label for score display."""
        return self.position.capitalize() + "."

    # ── Character sheet ───────────────────────────────────────────────────────────

    def character_sheet(self) -> str:
        from ..dnd.abilities import modifier, proficiency_bonus
        from ..dnd.armor     import get_ac

        hp_pct = int(self.hp / max(1, self.max_hp) * 100)
        prof   = proficiency_bonus(self.level)
        ac     = get_ac(self)

        lines = [
            f"&+WCharacter sheet for &N{self.name}\n",
            f"&wRace:&N  {self.race}   &wClass:&N {self.cclass}   "
            f"&wLevel:&N {self.level}   &wXP:&N {self.xp:,}",
            f"&wHP:&N    {self.hp}/{self.max_hp} ({hp_pct}%)   "
            f"&wAC:&N {ac}   &wProf Bonus:&N +{prof}",
            "",
            "&wAbility Scores&N",
            "  &x{:<3}  {:>5}  {:>5}  {:>5}  {:>8}  {}&N".format(
                "STAT", "BASE", "GEAR", "SHOWN", "EFFECTIVE", "MOD"),
            "  &w" + "─"*46 + "&N",
        ]

        race_obj = self._races.get(self.race)

        for stat_enum in Stats:
            ab       = stat_enum.abv
            base     = self.get_stat(ab)
            gear     = self._equipment_stat_bonus(ab)
            shown    = self.displayed_stat(ab)
            eff      = self.computed_stat(ab)
            mod      = modifier(eff)
            mult     = race_obj.get_multiplier(ab) if race_obj else 1.0
            sign     = "+" if mod >= 0 else ""

            gear_str = f"+{gear}" if gear else "—"
            eff_str  = f"{eff}" if mult != 1.0 else "—"

            # Highlight gear-maxed stats (shown == 100) in yellow
            color = "&+Y" if shown >= _DISPLAY_CAP else "&w"

            lines.append(
                f"  {color}{ab.upper():<3}&N"
                f"  {base:>5}"
                f"  {gear_str:>5}"
                f"  {shown:>5}"
                f"  {eff_str:>8}"
                f"  ({sign}{mod})"
            )

        lines.append("")

        # D&D Warrior extras
        dnd = self.dnd or {}
        if dnd.get("class") == "warrior":
            from ..dnd.classes.warrior import attack_count, active_features
            lines.append(
                f"&wAttacks/Round:&N {attack_count(self.level)}   "
                f"&wFighting Style:&N {dnd.get('fighting_style', '—')}"
            )
            sw   = dnd.get("second_wind_uses",  0)
            swm  = dnd.get("second_wind_max",   1)
            su   = dnd.get("action_surge_uses", 0)
            sum_ = dnd.get("action_surge_max",  1)
            hd   = dnd.get("hit_dice_remaining", 0)
            lines.append(
                f"&wSecond Wind:&N  &W{sw}&w/&W{swm}&N   "
                f"&wAction Surge:&N &W{su}&w/&W{sum_}&N   "
                f"&wHit Dice:&N &W{hd}&w/&W{self.level}&N"
            )
            feats = active_features(self.level)
            lines.append("&wFeatures:&N " + ", ".join(feats))

        if self.powers:
            lines.append("")
            lines.append("&wPowers:&N  " +
                         ", ".join(p.get("name", "?") for p in self.powers))

        # Equipped gear — highlight any with stat bonuses
        eq_lines = []
        for slot, item in self.equipment.items():
            if item is None: continue
            bonus_parts = [f"{k.upper()} +{v}"
                           for k, v in getattr(item, "stat_mods", {}).items() if v]
            bonus_str = "  &+Y[" + ", ".join(bonus_parts) + "]&N" if bonus_parts else ""
            eq_lines.append(f"  &w{slot:<18}&N {item.name}{bonus_str}")
        if eq_lines:
            lines.append("")
            lines.append("&wEquipped:&N")
            lines.extend(eq_lines)

        return "\n".join(lines)

    def pcs(self):
        from ..color import cprint
        cprint(self.character_sheet())

    def __str__(self):  return self.character_sheet()
    def __repr__(self): return (f"Character(name={self.name!r}, race={self.race!r}, "
                                f"class={self.cclass!r}, level={self.level})")
