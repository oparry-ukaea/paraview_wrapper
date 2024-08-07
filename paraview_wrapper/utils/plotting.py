predef_colors = dict(r=[1.0, 0.0, 0.0], g=[0.0, 1.0, 0.0], b=[0.0, 0.0, 1.0])


def get_color_array(name, arg):
    if isinstance(arg, str):
        vals = predef_colors.get(arg, predef_colors["r"])
    elif isinstance(arg, list):
        if len(arg) != 3:
            raise TypeError(
                f"get_color_array: expected a list with 3 elements, but got {len(arg)} elements"
            )
        vals = arg
        for val in vals:
            if not isinstance(val, float):
                raise TypeError(
                    f"get_color_array: expected all floats in values array but got {type(val)}"
                )
    result = [name]
    result.extend([str(v) for v in vals])
    return result
