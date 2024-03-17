The `GameData.cff` file is basically a relational database.
All values are in little endian.

The file is structured as follows:

* 20 bytes of general info (not yet interpreted)
* Tables in a [fixed order](./tirganach/structure.py). For each table:
  * 12 bytes header:
    * 0-5 unknown
    * 6-9 table length in bytes
    * 10-11 unknown
  * Table data. Exactly as long as the header length indicates,
    with fixed byte length per row [according to the represented entity](./tirganach/entities.py).  
    Strings are encoded in `windows-1252` and right-padded with `0x00` bytes.  
    Values are always at least one byte, even booleans (they are only `0x00` or `0x01`).  
    Some fields are flags - their individual bits encode certain bool values,
    but they are always part of a byte-aligned flag group
    (so when there's three flags, the byte can take values up to 0x07 and the remaining bits are unused).
