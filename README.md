# Blender Vector Field

This script takes in a json file of the format shown in
[`sample-vector-field.json`](sample-vector-field.json), an object line
[arrow.obj](arrow.obj), and the name of the collection you want to add the
vector to. It then creates a bunch of copies of [arrow.obj](arrow.obj) and puts
them in the collection with the orientations specified in the json file along
with the proper scaling and coloring.

# How to Use

There are only five steps.

1.  Create a model for the arrow or use [arrow.obj](arrow.obj).
1.  Put [`generate_vector_field.py`](generate_vector_field.py) in your blender
    project.
1.  Either create a material known as `arrow-material` or run the script once
    and edit the result.
1.  Create a `.json` file in the format specified below. You can use
    [`sample-vector-field.json`](sample-vector-field.json) as an example.
1.  Create a new python file for every vector field you want to generate.
1.  Each python file should create a `Vector_Field` object and then call
    `generate_vector_field`.

You can see the exact syntax for creating a `Vector_Field` object and for
calling the `generate_vector_field` function at the bottom of
[`generate_vector_field.py`](generate_vector_field.py).

# Notes

First, you can and probably should use another programming language to generate
the .json file for the vector fields. I have several of these scrips in
[demo](demo/). Second, it is important that you give unique names for the
collections you want to add the arrows to or else you're going to end up adding
vectors to the wrong collections, which usually means you're going to be adding
them to either the wrong scene or no scene at all. Lastly, you might need to
mess around with the `arrow-material` to get it to properly color all the
arrows. Something like this should suffice for most needs.

![In the shading tab, you should have an attribute node with attribute name of
"arrow-color" whose output color is mapped to the input base color of a
Principled BSDF and possibly the emission color](arrow-material.png)

# json Format

Currently, there are five main things in the json file.

-   `max_length`: The maximum possible length of a vector.
-   `min_length`: Vectors with a length below this are not put into the file.
-   `avg_length`: Vectors with this length are exactly half of `max_length`.
-   `colorscheme`: A list of colors and values to map to the color. If the color
    value of a vector is given by the value `col`, then the color in the
    rendered vector field will be interpolated between the two colors with the
    closest values. If `col` is less than the minimum color value, then the
    vector will have the color with the minimum value. Likewise, if `col` is
    greater than the maximum color value, then the vector will have the color
    with the maximum value.
    - `value_to_map_to_this_color`: Where we put colors on the real line.
    - `color_space`: Specified in the
      [`generate_vector_field.py`](generate_vector_field.py) function.
      Basically, it corresponds to a color space in python's `colormath`
      library.
    - `format`: `hex` if you use the format `#DC143C` and `num` if you use the
      format [ 1.0, 0.5, 1.0 ].
    - `color`: A standard way of specifying the color.
    - `kwargs`: Use this to override everything else, such as in the case for a
      spectral color (see the `colormath` library for more documentation).
-   `vectors`: A list of vectors.
    - `pos`: Where you want the vector to be.
    - `vec`: The vector you want to place.
    - `rot`: (Optional) The rotation around the z-axis before you rotate to the
      proper vector.
    - `col`: (Optional) By default, vectors are colored by their length. If you
      want to override it, provide this option.

I'm probably going to add more to this later, specifically for animation, but
not right now. If someone were to [pay me](https://ko-fi.com/josephmellor), I
might be more motivated to move forward with this script. Otherwise, I'm only
going to update the script when I need to update it.
