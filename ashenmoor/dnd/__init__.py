"""
ashenmoor.dnd
─────────────
D&D 5.5e rule mechanics.

Subpackages
───────────
  ashenmoor.dnd.abilities   — ability scores, modifiers, proficiency bonus
  ashenmoor.dnd.armor       — Armor Class calculation
  ashenmoor.dnd.rest        — short rest / long rest
  ashenmoor.dnd.classes     — class definitions (warrior, …)

Quick reference
───────────────
  Ability modifier = (score - 10) // 2
  Proficiency bonus: +2 at levels 1-4, +3 at 5-8, +4 at 9-12,
                     +5 at 13-16, +6 at 17-20

  Attack roll: d20 + ability_modifier + proficiency_bonus  ≥  target AC
  Crit: natural 20 → double the damage dice
  Auto-miss: natural 1
"""

from .abilities import modifier, proficiency_bonus, saving_throw_bonus
from .armor     import get_ac

__all__ = ["modifier", "proficiency_bonus", "saving_throw_bonus", "get_ac"]
