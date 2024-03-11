from os import PathLike
from typing import Type, IO

from tirganach.entities import Item, Localisation, Entity, ItemRequirement


class GameData:
	fields: dict[str, tuple[Type[Entity], int]] = {}
	raw: bytearray

	def __init__(self, frominput: bytes | str | PathLike[bytes]):
		if isinstance(frominput, PathLike) or isinstance(frominput, str):
			with open(frominput, 'rb') as fd:
				raw = fd.read()
		else:
			raw = frominput

		self.raw = bytearray(raw)

		for fname, finfo in self.fields.items():
			entity_type, offset = finfo
			new_instance = entity_type(raw[offset:offset+entity_type.length()])
			self.__setattr__(fname, new_instance)

	def _to_bytes(self):
		for fname, finfo in self.fields.items():
			instance: Entity = self.__getattribute__(fname)
			entity_type, offset = finfo
			self.raw[offset:offset+entity_type.length()] = instance._to_bytes()
		return bytes(self.raw)

	def save(self, filename):
		with open(filename, 'wb') as fd:
			fd.write(self._to_bytes())


class GameData154(GameData):
	fields = {
		# just testing so far
		'starring': (Item, 0x8a71d),
		'foolring': (Item, 0x8e7f1),
		'starringtext': (Localisation, 0x18900cd),
		'foolringtext': (Localisation, 0x34ae72b),
		'elvenworkertext': (Localisation, 0x131f1b),
		'foolringreq': (ItemRequirement, 0x99e21)
	}

