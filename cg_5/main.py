from tkinter import *
from tkinter import messagebox, colorchooser
import random
from const import *
from math import sqrt, acos, degrees, pi, sin, cos, radians, floor, fabs
import copy
import numpy as np
import matplotlib.pyplot as plt
import keyboard
from const import *
from time import time, sleep
import colorutils as cu


pressed = False

filling_color = FILL_COLOR
line_color = COLOR_LINE

filled = False


def move_start(event):
    canvas_win.scan_mark(event.x, event.y)


def move_move(event):
    canvas_win.scan_dragto(event.x, event.y, gain=1)


def pressed2(event):
    global pressed
    pressed = not pressed
    canvas_win.scan_mark(event.x, event.y)


def move_move2(event):
    if pressed:
        canvas_win.scan_dragto(event.x, event.y, gain=1)


def zoomer(event):
    if event.delta > 0 or event.num == 4:
        zoom(1.1)
    elif event.delta < 0  or event.num == 5:
        zoom(0.9)


def clear_canvas():
    canvas_win.delete("all")


def draw_dot(x, y, color):
    image_canvas.put(color, (x, y))


def sign(difference):
    if difference < 0:
        return -1
    elif difference == 0:
        return 0
    else:
        return 1


def draw_line(p1, p2, color):
    x1 = p1[0]
    y1 = p1[1]
    x2 = p2[0]
    y2 = p2[1]
    canvas_win.create_line(x1, y1, x2, y2, fill=color)


def read_dot():
    try:
        x = float(x_entry.get())
        y = float(y_entry.get())
    except:
        messagebox.showerror("Ошибка", "Неверные координаты точки")
        return
    add_dot(int(x), int(y))


def add_dot_click(event):
    x = event.x
    y = event.y
    add_dot(x, y)


def add_dot(x, y, last=True):
    global line_color
    cur_figure = len(dots) - 1
    dots[cur_figure].append([x, y])
    cur_dot = len(dots[cur_figure]) - 1
    if last:
        dotslist_box.insert(END, "%d. (%4d;%4d)" % (cur_dot + 1, x, y))
    if len(dots[cur_figure]) > 1:
        sides_list[cur_figure].append([dots[cur_figure][cur_dot - 1], dots[cur_figure][cur_dot]])
        draw_line(dots[cur_figure][cur_dot - 1], dots[cur_figure][cur_dot], line_color)


def close_figure():
    cur_figure = len(dots)
    cur_dot = len(dots[cur_figure - 1])
    if cur_dot < 3:
        messagebox.showerror("Ошибка", "Недостаточно точек, чтобы замкнуть фигуру")
    add_dot(dots[cur_figure - 1][0][0], dots[cur_figure - 1][0][1], last=False)
    dots.append(list())
    sides_list.append(list())
    dotslist_box.insert(END, "_______________________")


def find_line_coefficients(x1, y1, x2, y2):
    a = y1 - y2
    b = x2 - x1
    c = x1 * y2 - x2 * y1
    return a, b, c


def solve_lines_intersection(a1, b1, c1, a2, b2, c2):
    opr = a1 * b2 - a2 * b1
    opr1 = (-c1) * b2 - b1 * (-c2)
    opr2 = a1 * (-c2) - (-c1) * a2
    x = opr1 / opr
    y = opr2 / opr
    return x, y


def round_side(dot1, dot2):
    if dot1[1] == dot2[1]:
        return
    a_side, b_side, c_side = find_line_coefficients(dot1[0], dot1[1], dot2[0], dot2[1])
    if dot1[1] > dot2[1]:
        y_max = dot1[1]
        y_min = dot2[1]
        x = dot2[0]
    else:
        y_max = dot2[1]
        y_min = dot1[1]
        x = dot1[0]
    y = int(y_min)
    while y < y_max:
        a_scan_line, b_scan_line, c_scan_line = find_line_coefficients(x, y, x + 1, y)
        x_intersection, y_intersection = solve_lines_intersection(a_side, b_side, c_side, a_scan_line, b_scan_line, c_scan_line)
        if image_canvas.get(int(x_intersection) + 1, y) != TEMP_SIDE_COLOR_CHECK:
            image_canvas.put(TEMP_SIDE_COLOR, (int(x_intersection) + 1, y))
        else:
            image_canvas.put(TEMP_SIDE_COLOR, (int(x_intersection) + 2, y))
        y += 1
        canvas_win.update()


def round_figure():
    for figure in range(len(sides_list)):
        sides_num = len(sides_list[figure]) - 1
        for side in range(sides_num + 1):
            round_side(sides_list[figure][side][0], sides_list[figure][side][1])


def get_edges(dots):
    x_max = 0
    x_min = CV_WIDE
    y_max = CV_HEIGHT
    y_min = 0
    for figure in dots:
        for dot in figure:
            if dot[0] > x_max:
                x_max = dot[0]
            if dot[0] < x_min:
                x_min = dot[0]
            if dot[1] < y_max:
                y_max = dot[1]
            if dot[1] > y_min:
                y_min = dot[1]
    block_edges = (x_min, y_min, x_max, y_max)
    return block_edges


def zoom(scale):
    global sides_list, filling_color, line_color, canvas_win, filled
    old_dots = dots
    clean_canvas()
    for ind, figure in enumerate(old_dots):
        if len(figure) > 0:
            for n, dot in enumerate(figure):
                center_x = canvas_win.winfo_width() / 2
                center_y = canvas_win.winfo_height() / 2
                x = int(scale * (dot[0] - center_x) + center_x)
                y = int(scale * (dot[1] - center_y) + center_y)
                if n < len(figure) - 1:
                    add_dot(x, y, True)
            close_figure()
    if filled:
        parse_fill()

def fill_click():
    start_time = time()
    parse_fill()
    end_time = time()
    time_win(start_time, end_time)

def parse_fill():
    global filled
    cur_figure = len(dots) - 1
    if len(dots[cur_figure]) != 0:
        messagebox.showerror("Ошибка", "Последняя фигура не замкнута")
        return
    block_edges = get_edges(dots)
    if option_filling.get() == 1:
        delay = True
    else:
        delay = False
    round_figure()
    fill_with_flag(sides_list, block_edges, filling_color, delay=delay)
    filled = True


def fill_with_flag(sides_list, block_edges, color_fill, delay=False):

    canvas_win.update()

    x_max = int(block_edges[2])
    x_min = int(block_edges[0])

    y_max = int(block_edges[3])
    y_min = int(block_edges[1])



    for y in range(y_min, y_max - 1, -1):
        flag = False

        for x in range(x_min, x_max + 2):

            if image_canvas.get(x, y) == TEMP_SIDE_COLOR_CHECK:
                flag = not flag

            if flag:
                image_canvas.put(color_fill, (x, y))
            else:
                image_canvas.put(CV_COLOR, (x, y))

        if delay:
            canvas_win.update()
            sleep(0.0001 * 1)

    # Sides
    for fig in sides_list:
        for side in fig:
            draw_line(side[0], side[1], line_color)



def time_win(start_time, end_time):
   top = Toplevel(win)
   top['bg'] = "#0000ff"
   top.geometry("250x150")
   top.title("Время закраскиw")
   Label(top, text="Время: %-3.2f с" % (end_time - start_time), bg="white", fg='black').place(x=40, y=30, relheight=0.5, relwidth=0.70)


# def time_win(start_time, end_time):
#     win = Tk()
#     win.title("Время закраски")
#     win['bg'] = "#0000ff"
#     win.geometry("265x200+630+100")
#     win.resizable(False, False)
#     time_label = Label(win, text="Время: %-3.2f с" % (end_time - start_time), bg="white", fg='black')
#     time_label.place(x=40, y=30, relheight=0.5, relwidth=0.70)
#     return win


def choose_line_color():
    global line_color
    line_color = colorchooser.askcolor()[1]


def choose_fill_color():
    global filling_color
    filling_color = colorchooser.askcolor()[1]


def show_task():
    messagebox.showinfo(title='Условие', message=TASK)


def clean_canvas():
    global dots
    global sides_list
    global image_canvas
    canvas_win.delete("all")
    image_canvas = PhotoImage(width=CV_WIDE, height=CV_HEIGHT)
    canvas_win.create_image((CV_WIDE / 2, CV_HEIGHT / 2), image=image_canvas, state="normal")
    canvas_win.place(x=0, y=0)
    dots = [[]]
    sides_list = [[]]
    dotslist_box.delete(0, END)


if __name__ == "__main__":
    win = Tk()
    win['bg'] = WIN_COLOR
    win.geometry("%dx%d" % (WIN_WIDTH, WIN_HEIGHT))
    win.title("Лабораторная работа №5. Реализация алгоритмов растрового заполнения")
    canvas_win = Canvas(win, width=CV_WIDE, height=CV_HEIGHT, background=WIN_COLOR)
    image_canvas = PhotoImage(width=CV_WIDE, height=CV_HEIGHT)
    canvas_win.create_image((CV_WIDE / 2, CV_HEIGHT / 2), image=image_canvas, state="normal")
    canvas_win.place(x=0, y=0)
    canvas_win.create_rectangle(1, 1, CV_WIDE-1, CV_HEIGHT-1)
    x_text = Label(text="x: ", bg=BOX_COLOR)
    x_text.place(x=CV_WIDE + 60, y=180)
    x_entry = Entry(width=15)
    x_entry.place(x=CV_WIDE + 80, y=180)
    y_text = Label(text="y: ", bg=BOX_COLOR)
    y_text.place(x=CV_WIDE + 240, y=180)
    y_entry = Entry(width=15)
    y_entry.place(x=CV_WIDE + 260, y=180)
    add_dot_btn = Button(win, text="Добавить точку", width=20, command=lambda: read_dot())
    add_dot_btn.place(x=CV_WIDE + 160, y=210)
    make_figure_btn = Button(win, text="Замкнуть фигуру", width=15, command=lambda: close_figure())
    make_figure_btn.place(x=CV_WIDE + 80, y=80)
    dots = [[]]
    sides_list = [[]]
    dots_list_text = Label(win, text="Список точек", width=43, bg=MAIN_TEXT_COLOR)
    dots_list_text.place(x=CV_WIDE + 185, y=20)
    dotslist_box = Listbox(bg="white")
    dotslist_box.configure(height=7, width=20)
    dotslist_box.place(x=CV_WIDE + 240, y=50)
    color_text = Label(win, text="Закраска", width=43, bg=MAIN_TEXT_COLOR)
    color_text.place(x=CV_WIDE + 50, y=250)
    option_filling = IntVar()
    option_filling.set(1)
    draw_delay = Radiobutton(text="С задержкой", variable=option_filling, value=1,
                             bg=BOX_COLOR, activebackground=BOX_COLOR, highlightbackground=BOX_COLOR)
    draw_delay.place(x=CV_WIDE + 110, y=270)
    draw_without_delay = Radiobutton(text="Без задержки", variable=option_filling,
                                     value=2, bg=BOX_COLOR, activebackground=BOX_COLOR, highlightbackground=BOX_COLOR)
    draw_without_delay.place(x=CV_WIDE + 260, y=270)
    fill_figure_btn = Button(win, text="Заполнить", width=20, command=lambda: fill_click())
    fill_figure_btn.place(x=CV_WIDE + 170, y=300)
    task_btn = Button(win, width=15, text="Условия задачи", command=lambda: show_task())
    task_btn.place(x=CV_WIDE + 80, y=140)
    clear_win_btn = Button(win, width=15, text="Очистить холст", command=lambda: clean_canvas())
    clear_win_btn.place(x=CV_WIDE + 80, y=110)
    color_text = Label(win, text="Цвет", width=15, bg=MAIN_TEXT_COLOR)
    color_text.place(x=CV_WIDE + 175, y=340)
    option_color = IntVar()
    option_color.set(1)
    line_color_btn = Button(win, width=15, text="линий", command=lambda: choose_line_color())
    line_color_btn.place(x=CV_WIDE + 80, y=360)
    fill_color_btn = Button(win, width=15, text="заливки", command=lambda: choose_fill_color())
    fill_color_btn.place(x=CV_WIDE + 280, y=360)
    canvas_win.bind_all("<MouseWheel>", zoomer)
    canvas_win.bind("<Button-4>", zoomer)
    canvas_win.bind("<Button-5>", zoomer)
    canvas_win.bind("<1>", add_dot_click)
    win.mainloop()

