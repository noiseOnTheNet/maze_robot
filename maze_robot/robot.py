import tkinter as tk
import random

def bit(x: int):
    while x:
        yield x % 2
        x = x >> 1

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
        self.canvas.delete(tk.ALL)
        maxv = 2 ** (self.rows - 1) - 1
        maxh = 2 ** (self.cols - 1) - 1
        left_wall = 2 ** self.cols
        bottom_wall = 2 ** self.rows
        right_wall = 1
        top_wall = 1
        self.vwalls = [(random.randint(0,maxh) << 1) + left_wall + right_wall for _ in range(self.rows)]
        self.hwalls = [(random.randint(0,maxv) << 1) + top_wall + bottom_wall for _ in range(self.cols)]
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
