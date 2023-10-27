from paraview_sandbox.NESO import gen_movie, gen_img
from paraview_sandbox.utils import get_desktop_dir, get_output_dir, avi_to_mp4


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


def t4c2_img(data_dir, output_dir=get_desktop_dir()):
    """
    Image of 2D-coupled sim at the output time used in the t4c2 report.
    """
    gen_img(
        data_dir=data_dir,
        output_dir=output_dir,
        output_time=39.0,
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


def t4c3_movie_fluid_full(data_dir, host, output_dir=get_desktop_dir()):
    """
    Movie showing turbulence in fluid-only t4c3 sim (params optimised to boost turbulence).
    Given to WA, ET for demos at IAEA FEC.
    """
    output_basename = "t4c3_fluid-only_turb"
    gen_movie(
        "ne",
        data_dir=data_dir,
        output_dir=output_dir,
        output_fname=f"{output_basename}.avi",
        animation_settings=dict(FrameRate=20, FrameWindow=[1, 160], Quality=2),
        cbar_settings=dict(title="Δn"),
        data_settings=dict(
            range=[-15.0, 15.0],
            opacities=[(-15.0, 1.0), (0.0, 0.0), (15.0, 1.0)],
        ),
        view_settings=dict(
            pos=[21.68, 9.41, 11.91],
            fpt=[0.0, 0.0, 5.0],
            up=[-0.24, -0.15, 0.96],
            pscale=6.1,
        ),
        vtu_basename="hw_",
        host=host,
    )
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
