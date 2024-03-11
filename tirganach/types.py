from enum import Enum


class SchoolRequirement(Enum):
	LEVEL_ONLY = (0, 0)
	PIERCING_WEAPONS = (1, 1)
	LIGHT_BLADE_WEAPONS = (1, 2)
	LIGHT_BLUNT_WEAPONS = (1, 3)
	LIGHT_ARMOR = (1, 4)
	HEAVY_BLADE_WEAPONS = (2, 1)
	HEAVY_BLUNT_WEAPONS = (2, 2)
	HEAVY_ARMOR = (2, 3)
	SHIELDS = (2, 4)
	BOWS = (3, 1)
	CROSSBOWS = (3, 2)
	LIFE = (4, 1)
	NATURE = (4, 2)
	BOONS = (4, 3)
	FIRE = (5, 1)
	ICE = (5, 2)
	EARTH = (5, 3)
	ENCHANTMENT = (6, 1)
	OFFENSIVE = (6, 2)
	DEFENSIVE = (6, 3)
	DEATH = (7, 1)
	NECROMANCY = (7, 2)
	CURSE = (7, 3)


class Language(Enum):
	GERMAN = 0,
	ENGLISH = 1,
	FRENCH = 2,
	SPANISH = 3,
	ITALIAN = 4,
	HAEGAR = 5,
