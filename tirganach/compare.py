import sys
import shutil
from doreah.io import col

from .structure import GameData


def center_print(left_cell, center_cell, right_cell, pad_center=" ", separator=" "):
	left_cell = str(left_cell).rjust(30, " ")
	right_cell = str(right_cell).ljust(30, " ")
	center_cell = str(center_cell).center(25, pad_center)
	print(f"{col['red'](left_cell)} {separator} {center_cell} {separator}  {col['blue'](right_cell)}")


def compare(gd1: GameData, gd2: GameData):
	for tablename in gd1.tables():
		table1 = getattr(gd1, tablename)
		table2 = getattr(gd2, tablename)

		if table1._to_bytes() != table2._to_bytes():
			center_print("", "", "")
			center_print("", "", "", pad_center="_")
			center_print("", tablename, "", pad_center="_", separator="|")

		for row_idx in range(max(len(table1), len(table2))):
			row1 = table1[row_idx]
			row2 = table2[row_idx]

			if row1._to_bytes() != row2._to_bytes():
				center_print("", f"{row1.name} ({row_idx})" if hasattr(row1, 'name') else row_idx, "", pad_center="_")

			for attribute in row1._fields:
				if getattr(row1, attribute) != getattr(row2, attribute):
					center_print(getattr(row1, attribute), attribute, getattr(row2, attribute), separator="|")


if __name__ == '__main__':
	infiles = sys.argv[1:]
	compare(GameData(infiles[0]), GameData(infiles[1]))
