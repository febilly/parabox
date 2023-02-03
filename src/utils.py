import hpprime

class GateKeeper:
    @staticmethod
    def defined_xor(obj_a, obj_b):
        return (obj_a is None) != (obj_b is None)

    @staticmethod
    def check_pair(obj_a, obj_b, name_a = "arg_a", name_b = "arg_b"):
        if GateKeeper.defined_xor(obj_a, obj_b):
            raise ValueError("{} and {} must be both specified or both unspecified".format(name_a, name_b))
    
    @staticmethod
    def check_require(obj_a, obj_b, name_a = "arg_a", name_b = "arg_b"):
        if obj_a is not None and obj_b is None:
            raise ValueError("{} must be specified if {} is specified".format(name_b, name_a))

    @staticmethod
    def check_defined(obj, name = "arg"):
        if obj is None:
            raise ValueError("{} must be specified".format(name))

    @staticmethod
    def check_bounds(obj, lower = None, upper = None, name = "arg", message = None):
        if lower is not None and obj < lower:
            raise ValueError("{} must be greater than or equals to {}".format(name, lower) if message is None else message)
        if upper is not None and obj > upper:
            raise ValueError("{} must be less than or equals to {}".format(name, upper) if message is None else message)
    

class Color:
    @staticmethod
    def hsv_to_rgb(h, s, v):
        """
        Convert an HSV color to RGB.  [0, 1]^3 -> [0, 1]^3
                source: https://github.com/python/cpython/blob/3.11/Lib/colorsys.py#L145
        """
        if s == 0.0:
            return v, v, v
        i = int(h * 6.0) # XXX assume int() truncates!
        f = (h * 6.0) - i
        p = v*(1.0 - s)
        q = v*(1.0 - s*f)
        t = v*(1.0 - s*(1.0-f))
        i = i%6
        if i == 0:
            return v, t, p
        if i == 1:
            return q, v, p
        if i == 2:
            return p, v, t
        if i == 3:
            return p, q, v
        if i == 4:
            return t, p, v
        if i == 5:
            return v, p, q
        # Cannot get here
        return 0, 0, 0

    @staticmethod
    def hsv_to_rgb_int(h, s, v):
        """
        Convert an HSV color to a regular integer.  [0, 1]^3 -> int
        """
        r, g, b = Color.hsv_to_rgb(h, s, v)
        return int(r * 255) << 16 | int(g * 255) << 8 | int(b * 255)

class Graphics:
    @staticmethod
    def draw_box_pos(graphic, x1, y1, x2, y2, color, black_border = True):
        width = x2 - x1 + 1
        height = y2 - y1 + 1
        if black_border:
            hpprime.fillrect(graphic, x1, y1, width, height, 0x000000, color)
        else:
            hpprime.fillrect(graphic, x1, y1, width, height, color, color)

    @staticmethod
    def draw_box_area(graphic, area, color, black_border = True):
        Graphics.draw_box_pos(graphic, area[0][0], area[0][1], area[1][0], area[1][1], color, black_border)