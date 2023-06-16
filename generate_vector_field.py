import numpy as np
from colormath.color_conversions import convert_color
import colormath.color_objects as CO
import bpy
import orjson as json
from pprint import pprint
import math
import mathutils

color_space_text_to_color_object = {
    "spectral" : CO.SpectralColor,
    "Lab" : CO.LabColor,
    "LChab" : CO.LCHabColor,
    "LChuv" : CO.LCHuvColor,
    "Luv" : CO.LuvColor,
    "XYZ" : CO.XYZColor,
    "xyZ" : CO.xyYColor,
    "sRGB" : CO.sRGBColor,
    "AdobeRGB" : CO.AdobeRGBColor,
    "HSL" : CO.HSLColor,
    "HSV" : CO.HSVColor,
    "CMY" : CO.CMYColor,
    "CMYK" : CO.CMYKColor,
    "IPT" : CO.IPTColor
}

class Vector_Field:
    def __init__(self, filename, start_frame = 0):
        data = None
        with open(filename, "rb") as reader:
            data = json.loads(reader.read())
        self.avg_len = data["avg_len"]
        self.min_len = data["min_len"]
        self.max_len = data["max_len"]
        self.frame_offset = data["frame_offset"] if "frame_offset" in data else 0
        self.cur_frame = start_frame
        self.colorscheme = None
        self.parse_colorscheme(data["colorscheme"])
        self.vec_list = data["vectors"]
        self.prev_vec = None
        #self.pos_list = [ k["pos"] for k in data["vectors"] ]
        #self.vec_list = [ k["vec"] for k in data["vectors"] ]
        #self.rot_list = [ k["rot"] if "rot" in k else 0.0 for k in data["vectors"] ]
        #self.col_list = [ k["col"] if "col" in k else None for k in data["vectors"] ]

    def parse_colorscheme(self, unparsed_colorscheme):
        self.colorscheme = []
        for unparsed_color in unparsed_colorscheme:
            val = unparsed_color["value_to_map_to_this_color"]
            color_space = None
            if unparsed_color["color_space"] in color_space_text_to_color_object:
                color_space = color_space_text_to_color_object[
                    unparsed_color["color_space"]
                ]
            else:
                print("ERROR: Colorspace `{}` does not exist. The valid colorspaces are")
                pprint(color_space_text_to_color_object)
                print("For more info, check out https://python-colormath.readthedocs.io/en/latest/color_objects.html")
                # Hope I don't hit this
                return
            format = unparsed_color["format"]
            arg_list = []
            key_word_args = {}
            if format == "hex":
                arg_list_str = unparsed_color["color"]
                offset = 0
                if arg_list_str[0] == "#":
                    offset = 1
                for i in range(0, len(arg_list_str) // 2):
                    arg_list.append(int(arg_list_str[offset + 2 * i:offset + 2 * i + 2], 16) / 255.0)
            elif format == "num":
                arg_list = unparsed_color["color"]
            else:
                print("ERROR: We only support hex and num formats.")
                return
            if "kwargs" in unparsed_color:
                key_word_args = unparsed_color["kwargs"]
            self.colorscheme.append(
                (
                    val,
                    convert_color(color_space(*arg_list, **key_word_args), CO.LCHuvColor)
                )
            )
        self.colorscheme.sort(key=lambda x : x[0])
        pprint(self.colorscheme)

    def generate_vector_field(
        self,
        vector_obj_file_name,
        collection_name = "vector-field"
    ):
        collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(collection)

        # Get material
        material = bpy.data.materials.get("arrow-material")
        if material is None:
            # create material
            material = bpy.data.materials.new(name="arrow-material")

        base = bpy.ops.import_scene.obj(filepath=vector_obj_file_name)
        base = bpy.context.selected_objects[-1]
        base.name = collection_name + '-base-vec'

        for vec in self.vec_list:
            obj = self.generate_vector(base, vec)
            for coll in obj.users_collection:
                # Unlink the object
                coll.objects.unlink(obj)

            bpy.data.collections[collection_name].objects.link(obj)

            # Assign it to object
            if obj.data.materials:
                # assign to 1st material slot
                obj.data.materials[0] = material
            else:
                # no slots
                obj.data.materials.append(material)
        bpy.data.objects.remove(base, do_unlink = True)

    def ratio_to_successor_between_zero_and_one(
        self,
        l_in
    ):
        return l_in / (l_in + self.avg_len)

    #Needs to do an LCh interpolation between two adjacent colors
    def calc_color(
        self,
        length,
    ):
        if length - 1e-5 <= self.colorscheme[0][0]:
            return convert_color(self.colorscheme[0][1], CO.sRGBColor)
        if length + 1e-5 >= self.colorscheme[-1][0]:
            return convert_color(self.colorscheme[-1][1], CO.sRGBColor)
        cur_color_index = 0
        while cur_color_index < len(self.colorscheme) - 1 and length > self.colorscheme[cur_color_index][0]:
            cur_color_index += 1
        cur_color_index -= 1
        lower_color = self.colorscheme[cur_color_index]
        higher_color = self.colorscheme[cur_color_index + 1]
        if lower_color[1].lch_c < 10.0:
            lower_color[1].lch_h = higher_color[1].lch_h
        if higher_color[1].lch_c < 10.0:
            higher_color[1].lch_h = lower_color[1].lch_h
        min_hue = min(lower_color[1].lch_h, higher_color[1].lch_h)
        max_hue = max(lower_color[1].lch_h, higher_color[1].lch_h)
        if (max_hue - min_hue) > 180.0:
            if lower_color[1].lch_h < higher_color[1].lch_h:
                lower_color[1].lch_h += 360.0
            else:
                higher_color[1].lch_h += 360.0
        interp_val = (length - lower_color[0]) / (higher_color[0] - lower_color[0])
        return convert_color(
            CO.LCHuvColor(
                lower_color[1].lch_l * interp_val + higher_color[1].lch_l * (1 - interp_val),
                lower_color[1].lch_c * interp_val + higher_color[1].lch_c * (1 - interp_val),
                lower_color[1].lch_h * interp_val + higher_color[1].lch_h * (1 - interp_val)
            ),
            CO.sRGBColor
        )

    # I can give vecs names like
    # (0.1, 0.2, 0.3)
    # Also need to set color here. Color should be a property
    # Also need to set material here.
    def generate_vector(
        self,
        base,
        vector
    ):
        obj = base.copy()
        if type(vector) == dict:
            self.handle_single_vec(obj, vector)
        elif type(vector) == list:
            self.handle_single_vec(obj, vector)
            self.cur_frame = self.frame_offset
            for cur_vec in vector[1:]:
                self.handle_keyframe(obj, cur_vec)
        return obj

    def handle_single_vec(
        self,
        obj,
        vector
    ):
        pos = None
        vec = None
        if "pos" not in vector:
            print("ERROR: Need to define pos in the first vector in the list.")
            return
        else:
            pos = vector["pos"]
        if "vec" not in vector:
            print("ERROR: Need to define vec in the first vector in the list.")
            return
        else:
            vec = vector["vec"]
        self.prev_vec = vec
        rot = vector["rot"] if "rot" in vector else 0.0
        col = vector["col"] if "col" in vector else None
        l_in = np.linalg.norm(vec)
        l_out = self.max_len * self.ratio_to_successor_between_zero_and_one(l_in)
        color = None
        if col == None:
            color = self.calc_color(l_in)
        else:
            color = self.calc_color(col)
        obj.name = str(pos) + "--" + str(vec)
        obj.location = np.array(pos)
        obj.rotation_euler = Vector_Field.get_rot(vec, rot)
        obj.scale = np.array([l_out, l_out, l_out])
        obj["arrow-color"] = color.get_value_tuple()
        if l_in < self.min_len:
            obj.hide_render = True

    def handle_keyframe(
        self,
        obj,
        vector
    ):
        if "frame" in vector:
            self.cur_frame = vector["frame"]
        else:
            self.cur_frame += 1
        if "pos" in vector:
            obj.location = vector["pos"]
            obj.keyframe_insert(data_path="location", frame=self.cur_frame)
            if "pos_interpolation" in vector:
                action = bpy.data.actions.get(obj.animation_data.action.name)
                my_fcu = action.fcurves.find("location", index = 1)
                if vector["pos_interpolation"] == "linear":
                    my_fcu.keyframe_points[-1].interpolation = 'LINEAR'
                elif vector["pos_interpolation"] == "teleport":
                    my_fcu.keyframe_points[-1].interpolation = 'CONSTANT'
                my_fcu.update()
        rot = 0.0
        if "rot" in vector:
            rot = vector["rot"]
        l_in = np.linalg.norm(self.prev_vec)
        if "vec" in vector:
            vec = vector["vec"]
            self.prev_vec = vec
            obj.rotation_euler = Vector_Field.get_rot(vec, rot)
            obj.keyframe_insert(data_path="rotation_euler", frame=self.cur_frame)
            if "vec_interpolation" in vector:
                action = bpy.data.actions.get(obj.animation_data.action.name)
                my_fcu = action.fcurves.find("rotation_euler", index = 1)
                if vector["vec_interpolation"] == "linear":
                    my_fcu.keyframe_points[-1].interpolation = 'LINEAR'
                elif vector["vec_interpolation"] == "teleport":
                    my_fcu.keyframe_points[-1].interpolation = 'CONSTANT'
                my_fcu.update()
            l_in = np.linalg.norm(vec)
            if l_in < self.min_len or ("visible" in vector and vector["visible"] == False):
                obj.hide_render = True
                obj.keyframe_insert(data_path="hide_render", frame=self.cur_frame)
            l_out = self.max_len * self.ratio_to_successor_between_zero_and_one(l_in)
            obj.scale = np.array([l_out, l_out, l_out])
            obj.keyframe_insert(data_path="scale", frame=self.cur_frame)
            if "vec_interpolation" in vector:
                action = bpy.data.actions.get(obj.animation_data.action.name)
                my_fcu = action.fcurves.find("scale", index = 1)
                if vector["vec_interpolation"] == "linear":
                    my_fcu.keyframe_points[-1].interpolation = 'LINEAR'
                elif vector["vec_interpolation"] == "teleport":
                    my_fcu.keyframe_points[-1].interpolation = 'CONSTANT'
                my_fcu.update()
        col = vector["col"] if "col" in vector else None
        color = None
        if col == None:
            color = self.calc_color(l_in)
        else:
            color = self.calc_color(col)
        obj["arrow-color"] = color.get_value_tuple()
        obj.keyframe_insert(data_path='["arrow-color"]', frame=self.cur_frame)

    def get_rot(vec, rot):
        first_rot = mathutils.Matrix.Rotation(rot, 3, np.array([0, 0, 1]))
        v_len = np.linalg.norm(vec)
        vec /= v_len
        axis = np.cross(vec, np.array([0.0, 0.0, 1.0]))
        a_len = np.linalg.norm(axis)
        angle = np.arccos(vec[2])
        if angle < 1.0e-3:
            return first_rot.to_euler()
        if a_len < 1.0e-7:
            rot_mat = mathutils.Matrix.Diagonal([1, -1, -1])
            return (rot_mat @ first_rot).to_euler()

        axis /= a_len
        rot_mat = mathutils.Matrix.Rotation(math.pi, 3, [0, 0, 1]) @ mathutils.Matrix.Rotation(angle, 3, axis) @ first_rot

        return rot_mat.to_euler()

# EDIT THESE LINES TO FIT YOUR SPECIFIC CIRCUMSTANCE

#vec_field = Vector_Field("/path/to/json/file/that/has/the/data.json")
#vec_field.generate_vector_field("/path/to/arrow.obj", "name-of-collection-containing-vectors")
