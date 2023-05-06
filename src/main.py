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
"""

# level = Level(level)
# player = level.player
# from undo_record import UndoRecord
# level.undo_record.append(UndoRecord.Record.record_all(level.references))
# level.init_state.undo()
# player.pushed(directions.LEFT, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.RIGHT, level.undo_record)
# player.pushed(directions.DOWN, level.undo_record)
# player.pushed(directions.LEFT, level.undo_record)
# player.pushed(directions.DOWN, level.undo_record)
# player.pushed(directions.RIGHT, level.undo_record)
# player.pushed(directions.RIGHT, level.undo_record)
# player.pushed(directions.RIGHT, level.undo_record)
# player.pushed(directions.DOWN, level.undo_record)
# player.pushed(directions.RIGHT, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.RIGHT, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.LEFT, level.undo_record)
# player.pushed(directions.LEFT, level.undo_record)
# player.pushed(directions.RIGHT, level.undo_record)
# player.pushed(directions.DOWN, level.undo_record)
# player.pushed(directions.RIGHT, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.RIGHT, level.undo_record)
# player.pushed(directions.UP, level.undo_record)
# player.pushed(directions.LEFT, level.undo_record)



# start_time = hpprime.eval("time")
# for _ in range(100):
#     level.render(1)
# end_time = hpprime.eval("time")
# print(end_time - start_time)
