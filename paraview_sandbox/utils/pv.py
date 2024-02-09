def get_data_dim(vtu_data):
    info = vtu_data.GetDataInformation()
    bounds = info.GetBounds()
    for idim in [3, 2, 1]:
        if bounds[2 * idim - 1] > bounds[2 * idim - 2]:
            return idim


def gen_opacity_pts(opacity_vals):
    # Check types
    try:
        tmp_it1 = iter(opacity_vals)
        tmp_it2 = iter(opacity_vals[0])
        if len(opacity_vals[0]) != 2:
            raise TypeError
    except TypeError:
        print("opacity_values must be a list of 2-tuples [(val1,op1),(val2,op2)...]")
        raise

    pts = []
    for val_op in opacity_vals:
        pts.extend(val_op)
        pts.extend((0.5, 0.0))
    return pts
