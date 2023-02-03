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
    def __init__(self, string, palette_index=-1):
        self.rooms: dict[int, Room] = {}
        self.references: dict[int, list[Reference]] = {}
        self.graphic_mapping: dict[int, int] = {}
        self.graphic_splitter: GraphicSplitter = None
        self.player: Reference = None
        self.root_room: Room = None
        self.possessable_count: int = 0
        self.goal_count = 0
        self.undo_record = UndoRecord()
        self.palette_index = palette_index
        self.load(string)
        self.init_state = UndoRecord.Record.record_all(self.references)

    def add_reference(self, index: int, reference: Reference):
        if index in self.references:
            self.references[index].append(reference)
        else:
            self.references[index] = [reference]

    def load(self, string: str):
        """
        load a level from a string\n
        don't add references' room and parent_room, and rooms' reference when reading the string\n
        instead add them after the string is completely read\n
        """


        def argify_line(line: str):
            line = line.replace("\t", "").replace("\n", "").replace("\r", "")
            args = line.split(" ")
            return args

        def parse_header_line(line: str):
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

        def indent_count(line: str):
            count = 0
            for char in line:
                if char == "\t":
                    count += 1
                else:
                    break
            return count
        
        def extract_room_lines(lines: list[str]):
            """
            assuming the first line is a room line
            """
            room: list[str] = [lines[0]]
            indent = indent_count(lines[0])
            for line in lines[1:]:
                if indent_count(line) > indent:
                    room.append(line)
                else:
                    break
            return room

        def parse_room_line(line: str):
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
            floatinspace = (args[15] == "1")

            if id in self.rooms:
                raise ValueError("Duplicated room id: {}".format(id))
            if (args[12] == "1"):
                self.possessable_count += 1
                if self.possessable_count > 1:
                    raise NotImplementedError("More than one possessable block in the level, not supported")
            if (args[14] == "1"):
                    raise NotImplementedError("flipped blocks are not supported")
            
            room = Room(width, height, id, (hue, sat, val), fillwithwalls)
            if not floatinspace:
                reference = Reference(id, True, player)
                if player:
                    self.player = reference
                reference.pos = (x, y)
            else:
                reference = None
            
            return (room, reference)

        def parse_reference_line(line: str):
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
            floatinspace = (args[14] == "1")
            player = (args[10] == "1")

            if (args[5] == "1" or args[6] == "1" or args[7] == "1" or args[8] == "1"):
                raise NotImplementedError("infinity blocks are not supported")
            if (args[11] == "1"):
                self.possessable_count += 1
                if self.possessable_count > 1:
                    raise NotImplementedError("More than one possessable block in the level, not supported")
            if (args[13] == "1"):
                    raise NotImplementedError("flipped blocks are not supported")

            if not floatinspace:
                reference = Reference(id, exitblock, player)
                if player:
                    self.player = reference
                reference.pos = (x, y)
            else:
                reference = None

            return reference

        def parse_room(lines: list[str], add_reference=True):
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
                    room.wall_map[x][y] = True
                    if (args[3] == "1" or args[4] == "1"):
                        raise NotImplementedError("possessable walls are not supported")
                    index += 1
                elif args[0] == "Block":
                    sub_room_lines = extract_room_lines(lines[index:])
                    sub_room, sub_reference = parse_room(sub_room_lines)
                    if sub_reference is not None:
                        room.reference_map[sub_reference.pos[0]][sub_reference.pos[1]] = sub_reference
                    index += len(sub_room_lines)
                elif args[0] == "Ref":
                    sub_reference = parse_reference_line(line)
                    if sub_reference is not None:
                        room.reference_map[sub_reference.pos[0]][sub_reference.pos[1]] = sub_reference
                        self.add_reference(sub_reference.id, sub_reference)
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
            # assign references' room and parent_room
            for room in self.rooms.values():
                for x in range(room.width):
                    for y in range(room.height):
                        if room.reference_map[x][y] is not None:
                            room.reference_map[x][y].room = self.rooms[room.reference_map[x][y].id]
                            room.reference_map[x][y].parent_room = room

            # assign rooms' reference
            for room in self.rooms.values():
                if room.id in self.references:
                    for reference in self.references[room.id]:
                        if reference.exit_block:
                            room.reference = reference
                            break

        self.possessable_count = 0
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
        # self.player.room.is_block = True

    # def render(self, base_graphic, size: tuple[int, int] = (200, 200)):
    #     self.graphic_mapping = {}
    #     self.splitter_wall = GraphicSplitter(base_graphic, size[0], size[1], len(self.rooms), 0x000000)
    #     index = 0
    #     for room in self.rooms.values():
    #         virtual_graphic = self.splitter_wall.get_virtual_graphic(index)
    #         self.graphic_mapping[room.id] = index
    #         index += 1
    #         room.render(virtual_graphic, ((0, 0), (size[0] - 1, size[1] - 1)), self.rooms)

    def render(self, base_graphic, room = None, size: tuple[int, int] = (200, 200)):
        if room is None:
            room = self.player.parent_room
        background_color = 0
        if room.reference is not None:
            color = room.reference.parent_room.color[:2] + (room.reference.room.color[2] * 0.45,)
            background_color = utils.Color.hsv_to_rgb_int(*color)
        hpprime.dimgrob(base_graphic, 320, 240, background_color)
        render_pos = ((320 - size[0]) // 2, (240 - size[1]) // 2)
        virtual_graphic = VirtualGraphic(base_graphic, render_pos[0], render_pos[1], size[0], size[1])
        room.render(virtual_graphic, ((0, 0), (size[0] - 1, size[1] - 1)), self.rooms)
        hpprime.blit(0, 0, 0, base_graphic)

    def is_completed(self):
        if self.goal_count == 0:
            return False

        for room in self.rooms.values():
            if not room.is_completed():
                return False
        return True

    def play(self):
        self.render(1)
        while True:
            direction = get_input()
            if direction == actions.UP:
                self.player.pushed(directions.UP, self.undo_record)
            elif direction == actions.LEFT:
                self.player.pushed(directions.LEFT, self.undo_record)
            elif direction == actions.DOWN:
                self.player.pushed(directions.DOWN, self.undo_record)
            elif direction == actions.RIGHT:
                self.player.pushed(directions.RIGHT, self.undo_record)
            elif direction == actions.UNDO:
                self.undo_record.undo()
            elif direction == actions.RESTART:
                self.undo_record.append(UndoRecord.Record.record_all(self.references))
                self.init_state.undo()

            self.render(1)

            if self.is_completed():
                hpprime.eval("TEXTOUT_P(\"You win!\", G0, 0, 0, 7, #FFFF00h, 200, 0)")
                get_input()
                break
            