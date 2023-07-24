UP = 1
LEFT = 2
DOWN = 3
RIGHT = 4

def id_to_name(direction: int) -> str:
    if direction == UP:
        return "UP"
    elif direction == LEFT:
        return "LEFT"
    elif direction == DOWN:
        return "DOWN"
    elif direction == RIGHT:
        return "RIGHT"
    raise ValueError("invalid direction: {}".format(direction))
    

def turn_left(direction: int) -> int:
    if direction == UP:
        return LEFT
    elif direction == LEFT:
        return DOWN
    elif direction == DOWN:
        return RIGHT
    elif direction == RIGHT:
        return UP
    raise ValueError("invalid direction: {}".format(direction))


def turn_right(direction: int) -> int:
    if direction == UP:
        return RIGHT
    elif direction == RIGHT:
        return DOWN
    elif direction == DOWN:
        return LEFT
    elif direction == LEFT:
        return UP
    raise ValueError("invalid direction: {}".format(direction))

def reverse(direction: int) -> int:
    if direction == UP:
        return DOWN
    elif direction == DOWN:
        return UP
    elif direction == LEFT:
        return RIGHT
    elif direction == RIGHT:
        return LEFT
    raise ValueError("invalid direction: {}".format(direction))

def next_pos(pos: tuple[int, int], direction: int) -> tuple[int, int]:
    if direction == UP:
        return pos[0], pos[1] + 1
    elif direction == LEFT:
        return pos[0] - 1, pos[1]
    elif direction == DOWN:
        return pos[0], pos[1] - 1
    elif direction == RIGHT:
        return pos[0] + 1, pos[1]
    raise ValueError("invalid direction: {}".format(direction))

def enter_pos(enter_direction: int, width: int, height: int, is_flipped: bool, offset = 0.5) -> tuple[int, int]:
    offset += 1e-6
    if enter_direction == UP:
        unflipped_pos = (int(width * offset), 0)  # I think UP and DOWN are flipped
    elif enter_direction == LEFT:
        unflipped_pos = (width - 1, int(height * offset))
    elif enter_direction == DOWN:
        unflipped_pos = (int(width * offset), height - 1)
    elif enter_direction == RIGHT:
        unflipped_pos = (0, int(height * offset))
    else:
        raise ValueError("invalid direction: {}".format(enter_direction))

    if is_flipped:
        return (width - 1 - unflipped_pos[0], unflipped_pos[1])
    else:
        return unflipped_pos

def is_vertical(direction: int) -> bool:
    return direction == UP or direction == DOWN

def is_horizontal(direction: int) -> bool:
    return direction == LEFT or direction == RIGHT