from tkinter import messagebox, ttk, colorchooser, PhotoImage
from tkinter import *
import colorutils as cu
import threading
WIN_WIDTH = 1200
WIN_HEIGHT = 800

SIZE = 800
WIDTH = 100.0

TASK = "Метод Сазерленда-Коэна" \
        "\nШадрин Илья ИУ7-44 "\
       ""


# координаты точки из канвасовских в фактические
def to_coords(dot):
    return [(dot[0] - coord_center[0]) * m_board, (-dot[1] + coord_center[1]) * m_board]


# координаты точки из фактических в канвасовские
def to_canvas(dot):
    return [coord_center[0] + dot[0] / m_board, coord_center[1] - dot[1] / m_board]


# нарисовать отрезок
def draw_line():
    color = cu.Color(line_color[1])
    try:
        dot1 = to_canvas([int(x1_entry.get()), int(y1_entry.get())])
        dot2 = to_canvas([int(x2_entry.get()), int(y2_entry.get())])
    except ValueError:
        messagebox.showerror("Ошибка", "Некорректные координаты отрезка")
        return

    sides.append([dot1, dot2])
    history.append([dot1, dot2, 'line'])

    canvas_win.delete('lineHelper')
    canvas_win.create_line(dot1, dot2, fill=color, tag='line')


# нарисовать отсекатель
def draw_clipper():
    global clipper_coords
    canvas_win.delete('clipper', 'lineHelper')
    color = cu.Color(clipper_color[1])

    dot1 = to_canvas([int(x1_clipper_entry.get()), int(y1_clipper_entry.get())])
    dot2 = to_canvas([int(x2_clipper_entry.get()), int(y2_clipper_entry.get())])

    clipper_coords = [dot1, dot2]
    history.append([dot1, dot2, 'rectangle'])

    canvas_win.create_rectangle(dot1, dot2, outline=color, tag='clipper')


# отрисовка и вставка в листбокс добавленной точки
def draw_point(ev_x, ev_y, click_):
    global option_line, line_coords, clipper_coords, click_flag, start_line

    if click_:
        x, y = ev_x, ev_y
    else:
        x, y = to_canvas([ev_x, ev_y])

    x_y = to_coords([x, y])

    if click_flag == 1:
        start_line = [x, y]

    if option_line.get() == 0:
        if click_flag == 1:
            start_line = [x, y]

            x1_entry.delete(0, END)
            y1_entry.delete(0, END)
            x1_entry.insert(0, "%d" % x_y[0])
            y1_entry.insert(0, "%d" % x_y[1])
            canvas_win.delete('dot1')
            canvas_win.create_oval(x - 2, y - 2, x + 2, y + 2,
                                   outline='lightgreen', fill='lightgreen', activeoutline='pink', width=2, tag='dot1')

        if click_flag == 2:
            x2_entry.delete(0, END)
            y2_entry.delete(0, END)
            x2_entry.insert(0, "%d" % x_y[0])
            y2_entry.insert(0, "%d" % x_y[1])
            canvas_win.delete('dot2')
            canvas_win.create_oval(x - 2, y - 2, x + 2, y + 2,
                                   outline='lightgreen', fill='lightgreen', activeoutline='pink', width=2, tag='dot2')
            draw_line()

    elif option_line.get() == 1:
        if click_flag == 1:
            start_line = [x, y]
            x1_clipper_entry.delete(0, END)
            y1_clipper_entry.delete(0, END)
            x1_clipper_entry.insert(0, "%d" % x_y[0])
            y1_clipper_entry.insert(0, "%d" % x_y[1])
            canvas_win.delete('clipper1')
            canvas_win.create_oval(x - 2, y - 2, x + 2, y + 2,
                                   outline='pink', fill='pink', activeoutline='lightgreen', width=2, tag='clipper1')
        if click_flag == 2:
            x2_clipper_entry.delete(0, END)
            y2_clipper_entry.delete(0, END)
            x2_clipper_entry.insert(0, "%d" % x_y[0])
            y2_clipper_entry.insert(0, "%d" % x_y[1])
            canvas_win.delete('clipper2')
            canvas_win.create_oval(x - 2, y - 2, x + 2, y + 2,
                                   outline='pink', fill='pink', activeoutline='lightgreen', width=2, tag='clipper2')
            draw_clipper()


def get_dot_bits(clipper, dot):
    bits = 0b0000

    if dot[0] < clipper[0]:
        bits += 0b0001

    if dot[0] > clipper[1]:
        bits += 0b0010

    if dot[1] < clipper[2]:
        bits += 0b0100

    if dot[1] > clipper[3]:
        bits += 0b1000

    return bits


def check_visible(dot1_bits, dot2_bits):
    vision = 0  # частично видимый

    if dot1_bits == 0 and dot2_bits == 0:
        vision = 1  # видим
    elif dot1_bits & dot2_bits:
        vision = -1  # не видим

    return vision


def are_bits_equal(dot1_bits, dot2_bits, i):
    if (dot1_bits >> i) & 1 == (dot2_bits >> i) & 1:
        return True
    return False


def method_by_variant(clipper, line):
    dot1 = [line[0][0], line[0][1]]
    dot2 = [line[1][0], line[1][1]]

    fl = 0

    if dot1[0] == dot2[0]:
        fl = -1  # вертикальный
    else:
        m = (dot2[1] - dot1[1]) / (dot2[0] - dot1[0])

        if m == 0:
            fl = 1  # горизонтальный

    for i in range(4):
        dot1_bits = get_dot_bits(clipper, dot1)
        dot2_bits = get_dot_bits(clipper, dot2)

        vision = check_visible(dot1_bits, dot2_bits)

        if vision == -1:
            return  # выйти и не рисовать
        elif vision == 1:
            break  # нарисовать и выйти

        if are_bits_equal(dot1_bits, dot2_bits, i):
            continue

        if (dot1_bits >> i) & 1 == 0:
            tmp = dot1
            dot1 = dot2
            dot2 = tmp

        if fl != -1:  # если отрезок не вертикальный
            if i < 2:  # работаем с правой и левой сторонами
                dot1[1] = m * (clipper[i] - dot1[0]) + dot1[1]
                dot1[0] = clipper[i]
                continue
            else:  # работаем с нижней и верхней сторонами
                dot1[0] = (1 / m) * (clipper[i] - dot1[1]) + dot1[0]

        dot1[1] = clipper[i]

    res_color = cu.Color(result_color[1])
    canvas_win.create_line(dot1, dot2, fill=res_color, tag='result')


# отсечь
def cut_off_area():
    global clipper_coords

    if len(clipper_coords) < 1:
        messagebox.showinfo("Ошибка", "Не задан отсекатель")
        return

    if len(sides) < 1:
        messagebox.showinfo("Ошибка", "Не задан ни один отрезок")
        return

    clipper = [min(clipper_coords[0][0], clipper_coords[1][0]), max(clipper_coords[0][0], clipper_coords[1][0]),
               min(clipper_coords[0][1], clipper_coords[1][1]), max(clipper_coords[0][1], clipper_coords[1][1])]

    for line in sides:
        method_by_variant(clipper, line)


# определение и запись координат точки по клику
def click(event):
    global click_flag
    if event.x < 0 or event.x > WIN_WIDTH * win_k or event.y < 0 or event.y > WIN_HEIGHT * win_k:
        return

    if click_flag == 0:
        click_flag = 1
    elif click_flag == 1:
        click_flag = 2
    elif click_flag == 2:
        click_flag = 1

    draw_point(event.x, event.y, 1)


def draw_all():
    color_line = cu.Color(line_color[1])
    color_clipper = cu.Color(clipper_color[1])
    for figure in history:
        if figure[2] == 'line':
            canvas_win.create_line(figure[0], figure[1], fill=color_line, tag='line')
        elif figure[2] == 'rectangle':
            canvas_win.create_rectangle(figure[0], figure[1], outline=color_clipper, tag='clipper')


# изменение цвета отрезка, результата или отсекателя
def choose_color_line():
    global line_color
    line_color = colorchooser.askcolor()


def choose_color_result():
    global result_color
    result_color = colorchooser.askcolor()


def choose_color_clipper():
    global clipper_color
    clipper_color = colorchooser.askcolor()


#  очистка канваса
def clean_canvas():
    global canvas_color, history, sides, clipper_coords

    history = []
    sides = []
    clipper_coords = []
    canvas_win.delete('line', 'dot1', 'dot2', 'clipper1', 'clipper2', 'clipper', 'result')
    canvas_color = ((255, 255, 255), "#ffffff")
    canvas_win.configure(bg=cu.Color(canvas_color[1]))


# модификация окна
def config(event):
    if event.widget == win:
        global win_x, win_y, win_k, m, size, coord_center
        win_x = win.winfo_width()/WIN_WIDTH
        win_y = (win.winfo_height() + 35)/WIN_HEIGHT
        win_k = min(win_x, win_y)
        size = SIZE * win_k
        m = size / (2 * border + ten_percent)
        coord_center = [size / 2, size / 2]
        canvas_win.place(x=0, y=0, width=size, height=size)
        canvas_win.create_image((WIN_WIDTH / 2, WIN_HEIGHT / 2), image=image_canvas, state="normal")
        line_lbl.place(x=size+30+40+30, y=108, width=237, height=24)
        x1_lbl.place(x=size+30+40+10, y=135, width=30, height=18)
        y1_lbl.place(x=size+156+40+10+15, y=135, width=30, height=18)
        x1_entry.place(x=size+62+40, y=135, width=80+30, height=28)
        y1_entry.place(x=size+188+40+15, y=135, width=80+30, height=28)
        x2_lbl.place(x=size+30+40+10, y=162, width=30, height=18)
        y2_lbl.place(x=size+156+40+10+15, y=162, width=30, height=18)
        x2_entry.place(x=size+62+40, y=162, width=80+30, height=28)
        y2_entry.place(x=size+188+40+15, y=162, width=80+30, height=28)
        add_line.place(x=size+30+40, y=190, width=235+70, height=28)
        point1_radio.place(x=size+30+40+50, y=108)
        clipper_lbl.place(x=size+30+40+30, y=250, width=237, height=24)
        x1_clipper_lbl.place(x=size+30+40+10, y=282, width=30, height=18)
        y1_clipper_lbl.place(x=size+156+40+10+15, y=282, width=30, height=18)
        x1_clipper_entry.place(x=size+62+40, y=282, width=80+30, height=28)
        y1_clipper_entry.place(x=size+188+40+15, y=282, width=80+30, height=28)
        x2_clipper_lbl.place(x=size+30+40+10, y=304, width=30, height=18)
        y2_clipper_lbl.place(x=size+156+40+10+15, y=304, width=30, height=18)
        x2_clipper_entry.place(x=size+62+40, y=304, width=80+30, height=28)
        y2_clipper_entry.place(x=size+188+40+15, y=304, width=80+30, height=28)
        add_clipper.place(x=size+30+40, y=327+10, width=235+70, height=28)
        clipper1_radio.place(x=size+30+40+40, y=250)
        color_lbl.place(x=size+10, y=390, width=237, height=24)
        clipper_clr.place(x=size+30+40, y=417, width=111, height=25)
        line_clr.place(x=size+30+40, y=443, width=111, height=25)
        result_clr.place(x=size+30+40, y=469, width=111, height=25)
        bld.place(x=size+157+40, y=417, width=235, height=28)
        con.place(x=size+157+40, y=447, width=235, height=28)
        bgn.place(x=size+157+40, y=477, width=235, height=28)
        canvas_win.delete('all')


win = Tk()
win['bg'] = 'white'
win.geometry("%dx%d" % (WIN_WIDTH, WIN_HEIGHT))
win.title("Лабораторная работа №7. Реализация алгоритма отсечения отрезка регулярным отсекателем.")
color_lbl = Label(text="Цвет", bg='white', fg='black')
clipper_clr = Button(text="отсекателя", borderwidth=0, command=lambda: choose_color_clipper())
line_clr = Button(text="отрезка", borderwidth=0, command=lambda: choose_color_line())
result_clr = Button(text="результата", borderwidth=0, command=lambda: choose_color_result())
clipper_color = ((0, 0, 0), "#000000")  # черный
line_color = ((253, 189, 186), "#fdbdba")  # розовый
canvas_color = ((255, 255, 255), "#ffffff")  # белый
result_color = ((147, 236, 148), "#93ec94")  # светло-зеленый
canvas_win = Canvas(win, bg=cu.Color(canvas_color[1]))
image_canvas = PhotoImage(width=WIN_WIDTH, height=WIN_HEIGHT)
win.bind("<Configure>", config)
canvas_win.bind('<1>', click)
option_line = IntVar()
option_line.set(0)
line_lbl = Label(text="Координаты отрезка", bg='white', fg='black')
x1_lbl = Label(text="X", bg='white', fg='black')
y1_lbl = Label(text="Y", bg='white', fg='black')
x1_entry = Entry()
y1_entry = Entry()
x2_lbl = Label(text="X", bg='white', fg='black')
y2_lbl = Label(text="Y", bg='white', fg='black')
x2_entry = Entry()
y2_entry = Entry()
add_line = Button(text="Добавить отрезок", borderwidth=0, command=lambda: draw_line())
point1_radio = Radiobutton(variable=option_line, value=0, bg="white")
clipper_lbl = Label(text="Координаты отсекателя", bg='white', fg='black')
x1_clipper_lbl = Label(text="X", bg='white', fg='black')
y1_clipper_lbl = Label(text="Y", bg='white', fg='black')
x1_clipper_entry = Entry()
y1_clipper_entry = Entry()
x2_clipper_lbl = Label(text="X", bg='white', fg='black')
y2_clipper_lbl = Label(text="Y", bg='white',  fg='black')
x2_clipper_entry = Entry()
y2_clipper_entry = Entry()
add_clipper = Button(text="Начертить отсекатель", borderwidth=0, command=lambda: draw_clipper())
clipper1_radio = Radiobutton(variable=option_line, value=1, bg="white")
bld = Button(text="Отсечь", borderwidth=0, command=lambda: cut_off_area())
con = Button(text="Условие задачи", borderwidth=0, command=lambda: messagebox.showinfo("Задание", TASK))
bgn = Button(text="Очистить холст",  borderwidth=0, command=lambda: clean_canvas())
line_coords = []
clipper_coords = []
history = []
sides = []
clippers = []
click_flag = 0  # был ли клик
start_line = []
win_x = win_y = 1  # коэффициенты масштабирования окна по осям
win_k = 1  # коэффициент масштабирования окна (для квадратизации)
size = SIZE  # текущая длина/ширина (они равны) канваса
border = WIDTH  # граница (максимальная видимая координата на канвасе)
ten_percent = 0  # 10% от величины границы
m = size * win_k / border  # коэффициент масштабирования канваса
coord_center = [400, 400]  # центр координат (в координатах канваса)
m_board = 1  # коэффициент масштабирования при изменении масштаба канваса
xy_current = [-400, -350, -300, -250, -200, -150, -100, -50,
              0, 50, 100, 150, 200, 250, 300, 350, 400]
win.mainloop()
