from graphic_splitter import GraphicSplitter
from virtual_graphic import VirtualGraphic
from room import Room
from reference import Reference
import hpprime
from control import get_input
import directions
import actions
import button
from undo_record import UndoRecord
import utils
from palettes import Palettes

class Level:
    def __init__(self, string     , palette_index=-1):
        self.rooms                  = {}
        self.references                             = {}  # not including possessable walls and infs
        self.possessable_walls                  = []
        self.infexit_references                                  = {}  # the first index is the room id, the second is the infexit number
        self.infenter_references                                  = {}  # the first index is the room id, the second is the infenter number
        self.graphic_mapping                 = {}
        self.graphic_splitter                  = None
        self.players                       = {}
        self.root_room       = None
        self.goal_count = 0
        self.undo_record = UndoRecord()
        self.palette_index = palette_index
        self.load(string)
        self.init_state = UndoRecord.Record.record_all(self.references, self.possessable_walls, self.infexit_references, self.infenter_references)

    def add_reference(self, index     , reference           ):
        if reference.is_infexit:
            if index in self.infexit_references:
                self.infexit_references[index][reference.infexit_num] = reference
            else:
                self.infexit_references[index] = {reference.infexit_num: reference}
        if reference.is_infenter:
            from_index = reference.infenter_from_id
            if from_index in self.infenter_references:
                self.infenter_references[from_index][reference.infenter_num] = reference
            else:
                self.infenter_references[from_index] = {reference.infenter_num: reference}
        if not reference.is_infexit and not reference.is_infenter:
            if index in self.references:
                self.references[index].append(reference)
            else:
                self.references[index] = [reference]

    def load(self, string     ):
        """
        load a level from a string\n
        don't add references' room and parent_room, and rooms' reference when reading the string\n
        instead add them after the string is completely read\n
        """

        def argify_line(line     ):
            line = line.replace("\t", "").replace("\n", "").replace("\r", "")
            args = line.split(" ")
            return args

        def parse_header_line(line     ):
            """
            return whether the next line should still be header line
            """
            ignored_args = ["version", "draw_style", "custom_level_music"]
            unsupported_args = ["attempt_order", "shed", "inner_push"]
            args = argify_line(line)
            if args[0] == "#":
                return False
            elif args[0] == "custom_level_palette":
                self.palette_index = int(args[1])
            elif args[0] in ignored_args:
                return True
            elif args[0] in unsupported_args:
                raise NotImplementedError("Unsupported argument: {}".format(args[0]))
            else:
                raise ValueError("Unknown argument: {}".format(args[0]))

        def indent_count(line     ):
            count = 0
            for char in line:
                if char == "\t":
                    count += 1
                else:
                    break
            return count
        
        def extract_room_lines(lines           ):
            """
            assuming the first line is a room line
            """
            room            = [lines[0]]
            indent = indent_count(lines[0])
            for line in lines[1:]:
                if indent_count(line) > indent:
                    room.append(line)
                else:
                    break
            return room

        def parse_room_line(line     ):
            """
            return (room, reference)
            """
            args = argify_line(line)
            if args[0] != "Block":
                raise ValueError("Unknown room type: {}, expected: Block".format(args[0]))
            if len(args) != 17:
                raise ValueError("the room line \"{}\" should have 17 arguments, but got {}".format(line, len(args)))
            
            x = int(args[1])
            y = int(args[2])
            id = int(args[3])
            width = int(args[4])
            height = int(args[5])
            
            hue = float(args[6])
            sat = float(args[7])
            val = float(args[8])
            color = (hue, sat, val)
            color = Palettes().transfer_color(color, self.palette_index)
            hue, sat, val = color
            
            fillwithwalls = (args[10] == "1")
            player = (args[11] == "1")
            possessable = (args[12] == "1")
            playerorder = int(args[13])
            fliph = (args[14] == "1")
            floatinspace = (args[15] == "1")

            if id in self.rooms:
                raise ValueError("Duplicated room id: {}".format(id))

            room = Room(width, height, id, (hue, sat, val), fillwithwalls, False, False)
            # if not floatinspace:
            reference = Reference(id, (x, y), True, True, player, possessable, playerorder, fliph, False,
                                  floatinspace, 0, 0, 0, 0, 0)
            if player:
                self.players[playerorder] = reference
            # else:
            #     reference = None
            
            return (room, reference)

        def parse_reference_line(line     ):
            """
            return reference
            """
            args = argify_line(line)
            if args[0] != "Ref":
                raise ValueError("Unknown reference type: {}, expected: Ref".format(args[0]))
            if len(args) != 16:
                raise ValueError("the reference line \"{}\" should have 16 arguments, but got {}".format(line, len(args)))
            
            x = int(args[1])
            y = int(args[2])
            id = int(args[3])
            exitblock = (args[4] == "1")
            is_infexit = (args[5] == "1")
            infexit_num = int(args[6])
            is_infenter = (args[7] == "1")
            infenter_num = int(args[8])
            infenter_id = int(args[9])
            player = (args[10] == "1")
            possessable = (args[11] == "1")
            playerorder = int(args[12])
            fliph = (args[13] == "1")
            floatinspace = (args[14] == "1")

            # if not floatinspace:
            reference = Reference(id, (x, y), False, exitblock, player, possessable, playerorder, fliph, False,
                                  floatinspace, is_infexit, infexit_num, is_infenter, infenter_num, infenter_id)
            if player:
                self.players[playerorder] = reference
            # else:
            #     reference = None

            return reference

        def parse_room(lines           , add_reference=True):
            """
            return (room, reference)\n
            assuming the lines contain a room line and its contents in the following indented lines
            """
            room, reference = parse_room_line(lines[0])
            # this is the only place where we add rooms to the dicts
            self.rooms[room.id] = room
            if not add_reference:
                reference = None
            if reference is not None:
                self.add_reference(reference.id, reference)
            index = 1
            while index < len(lines):
                line = lines[index]
                args = argify_line(line)
                if args[0] == "Wall":
                    x = int(args[1])
                    y = int(args[2])
                    if args[4] == "1":
                        is_player = (args[3] == "1")
                        playerorder = int(args[5])
                        wall_reference = Reference(None, (x, y), False, True, is_player, True, playerorder, False, True,
                                                   False, 0, 0, 0, 0, 0)
                        room.reference_map[x][y] = wall_reference
                        self.possessable_walls.append(wall_reference)
                        if is_player:
                            self.players[playerorder] = wall_reference
                    else:
                        room.wall_map[x][y] = True
                    index += 1
                elif args[0] == "Block":
                    sub_room_lines = extract_room_lines(lines[index:])
                    sub_room, sub_reference = parse_room(sub_room_lines)
                    # if not sub_reference.float_in_space:  # we will remove these references in final cleanup
                    room.reference_map[sub_reference.pos[0]][sub_reference.pos[1]] = sub_reference
                    index += len(sub_room_lines)
                elif args[0] == "Ref":
                    sub_reference = parse_reference_line(line)
                    self.add_reference(sub_reference.id, sub_reference)
                    # if not sub_reference.float_in_space:  # we will remove these references in final cleanup
                    room.reference_map[sub_reference.pos[0]][sub_reference.pos[1]] = sub_reference
                    index += 1
                elif args[0] == "Floor":
                    x = int(args[1])
                    y = int(args[2])
                    info = ""
                    if args[3] == "Button":
                        type = button.BUTTON
                        self.goal_count += 1
                    elif args[3] == "PlayerButton":
                        type = button.PLAYER_BUTTON
                        self.goal_count += 1
                    elif args[3] == "FastTravel":
                        type = button.FAST_TRAVEL
                    elif args[3] == "Info":
                        type = button.INFO
                        info = args[4]
                    else:
                        raise ValueError("Unknown floor type: {}".format(args[3]))
                    room.buttons.append(button.Button((x, y), type, info))
                    index += 1

            return (room, reference)
        
        def assign():
            # assign references' level
            for reference_id in self.references:
                for reference in self.references[reference_id]:
                    reference.level = self
            for reference in self.possessable_walls:
                reference.level = self
            for reference_id in self.infexit_references:
                for reference in self.infexit_references[reference_id].values():
                    reference.level = self
            for reference_id in self.infenter_references:
                for reference in self.infenter_references[reference_id].values():
                    reference.level = self

            # assign references' room and parent_room
            for room in self.rooms.values():
                for x in range(room.width):
                    for y in range(room.height):
                        if room.reference_map[x][y] is not None:
                            if not room.reference_map[x][y].float_in_space:
                                room.reference_map[x][y].parent_room = room
                            if not room.reference_map[x][y].is_wall:
                                room.reference_map[x][y].room = self.rooms[room.reference_map[x][y].id]

            # references' "exitblock" overrides rooms' default exitblock (which is itself)
            for reference_id in self.references:
                for reference in self.references[reference_id]:
                    if not reference.is_room_generated and reference.is_exit_block:
                        for reference_2 in self.references[reference_id]:
                            if reference_2.is_room_generated:
                                reference_2.is_exit_block = False
                        break
            for room_id in self.infenter_references:
                for infenter in self.infenter_references[room_id].values():
                    if not infenter.is_room_generated and infenter.is_exit_block:
                        for reference in self.references[infenter.id]:
                            if reference.is_room_generated:
                                reference.is_exit_block = False
                        break

            # assign rooms' reference
            for room in self.rooms.values():
                if room.id in self.references:
                    for reference in self.references[room.id]:
                        if reference.is_exit_block:
                            room.exit_reference = reference
                            break
            for room_id in self.infenter_references:
                for infenter in self.infenter_references[room_id].values():
                    if infenter.is_exit_block:
                        infenter.room.exit_reference = infenter

            # remove float_in_space references from room.reference_map
            for room in self.rooms.values():
                for x in range(room.width):
                    for y in range(room.height):
                        if room.reference_map[x][y] is not None and room.reference_map[x][y].float_in_space:
                            room.reference_map[x][y] = None


        lines = string.split("\n")
        index = 0
        while index < len(lines):
            if lines[index].replace(" ", "").replace("\t", "").replace("\r", "") == "":
                lines.pop(index)
            else:
                index += 1
        index = 0
        while (index < len(lines) and parse_header_line(lines[index])):
            index += 1
        index += 1
        room, reference = parse_room(extract_room_lines(lines[index:]), False)
        self.root_room = room
        self.root_room.is_root_room = True
        self.root_room.not_block = True
        assign()


    def render(self, base_graphic, room=None, size                  = (200, 200)):
        player_to_focus = self.players[0]
        if room is None:
            room = player_to_focus.parent_room
        background_color = 0
        if room.exit_reference is not None and room.exit_reference.parent_room is not None:
            color = room.exit_reference.parent_room.color[:2] + (room.exit_reference.room.color[2] * 0.45,)
            background_color = utils.Color.hsv_to_rgb_int(*color)
        hpprime.dimgrob(base_graphic, 320, 240, background_color)
        render_pos = ((320 - size[0]) // 2, (240 - size[1]) // 2)
        virtual_graphic = VirtualGraphic(base_graphic, render_pos[0], render_pos[1], size[0], size[1])
        room.render(virtual_graphic, ((0, 0), (size[0] - 1, size[1] - 1)), player_to_focus.is_view_flipped)
        hpprime.blit(0, 0, 0, base_graphic)

    def is_completed(self):
        if self.goal_count == 0:
            return False

        for room in self.rooms.values():
            if not room.is_completed():
                return False
        return True


    def push_players(self, direction, undo_record, render=True, delay=0.1):
        for player_order in sorted(self.players):
            self.players[player_order].pushed(direction, undo_record, False)
            if render:
                self.render(1)
                if player_order != max(self.players):
                    hpprime.eval("WAIT({})".format(delay))

    def play(self):
        base_room = self.players[0].parent_room
        self.render(1)
        while True:
            action = get_input()
            if action == actions.UP:
                self.push_players(directions.UP, self.undo_record)
            elif action == actions.LEFT:
                if not self.players[0].is_view_flipped:
                    self.push_players(directions.LEFT, self.undo_record)
                else:
                    self.push_players(directions.RIGHT, self.undo_record)
            elif action == actions.DOWN:
                self.push_players(directions.DOWN, self.undo_record)
            elif action == actions.RIGHT:
                if not self.players[0].is_view_flipped:
                    self.push_players(directions.RIGHT, self.undo_record)
                else:
                    self.push_players(directions.LEFT, self.undo_record)
            elif action == actions.UNDO:
                self.undo_record.undo(self.players, self.infexit_references, self.infenter_references)
            elif action == actions.RESTART:
                self.undo_record.append(UndoRecord.Record.record_all(self.references, self.possessable_walls, self.infexit_references, self.infenter_references))
                self.init_state.undo(self.players, self.infexit_references, self.infenter_references)

            self.render(1)
            # self.render(1, base_room)

            if self.is_completed():
                hpprime.eval("TEXTOUT_P(\"You win!\", G0, 0, 0, 7, #FFFF00h, 200, 0)")
                get_input()
                break
