import itertools
import more_itertools
import numpy as np
import matplotlib.pyplot as plt
import math
import random
import time
import datetime
import multiprocessing as mp

class block:
  def __init__(self, x, y, z, fixed_orientation=None, fixed_position=None):
    self.x, self.y, self.z = x, y, z
    self.h = self.w = self.d = 0
    self.i = self.j = self.k = 0
    self.fixed_orientation = fixed_orientation
    self.fixed_position = fixed_position

  def orientations(self):
    if self.fixed_orientation:
      return self.fixed_orientation
    return set(itertools.permutations((self.x, self.y, self.z)))

  def __eq__(self, other):
    if isinstance(other, self.__class__):
      return self.x == other.x and self.y == other.y and self.z == other.z
    else:
      return False

  def __ne__(self, other):
    return not self.__eq__(other)

  def __repr__(self):
    size = "size (" + str(self.x) + "," + str(self.y) + "," + str(self.z) + ")"
    pos = ", pos (" + str(self.i) + "," + str(self.j) + "," + str(self.k) + ")"
    orientation = ", orientation (" + str(self.h) + "," + str(self.w) + "," + str(self.d) + ")"
    fixed_orientation = fixed_position = ""
    if self.fixed_orientation:
      fixed_orientation = ", fixed orientation: "
      fixed_orientation += str(self.fixed_orientation)   
    if self.fixed_position:
      fixed_position = ', fixed position: '
      fixed_position += str(self.fixed_position)
    return(size + pos + orientation + fixed_orientation + fixed_position)

N = 5
inventory = {}

inventory[2] = [
  (2, (1, 1, 1)),
  (1, (1, 1, 2)),
  (1, (1, 2, 2))
]

inventory[3] = [
  (6, (1, 2, 2)),
  (3, (1, 1, 1))
]

inventory[4] = [
  (4, (1, 1, 3)),
  (5, (1, 2, 4)),
  (1, (1, 2, 2)),
  (1, (2, 2, 2))
]

inventory[5] = [
  (1, (1, 1, 3), (1, 1, 3), (0, 0, 0)),  # fixed position+orientation tower
  (1, (1, 1, 3), (1, 3, 1), (1, 1, 3)),  # fixed position+orientation tower
  (1, (1, 1, 3), (3, 1, 1), (2, 4, 4)),  # fixed position+orientation tower
  (2, (1, 2, 4), (2, 4, 1)),             # fixed orientation rects 
  (2, (1, 2, 4), (1, 2, 4)),             # fixed orientation rects
  (9, (1, 2, 4)),                        # rects
  (1, (1, 2, 2)),                        # squares
  (1, (2, 2, 2)),                        # cubes
]

blocks = []
for i in inventory[N]:
  for j in range(i[0]):
    if len(i) == 4:
      bl = block(*i[1], i[2], i[3])
    elif len(i) == 3:
      bl = block(*i[1], i[2])
    else:
      bl = block(*i[1])
    blocks.append(bl)

fixed = [i for i in blocks if i.fixed_position]
variable = [i for i in blocks if not i.fixed_position]

print(len(fixed))
print(len(variable))
t = 1
for bl in variable:
  t *= len(bl.orientations())
print(t, "piece orientations")
permutations = list(more_itertools.distinct_permutations(variable))
pcnt = len(permutations)
print(pcnt, "permutations")
print(pcnt * t, "configurations")

class box:
  def __init__(self, N):
    plt.ion()
    self.N = N
    self.x, self.y, self.z = np.indices((self.N, self.N, self.N))
    self.fig = plt.figure()
    self.ax = self.fig.gca(projection='3d')
    self.reset()

  def reset(self):
    self.voxels = (self.x < 0) & (self.y < 0) & (self.z < 0)
    self.blocks = []
    self.ax.clear()
    self.ax.set_xlabel('X')
    self.ax.set_ylabel('Y')
    self.ax.set_zlabel('Z')

  def add_block(self, bl, orientation=None):
    if bl.fixed_orientation:
      x, y, z = bl.fixed_orientation
    elif orientation:
      x, y, z = orientation[0], orientation[1], orientation[2]
    else:
      x, y, z = bl.x, bl.y, bl.z
    if bl.fixed_position:
      i, j, k = bl.fixed_position
      if ((i + x <= self.N) and
          (j + y <= self.N) and
          (k + z <= self.N)):
        # If self.voxels has false values in a 3D grid starting at (i,j,k)
        # in which the new block can fit, add it there.
        shape = ((self.x >= i) & (self.x < i + x) & 
                 (self.y >= j) & (self.y < j + y) &
                 (self.z >= k) & (self.z < k + z))
        occupied = self.voxels & shape
        if not occupied.any():
          self.voxels |= shape
          bl.i = i
          bl.j = j
          bl.k = k
          self.blocks.append(bl)
          return True
      else:
        return False
    for k in range(self.N):
      for j in range(self.N):
        for i in range(self.N):
          if ((i + x <= self.N) and
              (j + y <= self.N) and
              (k + z <= self.N)):
            # If self.voxels has false values in a 3D grid starting at (i,j,k)
            # in which the new block can fit, add it there.
            shape = ((self.x >= i) & (self.x < i + x) & 
                     (self.y >= j) & (self.y < j + y) &
                     (self.z >= k) & (self.z < k + z))
            occupied = self.voxels & shape
            if not occupied.any():
              self.voxels |= shape
              bl.i, bl.j, bl.k = i, j, k
              bl.h, bl.w, bl.d = x, y, z
              self.blocks.append(bl)
              return True
    return False

  def rm_block(self):
    bl = self.blocks.pop()
    shape = ((self.x >= bl.i) & (self.x < bl.i + bl.h) & 
             (self.y >= bl.j) & (self.y < bl.j + bl.w) &
             (self.z >= bl.k) & (self.z < bl.k + bl.d))
    self.voxels &= np.logical_not(shape)

def log(p):
  print(int(time.time() - start_time), "seconds - ", end="")
  print("tried", ccnt, "configurations,", "permutation", p)

  def draw(self):
    display.clear_output(wait=True)
    self.ax.clear()
    self.ax.voxels(self.voxels, facecolor="green", edgecolor='k')
    display.display(plt.gcf())

ccnt = 0
pcnt = 0

def fit(box, blocks, p):
  global ccnt
  ccnt += 1
  if ccnt % 10000 == 0:
    log(p)
  #box.draw()
  if len(blocks) == 0:
    #mybox.draw()
    print("FIT", ccnt, "configurations,", "permutation", p)
    for bl in box.blocks:
      print(bl)
    return True
  bl = blocks[0]
  for orientation in bl.orientations():
    if box.add_block(bl, orientation):
      if fit(box, blocks[1:], p):
        return True
      else:
        box.rm_block()
  return False

start_time = time.time()

tasks = []
for li in permutations:
  mybox = box(N)
  for bl in fixed:
    mybox.add_block(bl)
  pcnt += 1
  tasks.append((mybox, li, pcnt))

pool = mp.Pool()
result = pool.starmap(fit, tasks)

print(int(time.time() - start_time), "seconds")

