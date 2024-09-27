import tkinter as tk
import random
from dataclasses import dataclass
from enum import Enum

class Direction(Enum):
    N = 0
    E = 1
    S = 2
    W = 3

N = Direction.N
E = Direction.E
S = Direction.S
W = Direction.W

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

class Maze:
    def __init__(self, rows: int=10, cols: int =10, seed: int | None =None):
        self.rows = rows
        self.cols = cols
        if seed is not None:
            random.seed(seed)
        self.__target = (random.randint(0,cols), random.randint(0,rows))

    @property
    def target(self):
        return self.__target

    def get_walls(self, x, y):
        result = []
        if self.vwalls[y] & (1 << x):
            result.append(Direction.W)
        if self.vwalls[y] & (1 << (x + 1)):
            result.append(Direction.E)
        if self.hwalls[x] & (1 << y):
            result.append(Direction.N)
        if self.hwalls[x] & (1 << (y + 1)):
            result.append(Direction.S)
        return set(result)

    def __random(self):
        maxv = 2 ** (self.rows - 1) - 1
        maxh = 2 ** (self.cols - 1) - 1
        left_wall = 2 ** self.cols
        bottom_wall = 2 ** self.rows
        right_wall = 1
        top_wall = 1
        self.vwalls = [(random.randint(0,maxh) << 1) + left_wall + right_wall for _ in range(self.rows)]
        self.hwalls = [(random.randint(0,maxv) << 1) + top_wall + bottom_wall for _ in range(self.cols)]

    def __kruskal(self):
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

    @classmethod
    def kruskal(cls, rows: int=10, cols: int =10, seed=None):
        maze = cls(rows, cols, seed)
        maze.__kruskal()
        return maze


    def random(cls, rows: int=10, cols: int =10, seed=None):
        maze = cls(rows, cols, seed)
        maze.__random()
        return maze

def create_maze(rows: int=10, cols: int =10, seed=None):
    return Maze.kruskal(rows, cols, seed)

class Robot:
    def __init__(self, maze=Maze.kruskal(), edge: int = 20, padding: int=50):
        self.maze= maze
        self.edge = edge
        self.padding = padding
        self.width = padding * 2 + self.maze.cols * edge
        self.height = padding * 2 + self.maze.rows *edge
        self.__x = 0
        self.__y = 0
        self.root = None
        self.canvas = None
        self.__pen_down = False

    def down_pen(self):
        self.__pen_down = True

    def up_pen(self):
        self.__pen_down = False

    @property
    def pen_down(self):
        return self.__pen_down

    @property
    def position(self):
        return (self.__x, self.__y)

    def view(self):
        self.root = tk.Tk()
        self.canvas = tk.Canvas(self.root,width=self.width,height=self.height)
        self.canvas.pack()
        self.plot()

    def __reticle_to_pixel_bbox(self, x, y, padding = 0):
        x1 = self.padding + self.edge * x + padding
        x2 = self.padding + self.edge * (x + 1) - padding
        y1 = self.padding + self.edge * y + padding
        y2 = self.padding + self.edge * (y + 1) - padding
        return (x1,y1,x2,y2)

    def __reticle_to_center(self, x, y):
        return (
            self.padding + self.edge * (x + .5),
            self.padding + self.edge * (y + .5)
        )

    def plot(self):
        if self.canvas is None:
            return
        self.canvas.delete(tk.ALL)
        for row,walls in enumerate(self.maze.vwalls):
            for col,wall in enumerate(bit(walls)):
                if wall:
                    x = self.padding + self.edge * col
                    y1 = self.padding + self.edge * row
                    y2 = self.padding + self.edge * (row + 1)
                    self.canvas.create_line(x, y1, x, y2)
        for col,walls in enumerate(self.maze.hwalls):
            for row,wall in enumerate(bit(walls)):
                if wall:
                    x1 = self.padding + self.edge * col
                    x2 = self.padding + self.edge * (col + 1)
                    y = self.padding + self.edge * row
                    self.canvas.create_line(x1, y, x2, y)

        bbox = self.__reticle_to_pixel_bbox(self.__x, self.__y, padding=1)
        self.robot_tag = self.canvas.create_oval(bbox, fill="blue")

        bbox = self.__reticle_to_pixel_bbox(*self.maze.target, padding=2)
        self.canvas.create_rectangle(bbox, fill="green")

    @property
    def walls(self):
        return self.maze.get_walls(self.__x, self.__y)

    def move(self, dirx: Direction):
        if dirx in self.walls:
            return False
        offset_x = 0
        offset_y = 0
        old_position = (self.__x, self.__y)
        match dirx:
            case Direction.N:
                self.__y = self.__y - 1
                offset_y = self.edge * -1
            case Direction.S:
                self.__y = self.__y + 1
                offset_y = self.edge
            case Direction.W:
                self.__x = self.__x - 1
                offset_x = self.edge * -1
            case Direction.E:
                self.__x = self.__x + 1
                offset_x = self.edge
        if self.canvas is not None:
            self.canvas.move(self.robot_tag, offset_x, offset_y)
            if self.__pen_down:
                line = self.__reticle_to_center(*old_position) + self.__reticle_to_center(self.__x, self.__y)
                self.canvas.create_line(line, fill="red")
        return True

    def exit(self):
        return (self.__x, self.__y) == self.maze.target
