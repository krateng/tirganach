class Field:
	offset: int
	len_bytes: int
	data_type: type

	def __init__(self, offset: int, len_bytes: int, data_type: type):
		self.offset = offset
		self.len_bytes = len_bytes
		self.data_type = data_type


class Entity:
	fields: dict[str, Field]

	def __init__(self, raw_bytes):
		#print("IN:", ' '.join(format(byte, '02x') for byte in raw_bytes))
		for fname, finfo in self.fields.items():
			byte_source = raw_bytes[finfo.offset:finfo.offset+finfo.len_bytes]
			if finfo.data_type is int:
				val = int.from_bytes(byte_source, byteorder='little', signed=True)
			elif finfo.data_type is str:
				val = byte_source.rstrip(b'\x00').decode('utf-8')
			else:
				raise NotImplemented()
			self.__setattr__(fname, val)

	def _to_bytes(self):
		result = bytearray(b'\x00' * self.length())
		for fname, finfo in self.fields.items():
			source = self.__getattribute__(fname)
			if finfo.data_type is int:
				val = source.to_bytes(finfo.len_bytes, byteorder='little', signed=True)
			elif finfo.data_type is str:
				val = source.encode('utf-8').ljust(finfo.len_bytes, b'\x00')
			else:
				raise NotImplemented()
			result[finfo.offset:finfo.offset+finfo.len_bytes] = val
		#print("OUT:", ' '.join(format(byte, '02x') for byte in result))
		return bytes(result)

	@classmethod
	def length(cls):
		return max(f.offset+f.len_bytes for f in cls.fields.values())

	def __init_subclass__(cls):
		# just make sure our definitions dont overlap
		bytes_accounted = set()
		for finfo in cls.fields.values():
			for b in range(finfo.offset, finfo.len_bytes):
				assert b not in bytes_accounted
				bytes_accounted.add(b)


# credit to https://github.com/Hokan-Ashir

class Item(Entity):

	fields = {
		'item_id': Field(offset=0, len_bytes=2, data_type=int),
		'strength': Field(offset=2, len_bytes=2, data_type=int),
		'stamina': Field(offset=4, len_bytes=2, data_type=int),
		'agility': Field(offset=6, len_bytes=2, data_type=int),
		'dexterity': Field(offset=8, len_bytes=2, data_type=int),
		'health': Field(offset=10, len_bytes=2, data_type=int),
		'charisma': Field(offset=12, len_bytes=2, data_type=int),
		'intelligence': Field(offset=14, len_bytes=2, data_type=int),
		'wisdom': Field(offset=16, len_bytes=2, data_type=int),
		'mana': Field(offset=18, len_bytes=2, data_type=int),
		'armor': Field(offset=20, len_bytes=2, data_type=int),
		'resist_fire': Field(offset=22, len_bytes=2, data_type=int),
		'resist_ice': Field(offset=24, len_bytes=2, data_type=int),
		'resist_black': Field(offset=26, len_bytes=2, data_type=int),
		'resist_mental': Field(offset=28, len_bytes=2, data_type=int),
		'speed_run': Field(offset=30, len_bytes=2, data_type=int),
		'speed_fight': Field(offset=32, len_bytes=2, data_type=int),
		'speed_cast': Field(offset=34, len_bytes=2, data_type=int)
	}


class Localisation(Entity):

	fields = {
		'text_id': Field(offset=0, len_bytes=2, data_type=int),
		'language_id': Field(offset=2, len_bytes=1, data_type=int),
		'is_dialogue': Field(offset=3, len_bytes=1, data_type=int),
		'dialogue_name': Field(offset=4, len_bytes=50, data_type=str),
		'text': Field(offset=54, len_bytes=512, data_type=str)
	}

