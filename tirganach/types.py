from enum import Enum, Flag
from typing import Type


class UnknownEnumMember:
	name: str
	value: tuple[int, ...]
	cls: Type[Enum]

	def __init__(self, value: tuple[int, ...], cls: Type[Enum]):
		self.value = value
		self.cls = cls
		self.name = f"<Unknown {self.cls.__name__}: {self.value}>"

	def __repr__(self):
		return self.name

	def __eq__(self, other):
		return self.value == other.value

	def __hash__(self):
		return int.from_bytes(b''.join(i.to_bytes(length=1, byteorder='little') for i in self.value), byteorder='little')


class School(Enum):
	UNKNOWN = (0, 1)
	LEVEL_ONLY = (0, 0)
	LIGHT_COMBAT = (1, 0)
	PIERCING_WEAPONS = (1, 1)
	LIGHT_BLADE_WEAPONS = (1, 2)
	LIGHT_BLUNT_WEAPONS = (1, 3)
	LIGHT_ARMOR = (1, 4)
	HEAVY_COMBAT = (2, 0)
	HEAVY_BLADE_WEAPONS = (2, 1)
	HEAVY_BLUNT_WEAPONS = (2, 2)
	HEAVY_ARMOR = (2, 3)
	SHIELDS = (2, 4)
	RANGED_COMBAT = (3, 0)
	BOWS = (3, 1)
	CROSSBOWS = (3, 2)
	WHITE_MAGIC = (4, 0)
	LIFE = (4, 1)
	NATURE = (4, 2)
	BOONS = (4, 3)
	ELEMENTAL_MAGIC = (5, 0)
	FIRE = (5, 1)
	ICE = (5, 2)
	EARTH = (5, 3)
	MIND_MAGIC = (6, 0)
	ENCHANTMENT = (6, 1)
	OFFENSIVE = (6, 2)
	DEFENSIVE = (6, 3)
	BLACK_MAGIC = (7, 0)
	DEATH = (7, 1)
	NECROMANCY = (7, 2)
	CURSE = (7, 3)


class Language(Enum):
	GERMAN = 0,
	ENGLISH = 1,
	FRENCH = 2,
	SPANISH = 3,
	ITALIAN = 4,
	_HAEGAR = 5,


class RuneRace(Enum):
	# apprently these are different from the race
	HEROES = 0,
	HUMANS = 1,
	ELVES = 2,
	DWARVES = 3,
	ORCS = 4,
	TROLLS = 5,
	DARKELVES = 6,


class Race(Enum):
	HUMANS = 1,
	DWARVES = 2,
	ELVES = 3,
	TROLLS = 4,
	ORCS = 5,
	DARKELVES = 6,

	# EPIC FACTIONS
	_CIRCLE = 211,

	# HUMAN FACTIONS
	_HAZIM = 203,
	_WULFGAR = 139,
	_LEONIDAR = 145,
	_UTRAN = 146,
	_REDLEGION = 160,
	_BRIARWOLVES = 159,
	_ORDEROFDAWN = 148,
	_GREYFELL = 175,
	_EMPYRIA = 208,
	_EMPYRIA2 = 207,
	_EMPYRIA_CITIZENS = 219,
	_KATHAI = 210,
	_REFUGEES = 191,

	# ELVEN FACTIONS
	_ELVES_SHIEL = 144,
	_ELVES_ELONI = 134,
	_WINTERGUARD = 192,
	_MEAN_WINTERGUARD = 163,

	# DWARVEN FACTIONS
	_FASTHOLME = 143,
	_HALLIT = 147,
	_HALLIT2 = 135,
	_EVIL_DWARVES = 158,
	_DWARF_GHOSTS = 220,

	# DROW FACTIONS
	_CRAIG_DARKELVES = 182,
	_CRIMSON_EMPIRE = 190,
	_NORCAINE = 137,
	_NORCAINE2 = 138,

	# ORC FACTIONS
	_SOCCER_ORCS = 194,
	_SHAROK = 136,
	_FIST_ORCS = 142,
	_ORCS_GRAG = 105,
	_CAVE_ORCS = 174,

	# CREATURES
	_DRAKELINGS = 162,
	_DRAKELINGS2 = 107,
	_DRAGONITZWIT = 151,
	_REAPER = 153,
	_GIANTS = 156,
	_GIANTS_UNIQUE = 113,
	_OGRES = 104,
	_KITHAR = 187,
	_KITHAR_UNIQUE = 181,
	_ELEMENTALS = 178,
	_ELEMENTALS2 = 133,
	_BLADES = 124,
	_BLADES2 = 205,
	_BLADES_UNIQUE = 183,
	_SOULFORGER = 214,
	_RAVENPASS_UNDEAD = 204,
	_SCREAMERS = 196,
	_SPECTRES = 117,
	_SUCCUBI = 123,
	_MINOTAURS = 176,
	_UROKS = 141,
	_UROKS2 = 140,
	_GARGOYLES = 102,
	_GARGOYLES_UNIQUE = 218,
	_MANTICORES = 108,
	_MANTICORES2 = 198,
	_GRIFFONS = 169,
	_AMRA = 118,
	_BEASTMEN = 111,
	_FLAYED = 201,
	_SHA = 206,
	_DARKWING = 221,
	_RISEN_DEAD = 173,
	_FIREDEMONS = 213,
	_GOBLINS = 100,
	_UNDEAD_GOBLINS = 101,
	_DEMONS = 121,
	_GHOULS = 116,
	_GOLEMS = 103,
	_SCYTHES = 200,
	_MUMMIES = 119,
	_MUMMIES2 = 199,
	_SKELETONS = 114,
	_SHADOWS = 179,
	_ZOMBIES = 115,
	_SPIDERS = 109,
	_BASILISKS = 122,
	_TREEWRAITHS_EVIL = 188,
	_SKERG = 193,
	_HADEKO = 215,
	_MEDUSAE = 112,

	# ANIMALS
	_BIRDS = 127,
	_COWS = 132,
	_BUFFALOES = 129,
	_RABBITS = 125,
	_PIGS = 128,
	_DEER = 131,
	_WOLVES = 130,
	_WOLVESANDBEARS = 172,
	_WOLVES2 = 149,
	_EVIL_WOLVES = 197,
	_WEREWOLVES = 195,
	_BEETLES = 110,
	_MONKEYS = 202,
	_TOADS = 189,

	# SPECIAL
	_GLADIATORS = 167,
	_MERCHANTS = 126,
	_MERCHANTS_COOP = 168,
	_COOP_ENEMIES = 180,
	_HUMANS_TUTORIAL = 171,
	_ORCS_TUTORIAL = 177,
	_GOBLINS_TUTORIAL = 170,
	_EASTEREGG = 186,
	_UNIQUE = 185,
	_UNIQUE2 = 152,
	_UNIQUE3 = 154,
	_UNIQUE4 = 0,
	_UNIQUE5 = 161,
	_UNIQUE6 = 150,


class Resource(Enum):
	_UNKNOWN = 0, # used by human grainfarm, cattle and med hq
	WOOD = 1,
	STONE = 2,
	LOGS = 3,
	MOONSILVER = 4,
	FOOD = 5,
	BERRIES = 6,
	IRON = 7,
	TREES = 8,
	GRAIN = 9
	_UNKNOWN1 = 10,
	FISH = 11,
	MUSHROOMS = 15,
	MEAT = 16,
	ARIA = 18,
	LENYA = 19,
	_UNKNOWN2 = 47,
	_UNKNOWN3 = 73,


class Gender(Enum):
	MALE = 0,
	FEMALE = 1,
	MALE_ESSENTIAL = 2,
	FEMALE_ESSENTIAL = 3,


class SlotConfiguration(Enum):
	ALL = 1,
	HANDS_AND_RINGS = 2,
	NONE = 3,


class EquipmentSlot(Enum):
	HELMET = 0,
	RIGHT_HAND = 1,
	CHEST = 2,
	LEFT_HAND = 3,
	RIGHT_RING = 4,
	LEGS = 5,
	LEFT_RING = 6,
	UNKNOWN = 12,


class ItemType(Enum):
	EQUIPMENT = 1,
	RUNE_INVENTORY = 2,
	RUNE_ADDED = 3,
	SCROLL = 4,
	SPELL = 5,
	UNIT_PLAN_INVENTORY = 6,
	BUILDING_PLAN_INVENTORY = 7,
	UNIT_PLAN_ADDED = 8,
	BUILDING_PLAN_ADDED = 9,
	QUEST_ITEM = 10,
	BLANK_SCROLL = 11,

	def determine_sub_type(self):
		if self in [self.RUNE_INVENTORY, self.RUNE_ADDED, self.UNIT_PLAN_INVENTORY, self.UNIT_PLAN_ADDED, self.BUILDING_PLAN_INVENTORY, self.BUILDING_PLAN_ADDED]:
			return RuneRace
		else:
			return EquipmentType


class EquipmentType(Enum):
	NOTHING = 0,
	HELMET = 1,
	UPPER = 2,
	LOWER = 3,
	RING = 6,
	ONEHANDED_WEAPON = 7,
	TWOHANDED_WEAPON = 8,
	SHIELD = 9,
	FULL_BODY = 10,
	FIGURE_NPC = 11,
	BOW = 12,
	FIGURE_HERO = 13,


class RaceFlags(Flag):
	UNDEAD = 1
	BREATHING = 2
	HUNTABLE = 4
	ANIMAL = 8
	HAS_SOUL = 16
	ATTACKS_BUILDINGS = 32
	BLEEDS = 64


class RaceAIFlags(Flag):
	DEFAULT = 1
	IDLE = 2
	STROLL_ALONG = 4
	NOMADIC = 8
	AGGRESSIVE = 16
	DEFENSIVE = 32
	SCRIPT = 64


class CultivationFlags(Flag):
	GRAIN = 1
	MUSHROOMS = 2
	TREES = 4
