from time import time, sleep
import os
import pygame
from typing import Union, Optional
import re
import tkinter as tk

LOGGING = False
SCREEN_SIZE = (320, 240)
SCALE = True
SCALE_FACTOR = 3
INTERPOLATION = True

SCALED_SCREEN_SIZE = (SCREEN_SIZE[0] * SCALE_FACTOR, SCREEN_SIZE[1] * SCALE_FACTOR)

window: Optional[pygame.Surface] = None
graphics: list[Optional[pygame.Surface]] = [None for _ in range(10)]
variables: dict[str, int] = {}

key_mapping = {
    pygame.K_F1: 0,
    pygame.K_F2: 1,
    pygame.K_UP: 2,
    pygame.K_PAGEUP: 2,
    pygame.K_F3: 3,
    pygame.K_HELP: 3,
    pygame.K_ESCAPE: 4,
    pygame.K_CLEAR: 4,
    pygame.K_HOME: 5,
    pygame.K_F4: 5,
    pygame.K_F5: 6,
    pygame.K_LEFT: 7,
    pygame.K_RIGHT: 8,
    pygame.K_F6: 9,
    pygame.K_F7: 10,
    pygame.K_F8: 11,
    pygame.K_DOWN: 12,
    pygame.K_PAGEDOWN: 12,
    pygame.K_F9: 13,
    pygame.K_a: 14,
    pygame.K_b: 15,
    pygame.K_c: 16,
    pygame.K_d: 17,
    pygame.K_e: 18,
    pygame.K_BACKSPACE: 19,
    pygame.K_DELETE: 19,
    pygame.K_CARET: 20,
    pygame.K_f: 20,
    pygame.K_g: 21,
    pygame.K_h: 22,
    pygame.K_i: 23,
    pygame.K_j: 24,
    pygame.K_k: 25,
    pygame.K_l: 26,
    pygame.K_m: 27,
    pygame.K_n: 28,
    pygame.K_COMMA: 29,
    pygame.K_o: 29,
    pygame.K_RETURN: 30,
    pygame.K_KP_ENTER: 30,
    pygame.K_p: 31,
    pygame.K_7: 32,
    pygame.K_q: 32,
    pygame.K_8: 33,
    pygame.K_r: 33,
    pygame.K_9: 34,
    pygame.K_s: 34,
    pygame.K_SLASH: 35,
    pygame.K_t: 35,
    pygame.K_TAB: 36,
    pygame.K_4: 37,
    pygame.K_u: 37,
    pygame.K_5: 38,
    pygame.K_v: 38,
    pygame.K_6: 39,
    pygame.K_w: 39,
    pygame.K_KP_MULTIPLY: 40,
    pygame.K_x: 40,
    pygame.K_LSHIFT: 41,
    pygame.K_RSHIFT: 41,
    pygame.K_1: 42,
    pygame.K_y: 42,
    pygame.K_2: 43,
    pygame.K_z: 43,
    pygame.K_3: 44,
    pygame.K_MINUS: 45,
    pygame.K_KP_MINUS: 45,
    pygame.K_COLON: 45,
    pygame.K_BACKQUOTE: 46,
    pygame.K_0: 47,
    pygame.K_QUOTEDBL: 47,
    pygame.K_PERIOD: 48,
    pygame.K_EQUALS: 48,
    pygame.K_SPACE: 49,
    pygame.K_UNDERSCORE: 49,
    pygame.K_PLUS: 50,
    pygame.K_SEMICOLON: 50
}

def check_flip(graphic):
    if graphic == 0:
        if SCALE and not INTERPOLATION:
            window.blit(pygame.transform.scale(graphics[graphic], SCALED_SCREEN_SIZE), (0, 0))
            pygame.display.flip()
        else:
            window.blit(graphics[graphic], (0, 0))
            pygame.display.flip()

def int_color_to_tuple(color):
    if color >> 24 == 0:
        return (color >> 16 & 0xFF, color >> 8 & 0xFF, color & 0xFF, 0xFF)
    else:
        return (color >> 16 & 0xFF, color >> 8 & 0xFF, color & 0xFF, 0xFF - color >> 24 & 0xFF)

def blit(target_graphic, x, y, source_graphic):
    if LOGGING:
        print(f"blit({target_graphic}, {x}, {y}, {source_graphic})")
    if SCALE and INTERPOLATION:
        x *= SCALE_FACTOR
        y *= SCALE_FACTOR
    graphics[target_graphic].blit(graphics[source_graphic], (x, y))
    check_flip(target_graphic)

def strblit2(target_graphic, x, y, width, height, source_graphic, source_x, source_y, source_width, source_height):
    if LOGGING:
        print(f"strblit2({target_graphic}, {x}, {y}, {width}, {height}, {source_graphic}, {source_x}, {source_y}, {source_width}, {source_height})")
    if SCALE and INTERPOLATION:
        x *= SCALE_FACTOR
        y *= SCALE_FACTOR
        width *= SCALE_FACTOR
        height *= SCALE_FACTOR
        source_x *= SCALE_FACTOR
        source_y *= SCALE_FACTOR
        source_width *= SCALE_FACTOR
        source_height *= SCALE_FACTOR
    source_rect = pygame.Rect(source_x, source_y, source_width, source_height)
    source_subsurface = graphics[source_graphic].subsurface(source_rect)
    scaled_subsurface = pygame.transform.scale(source_subsurface, (width, height))
    graphics[target_graphic].blit(scaled_subsurface, (x, y))
    check_flip(target_graphic)


def dimgrob(graphic, width, height, color):
    if LOGGING:
        print(f"dimgrob({graphic}, {width}, {height}, {color})")
    if SCALE and INTERPOLATION:
        width *= SCALE_FACTOR
        height *= SCALE_FACTOR
    canvas_size = (width, height)
    canvas = pygame.Surface(canvas_size, flags=pygame.SRCALPHA)
    color_tuple = int_color_to_tuple(color)
    canvas.fill(color_tuple)
    graphics[graphic] = canvas
    check_flip(graphic)

def translucent_rect(surface, color_tuple, x, y, width, height, line_width=0):
    if SCALE and INTERPOLATION:
        x *= SCALE_FACTOR
        y *= SCALE_FACTOR
        width *= SCALE_FACTOR
        height *= SCALE_FACTOR
        line_width *= SCALE_FACTOR
    rect_surface = pygame.Surface((width, height), flags=pygame.SRCALPHA)
    pygame.draw.rect(rect_surface, color_tuple, (0, 0, width, height), width=line_width)
    surface.blit(rect_surface, (x, y))

def rect(graphic, x, y, width, height, color):
    if LOGGING:
        print(f"rect({graphic}, {x}, {y}, {width}, {height}, {color})")
    # the scaling is done in translucent_rect
    color_tuple = int_color_to_tuple(color)
    translucent_rect(graphics[graphic], color_tuple, x, y, width, height, line_width=1)
    check_flip(graphic)

def fillrect(graphic, x, y, width, height, color_edge, color_fill):
    if LOGGING:
        print(f"fillrect({graphic}, {x}, {y}, {width}, {height}, {color_edge}, {color_fill})")
    # the scaling is done in translucent_rect
    color_edge_tuple = int_color_to_tuple(color_edge)
    color_fill_tuple = int_color_to_tuple(color_fill)
    translucent_rect(graphics[graphic], color_fill_tuple, x, y, width, height)
    if color_edge != color_fill:
        translucent_rect(graphics[graphic], color_edge_tuple, x, y, width, height, line_width=1)
    check_flip(graphic)


def grobh(graphic):
    if LOGGING:
        print(f"grobh({graphic})")
    height = graphics[graphic].get_height()
    if SCALE and INTERPOLATION:
        height //= SCALE_FACTOR
    return height


def grobw(graphic):
    if LOGGING:
        print(f"grobw({graphic})")
    width = graphics[graphic].get_width()
    if SCALE and INTERPOLATION:
        width //= SCALE_FACTOR
    return width

def eval(string):
    def get_files_list():
        current_dir = os.getcwd()
        file_list = os.listdir(current_dir)
        file_list = [file for file in file_list if os.path.isfile(os.path.join(current_dir, file))]
        return file_list

    def getkey():
        while event := pygame.event.poll():
            if event.type == pygame.QUIT:
                exit(0)
            if event.type == pygame.KEYDOWN and event.key in key_mapping:
                return key_mapping[event.key]

        return -1

    def choose(title, options):
        """
        显示一个包含一系列按钮的窗口，返回用户点击的按钮的序号。
        如果用户直接关闭窗口而没有选择，则返回0。

        :param title: 窗口内部的标题
        :param options: 选项列表
        :return: 用户点击的按钮的序号（从1开始）或0（如果用户关闭了窗口）
        """

        def button_clicked(index):
            global choice
            choice = index + 1
            root.destroy()

        def on_closing():
            global choice
            choice = 0
            root.destroy()

        root = tk.Tk()
        root.title('Choose one')

        # 在窗口内部显示标题
        title_label = tk.Label(root, text=title, font=('Arial', 16))
        title_label.pack(pady=10)

        for i, option in enumerate(options):
            btn = tk.Button(root, text=option, command=lambda idx=i: button_clicked(idx))
            btn.pack(pady=5)

        # 设置关闭窗口的回调
        root.protocol("WM_DELETE_WINDOW", on_closing)

        # 运行事件循环
        root.mainloop()

        return choice

    load_image_pattern = r'^ *G([0-9]) *:= *AFiles\("(.+)"\) *$'
    dimgrob_pattern = r'^ *DIMGROB_P\(G([0-9]), *([0-9]+), *([0-9]+), *(#?[0-9a-fA-F]+)h?\) *$'
    rectp_1_pattern = r'^ *RECT_P\(G([0-9]), *([0-9]+), *([0-9]+), *([0-9]+), *([0-9]+), *(#?[0-9a-fA-F]+)h?\) *$'
    rectp_2_pattern = r'^ *RECT_P\(G([0-9]), *([0-9]+), *([0-9]+), *([0-9]+), *([0-9]+), *(#?[0-9a-fA-F]+)h?, *(#?[0-9a-fA-F]+)h?\) *$'
    set_variable_pattern = r'^ *([A-Z]) *:= *([0-9]+) *$'
    get_variable_pattern = r'^ *([A-Z]) *$'
    choose_pattern = r'^ *CHOOSE\(([A-Z]), *(.+)\) *$'
    textout_pattern = r'^ *TEXTOUT_P\("(.+)", *(.+)\) *$'
    wait_pattern = r'^ *WAIT\(([0-9\.]+)\) *$'

    if LOGGING:
        if string != "GETKEY" and string != "GETKEY()":
            print(f"eval(\"{string}\")")
    if string == "time":
        return time()
    elif string == "AFiles" or string == "AFiles()":
        return get_files_list()
    elif string == "GETKEY" or string == "GETKEY()":
        key = getkey()
        if LOGGING:
            # print(f"GETKEY returns {key}")
            pass
        return key
    elif matched := re.match(load_image_pattern, string, re.IGNORECASE):
        graphic = int(matched.group(1))
        filename = matched.group(2)
        if LOGGING:
            print(f"Loading image {filename} into graphic {graphic}")
        temp_graphic = pygame.image.load(filename).convert_alpha()
        if SCALE and INTERPOLATION:
            temp_graphic = pygame.transform.scale_by(temp_graphic, SCALE_FACTOR)
        graphics[graphic] = temp_graphic
        check_flip(graphic)
    elif matched := re.match(dimgrob_pattern, string, re.IGNORECASE):
        graphic = int(matched.group(1))
        width = int(matched.group(2))
        height = int(matched.group(3))
        color = int(matched.group(4)[1:], 16) if matched.group(4)[0] == "#" else int(matched.group(4))
        if LOGGING:
            print(f"Creating graphic {graphic} with size {width}x{height} and color {color}")
        dimgrob(graphic, width, height, color)
        check_flip(graphic)
    elif matched := re.match(rectp_1_pattern, string, re.IGNORECASE):
        graphic = int(matched.group(1))
        x1 = int(matched.group(2))
        y1 = int(matched.group(3))
        x2 = int(matched.group(4))
        y2 = int(matched.group(5))
        width = x2 - x1 + 1
        height = y2 - y1 + 1
        color = int(matched.group(6)[1:], 16) if matched.group(6)[0] == "#" else int(matched.group(6))
        if LOGGING:
            print(f"Drawing rectangle {x1},{y1} {width}x{height} in graphic {graphic} with color {color}")
        fillrect(graphic, x1, y1, width, height, color, color)
        check_flip(graphic)
    elif matched := re.match(rectp_2_pattern, string, re.IGNORECASE):
        graphic = int(matched.group(1))
        x1 = int(matched.group(2))
        y1 = int(matched.group(3))
        x2 = int(matched.group(4))
        y2 = int(matched.group(5))
        width = x2 - x1 + 1
        height = y2 - y1 + 1
        color1 = int(matched.group(6)[1:], 16) if matched.group(6)[0] == "#" else int(matched.group(6))
        color2 = int(matched.group(7)[1:], 16) if matched.group(7)[0] == "#" else int(matched.group(7))
        if LOGGING:
            print(f"Drawing rectangle {x1},{y1} {width}x{height} in graphic {graphic} with edgecolor {color1} and fillcolor {color2}")
        fillrect(graphic, x1, y1, width, height, color1, color2)
        check_flip(graphic)
    elif matched := re.match(set_variable_pattern, string, re.IGNORECASE):
        variable = matched.group(1)
        value = int(matched.group(2))
        if LOGGING:
            print(f"Setting variable {variable} to {value}")
        variables[variable] = value
    elif matched := re.match(get_variable_pattern, string, re.IGNORECASE):
        variable = matched.group(1)
        if LOGGING:
            print(f"Getting variable {variable}")
        return variables[variable]
    elif matched := re.match(choose_pattern, string, re.IGNORECASE):
        variable = matched.group(1)
        args_string = matched.group(2)
        args_string = re.sub(r'\s*,\s*', ',', args_string)
        args_string = args_string[1:-1]
        args = args_string.split("\",\"")
        if LOGGING:
            print(f"Showing choose window with title {args[0]} and options {args[1:]}")
        variables[variable] = choose(args[0], args[1:])
        if LOGGING:
            print(f"User chose option {variables[variable]}")
    elif matched := re.match(textout_pattern, string, re.IGNORECASE):
        text = matched.group(1)
        args_string = matched.group(2)
        args_string = re.sub(r'\s*,\s*', ',', args_string)
        args = args_string.split(",")
        if args[0][0] == "G":
            graphic = int(args.pop(0)[1:])
        else:
            graphic = 0
        x = int(args.pop(0))
        y = int(args.pop(0))
        font_size = int(args.pop(0)) if len(args) > 0 and int(args[0]) != 0 else 3
        font_size = font_size * 2 + 8
        text_color = args.pop(0) if len(args) > 0 else 0
        if text_color[0] == "#" and text_color[-1] == "h":
            text_color = int(text_color[1:-1], 16)
        else:
            text_color = int(text_color)
        max_width = int(args.pop(0)) if len(args) > 0 else 0
        background_color = int(args.pop(0)) if len(args) > 0 else 0xFFFFFFFF

        if LOGGING:
            print(f"Drawing text \"{text}\" in graphic {graphic} at {x},{y} with font_size {font_size} and color {text_color}")

        if SCALE and INTERPOLATION:
            x *= SCALE_FACTOR
            y *= SCALE_FACTOR
            font_size *= SCALE_FACTOR

        text_color = int_color_to_tuple(text_color)
        background_color = int_color_to_tuple(background_color)
        if os.path.exists("PrimeSansFull.ttf"):
            font = pygame.font.Font("PrimeSansFull.ttf", font_size)
        else:
            font = pygame.font.Font(None, font_size)
        text_surface = font.render(text, True, text_color, background_color)
        if text_surface.get_width() > max_width > 0:
            text_surface = text_surface.subsurface((0, 0, max_width, text_surface.get_height()))
        graphics[graphic].blit(text_surface, (x, y))
        check_flip(graphic)
    elif matched := re.match(wait_pattern, string, re.IGNORECASE):
        seconds = float(matched.group(1))
        if LOGGING:
            print(f"Waiting for {seconds} seconds")
        sleep(seconds)


def textout(graphic, x, y, text, color):
    if LOGGING:
        print(f"textout({graphic}, {x}, {y}, {text}, {color})")
    font_size = 16
    if SCALE and INTERPOLATION:
        x *= SCALE_FACTOR
        y *= SCALE_FACTOR
        font_size *= SCALE_FACTOR
    font = pygame.font.Font("PrimeSansFull.ttf", font_size)
    text_surface = font.render(text, True, color)
    graphics[graphic].blit(text_surface, (x, y))
    check_flip(graphic)


def init():
    global window

    pygame.init()
    if SCALE:
        size = SCALED_SCREEN_SIZE
    else:
        size = SCREEN_SIZE

    window = pygame.display.set_mode(size)

    if SCALE and INTERPOLATION:
        dimgrob(0, *SCALED_SCREEN_SIZE, 0x00000000)
    else:
        dimgrob(0, *SCREEN_SIZE, 0x00000000)


init()
