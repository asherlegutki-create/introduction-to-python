"""
zones.the_void.mobs
───────────────────
Mob templates for The Void zone.

Add an entry to TEMPLATES for every NPC type that can appear in this zone.
Call spawn(key) to get a fresh independent Mob instance — place as many
copies in rooms as you like, each is independent.
"""

from ashenmoor.world import Mob
from ashenmoor.world.zone import make_spawner

TEMPLATES: dict[str, dict] = {
    "escbaalion": {
        "name": "&gEscbaalion&N",  # The c is silent
        "key_words": ("Escbaalion", "lizard", "lizardman"),
        "room_description": "&gEscbaalion&N licks his eyeball.",
        "description": (
            "   (The 'c' is silent)",
            "A humanoid lizard. He is &gdark-green&N, and has a short",
            "&Ccyan sail&N that runs from the top of his head to the end of his tail.",
            "He wears an almost &Xblack cloak&N, but wears &Rno&N pants.",
            "A &ybrown leather satchel&N is slung over his shoulder.",
            "Only &ghe&N knows what is inside his &ybag&N. . . .",
        ),
        "race": "Lizaroid",
        "class": "Sorcerer",
        "level": 2,
        "stats": [80, 50, 200, 90, 90, 70],
        "aggro": False,
        "wander": False,
        "killable": True,
    },
    "unicorn_blob": {
        "name": "&MUnicorn Blob&N",
        "key_words": ("unicorn", "blob"),
        "room_description": "&MUnicorn Blob&N wanders without a care in the world.",
        "description": (
            "   It is a &Mpurple blob of&N &mjelly&N.",
            "A &Ygolden unicorn horn&N protrudes from its forehead.",
            "Its eyes are cute and sparkly and &Xsouless&N.",
            "",
            "",
            "",
            "I wonder what it tastes like...?",
        ),
        "race": "Slime",
        "class": "",
        "level": 1,
        "stats": [70, 50, 160, 20, 20, 100],
        "aggro": False,
        "wander": True,
        "killable": True,
    },
    "glitch": {
        "name": "glitch",
        "key_words": ("glitch"),
        "room_description": "*Gl!tcH[:::] ruins* the [:::]reality *around it.[:::]",
        "description": (
            "It loo[:::]oks liKe a *olleh[:::]^,6 a-->g,[:::]%++$*",
            "TOIK! EUA LOMAXKJ UAZ ZNGZ ZNOY OY G IGKYGX IOVNKX",
            "[:::|:::|:::]",
            "_MuL-tiPle* c0_l0r$",
            "mu_ltI_plE $hAp_e$*",
            "[:::|:::|:::]",
            "ZOSK OY HAXTOTM ZNK KTJ OY TKGX",
            "ZNK SUUT XKLAYKY ZU YVKGQ",
            "ZNK CGRXAY YOTMY ZNK YUTM UL LKGX",
            "CNKT CK XKGIN ZNK LOTGR VKGQ",
            "[:::|:::|:::]",
            "*MROZIN OY TUC",
        ),
        "race": "Unknown",
        "class": "",
        "level": 50,
        "stats": [100, 100, 1000, 100, 100, 100],
        "aggro": False,
        "wander": True,
        "killable": True,
    },
    "duck": {
        "name": "Quack",
        "key_words": ("Quack", "duck"),
        "room_description": "Quack ruffles her tail.",
        "description": (
            "   Quack is a very cute duck.",
            "She has pristine white feathers.",
            "Her bill and feet are a &ydark-yellow&N.",
        ),
        "race": "Duck",
        "killable": False,
        "responses": {
            "hi": ("Quack replies: 'Well, hello there! How are you?'"),
            "good": (
                "Quack replies: 'That's nice to here. What can I help you with? I love helping.'"
            ),
            "bad": ("Quack replies: 'Oh, I'm sorry. How can I make you feel better?'"),
            "gun": (
                "Quack replies: 'You must mean my Duckzooka! Yeah, I made it myself.'",
                "'It's somewhere around here...'",
            ),
            "weapon": (
                "Quack replies: 'You must mean my Duckzooka! Yeah, I made it myself.'",
                "'It's somewhere around here...'",
            ),
            "isaac": ("Quack replies: 'I think I know an 'Isaac.' Do you know him?'"),
            "bread": ("Quack replies: 'Oooh! Do you have any?'"),
            "goodbye": ("Quack replies: 'Goodbye! See you later!'"),
            "thank you": (
                "Quack replies: 'You're so welcome! I'll be right here in case you need me. :) '"
            ),
            # "code": (
            #   "Quack replies: 'Oh, I remember these words. at least I think I do.'"
            #   "Quack pulls out reading glasses and clears her throat."
            #   "(Put code here)"
            #   "Quack replies: 'Did that help?'"
            # ),
        },
    },
}

spawn = make_spawner(TEMPLATES, lambda: Mob)
