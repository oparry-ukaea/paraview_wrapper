from paraview.simple import AnnotateTimeFilter, Show


def add_time_filter(dt, input_data, view, tlbl_settings={}):
    # Extract representation type name to make this usable for multiple types of images, charts
    repr_name = type(view.Representations[0]).__name__
    if len(view.Representations) != 1:
        print(
            f"add_time_filter: Multiple representations detected; using the first one ({repr_name})"
        )

    # Position bottom right, use engineering format by default
    tlbl_settings_int = dict(pos=[0.6, 0.1], fmt=".1E", fontsize=14, init_val=0.0)
    tlbl_settings_int.update(tlbl_settings)

    # Create an 'Annotate Time Filter'
    filter = AnnotateTimeFilter(
        registrationName="annotate_time_filter", Input=input_data
    )

    filter.Format = "Time: {time:" + tlbl_settings_int["fmt"] + "}"
    filter.Scale = dt
    filter.Shift = tlbl_settings_int["init_val"]

    # Show data in view
    # Includes fudge to make this work for different data representations
    if repr_name == "XYChartRepresentation":
        display = Show(filter, view, "ChartTextRepresentation")
        display.LabelLocation = "Any Location"
    elif repr_name == "UnstructuredGridRepresentation":
        display = Show(filter, view, "TextSourceRepresentation")
        display.WindowLocation = "Any Location"
    else:
        print(
            f"add_time_filter: Failed; not set up for [{repr_name}] representation type"
        )

    # Set common filter properties
    display.FontSize = tlbl_settings_int["fontsize"]
    display.Position = tlbl_settings_int["pos"]
