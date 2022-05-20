import math
from penrose import PenroseP3, BtileS
import random


class GenMap:

    def __init__(self, scale, gen=10):
        tiling = PenroseP3(scale, ngen=gen)

        theta = math.pi / 5
        rot = math.cos(theta) + 1j * math.sin(theta)
        A1 = scale + 0.j
        B = 0 + 0j
        C1 = C2 = A1 * rot
        A2 = A3 = C1 * rot
        C3 = C4 = A3 * rot
        A4 = A5 = C4 * rot
        C5 = -A1
        tiling.set_initial_tiles([BtileS(A1, B, C1), BtileS(A2, B, C2),
                                  BtileS(A3, B, C3), BtileS(A4, B, C4),
                                  BtileS(A5, B, C5)])
        tiling.make_tiling()
        self.tiles = tiling.get_tiles()

        # self.tiles = []
        # for i in tmp:
        #     flag = True
        #     for j in self.tiles:
        #         c1 = ((i[0][0] + i[2][0]) / 2, (i[0][1] + i[2][1]) / 2)
        #         c2 = ((j[0][0] + j[2][0]) / 2, (j[0][1] + j[2][1]) / 2)
        #         if self.same(c1, c2):
        #             flag = False
        #             print("1")
        #             break
        #     if flag:
        #         self.tiles.append(i)

        self.radius = 0
        for t in self.tiles:
            for p in t:
                if p[0] > self.radius:
                    self.radius = p[0]
        self.radius *= 0.95

    def gen_new_map(self, width, height):
        r = 0.5 * math.sqrt(width ** 2 + height ** 2)
        R = self.radius - r

        theta = random.random() * 2 * math.pi
        rho = math.sqrt(random.random()) * R
        x = rho * math.cos(theta) - width / 2.0
        y = rho * math.sin(theta) - height / 2.0

        rot = random.random() * 2 * math.pi

        up = y + height
        down = y
        left = x
        right = x + width

        cubes = []
        for t in self.tiles:
            flag = True
            for p in t:
                if not (left <= p[0] <= right and down <= p[1] <= up):
                    flag = False
                    break
            if flag:
                aa = (t[0][0] - x, t[0][1] - y)
                bb = (t[1][0] - x, t[1][1] - y)
                cc = (t[2][0] - x, t[2][1] - y)
                dd = (t[3][0] - x, t[3][1] - y)
                cubes.append((aa, bb, cc, dd))

        graph = self.construct_graph(cubes)

        hmax = float("-inf")
        hmin = float("inf")
        wmax = float("-inf")
        wmin = float("inf")
        for t in graph:
            if len(t[1]) < 2:
                continue
            for p in t[0]:
                if p[1] > hmax:
                    hmax = p[1]
                if p[1] < hmin:
                    hmin = p[1]
                if p[0] > wmax:
                    wmax = p[0]
                if p[0] < wmin:
                    wmin = p[0]

        graph2 = []
        for t in graph:
            aa = (t[0][0][0] - wmin, t[0][0][1] - hmin)
            bb = (t[0][1][0] - wmin, t[0][1][1] - hmin)
            cc = (t[0][2][0] - wmin, t[0][2][1] - hmin)
            dd = (t[0][3][0] - wmin, t[0][3][1] - hmin)
            graph2.append([(aa, bb, cc, dd), t[1]])

        return (wmax - wmin, hmax - hmin), graph2

    def construct_graph(self, cubes):
        graph = []
        for c in cubes:
            graph.append([c, []])

        for i in range(len(cubes)):
            if len(graph[i][1]) < 4:
                for j in range(i + 1, len(cubes)):
                    if len(graph[j][1]) < 4:
                        flag = 0
                        for p in cubes[i]:
                            for q in cubes[j]:
                                if self.same(p, q):
                                    flag += 1
                                    break
                            if flag == 2:
                                graph[i][1].append(j)
                                graph[j][1].append(i)
                                break
                    if len(graph[i][1]) == 4:
                        break
        return graph

    def same(self, x, y):
        return math.sqrt((x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2) < 0.01
