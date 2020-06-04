import random
from PIL import Image


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
        if self.x < a-1:
            self.neighbours.append(cells[self.x+1][self.y])
        if self.y < b-1:
            self.neighbours.append(cells[self.x][self.y+1])
        if self.x > 0:
            self.neighbours.append(cells[self.x-1][self.y])


def get_neighbours(cell, checkWalls=False):
    neighbours = []
    for n in cell.neighbours:
        if not n.visited and (not cell.walls[getWall(cell, n)] or not checkWalls):
            neighbours.append(n)
    return neighbours


def get_neighbours2(cell):
    neighbours = []
    for i, n in enumerate(cell.neighbours):
        if not n.visited and not cell.walls[getWall(cell, n)]:
            neighbours.append(n)
    return neighbours


def color_cell(cell, color):
    pixels[cell.x*4+1, cell.y*4+1] = color
    pixels[cell.x*4+2, cell.y*4+1] = color
    pixels[cell.x*4+1, cell.y*4+2] = color
    pixels[cell.x*4+2, cell.y*4+2] = color


def collor_wall(c1, c2, d, color):
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
    collor_wall(c2, c1, ['v', 'h'][wall % 2], color=(255, 255, 255))


if __name__ == '__main__':
    a = 100  # input()  # nuber of cells in a row
    b = 100  # input()  # number of cells in a collumn
    stack = []

    w, h = 4*a, 4*b
    img = Image.new("RGB", (w, h))
    pixels = img.load()
    # Make the cells white
    for i in range(w):
        for j in range(h):
            if (i % 4 != 0 and i % 4 != 3) and (j % 4 != 0 and j % 4 != 3):
                pixels[i, j] = (255, 255, 255)

    cells = [[Cell(x, y) for y in range(b)] for x in range(a)]
    for x in range(a):
        for y in range(b):
            cells[x][y].set_neighbours()

    stack.append(cells[0][0])
    stack[0].visited = True
    while stack:
        cur_cell = stack.pop(0)
        neighbours = get_neighbours(cur_cell)
        if neighbours:
            stack.insert(0, cur_cell)
            r = random.randint(0, len(neighbours)-1)
            new_cell = neighbours[r]
            remove_wall(cur_cell, new_cell)
            new_cell.visited = True
            stack.insert(0, new_cell)

    img = img.resize((w, h), Image.NEAREST)
    img.save('maze_unsolved.png')

    img2 = Image.open('maze_unsolved.png')
    pixels = img2.load()

    for x in range(a):
        for y in range(b):
            cells[x][y].visited = False

    stack = []
    stack.append(cells[0][0])
    stack[0].visited = True
    while cur_cell.x != a-1 or cur_cell.y != b-1:
        cur_cell = stack.pop(0)
        neighbours = get_neighbours(cur_cell, checkWalls=True)
        if neighbours:
            stack.insert(0, cur_cell)
            r = random.randint(0, len(neighbours)-1)
            new_cell = neighbours[r]
            new_cell.visited = True
            new_cell.parent = cur_cell
            stack.insert(0, new_cell)

    cur_cell.x = a-1
    cur_cell.y = b-1
    while cur_cell != cells[0][0]:
        wall = getWall(cur_cell, cur_cell.parent)
        collor_wall(cur_cell, cur_cell.parent, ['v', 'h'][wall % 2], color=(255, 0, 0))
        color_cell(cur_cell, color=(255, 0, 0))
        cur_cell = cur_cell.parent
    color_cell(cur_cell, color=(255, 0, 0))

    img2 = img2.resize((w, h), Image.NEAREST)
    img2.save('maze_solved.png')
