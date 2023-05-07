from tkinter import messagebox, ttk, colorchooser, PhotoImage
from tkinter import *
import colorutils as cu

WIN_WIDTH = 1200
WIN_HEIGHT = 800

SIZE = 800
WIDTH = 100.0

TASK = "Метод Сазерленда-Коэна" \
        "\nШадрин Илья ИУ7-44 "\
       ""

# координаты точки из канвасовских в фактические
def to_coords(dot):
    x = (dot[0] - coord_center[0]) * m_board
    y = (-dot[1] + coord_center[1]) * m_board

    return [x, y]


# координаты точки из фактических в канвасовские
def to_canva(dot):
    x = coord_center[0] + dot[0] / m_board
    y = coord_center[1] - dot[1] / m_board

    return [x, y]


# нарисовать отрезок
def draw_line():
    color = cu.Color(line_color[1])
    try:
        dot1 = to_canva([int(x1_entry.get()), int(y1_entry.get())])
        dot2 = to_canva([int(x2_entry.get()), int(y2_entry.get())])
    except ValueError:
        messagebox.showerror("Ошибка", "Некорректные координаты отрезка")
        return

    lines.append([dot1, dot2])
    history.append([dot1, dot2, 'line'])

    canvas_win.delete('lineHelper')
    canvas_win.create_line(dot1, dot2, fill=color, tag='line')


# нарисовать отсекатель
def draw_clipper():
    global clipper_coords
    canvas_win.delete('clipper', 'lineHelper')
    color = cu.Color(clipper_color[1])

    dot1 = to_canva([int(x1_clipper_entry.get()), int(y1_clipper_entry.get())])
    dot2 = to_canva([int(x2_clipper_entry.get()), int(y2_clipper_entry.get())])

    clipper_coords = [dot1, dot2]
    history.append([dot1, dot2, 'rectangle'])

    canvas_win.create_rectangle(dot1, dot2, outline=color, tag='clipper')


# отрисовка и вставка в листбокс добавленной точки
def draw_point(ev_x, ev_y, click_):
    global option_line, line_coords, clipper_coords, click_flag, start_line

    if click_:
        x, y = ev_x, ev_y
    else:
        x, y = to_canva([ev_x, ev_y])

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


def get_bit(dot_bits, i):
    return (dot_bits >> i) & 1


def are_bits_equal(dot1_bits, dot2_bits, i):
    if get_bit(dot1_bits, i) == get_bit(dot2_bits, i):
        return True

    return False


def method_sazerland_kohen(clipper, line):
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

        if get_bit(dot1_bits, i) == 0:
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


def cut_area_with_enter(event):
    cut_area()


# отсечь
def cut_area():
    global clipper_coords

    if len(clipper_coords) < 1:
        messagebox.showinfo("Ошибка", "Не задан отсекатель")
        return

    if len(lines) < 1:
        messagebox.showinfo("Ошибка", "Не задан ни один отрезок")
        return

    clipper = [min(clipper_coords[0][0], clipper_coords[1][0]), max(clipper_coords[0][0], clipper_coords[1][0]),
               min(clipper_coords[0][1], clipper_coords[1][1]), max(clipper_coords[0][1], clipper_coords[1][1])]

    for line in lines:
        method_sazerland_kohen(clipper, line)


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


# изменение цвета фона
def change_bg_color():
    global canvas_color
    canvas_color = colorchooser.askcolor()
    canvas_win.configure(bg=cu.Color(canvas_color[1]))


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


# при нажатии буквы w / s будет переключать радиобаттон (для быстрого задания концов отрезка или отсекателя)
def change_option_click_down(event):
    global option_line

    current_position = option_line.get()
    option_line.set((current_position + 1) % 2)


def change_option_click_up(event):
    global option_line

    current_position = option_line.get()
    option_line.set((current_position - 1) % 2)


# определить крайний отсекатель для ундо
def find_rectangle(history):
    for i in range(len(history) - 1, -1, -1):
        if history[i][2] == 'rectangle':
            return history[0:2]

    return []


#  отчистака канваса
def clean_canvas():
    global canvas_color, history, lines, clipper_coords

    history = []
    lines = []
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

        canvas_win.place(x=300 * win_x, y=0 * win_y, width=size, height=size)
        canvas_win.create_image((WIN_WIDTH / 2, WIN_HEIGHT / 2), image=image_canvas, state="normal")

        info_lbl.place(x=30 * win_x, y=17 * win_y, width=237 * win_x, height=65 * win_y)

        # координаты отрезка
        line_lbl.place(x=30 * win_x, y=108 * win_y, width=237 * win_x, height=24 * win_y)

        x1_lbl.place(x=30 * win_x, y=140 * win_y, width=30 * win_x, height=18 * win_y)
        y1_lbl.place(x=156 * win_x, y=140 * win_y, width=30 * win_x, height=18 * win_y)
        x1_entry.place(x=62 * win_x, y=140 * win_y, width=80 * win_x, height=20 * win_y)
        y1_entry.place(x=188 * win_x, y=140 * win_y, width=80 * win_x, height=20 * win_y)

        x2_lbl.place(x=30 * win_x, y=162 * win_y, width=30 * win_x, height=18 * win_y)
        y2_lbl.place(x=156 * win_x, y=162 * win_y, width=30 * win_x, height=18 * win_y)
        x2_entry.place(x=62 * win_x, y=162 * win_y, width=80 * win_x, height=20 * win_y)
        y2_entry.place(x=188 * win_x, y=162 * win_y, width=80 * win_x, height=20 * win_y)

        add_line.place(x=30 * win_x, y=185 * win_y, width=237 * win_x, height=25 * win_y)

        point1_radio.place(x=3 * win_x, y=108 * win_y)


        # координаты отсекателя
        clipper_lbl.place(x=30 * win_x, y=250 * win_y, width=196 * win_x, height=24 * win_y)

        x1_clipper_lbl.place(x=30 * win_x, y=282 * win_y, width=30 * win_x, height=18 * win_y)
        y1_clipper_lbl.place(x=156 * win_x, y=282 * win_y, width=30 * win_x, height=18 * win_y)
        x1_clipper_entry.place(x=62 * win_x, y=282 * win_y, width=80 * win_x, height=20 * win_y)
        y1_clipper_entry.place(x=188 * win_x, y=282 * win_y, width=80 * win_x, height=20 * win_y)

        x2_clipper_lbl.place(x=30 * win_x, y=304 * win_y, width=30 * win_x, height=18 * win_y)
        y2_clipper_lbl.place(x=156 * win_x, y=304 * win_y, width=30 * win_x, height=18 * win_y)
        x2_clipper_entry.place(x=62 * win_x, y=304 * win_y, width=80 * win_x, height=20 * win_y)
        y2_clipper_entry.place(x=188 * win_x, y=304 * win_y, width=80 * win_x, height=20 * win_y)

        add_clipper.place(x=30 * win_x, y=327 * win_y, width=237 * win_x, height=25 * win_y)

        clipper1_radio.place(x=3 * win_x, y=250 * win_y)

        info_clipper.place(x=228 * win_x, y=250 * win_y, width=40 * win_x, height=24 * win_y)


        # цвет фона, отсекателя, отрезка и результата
        color_lbl.place(x=30 * win_x, y=390 * win_y, width=237 * win_x, height=24 * win_y)

        bg_clr.place(x=30 * win_x, y=417 * win_y, width=111 * win_x, height=25 * win_y)
        clipper_clr.place(x=155 * win_x, y=417 * win_y, width=111 * win_x, height=25 * win_y)
        line_clr.place(x=30 * win_x, y=443 * win_y, width=111 * win_x, height=25 * win_y)
        result_clr.place(x=155 * win_x, y=443 * win_y, width=111 * win_x, height=25 * win_y)

        # отсечь
        bld.place(x=30 * win_x, y=500 * win_y, width=235 * win_x, height=32 * win_y)
        # условие
        con.place(x=30 * win_x, y=650 * win_y, width=235 * win_x, height=28 * win_y)
        # к начальным условиям
        bgn.place(x=157 * win_x, y=680 * win_y, width=109 * win_x, height=28 * win_y)
        canvas_win.delete('all')


# Окно tkinter
win = Tk()
win['bg'] = 'white'
win.geometry("%dx%d" % (WIN_WIDTH, WIN_HEIGHT))
win.title("Лабораторная работа №7. Реализация алгоритма отсечения отрезка регулярным отсекателем.")


# Цвета
color_lbl = Label(text="Цвет", bg='pink', font="AvantGardeC 14", fg='black')
bg_clr = Button(text="фона", borderwidth=0, command=lambda: change_bg_color())
clipper_clr = Button(text="отсекателя", borderwidth=0, command=lambda: choose_color_clipper())
line_clr = Button(text="отрезка", borderwidth=0, command=lambda: choose_color_line())
result_clr = Button(text="результата", borderwidth=0, command=lambda: choose_color_result())

clipper_color = ((0, 0, 0), "#000000")  # черный
line_color = ((253, 189, 186), "#fdbdba")  # розовый
canvas_color = ((255, 255, 255), "#ffffff")  # белый
result_color = ((147, 236, 148), "#93ec94")  # светло-зеленый


# Канвас
canvas_win = Canvas(win, bg=cu.Color(canvas_color[1]))
image_canvas = PhotoImage(width=WIN_WIDTH, height=WIN_HEIGHT)
win.bind("<Configure>", config)
canvas_win.bind('<1>', click)
win.bind('s', change_option_click_down)
win.bind('w', change_option_click_up)
win.bind("<Return>", cut_area_with_enter)


# выбор поля, куда вводятся координаты точки, которую тыкнули
option_line = IntVar()
option_line.set(0)


# информация о клавишах
INFO = "Нажмите Enter, чтобы отсечь"
info_lbl = Label(text=INFO, fg='grey', bg='lightgrey')

# отрезок
line_lbl = Label(text="Координаты отрезка", bg='pink', fg='black')
x1_lbl = Label(text="X", bg='lightgrey', fg='black')
y1_lbl = Label(text="Y", bg='lightgrey', fg='black')
x1_entry = Entry(bg='white', fg='black', borderwidth=0, insertbackground='black', justify='center')
y1_entry = Entry(bg='white', fg='black', borderwidth=0, insertbackground='black', justify='center')

x2_lbl = Label(text="X", bg='lightgrey', fg='black')
y2_lbl = Label(text="Y", bg='lightgrey', fg='black')
x2_entry = Entry(bg='white', fg='black', borderwidth=0, insertbackground='black', justify='center')
y2_entry = Entry(bg='white', fg='black', borderwidth=0, insertbackground='black', justify='center')
add_line = Button(text="Добавить отрезок", borderwidth=0, command=lambda: draw_line())
point1_radio = Radiobutton(variable=option_line, value=0, bg="grey", activebackground="grey", highlightbackground="grey")


# отсекатель
clipper_lbl = Label(text="Координаты отсекателя", bg='pink', fg='black')
x1_clipper_lbl = Label(text="X", bg='lightgrey', fg='black')
y1_clipper_lbl = Label(text="Y", bg='lightgrey', fg='black')
x1_clipper_entry = Entry(bg='white', fg='black', borderwidth=0, insertbackground='black', justify='center')
y1_clipper_entry = Entry(bg='white', fg='black', borderwidth=0, insertbackground='black', justify='center')
x2_clipper_lbl = Label(text="X", bg='lightgrey', fg='black')
y2_clipper_lbl = Label(text="Y", bg='lightgrey',  fg='black')
x2_clipper_entry = Entry(bg='white', fg='black', borderwidth=0, insertbackground='black', justify='center')
y2_clipper_entry = Entry(bg='white', fg='black',  borderwidth=0, insertbackground='black', justify='center')
add_clipper = Button(text="Начертить отсекатель", borderwidth=0, command=lambda: draw_clipper())
clipper1_radio = Radiobutton(variable=option_line, value=1, bg="grey", activebackground="grey", highlightbackground="grey")

INFO_CLIPPER = 'Регулярный отсекатель задается по двум точкам: ' \
               'верхней левой и нижней правой или верхней правой и нижней левой'
info_clipper = Button(text="?", borderwidth=0, command=lambda: messagebox.showinfo("Отсекатель", INFO_CLIPPER))


line_coords = []
clipper_coords = []
history = []

lines = []
clippers = []

click_flag = 0  # был ли клик
start_line = []


# Кнопки
bld = Button(text="Отсечь", borderwidth=0, command=lambda : cut_area())
con = Button(text="Условие задачи", borderwidth=0, command=lambda: messagebox.showinfo("Задание", TASK))
bgn = Button(text="Сброс",  borderwidth=0, command=lambda: clean_canvas())


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
