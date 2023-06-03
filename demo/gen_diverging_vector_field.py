#!/usr/bin/env python3

import json

obj = {
    "min_len" : 0.01,
    "avg_len" : 0.9,
    "max_len" : 1,
    "colorscheme" : [
        {
            "value_to_map_to_this_color" : 0.75,
            "color_space" : "sRGB",
            "format" : "hex",
            "color" : "#DC143C",
            "kwargs" : {}
        },
        {
            "value_to_map_to_this_color" : 0.25 + 0.5 * 1.0 / 3.0,
            "color_space" : "sRGB",
            "format" : "hex",
            "color" : "#1474DC",
            "kwargs" : {}
        },
        {
            "value_to_map_to_this_color" : 0.25 + 0.5 * 2.0 / 3.0,
            "color_space" : "sRGB",
            "format" : "num",
            "color" : [ 1.0, 0.0, 1.0 ],
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

half_side_length = 3

for i in range(-half_side_length, half_side_length + 1):
    for j in range(-half_side_length, half_side_length + 1):
        for k in range(-half_side_length, half_side_length + 1):
            if i == 0 and j == 0 and k == 0:
                continue
            sqr_mag = i * i + j * j + k * k
            obj["vectors"].append({
                "pos" : [ 2.0 * i, 2.0 * j, 2.0 * k ],
                "vec" : [ i / sqr_mag, j / sqr_mag, k / sqr_mag ],
            })

with open("diverging-field.json", "w") as writer:
    json.dump(obj, writer)
