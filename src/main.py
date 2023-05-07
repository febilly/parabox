from level import Level
import hpprime
import directions
from tileset import Tileset
from palettes import Palettes
from hub import select_level, load_levels_from_chapter, hub

Tileset().init(2, 9, 64, 64)
Palettes().init()

hub()

# level = Level(level)
# level.play()

# while True:
#     level = select_level()
#     level.play()

# levels = load_levels_from_chapter()
# for level in levels:
#     level.play()

level = """
version 4
#
Block -1 -1 0 9 9 0.6 0.8 1 1 0 0 0 0 0 0 0
	Ref 3 7 0 1 0 0 0 0 -1 0 0 0 1 0 0
	Wall 0 0 0 0 0
	Wall 0 1 0 0 0
	Wall 0 2 0 0 0
	Wall 0 3 0 0 0
	Wall 0 4 0 0 0
	Wall 0 5 0 0 0
	Wall 0 6 0 0 0
	Wall 0 7 0 0 0
	Wall 0 8 0 0 0
	Wall 1 7 0 0 0
	Wall 1 8 0 0 0
	Wall 2 7 0 0 0
	Wall 2 8 0 0 0
	Wall 3 8 0 0 0
	Wall 4 7 0 0 0
	Wall 4 8 0 0 0
	Wall 5 7 0 0 0
	Wall 5 8 0 0 0
	Wall 6 5 0 0 0
	Wall 6 8 0 0 0
	Wall 7 5 0 0 0
	Wall 7 6 0 0 0
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
	Floor 6 6 Button
	Floor 6 7 Button
	Floor 7 7 Button
	Block 2 2 3 5 5 0.1 0.8 1 1 0 0 0 0 0 0 0
		Wall 0 0 0 0 0
		Wall 0 1 0 0 0
		Wall 0 2 0 0 0
		Wall 0 3 0 0 0
		Wall 0 4 0 0 0
		Wall 1 0 0 0 0
		Wall 1 4 0 0 0
		Wall 2 0 0 0 0
		Wall 3 0 0 0 0
		Wall 3 4 0 0 0
		Wall 4 0 0 0 0
		Wall 4 1 0 0 0
		Wall 4 3 0 0 0
		Wall 4 4 0 0 0
	Block 2 4 2 3 3 0.4 0.8 1 1 0 0 0 0 0 0 0
		Wall 0 0 0 0 0
		Wall 0 1 0 0 0
		Wall 0 2 0 0 0
		Wall 1 0 0 0 0
		Wall 1 2 0 0 0
		Wall 2 0 0 0 0
		Wall 2 2 0 0 0
		Floor 1 1 PlayerButton
	Block 4 2 1 5 5 0.9 1 0.7 1 1 1 1 0 0 0 0
	Block 4 4 4 5 5 0.1 0.8 1 1 0 0 0 0 0 0 0
		Wall 0 0 0 0 0
		Wall 0 1 0 0 0
		Wall 0 2 0 0 0
		Wall 0 3 0 0 0
		Wall 0 4 0 0 0
		Wall 1 0 0 0 0
		Wall 1 4 0 0 0
		Wall 2 4 0 0 0
		Wall 3 0 0 0 0
		Wall 3 4 0 0 0
		Wall 4 0 0 0 0
		Wall 4 1 0 0 0
		Wall 4 3 0 0 0
		Wall 4 4 0 0 0
"""

# level = Level(level)
# player = level.player
# from undo_record import UndoRecord
# level.undo_record.append(UndoRecord.Record.record_all(level.references))
# level.init_state.undo()
# player.pushed(directions.DOWN, level.undo_record)
# player.pushed(directions.LEFT, level.undo_record)
# player.pushed(directions.LEFT, level.undo_record)
# player.pushed(directions.LEFT, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.RIGHT, level.undo_record)
# player.pushed(directions.LEFT, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.RIGHT, level.undo_record)
# player.pushed(directions.DOWN, level.undo_record)
# player.pushed(directions.DOWN, level.undo_record)
# player.pushed(directions.DOWN, level.undo_record)
# player.pushed(directions.RIGHT, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.LEFT, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.RIGHT, level.undo_record)
# player.pushed(directions.DOWN, level.undo_record)
# player.pushed(directions.RIGHT, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.LEFT, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.RIGHT, level.undo_record)
# player.pushed(directions.DOWN, level.undo_record)
# player.pushed(directions.DOWN, level.undo_record)
# player.pushed(directions.DOWN, level.undo_record)
# player.pushed(directions.DOWN, level.undo_record)
# player.pushed(directions.LEFT, level.undo_record)
# player.pushed(directions.LEFT, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.RIGHT, level.undo_record)
# player.pushed(directions.DOWN, level.undo_record)
# player.pushed(directions.RIGHT, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.DOWN, level.undo_record)
# player.pushed(directions.LEFT, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.LEFT, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.RIGHT, level.undo_record)
# player.pushed(directions.RIGHT, level.undo_record)
# player.pushed(directions.RIGHT, level.undo_record)
# player.pushed(directions.LEFT, level.undo_record)
# player.pushed(directions.DOWN, level.undo_record)
# player.pushed(directions.LEFT, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.DOWN, level.undo_record)
# player.pushed(directions.DOWN, level.undo_record)
# player.pushed(directions.RIGHT, level.undo_record)
# player.pushed(directions.RIGHT, level.undo_record)
# player.pushed(directions.RIGHT, level.undo_record)
# player.pushed(directions.LEFT, level.undo_record)
# player.pushed(directions.DOWN, level.undo_record)
# player.pushed(directions.DOWN, level.undo_record)
# player.pushed(directions.RIGHT, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.LEFT, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.RIGHT, level.undo_record)
# player.pushed(directions.RIGHT, level.undo_record)
# player.pushed(directions.LEFT, level.undo_record)
# player.pushed(directions.DOWN, level.undo_record)
# player.pushed(directions.LEFT, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.UP, level.undo_record)




# start_time = hpprime.eval("time")
# for _ in range(100):
#     level.render(1)
# end_time = hpprime.eval("time")
# print(end_time - start_time)
