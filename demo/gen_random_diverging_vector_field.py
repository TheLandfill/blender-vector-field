#!/usr/bin/env python3
import json
import numpy as np
import math as m
from pprint import pprint

obj = {
    "min_len" : 0.01,
    "avg_len" : 0.9,
    "max_len" : 1,
    "colorscheme" : [
        {
            "value_to_map_to_this_color" : 0.5,
            "color_space" : "sRGB",
            "format" : "hex",
            "color" : "#DC143C",
            "kwargs" : {}
        },
        {
            "value_to_map_to_this_color" : 0.25,
            "color_space" : "sRGB",
            "format" : "hex",
            "color" : "#1474DC",
            "kwargs" : {}
        },
        {
            "value_to_map_to_this_color" : 0.375,
            "color_space" : "sRGB",
            "format" : "num",
            "color" : [ 1.0, 0.0, 1.0 ],
            "kwargs" : {}
        },
        {
            "value_to_map_to_this_color" : 0.125,
            "color_space" : "sRGB",
            "format" : "hex",
            "color" : "#80FFC8",
            "kwargs" : {}
        }
    ],
    "vectors": []
}

half_side_length = 3.0
neg_bounds = [ -2.0 * half_side_length for k in range(3) ]
pos_bounds = [  2.0 * half_side_length for k in range(3) ]
volume = m.prod((b - a) for a, b in zip(neg_bounds, pos_bounds))

rng = np.random.default_rng()
sample = rng.uniform(neg_bounds, pos_bounds, size=(127000, 3)).tolist()
sample.sort(key = lambda x : x[0])
sample = [ np.array(k) for k in sample ]
print(sample[:10])
point_indices = []
num_points = 3000
radius_est = (volume / num_points) ** (1.0 / 3.0)
print("radius: {}".format(radius_est))
sqr_radius = radius_est ** 2
sample = [ k for k in sample if np.dot(k, k) > sqr_radius ]

viable_points = [ i for i in range(len(sample)) ]
grid = dict()
removed_points = set()
offset = np.array([0.0, 0.0, 0.0])
while len(viable_points) > 0:
    for point_index in viable_points:
        point = sample[point_index]
        x = int((point[0] - neg_bounds[0]) / (2.0 * radius_est) + offset[0])
        y = int((point[1] - neg_bounds[1]) / (2.0 * radius_est) + offset[1])
        z = int((point[2] - neg_bounds[2]) / (2.0 * radius_est) + offset[2])
        if (x, y, z) in grid:
            grid[(x, y, z)].append(point_index)
        else:
            grid[(x, y, z)] = [ point_index ]
    print("Num Cells: {}".format(len(grid)))
    for cell in grid.values():
        if len(cell) <= 2:
            point_indices.append(cell[0])
            removed_points.add(cell[0])
        else:
            rng.shuffle(cell)
            for point_index in cell[:len(cell) // 2]:
                removed_points.add(point_index)
    print("Number of Viable Points: {}".format(len(viable_points)))
    grid = {}
    offset = rng.uniform(low = 0.0, high = 1.0, size = 3)
    viable_points = [ point_index for point_index in viable_points if point_index not in removed_points ]

print("Number of Points: {}".format(len(point_indices)))

for point_index in point_indices:
    point = sample[point_index]
    sqr_mag = np.dot(point, point)
    mag = np.sqrt(sqr_mag)
    obj["vectors"].append({
        "pos" : point.tolist(),
        "vec" : (point / sqr_mag / mag).tolist()
    })

with open("random-diverging-field.json", "w") as writer:
    json.dump(obj, writer)
