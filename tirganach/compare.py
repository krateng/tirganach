import shutil

from .structure import GameData, GameData154

from doreah.io import col


def center_print(left_cell, center_cell, right_cell, header=False):
	filler = "_" if header else " "
	left_cell = str(left_cell).rjust(30, " ")
	right_cell = str(right_cell).ljust(30, " ")
	center_cell = str(center_cell).center(25, filler)
	if header:
		print(f"{left_cell}   {center_cell}   {right_cell}")
	else:
		print(f"{col['red'](left_cell)} | {center_cell} | {col['blue'](right_cell)}")



def compare(gd1: GameData, gd2: GameData):
	for name in gd1.fields:
		entry1 = getattr(gd1, name)
		entry2 = getattr(gd2, name)

		no_diffs_yet = True

		for fieldname in entry1._fields:
			fieldname: str
			value1 = getattr(entry1, fieldname)
			value2 = getattr(entry2, fieldname)

			if value1 != value2:
				if no_diffs_yet:
					center_print("", name, "", header=True)
					no_diffs_yet = False
				center_print(value1, fieldname, value2)