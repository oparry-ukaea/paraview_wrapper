from examples import (
    lapd_ne_blob_split,
    t4c2_img,
    t4c3_movie_coupled_fades_zoomed_out,
    t4c3_movie_fluid_full,
    t4c3_movie_coupled_zoomed_out,
    t4c3_movie_w_remote,
    t4c3_movie_zoomed_blob,
)


# Render LAPD blob-splitting sim
lapd_sim_path = ""
lapd_ne_blob_split(lapd_sim_path)


# Render fluid-particle image from t4c2 report
t4c2_path = ""
t4c2_img(t4c2_path)


# t4c3 coupled movies on remote host
t4c3_coupled_path_remote = ""
host_ip = ""
t4c3_movie_coupled_zoomed_out(t4c3_coupled_path_remote, host_ip)
t4c3_movie_w_remote(t4c3_coupled_path_remote, host_ip)

# t4c3 fluid-only movie on remote host
t4c3_fluid_only_path_remote = ""
t4c3_movie_fluid_full(t4c3_fluid_only_path_remote, host_ip)


# Render t4c3 movies locally
t4c3_coupled_path_local = ""
t4c3_movie_coupled_fades_zoomed_out(t4c3_coupled_path_local)
t4c3_movie_zoomed_blob(t4c3_coupled_path_local)
