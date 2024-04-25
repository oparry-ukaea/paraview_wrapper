#!/bin/env bash
nmpi=8
if [ $# -eq 1 ]; then
    nmpi="$1"
elif [ $# -gt 1 ]; then
    echo "start_server.bash: expected 0 or 1 args, got $#"
    exit 1
fi

nrunning=$(pgrep -c pvserver)
if [ "$nrunning" -gt 0 ]; then
    echo "start_server.bash: pvserver already running - $nrunning tasks including mpi"
    exit 2
fi

spack load mpich
mpirun -n "$nmpi" pvserver