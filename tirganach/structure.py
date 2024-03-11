from os import PathLike
from typing import Type, IO, get_origin, get_args

from tirganach.entities import Armor, Localisation, Entity, ItemRequirement, Building


class Table(list):
	amount: int
	entity_type: Type[Entity]

	def __init__(self, amount: int, entity_type: Type[Entity]):
		super().__init__([None] * amount)
		self.amount = amount
		self.entity_type = entity_type

	def where(self, **kwargs):
		return [e for e in self if all(getattr(e, k) == v for k,v in kwargs.items())]


class GameData:
	fields: dict[str, tuple[Type[Entity], int]] = {}
	raw: bytearray

	def __init__(self, from_input: bytes | str | PathLike[bytes]):
		if isinstance(from_input, PathLike) or isinstance(from_input, str):
			with open(from_input, 'rb') as fd:
				raw = fd.read()
		else:
			raw = from_input

		self.raw = bytearray(raw)

		for fname, finfo in self.fields.items():
			entity_type, offset, *other = finfo
			if get_origin(entity_type) is Table:
				amount = other[0]
				sub_entity_type: Type[Entity] = get_args(entity_type)[0]
				new_instances = Table(amount, sub_entity_type)
				for idx in range(0, amount):
					sub_offset = offset + (idx * sub_entity_type._length())
					new_instance: Entity = sub_entity_type(raw[sub_offset:sub_offset+sub_entity_type._length()])
					new_instance._game_data = self
					new_instances[idx] = new_instance
				self.__setattr__(fname, new_instances)
			else:
				new_instance: Entity = entity_type(raw[offset:offset+entity_type._length()])
				new_instance._game_data = self
				self.__setattr__(fname, new_instance)

	def _to_bytes(self):
		for fname, finfo in self.fields.items():
			entity_type, offset, *other = finfo
			if get_origin(entity_type) is Table:
				amount = other[0]
				sub_entity_type: Type[Entity] = get_args(entity_type)[0]
				instances: Table = self.__getattribute__(fname)
				for idx in range(0, amount):
					sub_offset = offset + (idx * sub_entity_type._length())
					instance: sub_entity_type = instances[idx]
					self.raw[sub_offset:sub_offset+sub_entity_type._length()] = instance._to_bytes()
			else:
				instance: Entity = self.__getattribute__(fname)
				self.raw[offset:offset+entity_type._length()] = instance._to_bytes()
		return bytes(self.raw)

	def save(self, filename):
		with open(filename, 'wb') as fd:
			fd.write(self._to_bytes())


class GameData154(GameData):
	fields = {
		# just testing so far
		'items': (Table[Armor], 0x8a71d, 462), # 0, 461
		'localisation': (Table[Localisation], 0x12f2e3, 115065), # 20, 43311, 95404
		'item_requirements': (Table[ItemRequirement], 0x99e21, 4), # 0
		'buildings': (Table[Building], 0x3f81c94, 140)
	}

