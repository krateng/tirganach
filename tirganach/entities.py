from enum import Enum

from .types import SchoolRequirement

class Field:
	offset: int
	len_bytes: int
	data_type: type

	def __init__(self, offset: int, len_bytes: int, data_type: type = None):
		self.offset = offset
		self.len_bytes = len_bytes
		self.data_type = data_type


class Entity:
	_fields: dict[str, Field]

	def __init__(self, raw_bytes):
		#print("IN:", ' '.join(format(byte, '02x') for byte in raw_bytes))
		for field_name, field_info in self._fields.items():
			byte_source = raw_bytes[field_info.offset:field_info.offset+field_info.len_bytes]
			if field_info.data_type is int:
				val = int.from_bytes(byte_source, byteorder='little', signed=True)
			elif field_info.data_type is str:
				val = byte_source.rstrip(b'\x00').decode('utf-8')
			elif field_info.data_type is bool:
				assert len(byte_source) == 1
				val = (byte_source[0] != 0)
			elif field_info.data_type is SchoolRequirement:
				intvals = tuple(byte for byte in byte_source)
				val = [e for e in SchoolRequirement if e.value == intvals][0]
			else:
				raise NotImplemented()
			self.__setattr__(field_name, val)

	def _to_bytes(self):
		result = bytearray(b'\x00' * self.length())
		for field_name, field_info in self._fields.items():
			source = self.__getattribute__(field_name)
			if field_info.data_type is int:
				val = source.to_bytes(field_info.len_bytes, byteorder='little', signed=True)
			elif field_info.data_type is str:
				val = source.encode('utf-8').ljust(field_info.len_bytes, b'\x00')
			elif field_info.data_type is bool:
				val = b'\x01' if source else b'\x00'
			elif field_info.data_type is SchoolRequirement:
				val = b''.join([i.to_bytes(1, byteorder='little') for i in source.value])
			else:
				raise NotImplemented()
			result[field_info.offset:field_info.offset+field_info.len_bytes] = val
		#print("OUT:", ' '.join(format(byte, '02x') for byte in result))
		return bytes(result)

	@classmethod
	def length(cls):
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

class Item(Entity):

	item_id: int = Field(0, 2)
	strength: int = Field(2, 2)
	stamina: int = Field(4, 2)
	agility: int = Field(6, 2)
	dexterity: int = Field(8, 2)
	health: int = Field(10, 2)
	charisma: int = Field(12, 2)
	intelligence: int = Field(14, 2)
	wisdom: int = Field(16, 2)
	mana: int = Field(18, 2)
	armor: int = Field(20, 2)
	resist_fire: int = Field(22, 2)
	resist_ice: int = Field(24, 2)
	resist_black: int = Field(26, 2)
	resist_mind: int = Field(28, 2)
	speed_run: int = Field(30, 2)
	speed_fight: int = Field(32, 2)
	speed_cast: int = Field(34, 2)


class ItemRequirement(Entity):

	item_id: int = Field(0, 2)
	requirement_number: int = Field(2, 1)
	#requirement_school: int = Field(3, 1)
	#requirement_school_sub: int = Field(4, 1)
	requirement_school: SchoolRequirement = Field(3, 2)
	level: int = Field(5, 1)


class Localisation(Entity):

	text_id: int = Field(0, 2)
	language_id: int = Field(2, 1)
	is_dialogue: bool = Field(3, 1)
	dialogue_name: str = Field(4, 50)
	text: str = Field(54, 512)


class UnitBuildingRequirement(Entity):

	unit_id: int = Field(0, 2)
	requirement_number: int = Field(2, 1)
	building_id: int = Field(3, 2)


class Building(Entity):

	building_id: int = Field(0, 2)
	race_id: int = Field(2, 1)
	enter_slot: int = Field(3, 1)
	slots_amount: int = Field(4, 1)
	health: int = Field(5, 2)
	name_id: int = Field(7, 2)
	worker_job_time: int = Field(14, 2)


class BuildingRequirement(Entity):

	building_id: int = Field(0, 2)
	resource_id: int = Field(2, 1)
	resource_amount: int = Field(3, 2)
