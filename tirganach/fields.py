import enum
import types
from enum import Enum
from typing import Type

from tirganach.types import UnknownEnumMember

debug_missing_enum_members = {}

# important to avoid errors:
# the field instance, unlike the entity one, does not refer to one field in the actual data
# one field instance is created per entity CLASS, to define how the field looks - there is no actual field instance
# for each field, these are simply the basic data types like int etc


class Field:
	offset: int
	len_bytes: int
	data_type: type
	type_decider: str
	# type decider stores the name of another field in the entity
	# the value of this field must be an enum which implements determine_sub_type

	def __init__(self, offset: int, len_bytes: int, data_type: type = None, type_decider: str = None):
		self.offset = offset
		self.len_bytes = len_bytes
		if data_type:
			self.data_type = data_type
		if type_decider:
			self.type_decider = type_decider

	def parse_bytes(self, byte_source: bytes, parent_entity=None):
		raise NotImplemented()

	def dump_bytes(self, source):
		raise NotImplemented()


class IntegerField(Field):
	data_type = int
	signed: bool = False

	def parse_bytes(self, byte_source: bytes, parent_entity=None):
		assert len(byte_source) == self.len_bytes
		return int.from_bytes(byte_source, byteorder='little', signed=self.signed)

	def dump_bytes(self, source: int):
		return source.to_bytes(self.len_bytes, byteorder='little', signed=self.signed)


class SignedIntegerField(IntegerField):
	signed = True


class StringField(Field):
	data_type = str

	def parse_bytes(self, byte_source: bytes, parent_entity=None):
		assert len(byte_source) == self.len_bytes
		return byte_source.rstrip(b'\x00').decode('windows-1252')

	def dump_bytes(self, source: str):
		result = source.encode('windows-1252').ljust(self.len_bytes, b'\x00')
		assert len(result) == self.len_bytes
		return result


class BoolField(Field):
	data_type = bool

	def parse_bytes(self, byte_source: bytes, parent_entity=None):
		assert len(byte_source) == 1 == self.len_bytes
		assert byte_source[0] in (0, 1)
		return byte_source[0] != 0

	def dump_bytes(self, source: bool):
		return b'\x01' if source else b'\x00'


class EnumField(Field):
	data_type: Type[Enum]

	def parse_bytes(self, byte_source: bytes, parent_entity=None):
		assert len(byte_source) == self.len_bytes
		int_values = tuple(byte for byte in byte_source)

		if isinstance(self.data_type, types.UnionType):
			correct_data_type = getattr(parent_entity, self.type_decider).determine_sub_type()
		elif issubclass(self.data_type, enum.Flag):
			correct_data_type = self.data_type
			int_values = int_values[0]
		else:
			correct_data_type = self.data_type

		try:
			return correct_data_type(int_values)
			#return [e for e in correct_data_type if e.value == int_values][0]
		except ValueError:
			debug_missing_enum_members.setdefault(correct_data_type, set()).add(int_values)
			return UnknownEnumMember(value=int_values, cls=correct_data_type)

	def dump_bytes(self, source: Enum):
		if isinstance(source, UnknownEnumMember):
			pass
			# val will also be in source.value
		else:
			assert isinstance(source, self.data_type)
		if isinstance(source, enum.Flag):
			source_value = [source.value]
		else:
			source_value = source.value
		result = b''.join([i.to_bytes(1, byteorder='little') for i in source_value])
		assert len(result) == self.len_bytes
		return result


class Relation:
	mapping: dict
	target_table: str
	multiple: bool
	attributes: list

	# todo: assign object directly to relation -> sets reference id

	def __init__(self, table_name: str, mapping: dict, multiple=False, attributes=[]):
		self.table_name = table_name
		self.mapping = mapping
		self.multiple = multiple
		self.attributes = attributes

	def __get__(self, instance, owner):
		if not instance: return None

		result = self._get_proxied(instance)
		for key in self.attributes:
			result = [getattr(r, key) for r in result]
		if not result:
			return None
		if not self.multiple:
			result = result[0]
		return result

	def __set__(self, instance, value):
		if self.multiple:
			print("Cannot set to iterable proxies!")
			raise ValueError()
		if not self.attributes:
			print("Cannot set Proxy directly!")
			raise ValueError()

		result = self._get_proxied(instance)
		for key in self.attributes[:-1]:
			result = [getattr(r, key) for r in result]
		assert len(result) == 1
		result = result[0]
		setattr(result, self.attributes[-1], value)

	def _get_proxied(self, instance):

		gd = instance._game_data
		table = getattr(gd, self.table_name)
		instanced_mapping = {}
		for k,v in self.mapping.items():
			if isinstance(v, str):
				instanced_mapping[k] = getattr(instance, v)
			else:
				instanced_mapping[k] = v
		result = table.where(**instanced_mapping)
		return result


class Alias:
	target: str

	def __init__(self, target):
		self.target = target

	def __get__(self, instance, owner):
		if not instance: return None
		return getattr(instance, self.target)

	def __set__(self, instance, value):
		if not instance: return None
		return setattr(instance, self.target, value)