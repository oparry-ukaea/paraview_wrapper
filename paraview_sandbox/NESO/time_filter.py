from paraview.simple import AnnotateTimeFilter, Show


def add_time_filter(dt, input_data, view, tlbl_settings={}):
    # Position bottom right, use engineering format by default
    tlbl_settings_int = dict(pos=[0.6, 0.1], fmt=".1E")
    tlbl_settings_int.update(tlbl_settings)

    # Create an 'Annotate Time Filter'
    filter = AnnotateTimeFilter(
        registrationName="annotate_time_filter", Input=input_data
    )

    filter.Format = "Time: {time:" + tlbl_settings_int["fmt"] + "}"
    filter.Scale = dt

    # show data in view
    display = Show(filter, view, "ChartTextRepresentation")

    # Set filter properties
    display.LabelLocation = "Any Location"
    display.Position = tlbl_settings_int["pos"]
