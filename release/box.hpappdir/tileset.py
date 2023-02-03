from singleton import singleton
import hpprime

@singleton
class Tileset:
    """
    read the tiles in the app folder and store them in a canvas
    we should call init() once on the start of the app
    """
    def __init__(self):
        self.inited = False
        pass

    def init(self, base_canvas     , temp_canvas     , height     , width     ):
        self.base_canvas = base_canvas
        self.temp_canvas = temp_canvas
        self.height = height
        self.width = width

        self.tileset = {}
        all_files = hpprime.eval("AFiles()")
        tile_files = list()
        for file in all_files:
            if not file.startswith("_") and file.endswith(".png") and file != "icon.png":
                tile_files.append(file)
        self.count = len(tile_files)
        # hpprime.dimgrob(base_canvas, self.width * self.count, self.height, 0xffffffff)
        hpprime.eval("DIMGROB_P(G{}, {}, {}, #FFFFFFFFh)".format(base_canvas, self.width * self.count, self.height))
        for index in range(self.count):
            hpprime.eval("G{}:=AFiles(\"{}\")".format(self.temp_canvas, tile_files[index]))
            hpprime.strblit2(base_canvas, index * self.width, 0, self.width, self.height, self.temp_canvas, 0, 0, self.width, self.height)
            self.tileset[tile_files[index][:-4]] = index

        self.inited = True

    def draw_tile_xy(self, name     , canvas     , x     , y     ):
        if not self.inited:
            raise Exception("Tileset not inited")
        if name not in self.tileset:
            raise Exception("{} not found in tileset".format(name))
        index = self.tileset[name]
        hpprime.blit(canvas, x, y, self.base_canvas)

    def draw_tile_size(self, name     , canvas     , x     , y     , height     , width     ):
        if not self.inited:
            raise Exception("Tileset not inited")
        if name not in self.tileset:
            raise Exception("{} not found in tileset".format(name))
        index = self.tileset[name]
        hpprime.strblit2(canvas, x, y, width, height, self.base_canvas, index * self.width, 0, self.width, self.height)

    def draw_tile_pos(self, name     , canvas     , x1, y1, x2, y2):
        self.draw_tile_size(name, canvas, x1, y1, x2 - x1 + 1, y2 - y1 + 1)

    def draw_tile_area(self, name     , canvas     , area                                         ):
        self.draw_tile_size(name, canvas, area[0][0], area[0][1], area[1][0] - area[0][0] + 1, area[1][1] - area[0][1] + 1)
