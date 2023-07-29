import gzip
import os

import directions
from level import Level
from palettes import Palettes
from tileset import Tileset

RENDER = False

Tileset().init(2, 9, 64, 64)
Palettes().init()

def test_level(level: Level, solution: str):
    for action_name in solution:
        if action_name == "U":
            direction = directions.UP
        elif action_name == "L":
            if not level.players[0].is_flipped:
                direction = directions.LEFT
            else:
                direction = directions.RIGHT
        elif action_name == "D":
            direction = directions.DOWN
        elif action_name == "R":
            if not level.players[0].is_flipped:
                direction = directions.RIGHT
            else:
                direction = directions.LEFT

        level.push_players(direction, level.undo_record, RENDER, 0)
    return level.is_completed()

# 获取当前目录下所有以.gz结尾的文件
gzs = []
for file in os.listdir():
    if file.endswith(".gz"):
        gzs.append(file)

gzs = sorted(gzs)

# 解压文件
for gz in gzs:
    print(f"Testing {gz}...")

    solution_filename = f"{gz[:-7]}_solution.txt"
    with open(solution_filename, "rt") as f:
        file_data = f.read()
        lines = file_data.split("\n")
        solutions = []
        for i in range(1, len(lines), 3):
            solutions.append(lines[i].replace(" ", ""))

    with gzip.open(gz, "rt") as f:
        chapter_data = f.read()
        levels_data = chapter_data.split("$")
        levels: list[Level] = []
        for data in levels_data:
            args = data.split("|")
            levels.append(Level(args[3], int(args[1])))

    for i in range(len(levels)):
        level = levels[i]
        solution = solutions[i]
        if test_level(level, solution):
            # print(f"Success: {gz} level {i + 1}")
            pass
        else:
            print(f"Failed: {gz} level {i + 1}")
