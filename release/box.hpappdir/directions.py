UP = 1
LEFT = 2
DOWN = 3
RIGHT = 4

def id_to_name(direction     )       :
    if direction == UP:
        return "UP"
    elif direction == LEFT:
        return "LEFT"
    elif direction == DOWN:
        return "DOWN"
    elif direction == RIGHT:
        return "RIGHT"
    raise ValueError("invalid direction: {}".format(direction))
    

def turn_left(direction     )       :
    if direction == UP:
        return LEFT
    elif direction == LEFT:
        return DOWN
    elif direction == DOWN:
        return RIGHT
    elif direction == RIGHT:
        return UP
    raise ValueError("invalid direction: {}".format(direction))


def turn_right(direction     )       :
    if direction == UP:
        return RIGHT
    elif direction == RIGHT:
        return DOWN
    elif direction == DOWN:
        return LEFT
    elif direction == LEFT:
        return UP
    raise ValueError("invalid direction: {}".format(direction))

def reverse(direction     )       :
    if direction == UP:
        return DOWN
    elif direction == DOWN:
        return UP
    elif direction == LEFT:
        return RIGHT
    elif direction == RIGHT:
        return LEFT
    raise ValueError("invalid direction: {}".format(direction))

def next_pos(pos                 , direction     )                   :
    if direction == UP:
        return pos[0], pos[1] + 1
    elif direction == LEFT:
        return pos[0] - 1, pos[1]
    elif direction == DOWN:
        return pos[0], pos[1] - 1
    elif direction == RIGHT:
        return pos[0] + 1, pos[1]
    raise ValueError("invalid direction: {}".format(direction))

def enter_pos(enter_direction     , width     , height     , offset = 0.5):
    offset += 1e-6
    if enter_direction == UP:
        return (int(width * offset), 0)
    elif enter_direction == LEFT:
        return (width - 1, int(height * offset))
    elif enter_direction == DOWN:
        return (int(width * offset), height - 1)
    elif enter_direction == RIGHT:
        return (0, int(height * offset))
    raise ValueError("invalid direction: {}".format(enter_direction))
