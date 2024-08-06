import ffmpeg
import os.path


def avi_to_gif(
    common_dir,
    fbase,
    fpath_in="",
    fpath_out="",
    overwrite_output=True,
    ffmpeg_output_options={},
):
    if not os.path.isdir(common_dir):
        raise FileNotFoundError(f"avi_to_gif: No directory at {common_dir}")
    if not fpath_in:
        fpath_in = os.path.join(common_dir, fbase + ".avi")
    if not os.path.isfile(fpath_in):
        raise FileNotFoundError(f"avi_to_gif: No input file at {fpath_in}")
    if not fpath_out:
        fpath_out = os.path.join(common_dir, fbase + ".gif")
    # ffmpeg_output_options_int = {"vf": "scale=0:-1:flags=lanczos", "vcodec": "pam"}
    # This seems to work more reliably
    ffmpeg_output_options_int = {
        "filter_complex": "[0:v] split [a][b];[a] palettegen [p];[b][p] paletteuse",
    }
    ffmpeg_output_options_int.update(ffmpeg_output_options)
    ffmpeg.input(fpath_in, f="avi").output(
        fpath_out, f="gif", **ffmpeg_output_options_int
    ).run(overwrite_output=overwrite_output)


def avi_to_mp4(
    common_dir,
    fbase,
    fpath_in="",
    fpath_out="",
    overwrite_output=True,
    ffmpeg_output_options={},
):
    if not os.path.isdir(common_dir):
        raise FileNotFoundError(f"avi_to_mp4: No directory at {common_dir}")
    if not fpath_in:
        fpath_in = os.path.join(common_dir, fbase + ".avi")
    if not os.path.isfile(fpath_in):
        raise FileNotFoundError(f"avi_to_mp4: No input file at {fpath_in}")
    if not fpath_out:
        fpath_out = os.path.join(common_dir, fbase + ".mp4")
    ffmpeg_output_options_int = dict(
        vcodec="libx264", vf="pad=ceil(iw/2)*2:ceil(ih/2)*2"
    )
    ffmpeg_output_options_int.update(ffmpeg_output_options)
    ffmpeg.input(fpath_in, f="avi").output(
        fpath_out, f="mp4", **ffmpeg_output_options_int
    ).run(overwrite_output=overwrite_output)
