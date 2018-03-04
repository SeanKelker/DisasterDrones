from random import randint
from numpy import ones, vstack
from numpy.linalg import lstsq
import numpy as np
import math

speedDrone1 = 20
speedDrone2 = 20
x_drone1_i = randint(0,100)
y_drone1_i = randint(0,100)
x_drone2_i = randint(0,100)
y_drone2_i = randint(0,100)
x_drone1_f = 50
y_drone1_f = 49
x_drone2_f = 25
y_drone2_f = 20

def path():
    points_1 = [(x_drone1_i, y_drone1_i), (x_drone1_f, y_drone1_f)]
    x_coord, y_coord = zip(*points_1)
    A = vstack([x_coord, ones(len(x_coord))]).T
    m1, c1 = lstsq(A, y_coord)[0]
    print("Line Solution is y = {m}x + {c}".format(m=m1, c=c1))
    points_2 = [(x_drone2_i, y_drone2_i), (x_drone2_f, y_drone2_f)]
    x_coord, y_coord = zip(*points_2)
    A = vstack([x_coord, ones(len(x_coord))]).T
    m2, c2 = lstsq(A, y_coord)[0]
    print("Line Solution is y = {m}x + {c}".format(m=m2, c=c2))
    a = np.array([[m1, 1], [m2, 1]])
    b = np.array([[c1], [c2]])
    intersection = (np.linalg.solve(a, b))
    print(intersection)
    dist_1  = math.hypot(intersection[0] - x_drone1_i, intersection[1] - y_drone1_i)
    dist_2  = math.hypot(intersection[0] - x_drone2_i, intersection[1] - y_drone2_i)
    time_1 = dist_1/speedDrone1
    time_2 = dist_2/speedDrone2
    print(time_1)
    print(time_2)
path()