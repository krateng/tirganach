from .types import SchoolRequirement, Language
from .fields import Field, IntegerField, StringField, BoolField, EnumField, SignedIntegerField


class Entity:
	_fields: dict[str, Field]

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
		return max(f.offset+f.len_bytes for f in cls._fields.values())

	def __init_subclass__(cls):
		# save info in _fields
		cls._fields = {}
		for field_name, field_type in cls.__annotations__.items():
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

class Armor(Entity):

	item_id: int = SignedIntegerField(0, 2)
	strength: int = IntegerField(2, 2)
	stamina: int = IntegerField(4, 2)
	agility: int = IntegerField(6, 2)
	dexterity: int = IntegerField(8, 2)
	health: int = IntegerField(10, 2)
	charisma: int = IntegerField(12, 2)
	intelligence: int = IntegerField(14, 2)
	wisdom: int = IntegerField(16, 2)
	mana: int = IntegerField(18, 2)
	armor: int = IntegerField(20, 2)
	resist_fire: int = IntegerField(22, 2)
	resist_ice: int = IntegerField(24, 2)
	resist_black: int = IntegerField(26, 2)
	resist_mind: int = IntegerField(28, 2)
	speed_run: int = IntegerField(30, 2)
	speed_fight: int = IntegerField(32, 2)
	speed_cast: int = IntegerField(34, 2)


class ItemRequirement(Entity):

	item_id: int = SignedIntegerField(0, 2)
	requirement_number: int = IntegerField(2, 1)
	#requirement_school: int = IntegerField(3, 1)
	#requirement_school_sub: int = IntegerField(4, 1)
	requirement_school: SchoolRequirement = EnumField(3, 2)
	level: int = SignedIntegerField(5, 1)


class Localisation(Entity):

	text_id: int = SignedIntegerField(0, 2)
	#language_id: int = IntegerField(2, 1)
	language: Language = EnumField(2, 1)
	is_dialogue: bool = BoolField(3, 1)
	dialogue_name: str = StringField(4, 50)
	text: str = StringField(54, 512)


class UnitBuildingRequirement(Entity):

	unit_id: int = SignedIntegerField(0, 2)
	requirement_number: int = IntegerField(2, 1)
	building_id: int = SignedIntegerField(3, 2)


class Building(Entity):

	building_id: int = SignedIntegerField(0, 2)
	race_id: int = IntegerField(2, 1)
	enter_slot: int = IntegerField(3, 1)
	slots_amount: int = IntegerField(4, 1)
	health: int = IntegerField(5, 2)
	name_id: int = SignedIntegerField(7, 2)
	worker_job_time: int = IntegerField(14, 2)


class BuildingRequirement(Entity):

	building_id: int = SignedIntegerField(0, 2)
	resource_id: int = IntegerField(2, 1)
	resource_amount: int = SignedIntegerField(3, 2)
