This is my attempt at creating a library for easier editing of the SpellForce `GameData.cff`.
It operates on low level data the way the database works internally, but hopefully high level abstractions
can be implemented on top of it eventually.

```python
from tirganach import GameData154
gd = GameData154('/games/SpellForce/data/GameData.cff')
ring = gd.items.where(item_id=7065)[0]
ring.mana = 42
gd.save("/games/SpellForce/data/GameData.cff")
```