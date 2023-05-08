from singleton import singleton

ROOT = 0
ORANGE = 1
BLUE = 2
PLAYER = 3
TEAL = 4
GREEN = 5

SPECIAL_COLORS: dict[tuple, int] = {
    (0, 0, 0.8): ROOT,
    (0.6, 0.8, 1): BLUE,
    (0.4, 0.8, 1): GREEN,
    (0.1, 0.8, 1): ORANGE,
    (0.9, 1, 0.7): PLAYER,
    (0.55, 0.8, 1): TEAL
}

SPECIAL_COLOR_NAMES: dict[int, str] = {
    ROOT: "root",
    ORANGE: "orange",
    BLUE: "blue",
    PLAYER: "player",
    TEAL: "teal",
    GREEN: "green"
}

SPECIAL_COLOR_INTS: dict[str, int] = {
    "root": ROOT,
    "orange": ORANGE,
    "blue": BLUE,
    "player": PLAYER,
    "teal": TEAL,
    "green": GREEN
}

@singleton
class Palettes:
    """
    read the palettes.txt in the app folder
    we should call init() once on the start of the app
    """
    def __init__(self):
        self.inited = False
        pass

    def init(self):
        self.palettes: dict[int, dict[int, tuple]] = {}
        
        file = open("palettes.txt", "r")
        content = file.read()
        file.close()
        palettes_text = content.split("\n\n")
        for text in palettes_text:
            palette: dict[int, tuple] = {}
            palette_index = -1
            lines = text.split("\n")
            for line in lines:
                if line == "":
                    continue
                args = line.split(" ")
                if args[0] == "palette":
                    palette_index = int(args[1])
                else:
                    if not args[0] in SPECIAL_COLOR_INTS:
                        raise Exception("Unknown color name: {}".format(args[0]))
                    color_index = SPECIAL_COLOR_INTS[args[0]]
                    color = (float(args[1]), float(args[2]), float(args[3]))
                    palette[color_index] = color
            if palette_index != -1:
                self.palettes[palette_index] = palette
            
        self.inited = True

    def transfer_color(self, color: tuple, palette_index: int):
        if not self.inited:
            raise Exception("Palette not inited")
        if palette_index < 0:
            return color
        if color in SPECIAL_COLORS:
            color_index = SPECIAL_COLORS[color]
            return self.palettes[palette_index][color_index]
        return color
            
