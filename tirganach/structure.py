from os import PathLike
from typing import Type, IO, get_origin, get_args

from tirganach.entities import Armor, Localisation, Entity, ItemRequirement, Building, BuildingRequirement, Creature, \
	CreatureStats, CreatureResourceRequirement, CreatureEquipment, CreatureSkill, Item, CreatureSpell, Spell, HeroSpell


class Table(list):
	amount: int
	entity_type: Type[Entity]
	entity_index: dict[tuple, Entity] = None

	def __init__(self, amount: int, entity_type: Type[Entity]):
		super().__init__([None] * amount)
		self.amount = amount
		self.entity_type = entity_type

	def where(self, **kwargs):
		if pkeys := self.entity_type._primary:
			if set(kwargs.keys()) == set(pkeys):
				ordered_pkeyvals = tuple(kwargs[pkey] for pkey in pkeys)
				result = self.entity_index.get(ordered_pkeyvals)
				if result:
					return [result]

		return [e for e in self if all(getattr(e, k) == v for k,v in kwargs.items())]

	def create_index(self):
		self.entity_index = self.entity_index or {}
		if pkeys := self.entity_type._primary:
			for element in self:
				if element:
					pkey_vals = tuple(getattr(element, pkey) for pkey in pkeys)
					self.entity_index[pkey_vals] = element


class GameData:
	fields: dict[str, tuple[Type[Entity], int]] = {}
	raw: bytearray
	_length: int

	def __init__(self, from_input: bytes | str | PathLike[bytes]):
		if isinstance(from_input, PathLike) or isinstance(from_input, str):
			with open(from_input, 'rb') as fd:
				raw = fd.read()
		else:
			raw = from_input

		self.raw = bytearray(raw)
		assert len(self.raw) == self._length

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
				new_instances.create_index()
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

	fields = {
		'armor': (Table[Armor], 0x897e8, 635),
		'items': (Table[Item], 0x6359e, 7101),
		'localisation': (Table[Localisation], 0x12d177, 115080),
		'item_requirements': (Table[ItemRequirement], 0x94450, 5104),
		'buildings': (Table[Building], 0x3f81c69, 207),
		'building_requirements': (Table[BuildingRequirement], 0x3f85bbe, 166),
		'creatures': (Table[Creature], 0x3f4cde6, 2617),
		'creature_stats': (Table[CreatureStats], 0x4421d, 2536),
		'creature_resources': (Table[CreatureResourceRequirement], 0x3f7defe, 128),
		'creature_equipment': (Table[CreatureEquipment], 0x3f75c32, 5905),
		'creature_skills': (Table[CreatureSkill], 0x613c1, 1374),
		'creature_spells': (Table[CreatureSpell], 0x3f7cf93, 787),
		'hero_spells': (Table[HeroSpell], 0x62ea3, 355),
		'spells': (Table[Spell], 0x20, 3439)
	}


class GameData161(GameData):
	_length = 66859988

	fields = {
		'items': (Table[Armor], 0x8a71d, 500+0), # 0, 461
		'localisation': (Table[Localisation], 0x12f2e3, 115065), # 20, 43311, 95404
		'item_requirements': (Table[ItemRequirement], 0x99e21, 100+0), # 0
		'buildings': (Table[Building], 0x3f81c94, 140)
	}
