from .types import School, Language, Race, Resource, SlotConfiguration, Gender, EquipmentSlot, ItemType, \
	EquipmentType, RuneRace, RaceFlags
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


# credit to
# Hokan-Ashir (https://github.com/Hokan-Ashir/SFGameDataEditor)
# leszekd25 (https://github.com/leszekd25/spellforce_data_editor)

# notes
# hokan base path: Editor/src/main/java/sfgamedataeditor/database
# leszek base path: SpellforceDataEditor/SFCFF/category%20forms
# hokan's creature is equivalent to leszekds unit

class Localisation(Entity):
	# leszekd25: Control15.cs
	# Hokan-Ashir: text/TextObject.java

	_primary = 'text_id', 'language'

	text_id: int = IntegerField(0, 2)
	#language_id: int = IntegerField(2, 1)
	language: Language = EnumField(2, 1)
	is_dialogue: bool = BoolField(3, 1)
	dialogue_name: str = StringField(4, 50)
	text: str = StringField(54, 512)

class Description(Entity):
	# leszekd25: Control41.cs

	description_id: int = IntegerField(0, 2)
	text_id: int = IntegerField(2, 2)

	text: str = Relation('localisation', {'text_id': 'text_id', 'language': Language.ENGLISH}, attributes=['text'])


class AdvancedDescription(Entity):
	# leszekd25: Control42.cs

	description_id: int = IntegerField(0, 2)
	text_id: int = IntegerField(2, 2)
	advanced_text_id: int = IntegerField(4, 2)

	text = Relation('localisation', {'text_id': 'text_id', 'language': Language.ENGLISH}, attributes=['text'])
	text2 = Relation('localisation', {'text_id': 'advanced_text_id', 'language': Language.ENGLISH}, attributes=['text'])


class ResourceName(Entity):
	# leszekd25: Control32.cs

	#resource_id: int = IntegerField(0, 1)
	resource: Resource = EnumField(0, 1)
	text_id: int = IntegerField(1, 2)

	name = Relation('localisation', {'text_id': 'text_id', 'language': Language.ENGLISH}, attributes=['text'])


class WeaponTypeName(Entity):
	# leszekd25: Control44.cs

	weapon_type_id: int = IntegerField(0, 2)
	text_id: int = IntegerField(2, 2)
	unknown: int = IntegerField(4, 1)

	name = Relation('localisation', {'text_id': 'text_id', 'language': Language.ENGLISH}, attributes=['text'])


class WeaponMaterialName(Entity):
	# leszekd25: Control45.cs

	weapon_material_id: int = IntegerField(0, 2)
	text_id: int = IntegerField(2, 2)

	name = Relation('localisation', {'text_id': 'text_id', 'language': Language.ENGLISH}, attributes=['text'])


class Level(Entity):
	# leszekd25: Control33.cs
	# Hokan-Ashir: player/level/stats/PlayerLevelStatsObject.java

	level: int = IntegerField(0, 1)
	health_factor: int = IntegerField(1, 2)
	mana_factor: int = IntegerField(3, 2)
	exp_required: int = IntegerField(5, 4)
	attribute_points: int = IntegerField(9, 1)
	skill_points: int = IntegerField(10, 1)
	damage_factor: int = IntegerField(11, 2)
	armor_factor: int = IntegerField(13, 2)


class NPCName(Entity):
	# leszekd25: Control37.cs

	npc_id: int = IntegerField(0, 4)
	name_id: int = IntegerField(4, 2)

	name = Relation('localisation', {'text_id': 'name_id', 'language': Language.ENGLISH}, attributes=['text'])


class Map(Entity):
	# leszekd25: Control38.cs

	map_id: int = IntegerField(0, 4)
	map_handle: str = StringField(5, 64)
	name_id: str = IntegerField(69, 2) # this works for some, leads to complete nonsense localisation for others???

	name = Alias('map_handle')
	maybe_name = Relation('localisation', {'text_id': 'name_id', 'language': Language.ENGLISH}, attributes=['text'])


class Portal(Entity):
	# leszekd25: Control39.cs

	portal_id: int = IntegerField(0, 2)
	map_id: int = IntegerField(2, 4)
	position_x: int = IntegerField(6, 2)
	position_y: int = IntegerField(8, 2)
	name_id: int = IntegerField(11, 2)

	name: str = Relation('localisation', {'text_id': 'name_id', 'language': Language.ENGLISH}, attributes=['text'])
	map: Map = Relation('maps', {'map_id': 'map_id'})


class Quest(Entity):
	# leszekd25: Control43.cs

	quest_id: int = IntegerField(0, 4)
	parent_quest_id: int = IntegerField(4, 4)
	name_id: int = IntegerField(9, 2)
	description_id: int = IntegerField(11, 2)
	order_index: int = IntegerField(13, 4)

	name: str = Relation('localisation', {'text_id': 'name_id', 'language': Language.ENGLISH}, attributes=['text'])
	description: str = Relation('advanced_descriptions', {'description_id': 'description_id'}, attributes=['text'])
	description2: str = Relation('advanced_descriptions', {'description_id': 'description_id'}, attributes=['text2'])
	# todo these dont seem to work

	parent_quest: 'Quest' = Relation('quests', {'quest_id': 'parent_quest_id'})
	sub_quests: 'list[Quest]' = Relation('quests', {'parent_quest_id': 'quest_id'}, multiple=True)


class RaceDB(Entity):
	# leszekd25: Control16.cs

	race_id: int = IntegerField(0, 1)
	range1: int = IntegerField(1, 1)
	range2: int = IntegerField(2, 1)
	range3: int = IntegerField(3, 1)
	percentage1: int = IntegerField(4, 1)
	percentage2: int = IntegerField(5, 1)
	percentage3: int = IntegerField(6, 1)
	name_id: int = IntegerField(7, 2)
	race_flags: RaceFlags = EnumField(9, 1)
	clan_id: int = IntegerField(10, 2)
	damage_taken_melee: int = IntegerField(12, 1)
	damage_taken_ranged: int = IntegerField(13, 1)
	unknown: int = IntegerField(14, 2)

	lua1: int = IntegerField(16, 1)
	lua2: int = IntegerField(17, 1)
	lua3: int = IntegerField(18, 1)
	unknown2: int = IntegerField(19, 1)
	unknown3: int = IntegerField(20, 2)

	retreat_chance1: int = IntegerField(22, 2)
	retreat_chance2: int = IntegerField(24, 2)
	attack_time_factor: int = IntegerField(26, 1)

	name = Relation('localisation', {'text_id': 'name_id', 'language': Language.ENGLISH}, attributes=['text'])


class Upgrade(Entity):
	# leszekd25: Control48.cs

	button_id: int = IntegerField(0, 2)
	building_id: int = IntegerField(2, 2)
	name_id: int = IntegerField(4, 2)
	description_id: int = IntegerField(6, 2) # not a normal localisation ref!!!
	cost_wood: int = IntegerField(8, 2)
	cost_stone: int = IntegerField(10, 2)
	cost_iron: int = IntegerField(12, 2)
	cost_lenya: int = IntegerField(14, 2)
	cost_aria: int = IntegerField(16, 2)
	cost_moonsilver: int = IntegerField(18, 2)
	cost_food: int = IntegerField(20, 2)
	button_handle: str = StringField(22, 64)
	research_time: int = IntegerField(88, 2)

	name: str = Relation('localisation', {'text_id': 'name_id', 'language': Language.ENGLISH}, attributes=['text'])
	description: str = Relation('descriptions', {'description_id': 'description_id'}, attributes=['text'])


class ItemInstall(Entity):
	# leszekd25: Control9.cs

	inventory_item_id: int = IntegerField(0, 2)
	installed_item_id: int = IntegerField(2, 2)

	inventory_item: 'Item' = Relation('items', {'item_id': 'inventory_item_id'})
	installed_item: 'Item' = Relation('items', {'item_id': 'installed_item_id'})

class ItemRequirement(Entity):
	# leszekd25: Control11.cs
	# Hokan-Ashir: items/requirements/ItemRequirementsObject.java

	item_id: int = IntegerField(0, 2)
	requirement_number: int = IntegerField(2, 1)
	#requirement_school: int = IntegerField(3, 1)
	#requirement_school_sub: int = IntegerField(4, 1)
	requirement_school: School = EnumField(3, 2)
	level: int = IntegerField(5, 1)


class ItemEffect(Entity):
	# leszekd25: Control12.cs
	# Hokan-Ashir: items/effects/ItemEffectsObject.java

	item_id: int = IntegerField(0, 2)
	effect_index: int = IntegerField(2, 1) # verify
	effect_id: int = IntegerField(3, 2)


class ItemUI(Entity):
	# leszekd25: Control13.cs

	item_id: int = IntegerField(0, 2)
	item_ui_index: int = IntegerField(2, 1)
	item_ui_handle: str = StringField(3, 64) # verify
	scaled_down: int = IntegerField(67, 2) # verify - why 2 bytes?


class SpellName(Entity):
	# leszekd25: Control2.cs
	# Hokan-Ashir: spells/names/SpellNameObject.java (sort of)

	_custom_length = 75
	_primary = 'spell_name_id',

	spell_name_id: int = IntegerField(0, 2)
	text_id: int = IntegerField(2, 2)
	spell_flags: int = IntegerField(4, 1)
	magic_type: int = IntegerField(5, 1)
	min_level: int = IntegerField(6, 1)
	max_level: int = IntegerField(7, 1)
	availability: int = IntegerField(8, 1)
	spell_ui_handle: str = StringField(9, 64)
	description_id: int = IntegerField(73, 2)

	name = Relation('localisation', {'text_id': 'text_id', 'language': Language.ENGLISH}, attributes=['text'])
	# so that the relation from spell gets passed through
	description = Relation('localisation', {'text_id': 'description_id', 'language': Language.ENGLISH}, attributes=['text'])


class SpellEffect(Entity):
	# leszekd25: Control14.cs
	# Hokan-Ashir: items/spelleffect/ItemSpellEffectsObject.java

	spell_item_id: int = IntegerField(0, 2)
	effect_id: int = IntegerField(2, 2)


class Spell(Entity):
	# leszekd25: Control1.cs
	# Hokan-Ashir: spells/parameters/SpellParametersObject.java

	_custom_length = 76
	_primary = 'spell_id',

	spell_id: int = IntegerField(0, 2)
	spell_name_id: int = IntegerField(2, 2)
	#spell_name: SpellName = EnumField(2, 2)
	req1_class: School = EnumField(4, 2)
	req1_level: int = IntegerField(6, 1)
	req2_class: School = EnumField(7, 2)
	req2_level: int = IntegerField(9, 1)
	req3_class: School = EnumField(10, 2)
	req3_level: int = IntegerField(12, 1)

	noidea: int = IntegerField(13, 3) # req 4 according to leszekd25

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

	effect_power: int = IntegerField(68, 2) # leszekd25
	effect_range: int = IntegerField(70, 2) # leszekd25

	#name: str = Relation('localisation', {'text_id': 'name_id', 'language': Language.ENGLISH}, attributes=['text'])
	name: str = Relation('spell_names', {'spell_name_id': 'spell_name_id'}, attributes=['name'])
	level: int = Alias('req1_level')
	effects: list[int] = Relation('spell_effects', {'spell_item_id': 'spell_id'}, attributes=['effect_id'], multiple=True)


class CreatureSpell(Entity):
	# leszekd25: Control20.cs
	# Hokan-Ashir: creatures/spells/CreatureSpellObject.java

	creature_id: int = IntegerField(0, 2)
	spell_position: int = IntegerField(2, 1)
	spell_id: int = IntegerField(3, 2)

	spell: Spell = Relation('spells', {'spell_id': 'spell_id'})


class HeroSpell(Entity):
	# leszekd25: Control6.cs
	# Hokan-Ashir: creatures/herospells/HeroSpellObject.java

	stats_id: int = IntegerField(0, 2)
	spell_position: int = IntegerField(2, 1)
	spell_id: int = IntegerField(3, 2)

	spell: Spell = Relation('spells', {'spell_id': 'spell_id'})


class CreatureSkill(Entity):
	# leszekd25: Control5.cs
	# Hokan-Ashir: creatures/skills/CreatureSkillObject.java

	stats_id: int = IntegerField(0 ,2)
	skill_school: School = EnumField(2, 2)
	#skill_school_class: int = IntegerField(2, 1)
	#skill_school_sub: int = IntegerField(3, 1)
	skill_level: int = IntegerField(4, 1)


class CreatureStats(Entity):
	# leszekd25: Control4.cs
	# HokanAshir: creatures/parameters/CreatureParameterObject.java

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

	random_init: int = IntegerField(19, 2) # from leszekd25

	resist_fire: int = IntegerField(21, 2)
	resist_ice: int = IntegerField(23, 2)
	resist_black: int = IntegerField(25, 2)
	resist_mind: int = IntegerField(27, 2)
	speed_walk: int = IntegerField(29, 2)
	speed_fight: int = IntegerField(31, 2)
	speed_cast: int = IntegerField(33, 2)
	size: int = IntegerField(35, 2)

	mana_usage: int = IntegerField(37, 2) # from leszekd25

	spawn_time: int = IntegerField(39, 4)
	gender: Gender = EnumField(43, 1)
	head_id: int = IntegerField(44, 2)
	equipment_slots: SlotConfiguration = EnumField(46, 1)

	skills: list[CreatureSkill] = Relation('creature_skills', {'stats_id': 'stats_id'}, multiple=True)
	spells: list[CreatureSpell] = Relation('creature_spells', {'creature_id': 'stats_id'}, multiple=True)
	hero_spells: list[CreatureSpell] = Relation('hero_spells', {'stats_id': 'stats_id'}, multiple=True)
	# todo are these connected to stats or creature?


class Armor(Entity):
	# leszekd25: Control8.cs
	# Hokan-Ashir: items/armor/parameters/ArmorParametersObject.java

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

	item: 'Item' = Relation('items', {'item_id': 'item_id'})
	requirements: list[ItemRequirement] = Relation('item_requirements', {'item_id': 'item_id'}, multiple=True)

	def info(self):
		return {
			'item_id': self.item_id,
			#'name': self.get_name(),
			#'race': self.race,
			'requirements': {r.requirement_school.name: r.level for r in self.requirements}
		}


class UnitBuildingRequirement(Entity):
	# leszekd25: Control23.cs
	# Hokan-Ashir: buildings/army/requirements/BuildingsArmyRequirementsObject.java
	# Hokan-Ashir: creatures/production/buildings/CreatureBuildingsObject.java
	# yeah they have the same offset, not sure why twice

	unit_id: int = IntegerField(0, 2)
	requirement_number: int = IntegerField(2, 1)
	building_id: int = IntegerField(3, 2)


class BuildingRequirement(Entity):
	# leszekd25: Control26.cs
	# Hokan-Ashir: buildings/requirements/BuildingsRequirementsObject.java

	building_id: int = IntegerField(0, 2)
	#resource_id: int = IntegerField(2, 1)
	resource: Resource = EnumField(2, 1)
	resource_amount: int = IntegerField(3, 2)


class Building(Entity):
	# leszekd25: Control24.cs
	# Hokan-Ashir: buildings/common/BuildingsObject.java

	_custom_length = 23
	_primary = 'building_id',

	building_id: int = IntegerField(0, 2)
	#race_id: int = IntegerField(2, 1)
	race: Race = EnumField(2, 1)
	enter_slot: int = IntegerField(3, 1)
	slots_amount: int = IntegerField(4, 1)
	health: int = IntegerField(5, 2)
	name_id: int = IntegerField(7, 2)
	rotate_center_x: int = IntegerField(9, 2)
	rotate_center_y: int = IntegerField(11, 2)
	collision_polygons: int = IntegerField(13, 1)
	worker_job_time: int = IntegerField(14, 2)
	required_building_id: int = IntegerField(16, 2)
	initial_angle: int = IntegerField(18, 2)
	description_id: int = IntegerField(20, 2)
	flags: int = IntegerField(22, 1)

	name: str = Relation('localisation', {'text_id': 'name_id', 'language': Language.ENGLISH}, attributes=['text'])
	description: str = Relation('localisation', {'text_id': 'description_id', 'language': Language.ENGLISH}, attributes=['text'])
	requirements: list[BuildingRequirement] = Relation('building_requirements', {'building_id': 'building_id'}, multiple=True)

	def info(self):
		return {
			'building_id': self.building_id,
			'name': self.name,
			'race': self.race,
			'requirements': {r.resource.name: r.resource_amount for r in self.requirements}
		}


class ItemSet(Entity):
	# leszekd25: Control49.cs

	set_id: int = IntegerField(0, 1)
	text_id: int = IntegerField(1, 2)
	set_type: int = IntegerField(3, 1)

	description: str = Relation('localisation', {'text_id': 'text_id', 'language': Language.ENGLISH}, attributes=['text'])


class Item(Entity):
	# leszekd25: Control7.cs
	# Hokan-Ashir: items/price/parameters/ItemPriceParametersObject.java

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
	inventory_match: 'Item' = Relation('item_installs', {'installed_item_id': 'item_id'}, attributes=['inventory_item'])
	installed_match: 'Item' = Relation('item_installs', {'inventory_item_id': 'item_id'}, attributes=['installed_item'])

	def info(self):
		return {
			'item_id': self.item_id,
			'item_type': self.item_type.name,
			'item_subtype': self.item_subtype.name,
			'name': self.name
		}


class Weapon(Entity):
	# leszekd25: Control10.cs
	# Hokan-Ashir: items/weapon/parameters/WeaponParametersObject.java

	item_id: int = IntegerField(0, 2)
	min_damage: int = IntegerField(2, 2)
	max_damage: int = IntegerField(4, 2)
	min_range: int = IntegerField(6, 2)
	max_range: int = IntegerField(8, 2)
	speed: int = IntegerField(10, 2)
	weapon_type: int = IntegerField(12, 2)
	material: int = IntegerField(14, 2)

	item: Item = Relation('items', {'item_id': 'item_id'})
	effects: list[int] = Relation('item_effects', {'item_id': 'item_id'}, attributes=['effect_id'], multiple=True)


class CreatureResourceRequirement(Entity):
	# leszekd25: Control21.cs
	# Hokan-Ashir: creatures/production/resources/CreatureResourcesObject.java

	creature_id: int = IntegerField(0, 2)
	#resource_id: int = IntegerField(2, 1)
	resource: Resource = EnumField(2, 1)
	resource_amount: int = IntegerField(3, 1)


class CreatureEquipment(Entity):
	# leszekd25: Control19.cs
	# Hokan-Ashir: creatures/equipment/CreatureEquipmentObject.java

	creature_id: int = IntegerField(0, 2)
	equipment_slot: EquipmentSlot = EnumField(2, 1)
	item_id: int = IntegerField(3, 2)

	item: Item = Relation('items', {'item_id': 'item_id'})


class SkillRequirement(Entity):
	# leszekd25: Control28.cs
	# Hokan-Ashir: skill/parameters/SkillParameterObject.java

	skill_id: int = IntegerField(0, 1) # what
	skill_level: int = IntegerField(1, 1)
	strength: int = IntegerField(2, 1)
	stamina: int = IntegerField(3, 1)
	agility: int = IntegerField(4, 1)
	dexterity: int = IntegerField(5, 1)
	charisma: int = IntegerField(6, 1)
	intelligence: int = IntegerField(7, 1)
	wisdom: int = IntegerField(8, 1)


class Skill(Entity):
	# leszekd25: Control27.cs

	major_type: int = IntegerField(0, 1)
	minor_type: int = IntegerField(1, 1)
	text_id: int = IntegerField(2, 2)

	name = Relation('localisation', {'text_id': 'text_id', 'language': Language.ENGLISH}, attributes=['text'])


class Creature(Entity):
	# leszekd25: Control18.cs
	# Hokan-Ashir: creatures/common/CreaturesCommonParameterObject.java
	_custom_length = 64
	_primary = 'creature_id',

	creature_id: int = IntegerField(0, 2)
	name_id: int = IntegerField(2, 2)
	stats_id: int = IntegerField(4 ,2)
	experience: int = IntegerField(6 ,4)
	experience_falloff: int = IntegerField(10, 2)
	money_copper: int = IntegerField(12, 4)
	gold_variance: int = IntegerField(16, 2)
	rangedness: int = IntegerField(18, 1)
	meat: int = IntegerField(19, 2)
	armor: int = IntegerField(21, 2)
	unit_handle: str = StringField(23, 40)
	placeable_editor: bool = BoolField(63, 1)

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