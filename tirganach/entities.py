from .types import SchoolRequirement, Language, Race, Resource, SlotConfiguration, Gender, EquipmentSlot, ItemType, \
	EquipmentType, RuneRace
from .fields import Field, IntegerField, StringField, BoolField, EnumField, SignedIntegerField, Relation, Alias


class Entity:
	_fields: dict[str, Field]
	_custom_length: int = None
	_primary: tuple[str] = None
	_raw: bytes

	def __init__(self, raw_bytes):
		self._raw = raw_bytes
		assert len(raw_bytes) == self._length()
		#print("IN:", ' '.join(format(byte, '02x') for byte in raw_bytes))
		for field_name, field_info in self._fields.items():
			byte_source = raw_bytes[field_info.offset:field_info.offset+field_info.len_bytes]
			val = field_info.parse_bytes(byte_source, parent_entity=self)
			self.__setattr__(field_name, val)

	def __repr__(self):
		if hasattr(self, 'name'):
			return f"<[{self.__class__.__name__}] {self.name}>"
		else:
			return f"<[{self.__class__.__name__}]>"


	def _to_bytes(self):
		result = bytearray(self._raw)
		for field_name, field_info in self._fields.items():
			source = self.__getattribute__(field_name)
			val = field_info.dump_bytes(source)
			result[field_info.offset:field_info.offset+field_info.len_bytes] = val
		#print("OUT:", ' '.join(format(byte, '02x') for byte in result))
		assert len(result) == self._length()
		return bytes(result)

	def _to_hex(self):
		return ' '.join(format(byte, '02x') for byte in self._to_bytes())

	@classmethod
	def _length(cls):
		return cls._custom_length or max(f.offset+f.len_bytes for f in cls._fields.values())

	def __init_subclass__(cls):
		# save info in _fields
		cls._fields = {}
		for field_name, field_type in cls.__annotations__.items():
			if isinstance(getattr(cls, field_name), Field):
				cls._fields[field_name] = getattr(cls, field_name)
				cls._fields[field_name].data_type = field_type
				field_info = cls._fields[field_name]

		# make sure our definitions dont overlap
		bytes_accounted = set()
		for field_info in cls._fields.values():
			for b in range(field_info.offset, field_info.offset + field_info.len_bytes):
				assert b not in bytes_accounted
				bytes_accounted.add(b)

	def set(self, **kwargs):
		for k, v in kwargs.items():
			setattr(self, k, v)


# credit to https://github.com/Hokan-Ashir

class Localisation(Entity):
	_primary = 'text_id', 'language'

	text_id: int = IntegerField(0, 2)
	#language_id: int = IntegerField(2, 1)
	language: Language = EnumField(2, 1)
	is_dialogue: bool = BoolField(3, 1)
	dialogue_name: str = StringField(4, 50)
	text: str = StringField(54, 512)


class ItemRequirement(Entity):

	item_id: int = IntegerField(0, 2)
	requirement_number: int = IntegerField(2, 1)
	#requirement_school: int = IntegerField(3, 1)
	#requirement_school_sub: int = IntegerField(4, 1)
	requirement_school: SchoolRequirement = EnumField(3, 2)
	level: int = IntegerField(5, 1)


class SpellName(Entity):
	_custom_length = 75
	_primary = ''

	spell_name_id: int = IntegerField(0, 2)
	text_id: int = IntegerField(2, 2)

	text = Relation('localisation', {'text_id': 'text_id', 'language': Language.ENGLISH}, attributes=['text'])
	# so that the relation from spell gets passed through


class Spell(Entity):
	_custom_length = 76
	_primary = 'spell_id',

	spell_id: int = IntegerField(0, 2)
	spell_name_id: int = IntegerField(2, 2)
	#spell_name: SpellName = EnumField(2, 2)
	req1_class: SchoolRequirement = EnumField(4, 2)
	req1_level: int = IntegerField(6, 1)
	req2_class: SchoolRequirement = EnumField(7, 2)
	req2_level: int = IntegerField(9, 1)
	req3_class: SchoolRequirement = EnumField(10, 2)
	req3_level: int = IntegerField(12, 1)

	noidea: int = IntegerField(13, 3)

	mana: int = IntegerField(16, 2)
	cast_time: int = IntegerField(18, 4)
	cooldown: int = IntegerField(22, 4)
	min_range: int = IntegerField(26, 2)
	max_range: int = IntegerField(28, 2)
	cast_type: int = IntegerField(30, 2)
	# 258 aura, # 257 spell, 1025 area

	p1: int = IntegerField(32, 4)
	p2: int = IntegerField(36, 4)
	p3: int = IntegerField(40, 4)
	p4: int = IntegerField(44, 4)
	p5: int = IntegerField(48, 4)
	p6: int = IntegerField(52, 4)
	p7: int = IntegerField(56, 4)
	p8: int = IntegerField(60, 4)
	p9: int = IntegerField(64, 4)

	#name: str = Relation('localisation', {'text_id': 'name_id', 'language': Language.ENGLISH}, attributes=['text'])
	name: str = Relation('spell_names', {'spell_name_id': 'spell_name_id'}, attributes=['text'])
	level: int = Alias('req1_level')


class CreatureSpell(Entity):

	creature_id: int = IntegerField(0, 2)
	spell_position: int = IntegerField(2, 1)
	spell_id: int = IntegerField(3, 2)

	spell: Spell = Relation('spells', {'spell_id': 'spell_id'})


class HeroSpell(Entity):

	stats_id: int = IntegerField(0, 2)
	skill_number: int = IntegerField(2, 1)
	spell_id: int = IntegerField(3, 2)

	spell: Spell = Relation('spells', {'spell_id': 'spell_id'})


class CreatureSkill(Entity):

	stats_id: int = IntegerField(0 ,2)
	skill_school: SchoolRequirement = EnumField(2, 2)
	#skill_school_class: int = IntegerField(2, 1)
	#skill_school_sub: int = IntegerField(3, 1)
	skill_level: int = IntegerField(4, 1)


class CreatureStats(Entity):
	_primary = 'stats_id',

	stats_id: int = IntegerField(0, 2)
	level: int = IntegerField(2, 2)
	race: Race = EnumField(4, 1)
	agility: int = IntegerField(5, 2)
	charisma: int = IntegerField(7, 2)
	dexterity: int = IntegerField(9, 2)
	intelligence: int = IntegerField(11, 2)
	stamina: int = IntegerField(13, 2)
	strength: int = IntegerField(15, 2)
	wisdom: int = IntegerField(17, 2)

	unknown1: int = IntegerField(19, 2)

	resist_fire: int = IntegerField(21, 2)
	resist_ice: int = IntegerField(23, 2)
	resist_black: int = IntegerField(25, 2)
	resist_mind: int = IntegerField(27, 2)
	speed_walk: int = IntegerField(29, 2)
	speed_fight: int = IntegerField(31, 2)
	speed_cast: int = IntegerField(33, 2)
	size: int = IntegerField(35, 2)

	unknown2: int = IntegerField(37, 2)

	spawn_time: int = IntegerField(39, 4)
	gender: Gender = EnumField(43, 1)
	head_id: int = IntegerField(44, 2)
	equipment_slots: SlotConfiguration = EnumField(46, 1)

	skills: list[CreatureSkill] = Relation('creature_skills', {'stats_id': 'stats_id'}, multiple=True)
	spells: list[CreatureSpell] = Relation('creature_spells', {'creature_id': 'stats_id'}, multiple=True)
	hero_spells: list[CreatureSpell] = Relation('hero_spells', {'stats_id': 'stats_id'}, multiple=True)
	# todo are these connected to stats or creature?


class Armor(Entity):
	_primary = 'item_id',

	item_id: int = IntegerField(0, 2)
	strength: int = SignedIntegerField(2, 2)
	stamina: int = SignedIntegerField(4, 2)
	agility: int = SignedIntegerField(6, 2)
	dexterity: int = SignedIntegerField(8, 2)
	health: int = SignedIntegerField(10, 2)
	charisma: int = SignedIntegerField(12, 2)
	intelligence: int = SignedIntegerField(14, 2)
	wisdom: int = SignedIntegerField(16, 2)
	mana: int = SignedIntegerField(18, 2)
	armor: int = IntegerField(20, 2)
	resist_fire: int = SignedIntegerField(22, 2)
	resist_ice: int = SignedIntegerField(24, 2)
	resist_black: int = SignedIntegerField(26, 2)
	resist_mind: int = SignedIntegerField(28, 2)
	speed_run: int = SignedIntegerField(30, 2)
	speed_fight: int = SignedIntegerField(32, 2)
	speed_cast: int = SignedIntegerField(34, 2)

	requirements: list[ItemRequirement] = Relation('item_requirements', {'item_id': 'item_id'}, multiple=True)

	def info(self):
		return {
			'item_id': self.item_id,
			#'name': self.get_name(),
			#'race': self.race,
			'requirements': {r.requirement_school.name: r.level for r in self.requirements}
		}


class UnitBuildingRequirement(Entity):

	unit_id: int = IntegerField(0, 2)
	requirement_number: int = IntegerField(2, 1)
	building_id: int = IntegerField(3, 2)


class BuildingRequirement(Entity):

	building_id: int = IntegerField(0, 2)
	#resource_id: int = IntegerField(2, 1)
	resource: Resource = EnumField(2, 1)
	resource_amount: int = IntegerField(3, 2)


class Building(Entity):
	_custom_length = 23
	_primary = 'building_id',

	building_id: int = IntegerField(0, 2)
	#race_id: int = IntegerField(2, 1)
	race: Race = EnumField(2, 1)
	enter_slot: int = IntegerField(3, 1)
	slots_amount: int = IntegerField(4, 1)
	health: int = IntegerField(5, 2)
	name_id: int = IntegerField(7, 2)
	worker_job_time: int = IntegerField(14, 2)

	name: str = Relation('localisation', {'text_id': 'name_id', 'language': Language.ENGLISH}, attributes=['text'])
	requirements: list[BuildingRequirement] = Relation('building_requirements', {'building_id': 'building_id'}, multiple=True)

	def info(self):
		return {
			'building_id': self.building_id,
			'name': self.name,
			'race': self.race,
			'requirements': {r.resource.name: r.resource_amount for r in self.requirements}
		}


class Item(Entity):
	_primary = 'item_id',

	item_id: int = IntegerField(0, 2)
	#type_id: int = IntegerField(2, 2)
	item_type: ItemType = EnumField(2, 1)
	item_subtype: RuneRace | EquipmentType = EnumField(3, 1, type_decider='item_type')
	name_id: int = IntegerField(4, 2)
	unit_stats_id: int = IntegerField(6, 2)
	army_stats_id: int = IntegerField(8, 2)
	building_id: int = IntegerField(10, 2)
	unknown1: int = IntegerField(12, 1)
	selling_price: int = IntegerField(13, 4)
	buying_price: int = IntegerField(17, 4)
	item_set_id: int = IntegerField(21, 1)

	unit_stats: CreatureStats = Relation('creature_stats', {'stats_id': 'unit_stats_id'})
	army_stats: CreatureStats = Relation('creature_stats', {'stats_id': 'army_stats_id'})
	building: Building = Relation('buildings', {'building_id': 'building_id'})
	name: str = Relation('localisation', {'text_id': 'name_id', 'language': Language.ENGLISH}, attributes=['text'])

	def info(self):
		return {
			'item_id': self.item_id,
			'item_type': self.item_type.name,
			'item_subtype': self.item_subtype.name,
			'name': self.name
		}


class CreatureResourceRequirement(Entity):

	creature_id: int = IntegerField(0, 2)
	#resource_id: int = IntegerField(2, 1)
	resource: Resource = EnumField(2, 1)
	resource_amount: int = IntegerField(3, 1)


class CreatureEquipment(Entity):

	creature_id: int = IntegerField(0, 2)
	equipment_slot: EquipmentSlot = EnumField(2, 1)
	item_id: int = IntegerField(3, 2)

	item: Item = Relation('items', {'item_id': 'item_id'})


class Creature(Entity):
	_custom_length = 64
	_primary = 'creature_id',

	creature_id: int = IntegerField(0, 2)
	name_id: int = IntegerField(2, 2)
	stats_id: int = IntegerField(4 ,2)
	experience: int = IntegerField(6 ,4)
	armor: int = IntegerField(21, 2)
	unit_name: str = StringField(23, 40)

	name: str = Relation('localisation', {'text_id': 'name_id', 'language': Language.ENGLISH}, attributes=['text'])
	stats: CreatureStats = Relation('creature_stats', {'stats_id': 'stats_id'})
	requirements: list[CreatureResourceRequirement] = Relation('creature_resources', {'creature_id': 'creature_id'}, multiple=True)
	equipment: list[CreatureEquipment] = Relation('creature_equipment', {'creature_id': 'creature_id'}, multiple=True)

	skills: list[CreatureSkill] = Relation('creature_skills', {'stats_id': 'creature_id'}, multiple=True)
	spells: list[CreatureSpell] = Relation('creature_spells', {'creature_id': 'stats_id'}, multiple=True)
	# todo are these connected to stats or creature?

	def info(self):
		stats = self.stats
		extra = {
			'level': stats.level,
			'race': stats.race,
			'gender': stats.gender,
			'equipment_slots': stats.equipment_slots,
			'skills': stats.skills
		} if stats else {}
		return {
			'name': self.name,
			'unit_name': self.unit_name,
			**extra,
			'requirements': {r.resource.name: r.resource_amount for r in self.requirements},
			'equipment': {e.equipment_slot.name: e.item_id for e in self.equipment}
		}