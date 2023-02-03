import hpprime
import utils
from virtual_graphic import VirtualGraphic


class GraphicSplitter:
    """
    split a actual graph into multiple virtual graphs
    """

    def __init__(self, canvas: int, block_width: int, block_height: int, amount: int,
                 default_color: int = 0xffffffff, check_overflow: bool = True):
        # gatekeeper
        utils.GateKeeper.check_bounds(block_width, 1, None, "block_width")
        utils.GateKeeper.check_bounds(block_height, 1, None, "block_height")
        utils.GateKeeper.check_bounds(canvas, 1, 9, "canvas")
        utils.GateKeeper.check_bounds(amount, 1, None, "amount")

        self.block_width = block_width
        self.block_height = block_height
        self.canvas_width = block_width * amount
        self.canvas_height = block_height
        self.canvas = canvas
        self.amount = amount
        self.default_color = default_color
        self.check_overflow = check_overflow

        # initialize the canvas
        # note: the canvas itself does not support alpha channel, and can only be completely transparent or opaque per pixel.

        # hpprime.dimgrob() doesn't support alpha channel, so we have to use hpprime.eval(dimgrob_p()) instead.
        hpprime.eval("dimgrob_p(G{}, {}, {}, {})".format(
            canvas, self.canvas_width, self.canvas_height, default_color))
        # hpprime.dimgrob(self.canvas, self.canvas_width, self.canvas_height, default_color)

    def get_virtual_graphic(self, index: int) -> VirtualGraphic:
        utils.GateKeeper.check_bounds(index, 0, self.amount - 1, "index")
        return VirtualGraphic(self.canvas, index * self.block_width, 0, self.block_width, self.block_height)

    @classmethod
    def copy_from(cls, other: "GraphicSplitter", canvas: int):
        obj = cls(canvas, other.block_width, other.block_height, other.amount,
                  other.default_color, other.check_overflow)
        hpprime.blit(canvas, 0, 0, other.canvas)
        return obj
