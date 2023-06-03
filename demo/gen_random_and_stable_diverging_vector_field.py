#!/usr/bin/env python3
import json
import numpy as np
import math as m
from pprint import pprint

obj = {
    "avg_len" : 1.0,
    "max_len" : 1.0,
    "colorscheme" : [
        {
            "value_to_map_to_this_color" : 1.0,
            "color_space" : "sRGB",
            "format" : "hex",
            "color" : "#DC143C",
            "kwargs" : {}
        },
        {
            "value_to_map_to_this_color" : 0.9,
            "color_space" : "sRGB",
            "format" : "hex",
            "color" : "#DB16A4",
            "kwargs" : {}
        },
        {
            "value_to_map_to_this_color" : 0.8,
            "color_space" : "sRGB",
            "format" : "hex",
            "color" : "#AC18DA",
            "kwargs" : {}
        },
        {
            "value_to_map_to_this_color" : 0.7,
            "color_space" : "sRGB",
            "format" : "hex",
            "color" : "#6919d9",
            "kwargs" : {}
        },
        {
            "value_to_map_to_this_color" : 0.5,
            "color_space" : "sRGB",
            "format" : "hex",
            "color" : "#1C71D8",
            "kwargs" : {}
        },
        {
            "value_to_map_to_this_color" : 0.25,
            "color_space" : "sRGB",
            "format" : "hex",
            "color" : "#80FFC8",
            "kwargs" : {}
        }
    ],
    "vectors": []
}

def gen_random_vector_field():
    half_side_length = 4.0
    neg_bounds = [ -half_side_length for k in range(3) ]
    pos_bounds = [  half_side_length for k in range(3) ]
    volume = m.prod((b - a) for a, b in zip(neg_bounds, pos_bounds))

    rng = np.random.default_rng()
    sample = rng.uniform(neg_bounds, pos_bounds, size=(127000, 3)).tolist()
    sample.sort(key = lambda x : x[0])
    sample = [ np.array(k) for k in sample ]
    print(sample[:10])
    point_indices = []
    num_points = 4000
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
        obj["vectors"].append({
            "pos" : [ 1.5 * k for k in point.tolist() ],
            "vec" : (point / sqr_mag).tolist()
        })


def gen_stable_vector_field():
    half_side_length = 4

    for i in range(-half_side_length, half_side_length + 1):
        for j in range(-half_side_length, half_side_length + 1):
            for k in range(-half_side_length, half_side_length + 1):
                if i == 0 and j == 0 and k == 0:
                    continue
                sqr_mag = i * i + j * j + k * k
                obj["vectors"].append({
                    "pos" : [ i * 1.5, j * 1.5, k * 1.5 ],
                    "vec" : [ i / sqr_mag, j / sqr_mag, k / sqr_mag ],
                })

gen_random_vector_field()
gen_stable_vector_field()

print("Num vecs: {}", len(obj["vectors"]))

with open("random-and-stable-diverging-field.json", "w") as writer:
    json.dump(obj, writer)
