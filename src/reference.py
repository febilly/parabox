import room
import directions
import object_types
import undo_record


class Reference:
    """
    a reference to a room
    player is a reference, too
    """

    def __init__(self, id, exit_block=True, is_player=False, is_flipped=False):
        self.id = id
        self.exit_block = exit_block
        self.is_player = is_player
        self.parent_room: room.Room = None
        self.room: room.Room = None
        self.pos: tuple[int, int] = (-1, -1)
        self.queried_poses: list[tuple[tuple[int, int], int]] = []  # (pos, direction)
        self.pressed_direction = None
        self.is_flipped_original = is_flipped  # whether this reference should have the "flipped" animation
        self.is_flipped_current = is_flipped  # whether this reference is flipped relative to its parent room
        pass

    def _get_next_pos(self, direction: int, tested: list["Reference"], can_exit, offset=0.5, is_flipped=False):
        """
        get the next object's pos in the given direction
        return an object_types.xxx or a tuple(room, pos, offset, is_flipped)
        the offset is where in the next ref should this ref enter
        is_flipped == next_obj.is_flipped_current xor self.is_flipped_current
        """
        if (self.pos, direction) in self.queried_poses:
            return object_types.INFINITY
        next_pos = directions.next_pos(self.pos, direction)
        if self.parent_room is None:
            return object_types.INFINITY
        elif self.parent_room.is_in_bound(next_pos):
            return (self.parent_room, next_pos, offset, is_flipped)
        elif not can_exit:
            return object_types.WALL  # TODO: check this
        else:
            # return the next pos of self.parent_room.reference
            if self.parent_room.reference is None:
                return object_types.WALL
            self.queried_poses.append((self.pos, direction))
            tested.append(self)
            # calculate the new offset after exiting the block
            if direction == directions.UP or direction == directions.DOWN:
                new_offset = (self.pos[0] + offset) / self.parent_room.width
            else:
                new_offset = (self.pos[1] + offset) / self.parent_room.height

            new_direction = direction
            if self.parent_room.reference.is_flipped_current:
                if directions.is_vertical(direction):
                    new_offset = 1 - new_offset
                else:
                    new_direction = directions.reverse(direction)

            return self.parent_room.reference._get_next_pos(new_direction, tested, can_exit, new_offset, is_flipped ^ self.is_flipped_current)

    def get_next_pos(self, direction: int, can_exit=True):
        """
        get the next object's pos in the given direction
        """
        tested: list["Reference"] = []
        result = self._get_next_pos(direction, tested, can_exit)
        for reference in tested:
            reference.queried_poses = []
        return result

    def get_next(self, direction: int, can_exit=True):
        pos = self.get_next_pos(direction, can_exit)
        if isinstance(pos, int):
            return pos
        else:
            return pos[0].get(pos[1])

    class MoveRecord:
        def __init__(self, reference: "Reference", new_parent_room, new_pos: tuple[int, int], is_flipped: bool):
            self.reference = reference
            self.new_parent_room = new_parent_room
            self.new_pos = new_pos
            self.is_flipped = is_flipped

    class MoveTracker:
        PUSH = 1
        ENTER = 2
        EAT = 3

        def __init__(self):
            self.actions: list[int] = []
            self.records: list[Reference.MoveRecord] = []

        def move_push(self, record: "Reference.MoveRecord"):
            self.records.append(record)
            self.actions.append(self.PUSH)

        def move_enter(self, record: "Reference.MoveRecord"):
            self.records.append(record)
            self.actions.append(self.ENTER)

        def move_eat(self, record: "Reference.MoveRecord"):
            self.records.append(record)
            self.actions.append(self.EAT)

        def pop_last(self):
            self.actions.pop()
            return self.records.pop()

    def conduct_record(self, records: list["Reference.MoveRecord"], undo: undo_record.UndoRecord):
        # find
        if records.count(records[-1]) < 2:
            head_index = 0
        else:
            head_index = records.index(records[-1])

        # record the original state
        undo.append(undo_record.UndoRecord.Record.from_move_records(records[head_index:]))

        # conduct
        for record in records[head_index:]:
            reference = record.reference
            # remove reference from old place
            old_pos = reference.pos
            old_map = reference.parent_room.reference_map
            if old_map[old_pos[0]][old_pos[1]] is reference:
                old_map[old_pos[0]][old_pos[1]] = None

            # add reference to new place
            reference.parent_room = record.new_parent_room
            new_pos = record.new_pos
            record.reference.pos = new_pos
            new_map = reference.parent_room.reference_map
            new_map[new_pos[0]][new_pos[1]] = reference
            reference.is_flipped_current ^= record.is_flipped

    def _pushed(self, direction: int, tracker: MoveTracker):
        """
        check if "self" object is pushable in the given direction
        """
        if self.pressed_direction is not None and self.pressed_direction != direction:
            return False
        next_pos = self.get_next_pos(direction)
        next_obj = self.get_next(direction)
        if next_obj == object_types.WALL:
            return False
        elif next_obj == object_types.GROUND:
            if not isinstance(next_pos, tuple):  # shut up vscode, I will check it, ok?
                raise TypeError("next_pos is a {}, not a tuple".format(type(next_pos)))
            tracker.move_push(self.MoveRecord(self, next_pos[0], next_pos[1], next_pos[3]))
            return True
        elif next_obj == object_types.INFINITY:
            return False
        elif self.pressed_direction is not None:  # and self.pressed_direction == direction
            if not isinstance(next_pos, tuple):
                raise TypeError("next_pos is a {}, not a tuple".format(type(next_pos)))
            tracker.move_push(self.MoveRecord(self, next_pos[0], next_pos[1], next_pos[3]))
            return True

        else:
            # recurse start here

            # check if the next object is pushable or enterable
            if not isinstance(next_obj, Reference):
                raise TypeError("next_obj is not a Reference")
            if not isinstance(next_pos, tuple):
                raise TypeError("next_pos is a {}, not a tuple".format(type(next_pos)))

            # push
            tracker.move_push(self.MoveRecord(self, next_pos[0], next_pos[1], next_pos[3]))
            self.pressed_direction = direction
            if next_obj._pushed(direction, tracker):
                return True
            tracker.pop_last()
            self.pressed_direction = None

            # enter
            if next_obj._entered_by(self, direction, tracker, next_pos[2]):
                return True

            # eat
            tracker.move_push(self.MoveRecord(self, next_pos[0], next_pos[1], next_pos[3]))
            self.pressed_direction = direction
            if next_obj._eaten_by(self, direction, tracker):
                return True
            tracker.pop_last()
            self.pressed_direction = None

            return False

    def pushed(self, direction: int, _undo_record: undo_record.UndoRecord, dry_run=False):
        """
        check if "self" object is pushable in the given direction
        """
        tracker = self.MoveTracker()
        result = self._pushed(direction, tracker)
        if result and not dry_run:
            self.conduct_record(tracker.records, _undo_record)
        for record in tracker.records:
            record.reference.pressed_direction = None
        return result

    def _entered_by(self, enterer: "Reference", direction: int, tracker: MoveTracker, offset=0.5):
        """
        check if other objects can enter "self" object in the given direction
        (direction is where the "other object" want to go)

        enter is special, because after ONE push or eat, the pusher or eater's pos is defined,
        but this is not the case for enter: the enterer might enter MULTIPLE times at the same time
        """
        if self.pressed_direction is not None:
            return False

        enter_pos = directions.enter_pos(direction, self.room.width, self.room.height, self.is_flipped_current, offset)
        enter_obj = self.room.get(enter_pos)
        if enter_obj == object_types.GROUND:
            tracker.move_enter(self.MoveRecord(enterer, self.room, enter_pos, self.is_flipped_current))
            return True
        if enter_obj == object_types.WALL:
            return False
        if enter_obj.pressed_direction is not None:
            # refer to eat.txt
            return False

        # recurse start here
        # prepare
        if self.is_flipped_current:
            enterer.is_flipped_current ^= True
        enterer_flipped = self.is_flipped_current

        tracker.move_enter(self.MoveRecord(self, self.parent_room, self.pos, self.is_flipped_current))
        self.pressed_direction = direction

        if directions.is_vertical(direction):
            new_offset = offset * self.room.width - enter_obj.pos[0]
        else:
            new_offset = offset * self.room.height - enter_obj.pos[1]

        new_direction = direction
        if self.is_flipped_current:
            if directions.is_vertical(direction):
                new_offset = 1 - new_offset
            else:
                new_direction = directions.reverse(direction)

        # push
        tracker.move_enter(self.MoveRecord(enterer, self.room, enter_pos, self.is_flipped_current))
        enterer.pressed_direction = new_direction
        if enter_obj._pushed(new_direction, tracker):
            if enterer_flipped:
                enterer.is_flipped_current ^= True
            return True
        tracker.pop_last()
        enterer.pressed_direction = None

        # enter
        if enter_obj._entered_by(enterer, new_direction, tracker, new_offset):
            if enterer_flipped:
                enterer.is_flipped_current ^= True
            return True

        # eat
        tracker.move_enter(self.MoveRecord(enterer, self.room, enter_pos, self.is_flipped_current))
        self.pressed_direction = new_direction
        if enter_obj._eaten_by(enterer, new_direction, tracker):  # FIXME: the enterer is not flipped yet, fix this!!!
            if enterer_flipped:
                enterer.is_flipped_current ^= True
            return True
        tracker.pop_last()
        enterer.pressed_direction = None

        # failed, clean up
        tracker.pop_last()
        self.pressed_direction = None

        if enterer_flipped:
            enterer.is_flipped_current ^= True

        return False


    def entered_by(self, enterer: "Reference", direction: int, _undo_record: undo_record.UndoRecord, offset=0.5, dry_run=False):
        """
        check if other objects can enter "self" object in the given direction
        (direction is where the "other object" want to go)
        """
        tracker = self.MoveTracker()
        result = self._entered_by(enterer, direction, tracker, offset)
        if result and not dry_run:
            self.conduct_record(tracker.records, _undo_record)
        for record in tracker.records:
            record.reference.pressed_direction = None
        return result

    def _eaten_by(self, eater: "Reference", direction: int, tracker: MoveTracker):
        """
        check if "self" objects can be eaten by the "eater" object in the given direction
        (direction is where the "eater" object want to go)
        suppose the eater is going to go to the position of "self" object
        """
        # TODO: is checking the is_being_pushed necessary?

        # precheck
        reversed_direction = directions.reverse(direction)
        eater_enter_pos = directions.enter_pos(reversed_direction, eater.room.width, eater.room.height, eater.is_flipped_current)
        eater_enter_obj = eater.room.get(eater_enter_pos)
        if eater_enter_obj == object_types.GROUND:
            tracker.move_eat(self.MoveRecord(self, eater.room, eater_enter_pos, eater.is_flipped_current))
            return True
        if eater_enter_obj == object_types.WALL:
            return False

        """
        now "self" block is in the next pos of "eater" block
        we need to check if the enter object is pushable or enterable in the reversed direction
        refer to eat.txt and eat_2.txt
        """
        # recurse start here
        # prepare
        if eater.is_flipped_current and directions.is_horizontal(reversed_direction):
            new_reversed_direction = directions.reverse(reversed_direction)
        else:
            new_reversed_direction = reversed_direction
        if eater.is_flipped_current:
            self.is_flipped_current ^= True
        self_flipped = eater.is_flipped_current

        tracker.move_eat(self.MoveRecord(self, eater.room, eater_enter_pos, eater.is_flipped_current))
        self.pressed_direction = direction
        if eater_enter_obj._pushed(new_reversed_direction, tracker):
            if self_flipped:
                self.is_flipped_current ^= True
            return True
        elif eater_enter_obj._entered_by(self, new_reversed_direction, tracker):
            if self_flipped:
                self.is_flipped_current ^= True
            return True
        tracker.pop_last()
        self.pressed_direction = None
        # "self" block can not eat eater_enter_obj
        # so no need to check it
        # otherwise, it will be "self" block entering the eater block, instead of being eaten
        if self_flipped:
            self.is_flipped_current ^= True

        return False

    def eaten_by(self, eater: "Reference", direction: int, _undo_record: undo_record.UndoRecord, dry_run=False):
        """
        check if "self" objects can be eaten by the "eater" object in the given direction
        (direction is where the "eater" object want to go)
        suppose the eater is going to go to the position of "self" object
        """
        tracker = self.MoveTracker()
        result = self._entered_by(eater, direction, tracker)
        if result and not dry_run:
            self.conduct_record(tracker.records, _undo_record)
        for record in tracker.records:
            record.reference.pressed_direction = None
        return result
