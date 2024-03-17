from os import PathLike
from typing import Type, IO, get_origin, get_args, TypeVar, Generic

from tirganach.entities import Armor, Localisation, Entity, ItemRequirement, Building, BuildingRequirement, Creature, \
	CreatureStats, CreatureResourceRequirement, CreatureEquipment, CreatureSkill, Item, CreatureSpell, Spell, HeroSpell, \
	SpellName, Upgrade, ItemInstall, Weapon, ItemEffect, ItemUI, SpellEffect, RaceDB, UnitBuildingRequirement, Skill, \
	SkillRequirement, ResourceName, Level, NPCName, Map, Portal, Description, AdvancedDescription, Quest, \
	WeaponTypeName, WeaponMaterialName, ItemSet

T = TypeVar('T', bound=Entity)


class Table(list[T], Generic[T]):
	offset: int
	entity_type: Type[Entity]
	entity_index: dict[tuple, Entity] = None

	def __init__(self, entity_type: Type[Entity], offset: int, rows: int):
		super().__init__([None] * rows)
		self.entity_type = entity_type
		self.offset = offset

	def where(self, **kwargs) -> list[T]:
		if pkeys := self.entity_type._primary:
			if set(kwargs.keys()) == set(pkeys):
				ordered_pkeyvals = tuple(kwargs[pkey] for pkey in pkeys)
				result = self.entity_index.get(ordered_pkeyvals)
				if result:
					return [result]

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
	_length: int
	_tables: dict[str, TableDefinition]

	def __init_subclass__(cls):
		# save info in _tables
		cls._tables = {}
		for table_name, table_type in cls.__annotations__.items():
			if isinstance(getattr(cls, table_name), TableDefinition):
				table_definition = getattr(cls, table_name)
				cls._tables[table_name] = table_definition

	def __init__(self, from_input: bytes | str | PathLike[bytes]):
		if isinstance(from_input, PathLike) or isinstance(from_input, str):
			with open(from_input, 'rb') as fd:
				raw = fd.read()
		else:
			raw = from_input

		self.raw = bytearray(raw)
		assert len(self.raw) == self._length

		for table_name, table_definition in self._tables.items():
			# size is saved in the table header!!!
			# this probably means we can add and remove rows now!
			table_header_offset = table_definition.offset - 6
			table_size_bytes = int.from_bytes(raw[table_header_offset: table_header_offset+4], byteorder='little', signed=False)
			table_size_rows = int(table_size_bytes / table_definition.entity_type._length())
			assert table_size_rows == (table_size_bytes / table_definition.entity_type._length())

			table = table_definition.create_table(rows=table_size_rows)

			for idx in range(0, table_size_rows):
				sub_offset = table_definition.offset + (idx * table_definition.entity_type._length())
				new_instance: Entity = table_definition.entity_type(raw[sub_offset:sub_offset+table_definition.entity_type._length()])
				new_instance._game_data = self
				table[idx] = new_instance

			table.create_index()
			self.__setattr__(table_name, table)

	def _to_bytes(self):
		for table_name, table_definition in self._tables.items():
			table_instance: Table = getattr(self, table_name)
			for idx in range(0, len(table_instance)):
				# todo: dynamic length, write to header!
				sub_offset = table_definition.offset + (idx * table_definition.entity_type._length())
				instance: table_definition.entity_type = table_instance[idx]
				self.raw[sub_offset:sub_offset+table_definition.entity_type._length()] = instance._to_bytes()

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
	_md5 = [
		'4a5025f4cc40aab46efde848e2a4682d',
		'7c1d33607b8920440b28c75d0db9c4ae', # polish
		'c09948dc3e9e2908383f844ec2b4a976' # russian
	]

	spells: Table[Spell] = TableDefinition(Spell, 0x20)
	spell_names: Table[SpellName] = TableDefinition(SpellName, 0x3fd20)
	creature_stats: Table[CreatureStats] = TableDefinition(CreatureStats, 0x4421d)
	creature_skills: Table[CreatureSkill] = TableDefinition(CreatureSkill, 0x613c1)
	hero_spells: Table[HeroSpell] = TableDefinition(HeroSpell, 0x62ea3)
	items: Table[Item] = TableDefinition(Item, 0x6359e)
	armor: Table[Armor] = TableDefinition(Armor, 0x897e8)
	item_installs: Table[ItemInstall] = TableDefinition(ItemInstall, 0x8f140)
	weapons: Table[Weapon] = TableDefinition(Weapon, 0x91734)
	item_requirements: Table[ItemRequirement] = TableDefinition(ItemRequirement, 0x94450)
	item_effects: Table[ItemEffect] = TableDefinition(ItemEffect, 0x9a492)
	item_ui: Table[ItemUI] = TableDefinition(ItemUI, 0x9f354)
	spell_effects: Table[SpellEffect] = TableDefinition(SpellEffect, 0x12b373)
	localisation: Table[Localisation] = TableDefinition(Localisation, 0x12d177)
	races: Table[RaceDB] = TableDefinition(RaceDB, 0x3f4b433)
	creatures: Table[Creature] = TableDefinition(Creature, 0x3f4cde6)
	creature_equipment: Table[CreatureEquipment] = TableDefinition(CreatureEquipment, 0x3f75c32)
	creature_spells: Table[CreatureSpell] = TableDefinition(CreatureSpell, 0x3f7cf93)
	creature_resources: Table[CreatureResourceRequirement] = TableDefinition(CreatureResourceRequirement, 0x3f7defe)
	unit_building_requirements: Table[UnitBuildingRequirement] = TableDefinition(UnitBuildingRequirement, 0x3f81b86)
	buildings: Table[Building] = TableDefinition(Building, 0x3f81c69)
	building_requirements: Table[BuildingRequirement] = TableDefinition(BuildingRequirement, 0x3f85bbe)
	skills: Table[Skill] = TableDefinition(Skill, 0x3f85f08)
	skill_requirements: Table[SkillRequirement] = TableDefinition(SkillRequirement, 0x3f85fd4)
	resource_names: Table[ResourceName] = TableDefinition(ResourceName, 0x3f8f1a1)
	levels: Table[Level] = TableDefinition(Level, 0x3f8f1d7)
	npc_names: Table[NPCName] = TableDefinition(NPCName, 0x3fab496)
	maps: Table[Map] = TableDefinition(Map, 0x3fb91b8)
	portals: Table[Portal] = TableDefinition(Portal, 0x3fbae9c)
	descriptions: Table[Description] = TableDefinition(Description, 0x3fbb8a1)
	advanced_descriptions: Table[AdvancedDescription] = TableDefinition(AdvancedDescription, 0x3fbcc89)
	quests: Table[Quest] = TableDefinition(Quest, 0x3fbd84d)
	weapon_type_names: Table[WeaponTypeName] = TableDefinition(WeaponTypeName, 0x3fc1d69)
	weapon_material_names: Table[WeaponMaterialName] = TableDefinition(WeaponMaterialName, 0x3fc1dde)
	upgrades: Table[Upgrade] = TableDefinition(Upgrade, 0x3fc203e)
	item_sets: Table[ItemSet] = TableDefinition(ItemSet, 0x3fc3346)


class GameData161(GameData):
	_length = 66859988

	items: Table[Armor] = TableDefinition(Armor, 0x8a71d),
	localisation: Table[Localisation] = TableDefinition(Localisation, 0x12f2e3),
	item_requirements: Table[ItemRequirement] = TableDefinition(ItemRequirement, 0x99e21),
	buildings: Table[Building] = TableDefinition(Building, 0x3f81c94)
