import tkinter as tk
import random
from dataclasses import dataclass

def bit(x: int):
    while x:
        yield x % 2
        x = x >> 1

@dataclass
class VWall:
    x: int
    y: int

    @property
    def cells(self):
        return ((self.x,self.y),(self.x+1,self.y))

    @property
    def row(self):
        return y

    @property
    def cols(self):
        return (self.x, self.x+1)

    def switch(self, hwalls, vwalls):
        vwalls[self.y] = vwalls[self.y] ^ (1 << (self.x + 1))
        return (hwalls, vwalls)

@dataclass
class HWall:
    x: int
    y: int

    @property
    def cells(self):
        return ((self.x,self.y),(self.x,self.y+1))

    @property
    def rows(self):
        return (self.y, self.y+1)

    @property
    def col(self):
        return self.x

    def switch(self, hwalls, vwalls):
        hwalls[self.x] = hwalls[self.x] ^ (1 << (self.y + 1))
        return (hwalls, vwalls)

class Robot:
    def __init__(self, rows: int=10, cols: int =10, edge: int = 20, padding: int=50):
        self.rows = rows
        self.cols = cols
        self.edge = edge
        self.padding = padding
        width = padding * 2 + cols * edge
        height = padding * 2 + rows *edge
        self.root = tk.Tk()
        self.canvas = tk.Canvas(self.root,width=width,height=height)
        self.canvas.pack()

    def random(self):
        maxv = 2 ** (self.rows - 1) - 1
        maxh = 2 ** (self.cols - 1) - 1
        left_wall = 2 ** self.cols
        bottom_wall = 2 ** self.rows
        right_wall = 1
        top_wall = 1
        self.vwalls = [(random.randint(0,maxh) << 1) + left_wall + right_wall for _ in range(self.rows)]
        self.hwalls = [(random.randint(0,maxv) << 1) + top_wall + bottom_wall for _ in range(self.cols)]

    def kruskal(self, seed=None):
        if seed is not None:
            random.seed(seed)

        # all walls
        self.vwalls = [2 ** (self.cols + 1) - 1 for _ in range(self.rows)]
        self.hwalls = [2 ** (self.rows + 1) - 1 for _ in range(self.cols)]

        # all disconnected
        universe = {frozenset([(x,y)]) for x in range(self.cols) for y in range(self.rows)}

        # random wall list
        walls = [
            VWall(x,y)
            for x in range(self.cols - 1)
            for y in range(self.rows)
        ] + [
            HWall(x,y)
            for x in range(self.cols)
            for y in range(self.rows - 1)
        ]
        random.shuffle(walls)

        for j,wall in enumerate(walls):
            self.plot()
            # stop if all connected
            if len(universe) == 1:
                break

            # are cells already connected?
            cell_a, cell_b = wall.cells
            set_a = next(filter(lambda x: cell_a in x,universe))
            if cell_b in set_a:
                continue

            set_b = next(filter(lambda x: cell_b in x,universe))

            # drop this wall
            self.hwalls, self.vwalls = wall.switch(self.hwalls, self.vwalls)
            # join the two sets
            universe = universe - {set_a, set_b}
            universe = universe | {set_a | set_b}


    def plot(self):
        self.canvas.delete(tk.ALL)
        for row,walls in enumerate(self.vwalls):
            for col,wall in enumerate(bit(walls)):
                if wall:
                    x = self.padding + self.edge * col
                    y1 = self.padding + self.edge * row
                    y2 = self.padding + self.edge * (row + 1)
                    self.canvas.create_line(x, y1, x, y2)
        for col,walls in enumerate(self.hwalls):
            for row,wall in enumerate(bit(walls)):
                if wall:
                    x1 = self.padding + self.edge * col
                    x2 = self.padding + self.edge * (col + 1)
                    y = self.padding + self.edge * row
                    self.canvas.create_line(x1, y, x2, y)
