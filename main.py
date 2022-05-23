# coding=UTF-8
from tkinter import *
from random import *
from time import *
from _thread import *
from getmap import *
import queue


def game_time():
    t = 0
    while not Cube.end and not Cube.is_new and not Cube.is_again:
        Cube.up_canvas.itemconfig(Cube.timer.text, text=t)
        t += 1
        sleep(1)


class Cube:
    state = 0  # 0 准备中 1 可以操作
    odd = 0  # 配色方案
    setting_window = None  # 设置窗口
    is_setting = 0  # 0 空闲 1 设置中
    space = False  # 按下空格
    hold_on = False  # 一次操作中

    up_canvas = None  # 上方画布
    main_canvas = None  # 主画布
    up_height = 130  # 主画布上方高度
    margin = 20  # 页面边缘留白
    height = 0  # 主画布高度 (不含留白，下同)
    height_scale = 1.0  # 地图高度 / 主画布高度
    width = 0  # 主画布宽度
    width_scale = 1.0  # 地图宽度 / 主画布宽度
    scale = 1  # penrose tiling的相对尺寸
    offset = (0, 0)  # penrose tiling的位置偏移

    v1 = 0  # 可变字符串
    v2 = 0
    v3 = 0

    mine = 60  # 雷数
    mine1 = 0  # 用户设置的雷数
    num = 0  # 格子数
    flag_number = 0  # 场上旗子数
    known = 0  # 已知格数
    index = []  # 所有格子列表
    mine_list = []  # 雷格列表
    safe_list = []  # 安全格列表
    wrong_list = []  # 判断失误格（标旗错误）列表
    is_new = True  # 本局是新生成的
    is_again = False  # 本局是重新开始上一局
    end = False  # 一局游戏是否结束
    first_click = None  # 新游戏第一次点开的格子
    bomb_mine = 0  # 直接点击导致输局的雷
    color = ['blue', 'green', 'red', 'purple', 'brown', 'cyan', 'white', 'gray']  # 数字颜色列表

    counter = None  # 雷数计数器
    timer = None  # 计时器
    face = None  # 笑脸
    genMap = None  # 地图生成器

    def __init__(self, a, b, c, d):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.center = ((a[0] + c[0]) * 0.5, (a[1] + c[1]) * 0.5)
        if (a[0] - c[0]) ** 2 + (a[1] - c[1]) ** 2 < (b[0] - d[0]) ** 2 + (b[1] - d[1]) ** 2:
            self.type = 0  # 瘦菱形
            if Cube.odd % 2:
                self.colorup = '#6bc235'
                self.colordown = '#fc9d9a'
            else:
                self.colorup = '#5ca7ba'
                self.colordown = '#fbb217'
        else:
            self.type = 1  # 胖菱形
            if Cube.odd % 2:
                self.colorup = '#aedd35'
                self.colordown = '#f9cdad'
            else:
                self.colorup = '#a7dce0'
                self.colordown = '#edde8b'
        self.neighbors = []  # 周围格列表
        self.number = -2  # 格子数字
        self.is_unknown = True  # 格子是否未知
        self.neighbor_flag_number = 0  # 格子周围格标旗数
        self.rhombus = Cube.main_canvas.create_polygon(self.a, self.b, self.c, self.d, fill=self.colordown,
                                                       outline='white',
                                                       width=4)  # 定位菱形
        self.text = Cube.main_canvas.create_text(self.center, text='', anchor=CENTER)  # 格子数字文本
        self.mine = self.create_mine(self.center[0], self.center[1], Cube.scale * 2)  # 雷
        self.x = self.create_x(Cube.scale * 2)  # 叉
        self.rect = Cube.main_canvas.create_polygon(self.a, self.b, self.c, self.d, fill=self.colorup,
                                                    outline='white', width=4)  # 盖子菱形
        self.flag = self.create_flag(self.center[0], self.center[1], Cube.scale * 2)  # 格子上的红旗
        self.showflag = False
        for i in self.flag:
            Cube.main_canvas.tag_bind(i, '<Button-3>', self.right)
        Cube.main_canvas.tag_bind(self.rect, '<Button-1>', self.left)
        Cube.main_canvas.tag_bind(self.rect, '<Button-3>', self.right)
        Cube.main_canvas.tag_bind(self.rect, '<ButtonRelease-1>', self.back)

    def create_flag(self, x, y, s):
        c1 = Cube.main_canvas.create_polygon(x - 2 * s, y - 7 * s, x - 2 * s, y - 1 * s, x + 3 * s, y - 1 * s,
                                             outline='red', fill='yellow', state='hidden', width=2 * s)
        c2 = Cube.main_canvas.create_line(x - 2 * s, y - 2 * s, x - 2 * s, y + 5 * s, fill='red', state='hidden',
                                          width=2 * s)
        c3 = Cube.main_canvas.create_line(x - 6 * s, y + 5 * s, x + 3 * s, y + 5 * s, fill='red', state='hidden',
                                          width=2 * s)
        return [c1, c2, c3]

    def create_mine(self, x, y, s):
        c1 = Cube.main_canvas.create_oval(x - 6 * s, y - 6 * s, x + 5 * s, y + 5 * s, fill='black', state='hidden')
        c2 = Cube.main_canvas.create_oval(x - 4 * s, y - 4 * s, x - 1 * s, y - 1 * s, fill='white', state='hidden')
        c3 = Cube.main_canvas.create_line(x - 8 * s, y, x + 8 * s, y, width=2 * s, state='hidden')
        c4 = Cube.main_canvas.create_line(x, y - 8 * s, x, y + 8 * s, width=2 * s, state='hidden')
        return [c1, c2, c3, c4]

    def create_x(self, s):
        a = 7 * s
        c1 = Cube.main_canvas.create_line(self.center[0] - a, self.center[1] - a, self.center[0] + a,
                                          self.center[1] + a, fill='red', state='hidden', width=2 * s)
        c2 = Cube.main_canvas.create_line(self.center[0] - a, self.center[1] + a, self.center[0] + a,
                                          self.center[1] - a, fill='red', state='hidden', width=2 * s)
        return [c1, c2]

    def find_neighbors(self, other):
        self.neighbors += [other]

    def start_game(self):
        Cube.face.shift_face(Cube.face.face)
        Cube.first_click = self
        Cube.is_new = False
        puzzle()
        start_new_thread(game_time, ())

    def left(self, event):
        if not Cube.space:
            Cube.hold_on = True
            if Cube.state:
                if not Cube.end:
                    if self.number != -1 or self.is_unknown:
                        Cube.face.shift_face(Cube.face.face)
                    if not self.showflag:
                        if self.is_unknown:
                            Cube.main_canvas.itemconfig(self.rect, fill='grey')
                        else:
                            for j in self.neighbors:
                                if not j.showflag and j.is_unknown:
                                    Cube.main_canvas.itemconfig(j.rect, fill='grey')

    def back(self, event):
        if Cube.space and not Cube.hold_on:
            self.right(event)
        else:
            Cube.hold_on = False
            if Cube.state:
                if Cube.is_new:
                    self.start_game()
                if Cube.is_again:
                    start_new_thread(game_time, ())
                    Cube.is_again = False
                if not Cube.end:
                    Cube.face.shift_face(Cube.face.normal_face)
                    if self.neighbor_flag_number != self.number:
                        for i in self.neighbors:
                            if i.is_unknown and not i.showflag:
                                Cube.main_canvas.itemconfig(i.rect, fill=i.colorup)
                    elif not self.is_unknown:
                        bomb = 0
                        for j in self.neighbors:
                            if not j.showflag and j.is_unknown:
                                if Cube.main_canvas.itemcget(j.mine[0], 'state') == 'hidden':
                                    j.back(event)
                                else:
                                    bomb = j
                        if bomb != 0:
                            bomb.back(event)
                if not Cube.end and not self.showflag and self.is_unknown:
                    Cube.main_canvas.itemconfig(self.rect, fill='')
                    self.appear()
                    if self.number == 0:
                        self.sweeping()
                if Cube.known == Cube.num - Cube.mine:
                    win()

    def appear(self):
        self.is_unknown = False
        if self.number != -1:
            Cube.main_canvas.itemconfig(self.rect, fill='')
            Cube.known += 1
        else:
            Cube.bomb_mine = self
            lose()

    def sweeping(self):
        que = queue.Queue()
        que.put(self)
        while not que.empty():
            a = que.get()
            if a.number == 0:
                for i in a.neighbors:
                    if i.is_unknown and not i.showflag:
                        i.appear()
                        que.put(i)

    def right(self, event):
        if Cube.state:
            if not Cube.is_new and not Cube.end and self.is_unknown:
                if not self.showflag and Cube.main_canvas.itemcget(self.rect, 'fill') != 'grey':
                    Cube.main_canvas.itemconfig(self.rect, fill=self.colordown)
                    for j in self.flag:
                        Cube.main_canvas.itemconfig(j, state='normal')
                    self.showflag = True
                    if self.number != -1:
                        Cube.wrong_list += [self]
                    for i in self.neighbors:
                        i.neighbor_flag_number += 1
                    Cube.flag_number += 1
                elif Cube.main_canvas.itemcget(self.rect, 'fill') != 'grey':
                    Cube.main_canvas.itemconfig(self.rect, fill=self.colorup)
                    for j in self.flag:
                        Cube.main_canvas.itemconfig(j, state='hidden')
                    self.showflag = False
                    if self.number != -1:
                        Cube.wrong_list.remove(self)
                    for i in self.neighbors:
                        i.neighbor_flag_number -= 1
                    Cube.flag_number -= 1
                Cube.counter.update_text()


class Timer:
    def __init__(self):
        self.text = Cube.up_canvas.create_text(Cube.width + Cube.margin - 10, 5, text='0', fill='red',
                                               font=('Verdana', 18, 'bold'), anchor=NE)


class Counter:
    def __init__(self):
        self.text = Cube.up_canvas.create_text(Cube.margin, 5, text=str(Cube.mine - Cube.flag_number), fill='red',
                                               font=('Verdana', 18, 'bold'), anchor=NW)

    def update_text(self):
        Cube.up_canvas.itemconfig(self.text, text=str(Cube.mine - Cube.flag_number))


class Face:
    def __init__(self, x, y):
        c1 = Cube.up_canvas.create_oval(0 + x, 0 + y, 20 + x, 20 + y, fill='yellow')
        c2 = Cube.up_canvas.create_line(6 + x, 14 + y, 15 + x, 14 + y)
        c3 = Cube.up_canvas.create_rectangle(6 + x, 7 + y, 7 + x, 8 + y, fill='black')
        c4 = Cube.up_canvas.create_rectangle(13 + x, 7 + y, 14 + x, 8 + y, fill='black')
        c5 = Cube.up_canvas.create_oval(8 + x, 11 + y, 12 + x, 16 + y)
        c6 = Cube.up_canvas.create_polygon(7 + x, 5 + y, 5 + x, 5 + y, 2 + x, 7 + y, 3 + x, 8 + y, 5 + x, 7 + y, 7 + x,
                                           7 + y, 8 + x, 8 + y, 9 + x, 7 + y, outline='black', fill='white')
        c7 = Cube.up_canvas.create_rectangle(3 + x, 7 + y, 4 + x, 8 + y)
        c8 = Cube.up_canvas.create_polygon(16 + x, 5 + y, 14 + x, 5 + y, 11 + x, 7 + y, 12 + x, 8 + y, 14 + x, 7 + y,
                                           16 + x, 7 + y, 17 + x, 8 + y, 18 + x, 7 + y, outline='black', fill='white')
        c9 = Cube.up_canvas.create_rectangle(12 + x, 7 + y, 13 + x, 8 + y)
        c10 = Cube.up_canvas.create_arc(3 + x, 3 + y, 17 + x, 17 + y, start=210, extent=125, style='arc')
        c11 = Cube.up_canvas.create_line(4 + x, 8 + y, 6 + x, 6 + y, 9 + x, 9 + y)
        c12 = Cube.up_canvas.create_line(12 + x, 8 + y, 14 + x, 6 + y, 17 + x, 9 + y)
        c13 = Cube.up_canvas.create_polygon(7 + x, 12 + y, 10 + x, 17 + y, 13 + x, 12 + y, outline='black', fill='red')
        self.normal_face = [c1, c2, c3, c4]
        self.face = [c1, c3, c4, c5]
        self.funny_face = [c1, c6, c7, c8, c9, c10]
        self.winning_face = [c1, c11, c12, c13]
        for i in [c1, c2, c3, c4, c6, c7, c8, c9, c10, c11, c12, c13]:
            Cube.up_canvas.tag_bind(i, '<Button-3>', restart)
            Cube.up_canvas.tag_bind(i, '<Button-1>', new)

    def shift_face(self, x):
        for i in x:
            Cube.up_canvas.lift(i)


def puzzle():
    Cube.mine_list = []
    Cube.safe_list = []
    Cube.index.remove(Cube.first_click)
    shuffle(Cube.index)
    Cube.mine_list = Cube.index[:Cube.mine]
    Cube.safe_list = Cube.index[Cube.mine:] + [Cube.first_click]
    for i in Cube.mine_list:
        for j in i.mine:
            Cube.main_canvas.itemconfig(j, state='normal')
        i.number = -1
    for k in Cube.safe_list:
        k.number = 0
        for n in k.neighbors:
            if n.number == -1:
                k.number += 1
        if k.number > 0:
            Cube.main_canvas.itemconfig(k.text, text='%d' % k.number, fill=Cube.color[k.number - 1],
                                        font=('Verdana', int(30 * Cube.scale), 'bold'))
    Cube.index += [Cube.first_click]


def win():
    if not Cube.end:
        Cube.face.shift_face(Cube.face.winning_face)
        for i in Cube.mine_list:
            if not i.showflag:
                i.right(1)
        Cube.end = True


def lose():
    Cube.end = True
    Cube.face.shift_face(Cube.face.funny_face)
    for i in Cube.mine_list:
        if not i.showflag:
            Cube.main_canvas.itemconfig(i.rect, fill='')
    Cube.main_canvas.itemconfig(Cube.bomb_mine.rhombus, fill='red')
    for j in Cube.wrong_list:
        Cube.main_canvas.itemconfig(j.text, text='')
        for k in j.flag:
            Cube.main_canvas.itemconfig(k, state='hidden')
        j.showflag = False
        for k in j.mine:
            Cube.main_canvas.itemconfig(k, state='normal')
        for k in j.x:
            Cube.main_canvas.itemconfig(k, state='normal')
        Cube.main_canvas.itemconfig(j.rect, fill='')


def cheating(event):
    cheat()


def cheat():
    if not Cube.is_new and not Cube.end:
        for i in Cube.safe_list:
            if i.showflag:
                i.right(1)
            if i.is_unknown:
                i.appear()
        win()


def restart(event):
    restore()


def restore():
    Cube.is_again = True
    Cube.face.shift_face(Cube.face.normal_face)
    Cube.known = 0
    if Cube.bomb_mine != 0:
        Cube.main_canvas.itemconfig(Cube.bomb_mine.rhombus, fill=Cube.bomb_mine.colordown)
    for i in Cube.index:
        Cube.main_canvas.itemconfig(i.rect, fill=i.colorup)
        i.is_unknown = True
        i.neighbor_flag_number = 0
        for j in i.flag:
            Cube.main_canvas.itemconfig(j, state='hidden')
        i.showflag = False
    for i in Cube.wrong_list:
        if i.number > 0:
            Cube.main_canvas.itemconfig(i.text, text='%d' % i.number, fill=Cube.color[i.number - 1],
                                        font=('Verdana', 15, 'bold'))
        for j in i.mine:
            Cube.main_canvas.itemconfig(j, state='hidden')
        for j in i.x:
            Cube.main_canvas.itemconfig(j, state='hidden')
    Cube.wrong_list = []
    Cube.flag_number = 0
    Cube.counter.update_text()
    Cube.up_canvas.itemconfig(Cube.timer.text, text='0')
    Cube.end = False


def root_menu():
    main_menu = Menu(root)
    start_menu = Menu(main_menu)
    main_menu.add_cascade(label="Start", menu=start_menu)
    start_menu.add_command(label='Restart', command=restore)
    start_menu.add_command(label='New Game', command=new_game)
    start_menu.add_separator()
    start_menu.add_command(label='Settings', command=settings)
    start_menu.add_separator()
    start_menu.add_command(label='Quit', command=root.quit)
    help_menu = Menu(main_menu)
    main_menu.add_cascade(label="Help", menu=help_menu)
    help_menu.add_command(label='Guide', command=guide)
    help_menu.add_command(label='Cheat', command=cheat)
    root.config(menu=main_menu)


def guiding(event):
    guide()


def guide():
    t = Toplevel(root)
    t.title('Guide')
    t.geometry(f'{400}x{250}')
    Label(t, justify='left', text='C: cheat\n\n'
                                  'G or H: guide\n\n'
                                  'N: new game\n\n'
                                  'R: restart\n\n'
                                  'Enter or S: settings\n\n'
                                  'Space + LeftMouse: right mouse\n\n'
                                  'Esc: quit\n\n').pack()
    Button(t, text='确定', command=t.withdraw).pack()


def new(event):
    new_game()


def new_game():
    Cube.state = 0
    Cube.odd += 1

    Cube.flag_number = 0
    Cube.known = 0
    Cube.mine_list = []
    Cube.safe_list = []
    Cube.end = False
    Cube.is_again = False
    Cube.first_click = None
    Cube.is_new = True
    Cube.bomb_mine = 0
    Cube.wrong_list = []
    Cube.up_canvas.itemconfig(Cube.timer.text, text='0')
    Cube.face.shift_face(Cube.face.normal_face)
    Cube.index = []
    Cube.main_canvas.delete("all")

    H = Cube.height * Cube.height_scale
    W = Cube.width * Cube.width_scale

    index = []
    m, graph = Cube.genMap.gen_new_map(W, H)
    Cube.num = len(graph)

    if H / W >= Cube.height / Cube.width:
        Cube.scale = Cube.height / H
    else:
        Cube.scale = Cube.width / W

    Cube.offset = (
        Cube.margin + (Cube.width - m[0] * Cube.scale) / 2, Cube.margin + (Cube.height - m[1] * Cube.scale) / 2)

    for c in graph:
        if len(c[1]) < 2:
            index.append(0)
        else:
            aa = (c[0][0][0] * Cube.scale + Cube.offset[0], c[0][0][1] * Cube.scale + Cube.offset[1])
            bb = (c[0][1][0] * Cube.scale + Cube.offset[0], c[0][1][1] * Cube.scale + Cube.offset[1])
            cc = (c[0][2][0] * Cube.scale + Cube.offset[0], c[0][2][1] * Cube.scale + Cube.offset[1])
            dd = (c[0][3][0] * Cube.scale + Cube.offset[0], c[0][3][1] * Cube.scale + Cube.offset[1])
            index.append(Cube(aa, bb, cc, dd))
    for i in range(Cube.num):
        for j in graph[i][1]:
            if not index[i] == 0 and not index[j] == 0:
                index[i].find_neighbors(index[j])
    for c in index:
        if not c == 0:
            Cube.index.append(c)
    Cube.num = len(Cube.index)
    if 0 < Cube.mine1 < Cube.num:
        Cube.mine = Cube.mine1
    elif Cube.mine1 == 0:
        Cube.mine = (int(Cube.num / 100) + 1) * 10
        if Cube.mine / Cube.num > 0.15:
            Cube.mine = int(Cube.num / 10) + 2
    else:
        Cube.mine = Cube.num - 1

    Cube.counter.update_text()

    Cube.state = 1


def setting(event):
    settings()


def settings():
    if not Cube.is_setting:
        Cube.is_setting = 1

        Cube.setting_window = Toplevel()
        Cube.setting_window.title('Settings')
        Label(Cube.setting_window, text='Width (0.5 to 2):').grid()
        Cube.v1 = StringVar()
        Cube.v1.set(f'{Cube.width_scale}')
        e = Entry(Cube.setting_window, textvariable=Cube.v1, width=5)
        e.grid(row=0, column=1)
        e.focus()
        e.select_adjust(len(Cube.v1.get()))
        Label(Cube.setting_window, text='Height (0.5 to 2):').grid(row=1, column=0)
        Cube.v2 = StringVar()
        Cube.v2.set(f'{Cube.height_scale}')
        Entry(Cube.setting_window, textvariable=Cube.v2, width=5).grid(row=1, column=1)
        Label(Cube.setting_window, text='Number of Mines (0 for auto):').grid(row=2, column=0)
        Cube.v3 = StringVar()
        Cube.v3.set(f'{Cube.mine1}')
        Entry(Cube.setting_window, textvariable=Cube.v3, width=5).grid(row=2, column=1)
        Label(Cube.setting_window, text='    ').grid(row=1, column=2)
        ok = Button(Cube.setting_window, text='OK')
        ok.grid(row=1, column=3)
        Label(Cube.setting_window, text='    ').grid(row=1, column=4)
        ok.bind('<Button-1>', set)
        Cube.setting_window.bind('<Return>', set)


def set(event):
    try:
        w = float(Cube.v1.get())
        h = float(Cube.v2.get())
        m = int(Cube.v3.get())
        Cube.width_scale = w
        Cube.height_scale = h
        Cube.mine1 = m
        if 0.5 > Cube.width_scale:
            Cube.width_scale = 0.5
        elif 2 < Cube.width_scale:
            Cube.width_scale = 2
        if 0.5 > Cube.height_scale:
            Cube.height_scale = 0.5
        elif 2 < Cube.height_scale:
            Cube.height_scale = 2
        if 0 > Cube.mine1:
            Cube.mine1 = 0
        new_game()

        Cube.setting_window.destroy()
        Cube.is_setting = 0
    except:
        return


def start():
    p = 1.0
    Cube.width = Screenwidth * p - 2 * Cube.margin
    Cube.height = Screenheight * p - Cube.up_height - 2 * Cube.margin

    Cube.genMap = GenMap(10000, 9)

    Cube.up_canvas = Canvas(root, relief='raised', bg='black', height=35, width=Screenwidth * p)
    Cube.up_canvas.bind('<Button-3>', restart)
    Cube.up_canvas.place(x=0, y=0)
    Cube.main_canvas = Canvas(root, height=Screenheight * p - Cube.up_height, width=Screenwidth * p, bg='white')
    Cube.up_canvas.bind('<Button-1>', new)
    Cube.main_canvas.place(x=0, y=35)

    Cube.counter = Counter()
    Cube.timer = Timer()
    Cube.face = Face(Cube.width / 2, 10)

    new_game()


def quiting(event):
    root.quit()


def space(event):
    Cube.space = True


def space_release(event):
    Cube.space = False


root = Tk()
root.title('Penrose Minesweeper')

Screenwidth = root.winfo_screenwidth()
Screenheight = root.winfo_screenheight()

root.geometry(f'{Screenwidth}x{Screenheight}')
root_menu()
root.bind('<Return>', setting)
root.bind('<s>', setting)
root.bind('<c>', cheating)
root.bind('<n>', new)
root.bind('<r>', restart)
root.bind('<g>', guiding)
root.bind('<h>', guiding)
root.bind('<Escape>', quiting)
root.bind('<space>', space)
root.bind('<KeyRelease-space>', space_release)

start()

root.mainloop()
