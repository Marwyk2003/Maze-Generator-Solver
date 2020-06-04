import random
from PIL import Image
from datetime import datetime
import os
import imageio
import numpy
import sys
import getopt


class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.visited = False
        self.walls = [True, True, True, True]
        self.neighbours = []
        self.parent = None

    def set_neighbours(self):
        if self.y > 0:
            self.neighbours.append(cells[self.x][self.y-1])
        if self.x < r-1:
            self.neighbours.append(cells[self.x+1][self.y])
        if self.y < c-1:
            self.neighbours.append(cells[self.x][self.y+1])
        if self.x > 0:
            self.neighbours.append(cells[self.x-1][self.y])

    def get_neighbours(self, checkWalls=False):
        neighbours = []
        for n in self.neighbours:
            if not n.visited and (not self.walls[getWall(self, n)] or not checkWalls):
                neighbours.append(n)
        return neighbours

    def color_cell(self, color):
        pixels[self.x*4+1, self.y*4+1] = color
        pixels[self.x*4+2, self.y*4+1] = color
        pixels[self.x*4+1, self.y*4+2] = color
        pixels[self.x*4+2, self.y*4+2] = color


def color_wall(c1, c2, d, color):
    if c1.x > c2.x or c1.y > c2.y:
        c1, c2 = c2, c1
    if d == 'h':
        pixels[c1.x*4+3, c1.y*4+1] = color
        pixels[c1.x*4+3, c1.y*4+2] = color
        pixels[c2.x*4, c2.y*4+1] = color
        pixels[c2.x*4, c2.y*4+2] = color
    elif d == 'v':
        pixels[c1.x*4+2, c1.y*4+3] = color
        pixels[c1.x*4+1, c1.y*4+3] = color
        pixels[c2.x*4+1, c2.y*4] = color
        pixels[c2.x*4+2, c2.y*4] = color


def getWall(c1, c2):
    if c1.x < c2.x:
        return 1
    if c1.x > c2.x:
        return 3
    if c1.y < c2.y:
        return 2
    if c1.y > c2.y:
        return 0


def remove_wall(c1, c2):
    wall = getWall(c1, c2)
    cells[c1.x][c1.y].walls[wall] = False
    cells[c2.x][c2.y].walls[(wall+2) % 4] = False
    color_wall(c2, c1, ['v', 'h'][wall % 2], color=(255, 255, 255))


if __name__ == '__main__':
    argv = sys.argv[1:]
    r = 0
    c = 0
    try:
        opts, args = getopt.getopt(argv, "hr:c:", ["rows=", "cols="])
    except getopt.GetoptError:
        print("Invalid command. Type -h to get help.")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('maze_generator.py -r <width> -c <height>')
            sys.exit()
        elif opt in ('-r', '--rows'):
            r = int(arg)
        elif opt in ('-c', '--cols'):
            c = int(arg)
    if r <= 0 or c <= 0:
        print("Number of rows and collumns must be positive.")
        sys.exit()

    today = datetime.now()

    PATH = f'maze_{today.strftime("%d%h%H%M%S")}'
    os.mkdir(PATH)

    img_w, img_h = 4*r, 4*c
    img = Image.new("RGB", (img_w, img_h))
    pixels = img.load()
    images = [img]

    # Make the cells white
    for i in range(img_w):
        for j in range(img_h):
            if (i % 4 != 0 and i % 4 != 3) and (j % 4 != 0 and j % 4 != 3):
                pixels[i, j] = (255, 255, 255)

    cells = [[Cell(x, y) for y in range(c)] for x in range(r)]
    for x in range(r):
        for y in range(c):
            cells[x][y].set_neighbours()

    print("Generating a maze...", end=" ", flush=True)

    with imageio.get_writer(f'{PATH}/generate.gif', mode='I', fps=50) as writer:
        stack = [cells[0][0]]
        stack[0].visited = True
        while stack:
            cur_cell = stack.pop(0)
            neighbours = cur_cell.get_neighbours()
            if neighbours:
                img = img.resize((img_w, img_h), Image.NEAREST)
                images.append(img)
                img = images[-1]
                pixels = img.load()

                if len(images) > 10000:
                    for im in images:
                        writer.append_data(numpy.array(im))
                    images = []

                stack.insert(0, cur_cell)
                rand = random.randint(0, len(neighbours)-1)
                new_cell = neighbours[rand]
                remove_wall(cur_cell, new_cell)
                new_cell.visited = True
                stack.insert(0, new_cell)

        for im in images:
            writer.append_data(numpy.array(im))

    img = img.resize((img_w, img_h), Image.NEAREST)
    img.save(f'{PATH}/maze_unsolved.png')

    print("done")
    print("solving the maze...", end=" ", flush=True)

    for x in range(r):
        for y in range(c):
            cells[x][y].visited = False

    stack = [cells[0][0]]
    stack[0].visited = True
    while cur_cell.x != r-1 or cur_cell.y != c-1:
        cur_cell = stack.pop(0)
        neighbours = cur_cell.get_neighbours(checkWalls=True)
        if neighbours:
            stack.insert(0, cur_cell)
            rand = random.randint(0, len(neighbours)-1)
            new_cell = neighbours[rand]
            new_cell.visited = True
            new_cell.parent = cur_cell
            stack.insert(0, new_cell)

    img = Image.open(f'{PATH}/maze_unsolved.png')
    pixels = img.load()

    cur_cell = cells[r-1][c-1]
    path = []
    path.append(cur_cell)
    while cur_cell != cells[0][0]:
        cur_cell = cur_cell.parent
        path.insert(0, cur_cell)

    images = [img]
    with imageio.get_writer(f'{PATH}/solve.gif', mode='I', fps=50) as writer:
        for i in range(len(path)):
            img = img.resize((img_w, img_h), Image.NEAREST)
            images.append(img)
            img = images[-1]
            pixels = img.load()

            if len(images) > 10000:
                for im in images:
                    writer.append_data(numpy.array(im))
                images = []

            if i < len(path)-1:
                wall = getWall(path[i], path[i+1])
                color_wall(path[i], path[i+1], ['v', 'h'][wall % 2], color=(255, 0, 0))
            path[i].color_cell(color=(255, 0, 0))
        for im in images:
            writer.append_data(numpy.array(im))
    img.save(f'{PATH}/maze_solved.png')

    print("done")
