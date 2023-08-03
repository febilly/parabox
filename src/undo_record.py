# import reference

MAX_ENTRIES = 1000

class UndoRecord:
    class Movement:
        # def __init__(self, reference: reference.Reference, parent_room, pos: tuple[int, int]):
        def __init__(self, reference, parent_room, pos: tuple[int, int], is_flipped: bool, is_view_flipped: bool, is_player: bool):
            self.reference = reference
            self.parent_room = parent_room
            self.pos = pos
            self.is_flipped = is_flipped
            self.is_view_flipped = is_view_flipped
            self.is_player = is_player

    class Record:
        def __init__(self):
            self.movements: list[UndoRecord.Movement] = []
        
        def append(self, movement: "UndoRecord.Movement"):
            self.movements.append(movement)

        @classmethod
        # def from_move_records(cls, move_records: list[reference.Reference.MoveRecord]):
        def from_move_records(cls, move_records):
            record = cls()
            for move_record in move_records:
                reference = move_record.reference
                record.append(UndoRecord.Movement(reference, reference.parent_room, reference.pos, reference.is_flipped, reference.is_view_flipped, reference.is_player))
            return record

        @classmethod
        # def record_all(cls, references: dict[int, list[reference.Reference]], possessable_walls: list[reference.Reference]):
        def record_all(cls, references, possessable_walls):
            record = cls()
            for reference_list in references.values():
                for reference in reference_list:
                    record.append(UndoRecord.Movement(reference, reference.parent_room, reference.pos, reference.is_flipped, reference.is_view_flipped, reference.is_player))
            for reference in possessable_walls:
                record.append(UndoRecord.Movement(reference, reference.parent_room, reference.pos, reference.is_flipped, reference.is_view_flipped, reference.is_player))
            return record

        def undo(self, level_players: dict):
            for movement in self.movements:
                reference = movement.reference
                # remove reference from old place
                old_pos = reference.pos
                old_map = reference.parent_room.reference_map
                if old_map[old_pos[0]][old_pos[1]] is reference:
                    old_map[old_pos[0]][old_pos[1]] = None

                # add reference to new place
                reference.parent_room = movement.parent_room
                new_pos = movement.pos
                movement.reference.pos = new_pos
                new_map = reference.parent_room.reference_map
                new_map[new_pos[0]][new_pos[1]] = reference
                reference.is_flipped = movement.is_flipped
                reference.is_view_flipped = movement.is_view_flipped
                reference.is_player = movement.is_player
                if movement.is_player:
                    level_players[reference.playerorder] = reference


    def __init__(self):
        self.undo_stack: list[UndoRecord.Record] = []

    def append(self, record: Record):
        while len(self.undo_stack) >= MAX_ENTRIES:
            self.undo_stack.pop(0)
        self.undo_stack.append(record)
        
    def undo(self, level_players: dict):
        if len(self.undo_stack) == 0:
            return
        self.undo_stack.pop().undo(level_players)
