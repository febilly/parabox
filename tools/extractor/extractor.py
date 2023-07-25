import gzip
import os
import shutil

puzzle_data = open("input/puzzle_data.txt", "r")
text = puzzle_data.read()
puzzle_data.close()
levels = text.split("\n")

level_dict: dict[str, dict[int, tuple[str, bool, str]]] = {}

chaper_names = {"a": "01_Intro",
              "b": "02_Enter",
              "c": "03_Empty",
              "d": "04_Eat",
              "e": "05_Reference",
              "L": "06_Swap",
              "f": "07_Center",
              "g": "08_Clone",
              "h": "09_Transfer",
              "i": "10_Open",
              "j": "11_Flip",
              "k": "12_Cycle",
              "m": "13_Player"}

for level in levels:
    if level == "":
        continue
    args = level.split(" ")
    name = args[0]
    palette_index = args[3]
    hard = args[4]  # 0 = normal, 1 = hard, 2 = special
    location = args[6]
    chapter = location[0]
    index = int(location[1:])
    puzzle_file = open(f"input/{name}.txt", "r")
    puzzle_text = puzzle_file.read()
    puzzle_file.close()
    if chapter not in level_dict:
        level_dict[chapter] = {}
    level_dict[chapter][index] = (name, palette_index, hard, puzzle_text)

if os.path.isfile("output"):
    raise Exception("name \"output\" is already being used by a file")
if not os.path.exists("output"):
    os.makedirs("output")
    
if os.path.isdir("output/palettes.txt"):
    raise Exception(f"name \"output/palettes.txt\" is already being used by a directory")
if os.path.isfile("output/palettes.txt"):
    os.remove("output/palettes.txt")
shutil.copy("input/palettes.txt", "output/palettes.txt")

for chapter in chaper_names:
    content = ""
    level_seperator = "$"
    arg_seperator = "|"
    indexs = list(level_dict[chapter])
    indexs.sort()
    for index in indexs:
        name, palette_index, hard, puzzle_text = level_dict[chapter][index]
        content += f"{name}{arg_seperator}{palette_index}{arg_seperator}{hard}{arg_seperator}{puzzle_text}{level_seperator}"
    content = content[:-1]

    gz_name = f"output/chapter_{chaper_names[chapter]}.txt.gz"
    if os.path.isdir(gz_name):
        raise Exception(f"name \"{gz_name}\" is already being used by a directory")
    compressed_file = gzip.open(gz_name, "wb")
    compressed_file.write(content.encode("utf-8"))
    compressed_file.close()
