import os.path

LOCATIONS = {}
LOCATIONS["repo_root"] = os.path.abspath(os.path.dirname(__file__) + "/..")
LOCATIONS["output_dir"] = os.path.normpath(
    os.path.join(LOCATIONS["repo_root"], "output")
)


def get_output_dir():
    return LOCATIONS["output_dir"]


def get_output_fpath(fname):
    return os.path.join(get_output_dir(), fname)
