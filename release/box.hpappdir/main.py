from level import Level
import hpprime
import directions
from tileset import Tileset
from palettes import Palettes
from hub import select_level, load_levels_from_chapter, hub

Tileset().init(2, 9, 64, 64)
Palettes().init()

hub()

level = """
version 4
#
Block -1 -1 0 7 7 0.6 0.8 1 1 0 0 0 0 0 0 0
	Ref 0 0 0 0 0 0 0 0 -1 0 0 0 0 0 0
	Ref 3 1 0 1 0 0 0 0 -1 0 0 0 1 0 0
	Wall 0 3 0 0 0
	Wall 0 4 0 0 0
	Wall 0 5 0 0 0
	Wall 0 6 0 0 0
	Wall 1 3 0 0 0
	Wall 1 4 0 0 0
	Wall 1 5 0 0 0
	Wall 1 6 0 0 0
	Wall 2 0 0 0 0
	Wall 2 1 0 0 0
	Wall 2 3 0 0 0
	Wall 2 4 0 0 0
	Wall 2 6 0 0 0
	Wall 3 0 0 0 0
	Wall 4 0 0 0 0
	Wall 4 1 0 0 0
	Wall 4 3 0 0 0
	Wall 4 6 0 0 0
	Wall 5 0 0 0 0
	Wall 5 1 0 0 0
	Wall 5 2 0 0 0
	Wall 5 3 0 0 0
	Wall 5 4 0 0 0
	Wall 5 5 0 0 0
	Wall 5 6 0 0 0
	Wall 6 0 0 0 0
	Wall 6 1 0 0 0
	Wall 6 2 0 0 0
	Wall 6 3 0 0 0
	Wall 6 4 0 0 0
	Wall 6 5 0 0 0
	Wall 6 6 0 0 0
	Block 0 1 1 5 5 0.9 1 0.7 1 1 1 1 0 0 0 0
	Block 2 2 3 5 5 0.1 0.8 1 0.4 0 0 0 0 0 0 0
		Wall 0 0 0 0 0
		Wall 0 1 0 0 0
		Wall 0 3 0 0 0
		Wall 0 4 0 0 0
		Wall 1 0 0 0 0
		Wall 1 1 0 0 0
		Wall 2 0 0 0 0
		Wall 2 1 0 0 0
		Wall 2 2 0 0 0
		Wall 2 3 0 0 0
		Wall 2 4 0 0 0
		Wall 3 0 0 0 0
		Wall 3 1 0 0 0
		Wall 3 2 0 0 0
		Wall 3 3 0 0 0
		Wall 3 4 0 0 0
		Wall 4 0 0 0 0
		Wall 4 1 0 0 0
		Wall 4 2 0 0 0
		Wall 4 3 0 0 0
		Wall 4 4 0 0 0
	Block 2 5 5 5 5 0.4 0.8 1 0.4 0 0 0 0 0 0 0
		Wall 4 0 0 0 0
		Wall 4 2 0 0 0
		Wall 4 3 0 0 0
		Wall 4 4 0 0 0
		Floor 2 2 PlayerButton
	Block 3 2 8 3 3 0.1 0.8 1 1 0 0 0 0 0 0 0
		Wall 0 0 0 0 0
		Wall 0 1 0 0 0
		Wall 0 2 0 0 0
		Wall 1 0 0 0 0
		Wall 1 2 0 0 0
		Wall 2 0 0 0 0
		Wall 2 1 0 0 0
		Wall 2 2 0 0 0
	Block 3 3 4 5 5 0.1 0.8 1 0.4 0 0 0 0 0 0 0
		Wall 0 0 0 0 0
		Wall 0 1 0 0 0
		Wall 0 2 0 0 0
		Wall 0 3 0 0 0
		Wall 0 4 0 0 0
		Wall 1 0 0 0 0
		Wall 1 1 0 0 0
		Wall 1 2 0 0 0
		Wall 1 3 0 0 0
		Wall 1 4 0 0 0
		Wall 2 0 0 0 0
		Wall 2 1 0 0 0
		Wall 2 2 0 0 0
		Wall 2 3 0 0 0
		Wall 2 4 0 0 0
		Wall 3 0 0 0 0
		Wall 4 0 0 0 0
		Wall 4 2 0 0 0
		Wall 4 3 0 0 0
		Wall 4 4 0 0 0
	Block 3 4 9 3 3 0.1 0.8 1 1 0 0 0 0 0 0 0
		Wall 0 0 0 0 0
		Wall 0 1 0 0 0
		Wall 0 2 0 0 0
		Wall 1 0 0 0 0
		Wall 1 2 0 0 0
		Wall 2 0 0 0 0
		Wall 2 1 0 0 0
		Wall 2 2 0 0 0
	Block 3 5 10 3 3 0.1 0.8 1 1 0 0 0 0 0 0 0
		Wall 0 0 0 0 0
		Wall 0 1 0 0 0
		Wall 0 2 0 0 0
		Wall 1 0 0 0 0
		Wall 1 2 0 0 0
		Wall 2 0 0 0 0
		Wall 2 1 0 0 0
		Wall 2 2 0 0 0
	Block 3 6 7 3 3 0.1 0.8 1 1 0 0 0 0 0 0 0
		Wall 0 0 0 0 0
		Wall 0 1 0 0 0
		Wall 0 2 0 0 0
		Wall 1 0 0 0 0
		Wall 1 2 0 0 0
		Wall 2 0 0 0 0
		Wall 2 1 0 0 0
		Wall 2 2 0 0 0
	Block 4 4 6 5 5 0.4 0.8 1 0.4 0 0 0 0 0 0 0
	Block 4 5 2 5 5 0.4 0.8 1 0.4 0 0 0 0 0 0 0
		Wall 0 1 0 0 0
"""

# level = Level(level)
# level.render(1)
# player = level.player
# from undo_record import UndoRecord
# level.undo_record.append(UndoRecord.Record.record_all(level.references))
# level.init_state.undo()
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.LEFT, level.undo_record)
# player.pushed(directions.LEFT, level.undo_record)
# player.pushed(directions.LEFT, level.undo_record)




# start_time = hpprime.eval("time")
# for _ in range(100):
#     level.render(1)
# end_time = hpprime.eval("time")
# print(end_time - start_time)
