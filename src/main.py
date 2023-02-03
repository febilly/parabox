from level import Level
import hpprime
import directions
from tileset import Tileset
from palettes import Palettes
from hub import select_level, load_levels_from_chapter, hub

level = """version 4
#
Block -1 -1 0 9 9 0 0 0.8 1 0 0 0 0 0 0 0
	Ref 2 3 1 0 0 0 0 0 -1 0 0 0 0 0 0
	Wall 0 0 0 0 0
	Wall 0 1 0 0 0
	Wall 0 2 0 0 0
	Wall 0 3 0 0 0
	Wall 0 4 0 0 0
	Wall 0 5 0 0 0
	Wall 0 6 0 0 0
	Wall 0 7 0 0 0
	Wall 0 8 0 0 0
	Wall 1 0 0 0 0
	Wall 1 1 0 0 0
	Wall 1 6 0 0 0
	Wall 1 7 0 0 0
	Wall 1 8 0 0 0
	Wall 2 0 0 0 0
	Wall 2 1 0 0 0
	Wall 2 7 0 0 0
	Wall 2 8 0 0 0
	Wall 3 0 0 0 0
	Wall 3 1 0 0 0
	Wall 3 8 0 0 0
	Wall 4 0 0 0 0
	Wall 4 1 0 0 0
	Wall 4 7 0 0 0
	Wall 4 8 0 0 0
	Wall 5 0 0 0 0
	Wall 5 1 0 0 0
	Wall 5 3 0 0 0
	Wall 5 4 0 0 0
	Wall 5 5 0 0 0
	Wall 5 6 0 0 0
	Wall 5 7 0 0 0
	Wall 5 8 0 0 0
	Wall 6 0 0 0 0
	Wall 6 1 0 0 0
	Wall 6 3 0 0 0
	Wall 6 4 0 0 0
	Wall 6 6 0 0 0
	Wall 6 7 0 0 0
	Wall 6 8 0 0 0
	Wall 7 0 0 0 0
	Wall 7 6 0 0 0
	Wall 7 7 0 0 0
	Wall 7 8 0 0 0
	Wall 8 0 0 0 0
	Wall 8 1 0 0 0
	Wall 8 2 0 0 0
	Wall 8 3 0 0 0
	Wall 8 4 0 0 0
	Wall 8 5 0 0 0
	Wall 8 6 0 0 0
	Wall 8 7 0 0 0
	Wall 8 8 0 0 0
	Floor 6 5 PlayerButton
	Floor 7 5 Button
	Block 2 5 1 3 3 0.6 0.8 1 1 0 0 0 0 0 0 0
		Wall 0 0 0 0 0
		Wall 0 2 0 0 0
		Wall 1 1 0 0 0
		Wall 2 0 0 0 0
		Wall 2 2 0 0 0
	Block 3 4 2 5 5 0.9 1 0.7 1 1 1 1 0 0 0 0
"""

Tileset().init(2, 9, 64, 64)
Palettes().init()

# level = Level(level)
# level.play()

hub()

# while True:
#     level = select_level()
#     level.play()

# levels = load_levels_from_chapter()
# for level in levels:
#     level.play()

# level = Level(level)
# player = level.player
# from undo_record import UndoRecord
# level.undo_record.append(UndoRecord.Record.record_all(level.references))
# level.init_state.undo()
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.LEFT, level.undo_record)
# player.pushed(directions.DOWN, level.undo_record)
# player.pushed(directions.DOWN, level.undo_record)
# player.pushed(directions.DOWN, level.undo_record)
# player.pushed(directions.DOWN, level.undo_record)



# start_time = hpprime.eval("time")
# for _ in range(100):
#     level.render(1)
# end_time = hpprime.eval("time")
# print(end_time - start_time)
