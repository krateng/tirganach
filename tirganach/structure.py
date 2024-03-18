from os import PathLike
from typing import Type, IO, get_origin, get_args, TypeVar, Generic

from tirganach.entities import Armor, Localisation, Entity, ItemRequirement, Building, BuildingRequirement, Creature, \
	CreatureStats, CreatureResourceRequirement, CreatureEquipment, CreatureSkill, Item, CreatureSpell, Spell, HeroSpell, \
	SpellName, Upgrade, ItemInstall, Weapon, ItemEffect, ItemUI, SpellEffect, RaceDB, UnitBuildingRequirement, Skill, \
	SkillRequirement, ResourceName, Level, NPCName, Map, Portal, Description, AdvancedDescription, Quest, \
	WeaponTypeName, WeaponMaterialName, ItemSet, Unknown3, Head, CreatureDrop, BuildingGraphics, MerchantInventory, \
	MerchantInventoryItem, MerchantPriceMultiplier, Object, ObjectGraphics, ObjectLoot, Unknown40, Terrain, Unknown47

T = TypeVar('T', bound=Entity)


class Table(list[T], Generic[T]):
	_raw: bytearray
	_game_data: 'GameData'

	offset: int
	entity_type: Type[Entity]
	entity_index: dict[tuple, Entity] = None

	def __init__(self, raw_bytes: bytes | bytearray, entity_type: Type[Entity], game_data: 'GameData'):
		self._raw = bytearray(raw_bytes)
		self.entity_type = entity_type
		self._game_data = game_data

		# we read the header here again, just for cleaner structure (rather than passing the info to the init)
		header = self._raw[0:12]
		table_size_bytes = int.from_bytes(header[6: 10], byteorder='little', signed=False)
		table_row_length = entity_type._length()
		table_size_rows = int(table_size_bytes / table_row_length)
		assert table_size_rows == (table_size_bytes / table_row_length)

		super().__init__([None] * table_size_rows)

		offset = 12
		for idx in range(0, table_size_rows):
			new_instance: entity_type = entity_type(self._raw[offset:offset+table_row_length])
			new_instance._game_data = self._game_data
			self[idx] = new_instance
			offset += table_row_length

		assert offset == len(raw_bytes)

		self.create_index()

	def _to_bytes(self):
		table_row_length = self.entity_type._length()

		self._raw[6: 10] = (len(self) * table_row_length).to_bytes(length=4, byteorder='little', signed=False)

		offset = 12
		for row in self:
			assert isinstance(row, self.entity_type)
			self._raw[offset: offset+table_row_length] = row._to_bytes()
			offset += table_row_length

		return self._raw

	def __repr__(self):
		return f"<[Table] {self.entity_type.__name__}>"

	def where(self, **kwargs) -> list[T]:
		if pkeys := self.entity_type._primary:
			if set(kwargs.keys()) == set(pkeys):
				ordered_pkeyvals = tuple(kwargs[pkey] for pkey in pkeys)
				result = self.entity_index.get(ordered_pkeyvals)
				if result:
					return [result]
				else:
					return []

		return [e for e in self if all(getattr(e, k) == v for k, v in kwargs.items())]

	def create_index(self):
		self.entity_index = self.entity_index or {}
		if pkeys := self.entity_type._primary:
			for element in self:
				if element:
					pkey_vals = tuple(getattr(element, pkey) for pkey in pkeys)
					self.entity_index[pkey_vals] = element


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
	#fields: dict[str, tuple[Type[Entity], int]] = {}
	raw: bytearray
	offsets: dict = {}
	_length: int = None
	_md5: str

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

	def __init__(self, from_input: bytes | str | PathLike[bytes]):
		if isinstance(from_input, PathLike) or isinstance(from_input, str):
			with open(from_input, 'rb') as fd:
				raw = fd.read()
		else:
			raw = from_input

		self.raw = bytearray(raw)
		if self._length:
			assert self._length == len(self.raw)
		offset = 0

		#skip file header
		offset += 20

		table_definitions = {name: annot for name, annot in self.__annotations__.items() if get_origin(annot) is Table}
		# guaranteed in correct order, PEP 468

		for table_name, table_definition in table_definitions.items():

			table_entity_type: Type[Entity] = get_args(table_definition)[0]

			# need to already read the header so we know how many bytes to send to the table init
			table_header = self.raw[offset: offset+12]
			table_size_bytes = int.from_bytes(table_header[6: 10], byteorder='little', signed=False)

			offset += 12
			if table_name in self.offsets:
				assert offset == self.offsets[table_name]
			table_body = self.raw[offset: offset+table_size_bytes]
			table = Table(raw_bytes=table_header + table_body, entity_type=table_entity_type, game_data=self)

			offset += table_size_bytes

			setattr(self, table_name, table)

		assert offset == len(self.raw)

	def _to_bytes(self):

		offset = 0

		#skip file header
		offset += 20

		table_definitions = self.__annotations__

		for table_name, table_definition in table_definitions.items():
			table_entity_type: Type[Entity] = get_args(table_definition)[0]
			table_instance: Table = getattr(self, table_name)
			table_raw = table_instance._to_bytes()
			self.raw[offset: offset+len(table_raw)] = table_raw

			offset += len(table_raw)

		return bytes(self.raw)

	def save(self, filename):
		with open(filename, 'wb') as fd:
			fd.write(self._to_bytes())

	def debug_definition_range(self):
		block_size = 1024 * 256
		bytes_accounted = [False] * self._length
		for tabletype, offset, length in self.fields.values():
			for byte in range(offset, offset + (get_args(tabletype)[0]._length() * length)):
				bytes_accounted[byte] = True
		blocks = [0] * round(self._length / block_size)
		for blockindex in range(len(blocks)):
			for byteindex in range(blockindex*block_size, (blockindex+1)*block_size):
				if bytes_accounted[byteindex]:
					blocks[blockindex] = True
					break

		print(''.join(('1' if a else '0') for a in blocks))


class GameData154(GameData):
	_length = 66859922

	offsets = {
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


# TODO figure out of this is consistent across versions, with just different table sizes, then we can get rid of those definitions
class GameData161(GameData):
	_length = 66859988

	#items: Table[Armor] = TableDefinition(Armor, 0x8a71d),
	#localisation: Table[Localisation] = TableDefinition(Localisation, 0x12f2e3),
	#item_requirements: Table[ItemRequirement] = TableDefinition(ItemRequirement, 0x99e21),
	#buildings: Table[Building] = TableDefinition(Building, 0x3f81c94)
