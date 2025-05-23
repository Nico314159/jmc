"""Module containing vanilla commands"""

COMMANDS = {
    # OP Level 0-2
    "advancement",
    "attribute",
    "bossbar",
    "clear",
    "clone",
    "damage",
    "data",
    "datapack",
    "debug",
    "defaultgamemode",
    "difficulty",
    "effect",
    "enchant",
    "execute",
    "experience",
    "fill",
    "fillbiome",
    "forceload",
    "function",
    "gamemode",
    "gamerule",
    "give",
    "help",
    "item",
    "kill",
    "list",
    "locate",
    "locatebiome",
    "loot",
    "me",
    "msg",
    "particle",
    "placefeature",
    "playsound",
    "random",
    "ride",
    "recipe",
    "reload",
    "return",
    "rotate",
    "say",
    "schedule",
    "scoreboard",
    "seed",
    "setblock",
    "setworldspawn",
    "spawnpoint",
    "spectate",
    "spreadplayers",
    "stopsound",
    "summon",
    "tag",
    "team",
    "teammsg",
    "teleport",
    "tell",
    "tellraw",
    "time",
    "title",
    "tm",
    "tp",
    "trigger",
    "w",
    "weather",
    "whitelist",
    "worldborder",
    "xp",
    # OP Level 3-4
    "jfr",
    "perf",
    "publish",
    "save-all",
    "save-off",
    "save-on",
    "stop",
    "ban",
    "ban-ip",
    "banlist",
    "debug",
    "deop",
    "kick",
    "op",
    "pardon",
    "pardon-ip",
    "setidletimeout",
    "whitelist",
}
"""All vanilla command (first argument only)"""

VANILLA_CONDITIONS = {
    "biome",
    "block",
    "blocks",
    "data",
    "dimension",
    "entity",
    "function",
    "loaded",
    "predicate",
    "score",
    "items",
}
"""All vanilla arguments to `execute if`"""
