import room
import directions
import object_types
import undo_record
import utils
from canvas import Canvas
from location import Location

try:
    from typing import Optional, TYPE_CHECKING
    if TYPE_CHECKING:
        from level import Level
        from room import Room
except:
    pass

class Reference:
    """
    a reference to a room
    players and possessable walls are references, too
    """

    def __init__(self, id, pos, is_room_generated, is_exit_block, is_player, is_possessable, playerorder, is_flipped,
                 is_wall, float_in_space, is_infexit, infexit_num, is_infenter, infenter_num, infenter_from_id):
        self.id = id
        self.pos: tuple[int, int] = pos
        self.is_room_generated = is_room_generated
        self.is_exit_block = is_exit_block
        self.is_player = is_player
        self.is_possessable = is_possessable
        self.playerorder = playerorder
        self.parent_room: Optional[room.Room] = None
        self.room: Optional[room.Room] = None
        self.queried_directions: list[int] = []  # (pos, direction)
        self.pressed_direction = None
        self.is_flipped = is_flipped  # whether this reference is flipped relative to its parent room
        self.is_view_flipped = False  # when rendering and focused on this ref, whether the view is flipped
        self.is_wall = is_wall
        self.level = None
        self.float_in_space = float_in_space

        self.is_infexit = is_infexit
        self.infexit_num = infexit_num  # always 1 less than the number of displayed ∞
        self.is_infenter = is_infenter
        self.infenter_num = infenter_num  # always 1 less than the number of displayed ε

        # self.infexit_to_references: dict[int, "Reference"] = {}  # degree -> reference
        self.infenter_from_id = infenter_from_id
        # self.infenter_to_rooms: dict[int, room] = {}  # degree -> room
        pass

    def __str__(self):
        return "Reference{}".format(self.id)

    def is_nonenterable(self):  # with golden outline
        return self.is_infexit or (self.parent_room is not None and self.parent_room.is_void)

    def get_infexit_reference(self, degree):
        if self.id in self.level.infexit_references and degree in self.level.infexit_references[self.id]:
            return self.level.infexit_references[self.id][degree]
        else:
            # create a new void room containing the infexit
            new_void_room_id = max(self.level.rooms) + 1
            new_void_room = room.Room(7, 7, new_void_room_id, (0, 0, 0.8), False, True, True)
            # self.level.rooms[new_void_room_id] = new_void_room  # don't add generated void room to the level.rooms
            new_infexit = Reference(self.id, (3, 3), False, False, False, False, 0, False, False, False, True, degree, False, 0, 0)
            new_infexit.level = self.level
            new_infexit.room = self.room
            new_infexit.parent_room = new_void_room
            new_void_room.reference_map[3][3] = new_infexit
            if self.id in self.level.infexit_references:
                self.level.infexit_references[self.id][degree] = new_infexit
            else:
                self.level.infexit_references[self.id] = {degree: new_infexit}
            return new_infexit

    def get_infenter_reference(self, degree):
        if self.id in self.level.infenter_references and degree in self.level.infenter_references[self.id]:
            return self.level.infenter_references[self.id][degree]
        else:
            # create a new void room containing the infenter
            new_epsilon_room_id = max(self.level.rooms) + 1
            new_epsilon_room = room.Room(5, 5, new_epsilon_room_id, (0.25, 0.83, 0.82), False, True, False)
            new_epsilon_reference = Reference(new_epsilon_room_id, (3, 3), True, False, False, False, 0, False, False, False, False, 0, True, degree, 0)
            new_epsilon_room.exit_reference = new_epsilon_reference
            new_epsilon_reference.room = new_epsilon_room
            new_epsilon_reference.level = self.level
            # self.level.rooms[new_epsilon_room_id] = new_epsilon_room  # don't add generated epsilon things to the level.references
            # self.level.references[new_epsilon_room_id].append(new_epsilon_reference)  # don't add generated epsilon things to the level.references

            new_void_room_id = max(self.level.rooms) + 1
            new_void_room = room.Room(7, 7, new_void_room_id, (0, 0, 0.8), False, True, True)
            new_void_room.reference_map[3][3] = new_epsilon_reference
            new_epsilon_reference.parent_room = new_void_room
            new_void_room.reference_map[3][3] = new_epsilon_reference
            if self.id in self.level.infenter_references:
                self.level.infenter_references[self.id][degree] = new_epsilon_reference
            else:
                self.level.infenter_references[self.id] = {degree: new_epsilon_reference}
            return new_epsilon_reference


    class MoveRecord:
        def __init__(self, reference: "Reference", new_parent_room, new_pos: tuple[int, int], is_flipped: bool, is_player=None):
            self.reference = reference
            self.new_parent_room = new_parent_room
            self.new_pos = new_pos
            self.is_flipped = is_flipped
            self.is_player = is_player

        def __eq__(self, other):
            return self.reference == other.reference  # TODO: check this

    class MoveTracker:
        PUSH = 1
        ENTER = 2
        EAT = 3
        POSSESS = 4

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

        def move_possess(self, record: "Reference.MoveRecord"):
            self.records.append(record)
            self.actions.append(self.POSSESS)

        def pop_last(self):
            self.actions.pop()
            return self.records.pop()

    def conduct_record(self, records: list["Reference.MoveRecord"], undo: undo_record.UndoRecord):
        # find the cycle
        if records.count(records[-1]) < 2:
            records_to_conduct = records
        else:
            records_to_conduct = records[records.index(records[-1]):-1]

        # record the original state
        undo.append(undo_record.UndoRecord.Record.from_move_records(records_to_conduct))

        # conduct
        for record in records_to_conduct:
            reference = record.reference
            if reference.float_in_space:
                continue

            # remove reference from old place
            old_pos = reference.pos
            old_map = reference.parent_room.reference_map
            if old_map[old_pos[0]][old_pos[1]] is reference:
                old_map[old_pos[0]][old_pos[1]] = None

            # add reference to new place
            reference.is_flipped ^= record.is_flipped
            if not reference.parent_room == record.new_parent_room:
                reference.is_view_flipped ^= record.is_flipped
            reference.parent_room = record.new_parent_room
            new_pos = record.new_pos
            reference.pos = new_pos
            new_map = reference.parent_room.reference_map
            new_map[new_pos[0]][new_pos[1]] = reference
            if record.is_player is not None:
                if record.is_player:
                    self.level.players[reference.playerorder] = reference
                reference.is_player = record.is_player

    def _pushed(self, direction: int, tracker: MoveTracker, is_first_movement=False):
        """
        check if "self" object is pushable in the given direction
        """
        if self.pressed_direction is not None and self.pressed_direction != direction:
            return False
        location = Location(self.parent_room, self.pos)
        next_location = location.get_next_location(direction)
        if next_location is None:
            return False
        next_obj_type = next_location.get_type()
        if next_obj_type == object_types.WALL:
            return False
        elif next_obj_type == object_types.GROUND:
            tracker.move_push(self.MoveRecord(self, next_location.room, next_location.pos, next_location.is_relatively_flipped))
            return True
        elif self.pressed_direction is not None:  # and self.pressed_direction == direction
            tracker.move_push(self.MoveRecord(self, next_location.room, next_location.pos, next_location.is_relatively_flipped))
            return True

        else:
            next_obj = next_location.get_reference()

            # check if the next object is pushable or enterable
            # possessable walls are only possessable, not pushable or something else
            if not next_obj.is_wall:
                # prepare
                # "next_pos[3]" == "is_flipped"
                new_direction = directions.reverse(direction) if next_location.is_relatively_flipped and directions.is_horizontal(direction) else direction
                if next_location.is_relatively_flipped:
                    self.is_flipped ^= True
                self_flipped = next_location.is_relatively_flipped

                # push
                tracker.move_push(self.MoveRecord(self, next_location.room, next_location.pos, next_location.is_relatively_flipped))
                self.pressed_direction = direction
                if next_obj._pushed(new_direction, tracker, False):
                    if self_flipped:
                        self.is_flipped ^= True
                    return True
                tracker.pop_last()
                self.pressed_direction = None

                if not next_obj.is_nonenterable():
                    # enter
                    self.pressed_direction = direction
                    if next_obj._entered_by(self, new_direction, tracker, next_location.offset, next_location.is_relatively_flipped, is_first_movement):
                        if self_flipped:
                            self.is_flipped ^= True
                        return True
                    self.pressed_direction = None

                    if not (self.is_wall or self.is_nonenterable()):
                        # eat
                        tracker.move_push(self.MoveRecord(self, next_location.room, next_location.pos, next_location.is_relatively_flipped))
                        self.pressed_direction = direction
                        if next_obj._eaten_by(self, new_direction, tracker):
                            if self_flipped:
                                self.is_flipped ^= True
                            return True
                        tracker.pop_last()
                        self.pressed_direction = None

                # clean up
                if self_flipped:
                    self.is_flipped ^= True

            # possess
            if is_first_movement:
                self.pressed_direction = direction
                if next_obj._possessed_by(self, direction, tracker, next_location.offset):
                    return True
                self.pressed_direction = None

            return False

    def pushed(self, direction: int, _undo_record: undo_record.UndoRecord, dry_run=False):
        """
        check if "self" object is pushable in the given direction
        """
        tracker = self.MoveTracker()
        result = self._pushed(direction, tracker, True)
        if result and not dry_run:
            self.conduct_record(tracker.records, _undo_record)
        for record in tracker.records:
            record.reference.pressed_direction = None
        return result

    def _entered_by(self, enterer: "Reference", direction: int, tracker: MoveTracker, outer_offset=0.5,
                    enterer_already_should_flip=False, is_first_movement=False, infenter_degree=0):
        """
        check if other objects can enter "self" object in the given direction
        (direction is where the "other object" want to go)

        enter is special, because after ONE push or eat, the pusher or eater's pos is defined,
        but this is not the case for enter: the enterer might enter MULTIPLE times at the same time
        """
        class EnterInfo:
            def __init__(self, room, outer_offset):
                self.room = room
                self.outer_offset = outer_offset

            def __eq__(self, other):
                return self.room == other.room and self.outer_offset == other.outer_offset

        if self.pressed_direction is not None and self.pressed_direction != direction:
            return False

        enter_pos = directions.enter_pos(direction, self.room.width, self.room.height, self.is_flipped, outer_offset)
        enter_obj = self.room.get(enter_pos)
        if enter_obj == object_types.GROUND:
            tracker.move_enter(self.MoveRecord(enterer, self.room, enter_pos, enterer_already_should_flip ^ self.is_flipped))
            return True
        if enter_obj == object_types.WALL:
            return False

        # enterer_direction is the direction that the enterer will go after entering
        if self.is_flipped:
            if directions.is_vertical(direction):
                enterer_direction = direction
                inner_offset = 1 - outer_offset
            else:
                enterer_direction = directions.reverse(direction)
                inner_offset = outer_offset
        else:
            enterer_direction = direction
            inner_offset = outer_offset

        # this is part of the preparation for the recursion
        # we move this part here because we need the enterer_direction to decide whether we need to do an early return
        if directions.is_vertical(direction):
            new_offset = inner_offset * self.room.width - enter_obj.pos[0]
        else:
            new_offset = inner_offset * self.room.height - enter_obj.pos[1]

        # this is the "early return" said above
        if enter_obj.pressed_direction is not None and enter_obj.pressed_direction != enterer_direction:
            # refer to eat.txt
            return False

        # recurse start here
        # possessable walls are only possessable, not pushable or something else
        if not enter_obj.is_wall:
            # prepare
            if self.is_flipped:
                enterer.is_flipped ^= True
            enterer_flipped = self.is_flipped
            tracker.move_enter(self.MoveRecord(self, self.parent_room, self.pos, False))  # we record this so that when we are wiping pressed_direction, we know we need to wipe it for "self" too
            self.pressed_direction = direction

            # push
            tracker.move_enter(self.MoveRecord(enterer, self.room, enter_pos, enterer_already_should_flip ^ self.is_flipped))
            enterer.pressed_direction = enterer_direction
            if enter_obj._pushed(enterer_direction, tracker, False):
                if enterer_flipped:
                    enterer.is_flipped ^= True
                return True
            tracker.pop_last()
            enterer.pressed_direction = None

            if not enter_obj.is_nonenterable():
                # enter
                this_enter_info = EnterInfo(self.room, outer_offset)
                next_enter_info = EnterInfo(enter_obj.room, new_offset)
                if this_enter_info == next_enter_info:
                    # self is being infentered
                    # enterer is enter infenter instead of self
                    infenter = self.get_infenter_reference(infenter_degree)
                    if infenter._entered_by(enterer, enterer_direction, tracker, new_offset, enterer_already_should_flip, is_first_movement, infenter_degree + 1):
                        if enterer_flipped:
                            enterer.is_flipped ^= True
                        return True
                else:
                    if enter_obj._entered_by(enterer, enterer_direction, tracker, new_offset, enterer_already_should_flip ^ self.is_flipped, is_first_movement, infenter_degree):
                        if enterer_flipped:
                            enterer.is_flipped ^= True
                        return True

                if not (enterer.is_wall or enterer.is_nonenterable()):
                    # eat
                    tracker.move_enter(self.MoveRecord(enterer, self.room, enter_pos, enterer_already_should_flip ^ self.is_flipped))
                    # self.pressed_direction = enterer_direction  TODO: check whether we should set "self.pressed_direction" or "enterer.pressed_direction"
                    enterer.pressed_direction = enterer_direction
                    if enter_obj._eaten_by(enterer, enterer_direction, tracker):
                        if enterer_flipped:
                            enterer.is_flipped ^= True
                        return True
                    tracker.pop_last()
                    enterer.pressed_direction = None

            # failed, clean up
            self.pressed_direction = None
            tracker.pop_last()
            if enterer_flipped:
                enterer.is_flipped ^= True

        # possess
        if is_first_movement:
            self.pressed_direction = direction
            if enter_obj._possessed_by(enterer, direction, tracker, new_offset):
                return True
            self.pressed_direction = None

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
        eater_enter_pos = directions.enter_pos(reversed_direction, eater.room.width, eater.room.height, eater.is_flipped)
        eater_enter_obj = eater.room.get(eater_enter_pos)
        if eater_enter_obj == object_types.GROUND:
            tracker.move_eat(self.MoveRecord(self, eater.room, eater_enter_pos, eater.is_flipped))
            return True
        if eater_enter_obj == object_types.WALL:
            return False

        """
        now "self" block is in the next pos of "eater" block
        we need to check if the enter object is pushable or enterable in the reversed direction
        refer to eat.txt and eat_2.txt
        """

        # possessable walls are only possessable, not pushable or something else
        if eater_enter_obj.is_wall:
            return False

        # recurse start here
        # prepare
        if eater.is_flipped and directions.is_horizontal(reversed_direction):
            enter_obj_direction = directions.reverse(reversed_direction)
        else:
            enter_obj_direction = reversed_direction
        if eater.is_flipped:
            self.is_flipped ^= True
        self_flipped = eater.is_flipped

        # push
        tracker.move_eat(self.MoveRecord(self, eater.room, eater_enter_pos, eater.is_flipped))
        self.pressed_direction = enter_obj_direction
        if eater_enter_obj._pushed(enter_obj_direction, tracker):
            if self_flipped:
                self.is_flipped ^= True
            return True
        tracker.pop_last()
        self.pressed_direction = None

        if not eater_enter_obj.is_nonenterable():
            if eater.room == eater_enter_obj.room:
                # self is being infentered
                # enterer is enter infenter instead of self
                if eater.is_infenter:
                    next_degree = eater.infenter_num + 1
                else:
                    next_degree = 0
                infenter = eater.get_infenter_reference(next_degree)
                if infenter._entered_by(self, enter_obj_direction, tracker, 0.5, eater.is_flipped, False, 1):
                    if self_flipped:
                        self.is_flipped ^= True
                    return True

            # enter
            if eater_enter_obj._entered_by(self, enter_obj_direction, tracker, 0.5, eater.is_flipped, False):
                if self_flipped:
                    self.is_flipped ^= True
                return True
        # "self" block can not eat eater_enter_obj
        # so no need to check it
        # otherwise, it will be eater block entering the "self" block, instead of eating "self" block
        if self_flipped:
            self.is_flipped ^= True

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


    def _possessed_by(self, ghost_holder: "Reference", direction: int, tracker: MoveTracker, outer_offset=0.5):
        """
        check if "self" objects can be possessed by the "ghost_holder" object in the given direction
        (direction is where the "ghost_holder" object want to go)
        suppose the ghost_holder is going to go to the position of "self" object
        """

        # precheck, check if ghost_holder is player and if self is possessable
        if not ghost_holder.is_player or self.is_player:
            return False
        if self.is_possessable:
            tracker.move_possess(self.MoveRecord(ghost_holder, ghost_holder.parent_room, ghost_holder.pos, False, False))
            tracker.move_possess(self.MoveRecord(self, self.parent_room, self.pos, False, True))
            return True

        return False


    def possessed_by(self, ghost_holder: "Reference", direction: int, _undo_record: undo_record.UndoRecord, dry_run=False):
        """
        check if "self" objects can be possessed by the "ghost_holder" object in the given direction
        (direction is where the "ghost_holder" object want to go)
        suppose the ghost_holder is going to go to the position of "self" object
        """
        tracker = self.MoveTracker()
        result = self._possessed_by(ghost_holder, direction, tracker, 0.5)
        if result and not dry_run:
            self.conduct_record(tracker.records, _undo_record)
        for record in tracker.records:
            record.reference.pressed_direction = None
        return result


    def render(self, canvas: Canvas, area: tuple[tuple[int, int], tuple[int, int]],
               parent_room_wall_color_int, render_as_flipped: bool):
        """
        area: (left_bottom, right_top), both are (x, y)
        """

        if not self.is_wall:
            self.room.render(canvas, area, render_as_flipped ^ self.is_flipped)
            canvas.draw_empty_box_area(area, 0)
        else:
            canvas.draw_filled_box_area(area, parent_room_wall_color_int)

        if self.is_player:
            canvas.draw_tile_area("Player", area)
        if self.is_possessable and not self.is_player:
            canvas.draw_tile_area("Possessable", area)
        if self.is_infexit:
            canvas.draw_filled_box_area(area, 0xa0000000)
            canvas.draw_tile_area("Infinity", area)
        if self.is_infenter:
            canvas.draw_tile_area("Epsilon", area)

        if not (self.is_exit_block or self.is_infexit):
            canvas.draw_filled_box_area(area, 0x80ffffff, 0)
        if self.is_nonenterable() and not self.is_player:
            canvas.draw_empty_box_area(area, 0xffe700)
