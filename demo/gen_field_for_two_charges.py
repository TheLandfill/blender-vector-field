#!/usr/bin/env python3
import json
import numpy as np
import math as m
from pprint import pprint

obj = {
    "avg_len" : 1.0,
    "max_len" : 1.0,
    "min_len" : 0.1,
    "colorscheme" : [
        {
            "value_to_map_to_this_color" : -1.0,
            "color_space" : "sRGB",
            "format" : "hex",
            "color" : "#DC143C",
            "kwargs" : {}
        },
        {
            "value_to_map_to_this_color" : -2.0 / 3.0,
            "color_space" : "sRGB",
            "format" : "hex",
            "color" : "#DB16A4",
            "kwargs" : {}
        },
        {
            "value_to_map_to_this_color" : -1.0 / 3.0,
            "color_space" : "sRGB",
            "format" : "hex",
            "color" : "#AC18DA",
            "kwargs" : {}
        },
        {
            "value_to_map_to_this_color" : -1.0 / 6.0,
            "color_space" : "sRGB",
            "format" : "hex",
            "color" : "#AAAAAA",
            "kwargs" : {}
        },
        {
            "value_to_map_to_this_color" :  1.0 / 6.0,
            "color_space" : "sRGB",
            "format" : "hex",
            "color" : "#AAAAAA",
            "kwargs" : {}
        },
        {
            "value_to_map_to_this_color" :  1.0 / 3.0,
            "color_space" : "sRGB",
            "format" : "hex",
            "color" : "#80FFC8",
            "kwargs" : {}
        },
        {
            "value_to_map_to_this_color" :  2.0 / 3.0,
            "color_space" : "sRGB",
            "format" : "hex",
            "color" : "#1969d9",
            "kwargs" : {}
        },
        {
            "value_to_map_to_this_color" :  1.0,
            "color_space" : "sRGB",
            "format" : "hex",
            "color" : "#1C31FF",
            "kwargs" : {}
        },
    ],
    "vectors": []
}

neg_bounds = [ -6, -6, -4 ]
pos_bounds = [  6,  6,  4 ]

charge_pos = [
    [-2, 0, 0],
    [ 2, 0, 0]
]
charge_mag = [
     1.0,
    -1.0
]
charge_pos = [ 1.5 * np.array(k) for k in charge_pos ]

def add_field_vec(point):
    dist_vec = [ point - k for k in charge_pos ]
    sqr_mag_list = [ np.dot(k, k) for k in dist_vec ]
    for sqr_mag in sqr_mag_list:
        if sqr_mag < 1.0e-4:
            return
    mag_list = [ np.sqrt(k) for k in sqr_mag_list ]
    field_vec = sum(
        3.0 * q * r_vec / r_sqr / r
        for q, r_vec, r_sqr, r in zip(
            charge_mag,
            dist_vec,
            sqr_mag_list,
            mag_list
        )
    )
    potential = sum(
        1.25 * q / r
        for q, r in zip(
            charge_mag,
            mag_list
        )
    )
    point_check = np.array([2.0, 0.0, 0.0])
    point_check -= point
    if np.dot(point_check, point_check) < 1e-7:
        print("point = ", end = '')
        pprint(point)
        print("dist_vec = ", end = '')
        pprint(dist_vec)
        print("sqr_mag_list = ", end = '')
        pprint(sqr_mag_list)
        print("field_vec = ", end = '')
        pprint(field_vec)
        print("potential = {}".format(potential))
    obj["vectors"].append({
        "pos" : point.tolist(),
        "vec" : field_vec.tolist(),
        "col" : potential
    })

def gen_random_vector_field():
    volume = m.prod(float(b - a) for a, b in zip(neg_bounds, pos_bounds))

    rng = np.random.default_rng()
    sample = rng.uniform(neg_bounds, pos_bounds, size=(127000, 3))
    # sample.sort(key = lambda x : x[0])
    # sample = [ np.array(k) for k in sample ]
    print(sample[:10])
    point_indices = []
    num_points = 4000
    radius_est = (volume / num_points) ** (1.0 / 3.0)
    print("radius: {}".format(radius_est))
    sqr_radius = radius_est ** 2
    for charge_point in charge_pos:
        sample = [ k for k in sample if np.dot(k - charge_point, k - charge_point) > sqr_radius ]
    print("Num points far enough from charge: {}".format(len(sample)))

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
        add_field_vec(sample[point_index])

def gen_stable_vector_field():
    temp_neg_bounds = [ k // 2 for k in neg_bounds ]
    temp_pos_bounds = [ k // 2 for k in pos_bounds ]
    ranges = [ range(bottom, top + 1) for bottom, top in zip(temp_neg_bounds, temp_pos_bounds) ]
    for i in ranges[0]:
        for j in ranges[1]:
            for k in ranges[2]:
                point = 2.0 * np.array([i, j, k])
                add_field_vec(point)

gen_random_vector_field()
gen_stable_vector_field()

print("Num vecs: {}".format(len(obj["vectors"])))

with open("two-charge-field.json", "w") as writer:
    json.dump(obj, writer)
