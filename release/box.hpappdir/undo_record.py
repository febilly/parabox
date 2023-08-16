# import reference

MAX_ENTRIES = 1000

class UndoRecord:
    class Movement:
        # def __init__(self, reference: reference.Reference, parent_room, pos: tuple[int, int]):
        def __init__(self, reference, parent_room, pos                 , is_flipped      , is_view_flipped      , is_player      ):
            self.reference = reference
            self.parent_room = parent_room
            self.pos = pos
            self.is_flipped = is_flipped
            self.is_view_flipped = is_view_flipped
            self.is_player = is_player

    class Record:
        def __init__(self):
            self.movements                            = []
            self.infexit_references                  = None
            self.infenter_references                  = None

        def append(self, movement                       ):
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
        def record_all(cls, references                 , possessable_walls      , infexit_references                 , infenter_references                 ):
            record = cls()
            for reference_list in references.values():
                for reference in reference_list:
                    record.append(UndoRecord.Movement(reference, reference.parent_room, reference.pos, reference.is_flipped, reference.is_view_flipped, reference.is_player))
            for reference in possessable_walls:
                record.append(UndoRecord.Movement(reference, reference.parent_room, reference.pos, reference.is_flipped, reference.is_view_flipped, reference.is_player))
            for reference_id in infexit_references:
                for reference in infexit_references[reference_id].values():
                    record.append(UndoRecord.Movement(reference, reference.parent_room, reference.pos, reference.is_flipped, reference.is_view_flipped, reference.is_player))
            record.infexit_references = {key: val.copy() for key, val in infexit_references.items()}
            record.infenter_references = {key: val.copy() for key, val in infenter_references.items()}
            return record

        def undo(self, level_players      , infexit_references                 , infenter_references                 ):
            for movement in self.movements:
                reference = movement.reference
                if reference.float_in_space:
                    continue

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

            if self.infexit_references is not None:
                # we can't just use "=" here because we want to copy the lists to the Level.infexit_references
                infexit_references.clear()
                infexit_references.update({key: val.copy() for key, val in self.infexit_references.items()})
            if self.infenter_references is not None:
                infenter_references.clear()
                infenter_references.update({key: val.copy() for key, val in self.infenter_references.items()})


    def __init__(self):
        self.undo_stack                          = []

    def append(self, record        ):
        while len(self.undo_stack) >= MAX_ENTRIES:
            self.undo_stack.pop(0)
        self.undo_stack.append(record)
        
    def undo(self, level_players      , infexit_references                 , infenter_references                 ):
        if len(self.undo_stack) > 0:
            self.undo_stack.pop().undo(level_players, infexit_references, infenter_references)
