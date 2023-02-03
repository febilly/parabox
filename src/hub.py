from decompress import decompress
from level import Level
import hpprime

def long_select(prompt: str, options: list[str]) -> int:
    if len(options) <= 14:
        hpprime.eval("A:=0")
        choice = 0
        while choice == 0:
            hpprime.eval("CHOOSE(A, \"{}\", \"{}\")".format(prompt, "\", \"".join(options)))
            choice = int(hpprime.eval("A"))
        return choice - 1
    else:
        # prepare the pages
        page_count = (len(options) + 9) // 12
        pages: list[list[str]] = []
        # first page
        pages.append(options[:13])
        index = 13
        pages[0].append("Next Page")
        # middle pages
        for _ in range(page_count - 2):
            pages.append(options[index:index + 12])
            pages[-1].insert(0, "Previous Page")
            pages[-1].append("Next Page")
            index += 12
        # last page
        pages.append(options[index:])
        pages[-1].insert(0, "Previous Page")

        # select
        current_page = 0
        hpprime.eval("A:=0")
        choice = 0
        while choice == 0:
            hpprime.eval("CHOOSE(A, \"{} Page {}\", \"{}\")"
                         .format(prompt, current_page + 1, "\", \"".join(pages[current_page])))
            choice = int(hpprime.eval("A"))
            
            if current_page < page_count - 1 and choice == 14:
                current_page += 1
                hpprime.eval("A:=0")
                choice = 0
            elif current_page > 0 and choice == 1:
                current_page -= 1
                hpprime.eval("A:=0")
                choice = 0
                
        return choice - 1 + current_page * 12
    
    
def select_level() -> Level:
    all_files = hpprime.eval("AFiles()")
    all_files.sort()
    gz_files = list()
    chapters: list[str] = []
    for file in all_files:
        if file.startswith("chapter_"):
            gz_files.append(file)
            chapters.append(file[11:-7])
    
    hpprime.eval("A:=0")
    choice = long_select("Select a chapter", chapters)    
    gz_file = gz_files[choice]
    chapter_data = decompress(gz_file)
    levels = chapter_data.split("$")
    args: list[list] = []
    names: list[str] = []
    for level in levels:
        args.append(level.split("|"))
        difficulty = ""
        if args[-1][2] == "0":
            difficulty = "Easy"
        elif args[-1][2] == "1":
            difficulty = "Hard"
        elif args[-1][2] == "2":
            difficulty = "Special"
        names.append("{} {}".format(difficulty, args[-1][0]))

    hpprime.eval("A:=0")
    choice = long_select("Select a level", names)  
    return Level(args[choice][3], int(args[choice][1]))


def load_levels_from_chapter() -> list[Level]:
    all_files = hpprime.eval("AFiles()")
    all_files.sort()
    gz_files = list()
    chapters: list[str] = []
    for file in all_files:
        if file.startswith("chapter_"):
            gz_files.append(file)
            chapters.append(file[11:-7])
    
    hpprime.eval("A:=0")
    choice = long_select("Select a chapter", chapters)    
    gz_file = gz_files[choice]
    chapter_data = decompress(gz_file)
    levels_data = chapter_data.split("$")

    levels: list[Level] = []
    for data in levels_data:
        args = data.split("|")
        levels.append(Level(args[3], int(args[1])))
    
    return levels

def hub():
    options = ["Play a Chapter", "Select a Level"]
    choice = long_select("Select an option", options)
    if choice == 0:
        levels = load_levels_from_chapter()
        for level in levels:
            level.play()
    elif choice == 1:
        while True:
            level = select_level()
            level.play()