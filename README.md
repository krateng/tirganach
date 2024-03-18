A Python library for easier editing of the SpellForce `GameData.cff`.

Information about the file structure was gathered from
* [Hokan-Ashir/SFGameDataEditor](https://github.com/Hokan-Ashir/SFGameDataEditor)
* [leszekd25/spellforce_data_editor](https://github.com/leszekd25/spellforce_data_editor)

If you're here to reverse engineer the file / create your own library, have a look at [this short explanation](./EXPLANATION.md).

Here's how you use `tirganach`:

```python
from tirganach import GameData
from tirganach.types import *
import random

gd = GameData('/games/SpellForce/data/GameData.cff')

# let's make a cool item
ring = gd.armor.where(item_id=7065)[0]
ring.mana = 500
ring.health = 300
ring.item.name = "Ring of Cheaters"

# make Azula one of our heroes
sondra = gd.items.where(item_id=4425)[0]
sondra.inventory_match.name = "Rune Princess Azula"
sondra.name = "Princess Azula"
sondra.unit_stats.head_id = 27
sondra.unit_stats.size = 90 # canonically smol

sondra.unit_stats.skills[0].set(skill_school=School.LIGHT_COMBAT, skill_level=20)
sondra.unit_stats.skills[1].set(skill_school=School.LIGHT_BLADE_WEAPONS, skill_level=20)
sondra.unit_stats.skills[2].set(skill_school=School.LIGHT_ARMOR, skill_level=20)
sondra.unit_stats.skills[3].set(skill_school=School.RANGED_COMBAT, skill_level=15)
sondra.unit_stats.skills[4].set(skill_school=School.BOWS, skill_level=15)
sondra.unit_stats.skills[5].set(skill_school=School.ELEMENTAL_MAGIC, skill_level=20)
sondra.unit_stats.skills[6].set(skill_school=School.FIRE, skill_level=20)

cool_fire_spells = gd.spells.where(level=20, req1_class=School.FIRE)
random.shuffle(cool_fire_spells)

sondra.unit_stats.hero_spells[0].set(spell_id=cool_fire_spells[0].spell_id)
sondra.unit_stats.hero_spells[1].set(spell_id=cool_fire_spells[1].spell_id)
sondra.unit_stats.hero_spells[2].set(spell_id=cool_fire_spells[2].spell_id)

# now let's make elves OP
for rune in gd.items.where(item_type=ItemType.RUNE_INVENTORY, item_subtype=RuneRace.ELVES):
    rune.unit_stats.set(agility=120, dexterity=120, intelligence=120, wisdom=150)

gd.save("/games/SpellForce/data/GameData.cff")
```