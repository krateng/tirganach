import hashlib
from os import PathLike
from typing import Type, get_origin, get_args, TypeVar, Generic

from tirganach.entities import Armor, Localisation, Entity, ItemRequirement, Building, BuildingRequirement, Creature, \
	CreatureStats, CreatureResourceRequirement, CreatureEquipment, CreatureSkill, Item, CreatureSpell, Spell, HeroSpell, \
	SpellName, Upgrade, ItemInstall, Weapon, ItemEffect, ItemUI, SpellEffect, RaceDB, UnitBuildingRequirement, Skill, \
	SkillRequirement, ResourceName, Level, NPCName, Map, Portal, Description, AdvancedDescription, Quest, \
	WeaponTypeName, WeaponMaterialName, ItemSet, Unknown3, Head, CreatureDrop, BuildingGraphics, MerchantInventory, \
	MerchantInventoryItem, MerchantPriceMultiplier, Object, ObjectGraphics, ObjectLoot, Unknown40, Terrain, Unknown47

T = TypeVar('T', bound=Entity)


class Table(list[T], Generic[T]):
	_header: bytearray
	_game_data: 'GameData'

	offset: int
	entity_type: Type[T]
	entity_index: dict[tuple, T] = None
	primary_keys: tuple # sorted alphabetically!

	def __init__(self, raw_bytes: bytes | bytearray, entity_type: Type[T], game_data: 'GameData'):
		self.entity_type = entity_type
		self.primary_keys = tuple(sorted(field_name for field_name, field in entity_type._fields.items() if field.primary))
		self._game_data = game_data

		offset = 0

		# we read the header here again, just for cleaner structure (rather than passing the info to the init)
		header = raw_bytes[0:12]
		self._header = header
		offset += 12

		table_size_bytes = int.from_bytes(header[6: 10], byteorder='little', signed=False)
		table_row_length = entity_type._length()
		table_size_rows = int(table_size_bytes / table_row_length)
		assert table_size_rows == (table_size_bytes / table_row_length)
		super().__init__([None] * table_size_rows)

		for idx in range(0, table_size_rows):
			new_instance: entity_type = entity_type(raw_bytes[offset:offset+table_row_length], game_data=self._game_data)
			self[idx] = new_instance
			offset += table_row_length

		assert offset == len(raw_bytes)

		self.create_index()

	def _to_bytes(self):
		table_row_length = self.entity_type._length()

		offset = 0
		result = bytearray()

		# header
		self._header[6: 10] = (len(self) * table_row_length).to_bytes(length=4, byteorder='little', signed=False)
		result += self._header
		offset += 12

		for row in self:
			assert isinstance(row, self.entity_type)
			result += row._to_bytes()
			offset += table_row_length
			assert len(result) == offset

		return result

	def _to_hex(self):
		return ' '.join(format(byte, '02x') for byte in self._to_bytes())

	def __repr__(self):
		return f"<[Table] {self.entity_type.__name__}>"

	def where(self, **kwargs) -> list[T]:
		if self.primary_keys:
			if set(kwargs.keys()) == set(self.primary_keys):
				ordered_pkeyvals = tuple(kwargs[pkey] for pkey in self.primary_keys)
				result = self.entity_index.get(ordered_pkeyvals)
				if result:
					return [result]
				else:
					return []

		return [e for e in self if all(getattr(e, k) == v for k, v in kwargs.items())]

	def create_index(self):
		self.entity_index = self.entity_index or {}
		if self.primary_keys:
			for element in self:
				if element:
					ordered_pkeyvals = tuple(getattr(element, pkey) for pkey in self.primary_keys) #alphabetical
					self.entity_index[ordered_pkeyvals] = element


class TableDefinition:
	# this is the equivalent of a field
	# we only want the actual table instance for the specific table in a loaded gamedata
	# so this class is used to just inform how the generic table looks for that gamedata
	# UNNEEDED FOR NOW since order is predefined, offsets and lengths are in the data
	entity_type: Type[Entity]
	offset: int

	def __init__(self, entity_type: Type[Entity], offset: int):
		self.entity_type = entity_type
		self.offset = offset

	def create_table(self, rows: int):
		return Table(entity_type=self.entity_type, offset=self.offset, rows=rows)


class GameData:
	_header: bytearray
	_offsets: dict = {}
	_length: int = None
	_md5: str = None

	spells: Table[Spell]
	spell_names: Table[SpellName]
	unknown3: Table[Unknown3]
	creature_stats: Table[CreatureStats]
	creature_skills: Table[CreatureSkill]
	hero_spells: Table[HeroSpell]
	items: Table[Item]
	armor: Table[Armor]
	item_installs: Table[ItemInstall]
	weapons: Table[Weapon]
	item_requirements: Table[ItemRequirement]
	item_effects: Table[ItemEffect]
	item_ui: Table[ItemUI]
	spell_effects: Table[SpellEffect]
	localisation: Table[Localisation]
	races: Table[RaceDB]
	heads: Table[Head]
	creatures: Table[Creature]
	creature_equipment: Table[CreatureEquipment]
	creature_spells: Table[CreatureSpell]
	creature_resources: Table[CreatureResourceRequirement]
	drops: Table[CreatureDrop]
	unit_building_requirements: Table[UnitBuildingRequirement]
	buildings: Table[Building]
	building_graphics: Table[BuildingGraphics]
	building_requirements: Table[BuildingRequirement]
	skills: Table[Skill]
	skill_requirements: Table[SkillRequirement]
	merchant_inventories: Table[MerchantInventory]
	merchant_inventory_items: Table[MerchantInventoryItem]
	merchant_price_multipliers: Table[MerchantPriceMultiplier]
	resource_names: Table[ResourceName]
	levels: Table[Level]
	objects: Table[Object]
	object_graphics: Table[ObjectGraphics]
	object_loot: Table[ObjectLoot]
	npc_names: Table[NPCName]
	maps: Table[Map]
	portals: Table[Portal]
	unknown40: Table[Unknown40]
	descriptions: Table[Description]
	advanced_descriptions: Table[AdvancedDescription]
	quests: Table[Quest]
	weapon_type_names: Table[WeaponTypeName]
	weapon_material_names: Table[WeaponMaterialName]
	terrain: Table[Terrain]
	unknown47: Table[Unknown47]
	upgrades: Table[Upgrade]
	item_sets: Table[ItemSet]

	def table_info(self):
		return {name: annot for name, annot in self.__annotations__.items() if get_origin(annot) is Table}

	def tables(self):
		return {name: getattr(self, name) for name in self.table_info()}

	def get_table(self, entity_type: Type[Entity]) -> Table[Entity]:
		for name, annot in self.table_info().items():
			if get_args(annot)[0] is entity_type:
				return self.tables()[name]

	def __init__(self, from_input: bytes | str | PathLike[bytes]):
		if isinstance(from_input, PathLike) or isinstance(from_input, str):
			with open(from_input, 'rb') as fd:
				raw = fd.read()
		else:
			raw = from_input

		raw = bytearray(raw)
		if self._length:
			assert self._length == len(raw)
		if self._md5:
			hsh = hashlib.md5()
			hsh.update(raw)
			assert hsh.hexdigest() == self._md5
		offset = 0

		# header
		self._header = raw[0:20]
		offset += 20

		for table_name, table_definition in self.table_info().items():
			# guaranteed in correct order, PEP 468

			table_entity_type: Type[Entity] = get_args(table_definition)[0]

			# need to already read the header so we know how many bytes to send to the table init
			table_header = raw[offset: offset+12]
			table_size_bytes = int.from_bytes(table_header[6: 10], byteorder='little', signed=False)

			offset += 12
			if table_name in self._offsets:
				assert offset == self._offsets[table_name]
			table_body = raw[offset: offset+table_size_bytes]
			table = Table(raw_bytes=table_header + table_body, entity_type=table_entity_type, game_data=self)

			offset += table_size_bytes

			setattr(self, table_name, table)

		assert offset == len(raw)

	def _to_bytes(self):

		offset = 0
		result = bytearray()

		#header
		result += self._header
		offset += 20

		for table_name, table_definition in self.table_info().items():
			table_entity_type: Type[Entity] = get_args(table_definition)[0]
			table_instance: Table = getattr(self, table_name)
			table_raw = table_instance._to_bytes()
			result += table_raw
			offset += len(table_raw)
			assert offset == len(result)

		return bytes(result)

	def save(self, filename):
		with open(filename, 'wb') as fd:
			fd.write(self._to_bytes())


# gamedatas from different versions aren't actually structurally different, so we can just use the base class to load
# these classes are now here to specifiy information about the vanilla files (in order to verify integrity)

class GameData154(GameData):
	_length = 66859922

	# these are for the table bodies, not the header!
	_offsets = {
		'spells': 0x20,
		'spell_names': 0x3fd20,
		'unknown3': 0x44205,
		'creature_stats': 0x4421d,
		'creature_skills': 0x613c1,
		'hero_spells': 0x62ea3,
		'items': 0x6359e,
		'armor': 0x897e8,
		'item_installs': 0x8f140,
		'weapons': 0x91734,
		'item_requirements': 0x94450,
		'item_effects': 0x9a492,
		'item_ui': 0x9f354,
		'spell_effects': 0x12b373,
		'localisation': 0x12d177,
		'races': 0x3f4b433,
		'heads': 0x3f4c1da,
		'creatures': 0x3f4cde6,
		'creature_equipment': 0x3f75c32,
		'creature_spells': 0x3f7cf93,
		'creature_resources': 0x3f7defe,
		'drops': 0x3f7e10a,
		'unit_building_requirements': 0x3f81b86,
		'buildings': 0x3f81c69,
		'building_graphics': 0x3f82f0e,
		'building_requirements': 0x3f85bbe,
		'skills': 0x3f85f08,
		'skill_requirements': 0x3f85fd4,
		'merchant_inventories': 0x3f864cc,
		'merchant_inventory_items': 0x3f867d8,
		'merchant_price_multipliers': 0x3f8e7b8,
		'resource_names': 0x3f8f1a1,
		'levels': 0x3f8f1d7,
		'objects': 0x3f8f4e0,
		'object_graphics': 0x3fa52a8,
		'object_loot': 0x3fa5c53,
		'npc_names': 0x3fab496,
		'maps': 0x3fb91b8,
		'portals': 0x3fbae9c,
		'unknown40': 0x3fbb88f,
		'descriptions': 0x3fbb8a1,
		'advanced_descriptions': 0x3fbcc89,
		'quests': 0x3fbd84d,
		'weapon_type_names': 0x3fc1d69,
		'weapon_material_names': 0x3fc1dde,
		'terrain': 0x3fc1e06,
		'unknown47': 0x3fc1ff2,
		'upgrades': 0x3fc203e,
		'item_sets': 0x3fc3346,
	}


class GameData154EN(GameData154):
	_md5 = '4a5025f4cc40aab46efde848e2a4682d'


class GameData154RU(GameData154):
	_md5 = 'c09948dc3e9e2908383f844ec2b4a976'


class GameData154PL(GameData154):
	_md5 = '7c1d33607b8920440b28c75d0db9c4ae'


class GameData161(GameData):
	_length = 66859988
