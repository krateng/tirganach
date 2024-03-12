from .types import SchoolRequirement, Language, Race, Resource, Slots, Gender
from .fields import Field, IntegerField, StringField, BoolField, EnumField, SignedIntegerField, Relation


class Entity:
	_fields: dict[str, Field]
	_custom_length: int = None

	def __init__(self, raw_bytes):
		#print("IN:", ' '.join(format(byte, '02x') for byte in raw_bytes))
		for field_name, field_info in self._fields.items():
			byte_source = raw_bytes[field_info.offset:field_info.offset+field_info.len_bytes]
			val = field_info.parse_bytes(byte_source)
			self.__setattr__(field_name, val)

	def _to_bytes(self):
		result = bytearray(b'\x00' * self._length())
		for field_name, field_info in self._fields.items():
			source = self.__getattribute__(field_name)
			val = field_info.dump_bytes(source)
			result[field_info.offset:field_info.offset+field_info.len_bytes] = val
		#print("OUT:", ' '.join(format(byte, '02x') for byte in result))
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


# credit to https://github.com/Hokan-Ashir

class ItemRequirement(Entity):

	item_id: int = IntegerField(0, 2)
	requirement_number: int = IntegerField(2, 1)
	#requirement_school: int = IntegerField(3, 1)
	#requirement_school_sub: int = IntegerField(4, 1)
	requirement_school: SchoolRequirement = EnumField(3, 2)
	level: int = IntegerField(5, 1)


class Armor(Entity):

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
			'requirements': {r.requirement_school: r.level for r in self.requirements}
		}


class Localisation(Entity):

	text_id: int = IntegerField(0, 2)
	#language_id: int = IntegerField(2, 1)
	language: Language = EnumField(2, 1)
	is_dialogue: bool = BoolField(3, 1)
	dialogue_name: str = StringField(4, 50)
	text: str = StringField(54, 512)


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
			'requirements': {r.resource: r.resource_amount for r in self.requirements}
		}


class CreatureStats(Entity):

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

	resist_fire: int = IntegerField(21, 2)
	resist_ice: int = IntegerField(23, 2)
	resist_black: int = IntegerField(25, 2)
	resist_mind: int = IntegerField(27, 2)
	speed_walk: int = IntegerField(29, 2)
	speed_fight: int = IntegerField(31, 2)
	speed_cast: int = IntegerField(33, 2)
	size: int = IntegerField(35, 2)

	spawn_time: int = IntegerField(39, 4)
	gender: Gender = EnumField(43, 1)
	equipment_slots: Slots = EnumField(46, 1)


class Creature(Entity):
	_custom_length = 64

	creature_id: int = IntegerField(0, 2)
	name_id: int = IntegerField(2, 2)
	stats_id: int = IntegerField(4 ,2)
	experience: int = IntegerField(6 ,4)
	armor: int = IntegerField(21, 2)
	unit_name: str = StringField(23, 40)

	name: str = Relation('localisation', {'text_id': 'name_id', 'language': Language.ENGLISH}, attributes=['text'])
	stats: CreatureStats = Relation('creature_stats', {'stats_id': 'stats_id'})

	def info(self):
		stats = self.stats
		return {
			'name': self.name,
			'unit_name': self.unit_name,
			'level': stats.level,
			'race': stats.race,
			'gender': stats.gender,
			'equipment_slots': stats.equipment_slots
		}