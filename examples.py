from paraview_sandbox.NESO import fluid_slice, gen_movie, gen_img, line_plot_1d, PyExpr
from paraview_sandbox.utils import (
    avi_to_mp4,
    get_desktop_dir,
    get_nektar_params,
    get_output_dir,
)


def driftwave_movie(
    data_dir,
    host="",
    output_basename="driftwave",
    output_dir=get_desktop_dir(),
    animation_settings=dict(FrameRate=15, FrameWindow=[1, 200], Quality=2),
    max_val=1.0,
    tlbl_settings=dict(pos=[0.02, 0.02], fontsize=32),
    view_settings=dict(
        pos=[6.4, 0.0, 109.3],
        fpt=[6.4, 0.0, 0.0],
        up=[0.0, 1, 0.0],
        pscale=23.4,
    ),
):
    """
    Movie showing turbulence in 2D HW (nektar-driftwave).
    """

    # Set checkpoint dt from nektar params
    nek_params = get_nektar_params(data_dir)
    dt_chk = nek_params["TimeStep"] * nek_params["IO_CheckSteps"]

    gen_movie(
        "n",
        data_dir=data_dir,
        output_dir=output_dir,
        dt=dt_chk,
        output_fname=f"{output_basename}.avi",
        animation_settings=animation_settings,
        cbar_settings=dict(
            title="Δn", label_fontsize=20, pos=[0.9, 0.06], title_fontsize=20
        ),
        data_settings=dict(
            # opacities=[(-max_val, 1.0), (0.0, 0.0), (max_val, 1.0)],
            range=[-max_val, max_val],
            render_type="Surface",
        ),
        tlbl_settings=tlbl_settings,
        view_settings=view_settings,
        vtu_basename="square_quads_",
        host=host,
    )
    avi_to_mp4(output_dir, output_basename)


def lapd_ne_blob_split(data_dir, output_dir=get_desktop_dir()):
    """
    Movie of ne in simplified LAPD sim, showing blob splitting.
    """
    output_basename = "lapd_blob-split"
    gen_movie(
        "ne",
        data_dir=data_dir,
        output_dir=output_dir,
        output_fname=f"{output_basename}.avi",
        view_settings=dict(
            pos=[-30, 13, -10], fpt=[0.0, 0.0, 8.0], up=[0.25, 1.0, 0.25], pscale=6.1
        ),
        data_settings=dict(range=[1.0, 1.4], opacities=[(1.0, 0.0), (1.4, 1.0)]),
    )
    avi_to_mp4(get_desktop_dir(), output_basename)


def ne_Ge_line_plot(
    data_dir,
    host="",
    output_dir=get_desktop_dir(),
    animation_settings={},
    line_dim=0,
):
    nek_params = get_nektar_params(data_dir)

    # Read params from the Nektar session file
    delta = nek_params["delta"]
    T = nek_params.get("T", 1.0)
    nstar = nek_params.get("nstar", 1.0)
    dt_chk = nek_params["TimeStep"] * nek_params["IO_CheckSteps"]
    series_colors = {}
    series_colors["ne Equilibrium"] = "g"
    series_colors["Ge Equilibrium"] = "r"
    plot_settings = dict(
        xlabel="z",
        xrange=[0.0, 2.0],
        yrange=[-1.2, 1.1 * (delta + 1 / delta)],
        colors=series_colors,
        legend_pos=[260, 80],
    )
    output_basename = f"1Din{line_dim+1}DDoutflow_delta{delta}_ne-Ge_profs"

    tlbl_settings = {}
    # Add some expressions to the line plot
    nstar_rootT = f"{nstar}*sqrt({T})"
    z_str = f"(inputs[0].Points[:,{line_dim}]-1)"
    c_str = f"{nstar_rootT}*({delta}+1/{delta})"
    R_str = f"{nstar_rootT}*sqrt({delta}**2+1/{delta}**2+2-4*{z_str}**2)"
    ne_str = f"({c_str}+{R_str})/2/{T}"
    # u_str = f"({c_str}-{R_str})/2/{nstar}/{z_str}"
    # Ge_str = f"({ne_str})*({u_str})"
    Ge_str = f"({nstar})*({z_str})"
    exprs_to_plot = [
        PyExpr(
            "ne Equilibrium",
            ne_str,
        ),
        PyExpr(
            "Ge Equilibrium",
            Ge_str,
        ),
    ]

    line_plot_1d(
        ["ne", "Ge"],
        data_dir,
        output_dir,
        host=host,
        line_dim=line_dim,
        dt=dt_chk,
        animation_settings=animation_settings,
        exprs_to_plot=exprs_to_plot,
        output_basename=output_basename,
        plot_settings=plot_settings,
        tlbl_settings=tlbl_settings,
        vtu_basename="outflow1d",
    )
    avi_to_mp4(output_dir, output_basename)


def t4c2_1d_profs(
    data_dir,
    output_basename="t4c2_1dprofs",
    output_dir=get_desktop_dir(),
    animation_settings={},
):
    """
    Plot rho, u, T from 1D / 1D-in-2D SimpleSOL prob. Also demonstrates setting custom colors and linestyles
    """

    # Read params from the Nektar session file
    nek_params = get_nektar_params(data_dir)
    dt_chk = nek_params["TimeStep"] * nek_params["IO_CheckSteps"]
    plot_settings = dict(
        xrange=[0.0, 110.0],
        yrange=[-1.2, 2.5],
        lstys=dict(u=1, T=1),
        colors=dict(rho="b", u="g", T="r"),
    )

    tlbl_settings = {}

    # Store paraview data accessor strings to make expressions more readable
    rho = "inputs[0].PointData['rho']"
    rhou = "inputs[0].PointData['rhou']"
    E = "inputs[0].PointData['E']"
    gamma = nek_params["Gamma"]
    R = nek_params["GasConstant"]

    # Add u and T to the plot
    exprs_to_plot = [
        PyExpr("u", f"{rhou}/inputs[0].PointData['rho']"),
        PyExpr("T", f"({E}-({rhou}*{rhou}/{rho})/2)/{rho}*({gamma}-1.0)/{R}"),
    ]

    # Make line plot (rho is the only non-derived variable to be plotted, others are generated by expressions)
    line_plot_1d(
        ["rho"],
        data_dir,
        output_dir,
        dt=dt_chk,
        pt2=[110.0, 0.0, 0.0],
        animation_settings=animation_settings,
        exprs_to_plot=exprs_to_plot,
        output_basename=output_basename,
        plot_settings=plot_settings,
        tlbl_settings=tlbl_settings,
    )


def t4c2_img(data_dir, output_dir=get_desktop_dir()):
    """
    Image of 2D-coupled sim at the output time used in the t4c2 report.
    """
    gen_img(
        data_dir,
        "rho",
        39.0,
        output_dir=output_dir,
        part_data_fname="SimpleSOL_particle_trajectory.h5part",
    )


def t4c3_movie_coupled_fades_zoomed_out(data_dir, output_dir=get_desktop_dir()):
    """
    Movie showing (fluid-only) ne in coupled t4c3 sim.
    Color scale config is appropriate for blob that dissipates (high-ish alpha)
    """
    output_basename = "t4c3_coupled_zoomed-out_fades"
    gen_movie(
        "ne",
        data_dir=data_dir,
        output_dir=output_dir,
        output_fname=f"{output_basename}.avi",
        vtu_basename="hw_",
        animation_settings=dict(FrameRate=8, FrameWindow=[1, 200], Quality=2),
        cbar_settings=dict(title="$n_e~/~10^{17} m^{-3}$"),
        view_settings=dict(
            pos=[4.2, 19.0, 3.2], fpt=[0.0, 0.0, 5.0], up=[1.0, -0.2, 0.1], pscale=6.1
        ),
        data_settings=dict(
            range=[-0.7, 6.0],
            opacities=[(-0.7, 0.0), (0.0, 0.0), (0.8, 0.15), (6.0, 1.0)],
        ),
    )
    avi_to_mp4(get_desktop_dir(), output_basename)


def t4c3_movie_coupled_zoomed_out(data_dir, host):
    """
    Coupled ne movie (showing fluid only) rendered on a remote host and converted to mp4.
    Shows evolution of blob.
    """
    output_basename = "t4c3_coupled_zoomed-out"
    gen_movie(
        "ne",
        data_dir=data_dir,
        output_dir=get_desktop_dir(),
        output_fname=f"{output_basename}.avi",
        vtu_basename="hw_",
        animation_settings=dict(
            FrameRate=8, FrameWindow=[1, 200], ImageResolution=[1920, 1080], Quality=2
        ),
        cbar_settings=dict(len=0.3, pos=[0.9, 0.05], title="$n_e~/~10^{17} m^{-3}$"),
        view_settings=dict(
            pos=[23.6, 0.14, 4.1], fpt=[0.0, 0.0, 5.0], up=[0.3, 0.03, 1.0], pscale=6.12
        ),
        data_settings=dict(
            range=[-0.7, 6.0],
            opacities=[(-0.7, 0.0), (0.0, 0.0), (0.8, 0.15), (6.0, 1.0)],
            render_type="Volume",
        ),
        host=host,
    )
    avi_to_mp4(get_desktop_dir(), output_basename)


def t4c3_movie_fluid_full(data_dir, host):
    hw3d_fluid_only_movie(data_dir, host=host, output_basename="t4c3_fluid-only_turb")


def t4c4_HW3D_imgs(data_dir, output_dir=get_desktop_dir()):
    """
    Images of a 3DHW sim used in the t4c4 report.
    """
    for output_time in [0.0, 50.0, 100.0, 160.0]:
        gen_img(
            data_dir,
            "ne",
            output_time,
            fluid_props=dict(
                cbar_pos=[0.03, 0.04],
                cbar_orient="Vertical",
                cbar_range=[-12, 12],
                cbar_title=r"n$_e$",
                opacities=[(-12.0, 1.0), (0.0, 0.0), (12.0, 1.0)],
                render_mode="Resample To Image",
            ),
            fluid_vtu_basename="hw",
            fluid_view_settings=dict(
                fpt=[0.0, 0.0, 5.0],
                pos=[20.4, -7.7, -4.3],
                pscale=6.12,
                up=[-0.4, 0.090, -0.91],
            ),
            output_basename="t4c4_HW3D",
            output_dir=output_dir,
        )


def hw3d_fluid_only_movie(
    data_dir,
    var="ne",
    host="",
    convert_to_mp4=False,
    output_basename="3DHW",
    output_dir=get_desktop_dir(),
    animation_settings=dict(FrameRate=20, FrameWindow=[1, 160], Quality=2),
    max_val=15.0,
    tlbl_settings={},
    view_settings=dict(
        pos=[21.68, 9.41, 11.91],
        fpt=[0.0, 0.0, 5.0],
        up=[-0.24, -0.15, 0.96],
        pscale=6.1,
    ),
):
    """
    Movie showing turbulence in fluid-only t4c3 sim (params optimised to boost turbulence).
    Given to WA, ET for demos at IAEA FEC.
    """

    # Set checkpoint dt from nektar params
    nek_params = get_nektar_params(data_dir)
    dt_chk = nek_params["TimeStep"] * nek_params["IO_CheckSteps"]

    gen_movie(
        var,
        data_dir=data_dir,
        output_dir=output_dir,
        dt=dt_chk,
        output_fname=f"{output_basename}.avi",
        animation_settings=animation_settings,
        cbar_settings=dict(title="Δn"),
        data_settings=dict(
            range=[-max_val, max_val],
            opacities=[(-max_val, 1.0), (0.0, 0.0), (max_val, 1.0)],
        ),
        tlbl_settings=tlbl_settings,
        view_settings=view_settings,
        vtu_basename="hw_",
        host=host,
    )
    if convert_to_mp4:
        avi_to_mp4(output_dir, output_basename)


def t4c3_movie_w_remote(data_dir, host, output_dir=get_desktop_dir()):
    """
    Movie of vorticity in t4c3 coupled sim.
    """
    output_basename = "t4c3_w"
    gen_movie(
        "w",
        data_dir=data_dir,
        output_dir=get_desktop_dir(),
        output_fname=f"{output_basename}.avi",
        vtu_basename="hw_",
        animation_settings=dict(FrameRate=8, FrameWindow=[40, 200], Quality=2),
        cbar_settings=dict(title="$w$"),
        view_settings=dict(pos=[19.0, 9.6, 15.4], up=[-0.15, 0.85, -0.51]),
        data_settings=dict(
            range=[0.01, 0.1],
            render_mode="Projected tetra",
            opacities=[(0.01, 0.0), (0.03, 0.0), (0.07, 0.5), (0.1, 1.0)],
        ),
        host=host,
    )
    avi_to_mp4(get_desktop_dir(), output_basename)


def t4c3_movie_zoomed_blob(data_dir, output_dir=get_desktop_dir()):
    """
    Zoomed-in movie of ionised blob (density) forming in t4c3 coupled sim.
    Used in a talk by Ian C, also given to WA, ET for demos at IAEA FEC.
    """

    output_basename = "t4c3_coupled-zoom"
    gen_movie(
        "ne",
        data_dir=data_dir,
        output_dir=output_dir,
        output_fname=f"{output_basename}.avi",
        particle_fname="particle_trajectory.h5part",
        vtu_basename="hw_",
        animation_settings=dict(
            FrameRate=5, FrameWindow=[1, 45], ImageResolution=[1104, 789], Quality=2
        ),
        cbar_settings=dict(title="Δn", pos=[0.88, 0.06]),
        view_settings=dict(
            pos=[2.72, 0.53, 0.28],
            fpt=[1.55, 0.64, 3.36],
            up=[0.89, -0.30, 0.35],
            show_axes_grid=0,
        ),
        data_settings=dict(
            range=[0.0, 7.5],
            opacities=[(0.00, 0.0), (7.5, 1.0)],
        ),
        particle_props=dict(
            cbar_len=0.3,
            cbar_pos=[0.04, 0.89],
            cbar_title="Neutral particle weight",
            psize=2.5,
        ),
    )
    avi_to_mp4(get_desktop_dir(), output_basename)


def hw2d_comp_slice(
    data_dir,
    var,
    chk_num=None,
    host="",
    output_basename="",
    output_dir=get_desktop_dir(),
    animation_settings=dict(FrameRate=20, FrameWindow=[1, 100], Quality=2),
    tlbl_settings={},
    fluid_view_settings=dict(
        pos=[8.15e-3, 8.15e-3, 5.043335426733482],
        fpt=[8.15e-3, 8.15e-3, 5.0],
        up=[0.0, 1.0, 0.0],
        pscale=5.000013284482842,
        show_axes_grid=1,
        show_orient_axes=0,
    ),
):
    max_vals = dict(ne=2e-11, w=0.2, phi=5e-8)
    fluid_props = dict(cbar_orient="Vertical", cbar_pos=[0.05, 0.05])
    if var in max_vals:
        fluid_props["cbar_range"] = [-max_vals[var], max_vals[var]]

    # Compute dt if no single chk file specified (i.e. for animations)
    dt_chk = None
    if chk_num is None:
        # Set checkpoint dt from nektar params
        nek_params = get_nektar_params(data_dir)
        dt_chk = nek_params["TimeStep"] * nek_params["IO_CheckSteps"]
        unit = tlbl_settings.get("unit", "")
        if unit == "us":
            dt_chk /= nek_params["omega_ci"] * 1e-6

    fluid_slice(
        data_dir,
        var,
        dt=dt_chk,
        animation_settings=animation_settings,
        output_time=chk_num,
        host=host,
        output_basename=output_basename,
        output_dir=output_dir,
        slice_settings={},
        fluid_props=fluid_props,
        fluid_view_settings=fluid_view_settings,
        tlbl_settings=tlbl_settings,
    )


def hw3d_comp_movie(
    data_dir,
    host="",
    output_basename="",
    output_dir=get_desktop_dir(),
    animation_settings=dict(FrameRate=20, FrameWindow=[1, 100], Quality=2),
    max_val=0.1,
    tlbl_settings={},
    view_settings=dict(
        pos=[8.15e-3, 8.15e-3, -14.3],
        fpt=[8.15e-3, 8.15e-3, 5.0],
        up=[0.0, 1.0, 0.0],
        pscale=0.009276864953126482,
        show_axes_grid=1,
        show_orient_axes=0,
    ),
):
    """
    Slice movie for comparison of H3 / NESO HW sims
    """

    # # Set checkpoint dt from nektar params
    # nek_params = get_nektar_params(data_dir)
    # dt_chk = nek_params["TimeStep"] * nek_params["IO_CheckSteps"]
    raise NotImplementedError("hw3d_comp_movie not finished yet")
    # avi_to_mp4(output_dir, output_basename)
