This is my attempt at creating a library for easier editing of the SpellForce `GameData.cff`.
There are some options out there, but they usually provide a full Editor / GUI - I wanted a clean library that other stuff can be implemented on top of.

```python
from tirganach import GameData154
gd = GameData154('/games/SpellForce/data/GameData.cff')
ring = gd.items.where(item_id=7065)[0]
ring.mana = 42
gd.save("/games/SpellForce/data/GameData.cff")
```