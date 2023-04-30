import threading
from tkinter import *
from tkinter import messagebox, colorchooser
from const import *
from time import time, sleep


pressed = False
filling_color = FILL_COLOR
line_color = COLOR_LINE
filled = False
drawing = False
debounced_timer = None
debounced_scale = 1.0


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
    global drawing
    if not drawing:
        if event.delta > 0 or event.num == 4:
            debounce(0.1)(zoom)(1.1)
        elif event.delta < 0 or event.num == 5:
            debounce(0.1)(zoom)(0.9)


def zoom(scale):
    global edges, filling_color, line_color, canvas_win
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
        draw_edges_and_fill_figure()


def debounce(wait_time):
    global debounced_timer, debounced_scale

    def decorator(function):
        def debounced(*args, **kwargs):
            global debounced_timer, debounced_scale

            def call_function():
                global debounced_timer, debounced_scale
                debounced_timer = None
                scale = debounced_scale
                debounced_scale = 1.0
                canvas_win.after(1, function, scale)
            if debounced_timer is not None:
                debounced_scale = debounced_scale * args[0]
                debounced_timer.cancel()
            else:
                debounced_scale = args[0]
            debounced_timer = threading.Timer(wait_time, call_function)
            debounced_timer.start()
        debounced_timer = None
        return debounced
    return decorator


def clear_canvas():
    canvas_win.delete("all")


def draw_dot(x, y, color):
    image_canvas.put(color, (x, y))


def draw_line(point_one, point_two, color):
    canvas_win.create_line(point_one[0], point_one[1], point_two[0], point_two[1], fill=color)


def read_dot():
    try:
        x = float(x_entry.get())
        y = float(y_entry.get())
    except:
        messagebox.showerror("Ошибка", "Неверно введены координаты точки")
        return
    add_dot(int(x), int(y))


def click(event):
    x = event.x
    y = event.y
    add_dot(x, y)


def add_dot(x, y, last=True):
    global line_color
    cur_figure = len(dots) - 1
    dots[cur_figure].append([x, y])
    cur_dot = len(dots[cur_figure]) - 1
    if last:
        dots_list_box.insert(END, "%d. (%4d;%4d)" % (cur_dot + 1, x, y))
    if len(dots[cur_figure]) > 1:
        edges[cur_figure].append([dots[cur_figure][cur_dot - 1], dots[cur_figure][cur_dot]])
        draw_line(dots[cur_figure][cur_dot - 1], dots[cur_figure][cur_dot], line_color)


def close_figure():
    cur_figure = len(dots)
    cur_dot = len(dots[cur_figure - 1])
    if cur_dot < 3:
        messagebox.showerror("Ошибка", "Недостаточно точек, чтобы замкнуть фигуру")
    add_dot(dots[cur_figure - 1][0][0], dots[cur_figure - 1][0][1], last=False)
    dots.append(list())
    edges.append(list())
    dots_list_box.insert(END, "_______________________")


def find_line_coefficients(x1, y1, x2, y2):
    return y1 - y2, x2 - x1, x1 * y2 - x2 * y1


def find_dot_of_intersection(a1, b1, c1, a2, b2, c2):
    x = ((-c1) * b2 - b1 * (-c2)) / (a1 * b2 - a2 * b1)
    y = (a1 * (-c2) - (-c1) * a2) / (a1 * b2 - a2 * b1)
    return x, y


def draw_edge(point_one, point_two):
    if point_one[1] == point_two[1]:
        return
    sa, sb, sc = find_line_coefficients(point_one[0], point_one[1], point_two[0], point_two[1])
    if point_one[1] > point_two[1]:
        y_max, y_min, x = point_one[1], point_two[1], point_two[0]
    else:
        y_max, y_min, x = point_two[1], point_one[1], point_one[0]
    y = int(y_min)
    while y < y_max:
        a, b, c = find_line_coefficients(x, y, x + 1, y)
        x_intersection, y_intersection = find_dot_of_intersection(sa, sb, sc, a, b, c)
        if image_canvas.get(int(x_intersection) + 1, y) != TEMP_SIDE_COLOR_CHECK:
            image_canvas.put(TEMP_SIDE_COLOR, (int(x_intersection) + 1, y))
        else:
            image_canvas.put(TEMP_SIDE_COLOR, (int(x_intersection) + 2, y))
        y += 1
        canvas_win.update()


def draw_edges_of_figure():
    for figure in range(len(edges)):
        sides_amount = len(edges[figure]) - 1
        for side in range(sides_amount + 1):
            draw_edge(edges[figure][side][0], edges[figure][side][1])


def find_borders_of_area(dots):
    x_max = 0
    x_min = CV_WIDTH
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
    return x_max, x_min, y_max, y_min


def draw_edges_and_fill_figure():
    global filled, drawing
    drawing = True
    cur_figure = len(dots) - 1
    if len(dots[cur_figure]) != 0:
        messagebox.showerror("Ошибка", "Последняя фигура не замкнута")
        return
    if option.get() == 1:
        delay = True
    else:
        delay = False
    draw_edges_of_figure()
    fill_with_flag(edges, filling_color, delay=delay)
    filled = True
    drawing = False


def fill_with_flag(edges, color_fill, delay=False):
    canvas_win.update()
    x_max, x_min, y_max, y_min = find_borders_of_area(dots)
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
    for fig in edges:
        for side in fig:
            draw_line(side[0], side[1], line_color)


def choose_line_color():
    global line_color
    line_color = colorchooser.askcolor()[1]


def choose_fill_color():
    global filling_color
    filling_color = colorchooser.askcolor()[1]


def fill_click():
    global filling_color
    start_time = time()
    draw_edges_and_fill_figure()
    end_time = time()
    measure_fill_time(start_time, end_time, filling_color)


def show_task():
    messagebox.showinfo(title='Условие', message=TASK)


def measure_fill_time(start_time, end_time, color):
   top = Toplevel(win)
   top['bg'] = color
   top.geometry("250x150")
   top.title("Время закраски")
   Label(top, text="Время: %-3.2f с" % (end_time - start_time), bg="white", fg='black').place(x=40, y=30, relheight=0.5, relwidth=0.70)


def clean_canvas():
    global dots
    global edges
    global image_canvas
    canvas_win.delete("all")
    image_canvas = PhotoImage(width=CV_WIDTH, height=CV_HEIGHT)
    canvas_win.create_image((CV_WIDTH / 2, CV_HEIGHT / 2), image=image_canvas, state="normal")
    canvas_win.place(x=0, y=0)
    dots = [[]]
    edges = [[]]
    dots_list_box.delete(0, END)


if __name__ == "__main__":
    win = Tk()
    win['bg'] = WIN_COLOR
    win.geometry("%dx%d" % (WIN_WIDTH, WIN_HEIGHT))
    win.title("Лабораторная работа №5. Растровое заполнение")
    canvas_win = Canvas(win, width=CV_WIDTH, height=CV_HEIGHT, background=WIN_COLOR)
    image_canvas = PhotoImage(width=CV_WIDTH, height=CV_HEIGHT)
    canvas_win.create_image((CV_WIDTH / 2, CV_HEIGHT / 2), image=image_canvas, state="normal")
    canvas_win.place(x=0, y=0)
    canvas_win.create_rectangle(1, 1, CV_WIDTH-1, CV_HEIGHT-1)
    x_text = Label(text="x: ", bg=BOX_COLOR)
    x_text.place(x=CV_WIDTH + 60, y=180)
    x_entry = Entry(width=15)
    x_entry.place(x=CV_WIDTH + 80, y=180)
    y_text = Label(text="y: ", bg=BOX_COLOR)
    y_text.place(x=CV_WIDTH + 240, y=180)
    y_entry = Entry(width=15)
    y_entry.place(x=CV_WIDTH + 260, y=180)
    add_dot_btn = Button(win, text="Добавить точку", width=20, command=lambda: read_dot())
    add_dot_btn.place(x=CV_WIDTH + 160, y=210)
    make_figure_btn = Button(win, text="Замкнуть фигуру", width=15, command=lambda: close_figure())
    make_figure_btn.place(x=CV_WIDTH + 80, y=80)
    dots = [[]]
    edges = [[]]
    dots_list_text = Label(win, text="Список точек", width=43, bg=MAIN_TEXT_COLOR)
    dots_list_text.place(x=CV_WIDTH + 185, y=20)
    dots_list_box = Listbox(bg="white")
    dots_list_box.configure(height=7, width=20)
    dots_list_box.place(x=CV_WIDTH + 240, y=50)
    color_text = Label(win, text="Закраска", width=43, bg=MAIN_TEXT_COLOR)
    color_text.place(x=CV_WIDTH + 50, y=250)
    option = IntVar()
    option.set(1)
    draw_delay = Radiobutton(text="С задержкой", variable=option, value=1,
                             bg=BOX_COLOR, activebackground=BOX_COLOR, highlightbackground=BOX_COLOR)
    draw_delay.place(x=CV_WIDTH + 110, y=270)
    draw_without_delay = Radiobutton(text="Без задержки", variable=option,
                                     value=2, bg=BOX_COLOR, activebackground=BOX_COLOR, highlightbackground=BOX_COLOR)
    draw_without_delay.place(x=CV_WIDTH + 260, y=270)
    task_btn = Button(win, width=15, text="Условия задачи", command=lambda: show_task())
    task_btn.place(x=CV_WIDTH + 80, y=140)
    fill_figure_btn = Button(win, text="Закрасить", width=20, command=lambda: fill_click())
    fill_figure_btn.place(x=CV_WIDTH + 170, y=300)
    clear_win_btn = Button(win, width=15, text="Очистить холст", command=lambda: clean_canvas())
    clear_win_btn.place(x=CV_WIDTH + 80, y=110)
    color_text = Label(win, text="Цвет", width=15, bg=MAIN_TEXT_COLOR)
    color_text.place(x=CV_WIDTH + 175, y=340)
    option_color = IntVar()
    option_color.set(1)
    line_color_btn = Button(win, width=15, text="линий", command=lambda: choose_line_color())
    line_color_btn.place(x=CV_WIDTH + 80, y=360)
    fill_color_btn = Button(win, width=15, text="заливки", command=lambda: choose_fill_color())
    fill_color_btn.place(x=CV_WIDTH + 280, y=360)
    canvas_win.bind_all("<MouseWheel>", zoomer)
    canvas_win.bind("<Button-4>", zoomer)
    canvas_win.bind("<Button-5>", zoomer)
    canvas_win.bind("<1>", click)
    win.mainloop()
