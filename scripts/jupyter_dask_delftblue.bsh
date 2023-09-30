#!/bin/bash
### Initialize the server
#SBATCH --partition=compute ## one of 'compute', 'gpu', 'memory'
#SBATCH --ntasks=1
#SBATCH --time=23:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=4G
#SBATCH --account=innovation ## replace with research-<faculty>-<department>. This will enable to request more resources.

source ~/.bashrc
conda activate jupyter_dask

node=`hostname -s`
port=`shuf -i 8400-9400 -n 1`
if [ -z ${lport:+x} ]; then lport="8889" ; else lport=${lport}; fi

echo "Run the following on your local machine: "
echo "ssh -i /path/to/private/ssh/key -N -L ${lport}:${node}:${port} ${USER}@login.delftblue.tudelft.nl"

jupyter lab --no-browser --port=${port} --ip=${node}
