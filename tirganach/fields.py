from enum import Enum
from typing import Type

# important to avoid errors:
# the field instance, unlike the entity one, does not refer to one field in the actual data
# one field instance is created per entity CLASS, to define how the field looks - there is no actual field instance
# for each field, these are simply the basic data types like int etc


class Field:
	offset: int
	len_bytes: int
	data_type: type

	def __init__(self, offset: int, len_bytes: int, data_type: type = None):
		self.offset = offset
		self.len_bytes = len_bytes
		if data_type:
			self.data_type = data_type

	def parse_bytes(self, byte_source: bytes):
		raise NotImplemented()

	def dump_bytes(self, source):
		raise NotImplemented()


class IntegerField(Field):
	data_type = int
	signed: bool = False

	def parse_bytes(self, byte_source: bytes):
		assert len(byte_source) == self.len_bytes
		return int.from_bytes(byte_source, byteorder='little', signed=self.signed)

	def dump_bytes(self, source: int):
		return source.to_bytes(self.len_bytes, byteorder='little', signed=self.signed)


class SignedIntegerField(IntegerField):
	signed = True


class StringField(Field):
	data_type = str

	def parse_bytes(self, byte_source: bytes):
		assert len(byte_source) == self.len_bytes
		return byte_source.rstrip(b'\x00').decode('windows-1252')

	def dump_bytes(self, source: str):
		return source.encode('utf-8').ljust(self.len_bytes, b'\x00')


class BoolField(Field):
	data_type = bool

	def parse_bytes(self, byte_source: bytes):
		assert len(byte_source) == 1 == self.len_bytes
		return byte_source[0] != 0

	def dump_bytes(self, source: bool):
		return b'\x01' if source else b'\x00'


class EnumField(Field):
	data_type: Type[Enum]

	def parse_bytes(self, byte_source: bytes):
		assert len(byte_source) == self.len_bytes
		int_values = tuple(byte for byte in byte_source)
		return [e for e in self.data_type if e.value == int_values][0]

	def dump_bytes(self, source: Enum):
		assert isinstance(source, self.data_type)
		return b''.join([i.to_bytes(1, byteorder='little') for i in source.value])