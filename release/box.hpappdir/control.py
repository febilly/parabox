import actions
import hpprime

KEY_MAPPING = {2: actions.UP, 7: actions.LEFT, 12: actions.DOWN, 8: actions.RIGHT,
               18: actions.UP, 23: actions.LEFT, 24: actions.DOWN, 25: actions.RIGHT,
               19: actions.UNDO, 49: actions.UNDO, 4: actions.RESTART, 30: actions.ENTER}

def get_input()       :
    while True:
        key = hpprime.eval("GETKEY")
        if key in KEY_MAPPING:
            return KEY_MAPPING[key]