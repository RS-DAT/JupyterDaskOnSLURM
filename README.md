# Jupyter and Dask on SLURM

This repository contains instructions  to setup and run a JupyterLab server and a Dask cluster on a SLURM system. Examples have been run on the [Spider data processing platform](https://spiderdocs.readthedocs.io) hosted by [SURF](https://www.surf.nl).

## Installation 

Clone and access this repository:
```shell
git clone http://github.com/RS-DAT/JupyterDaskOnSLURM.git 
cd JupyterDaskOnSLURM
```

The required packages are most easily installed via the `conda` package manager. In order to install it, download and run the Miniconda install script:
```shell
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
chmod +x Miniconda3-latest-Linux-x86_64.sh
./Miniconda3-latest-Linux-x86_64.sh
```
After accepting the license term and selecting the installation location (the default is `${HOME}/miniconda3`), type `yes` to initialize Miniconda3. Logout/login to activate.

Create a new environment with Dask, Dask-Jobqueue, JupyterLab and its Dask extension using the provided environment file:
```shell
conda env create -f environment.yaml
```

Activate the environment and install additional dependencies using `conda`/`pip`, as required by each use case:
```shell
conda activate dask_jupyter
conda install ...
pip install ...
```

## Configuration

### Jupyter

Configure the password to access the JupyterLab interface:
```shell
jupyter server --generate-config
jupyter server password
```
and make the Jupyter config file readable by the current user only:
```shell
chmod 400 ~/.jupyter/jupyter_server_config.py 
```

### Dask

The repository folder [`config`](./config) contains the configuration files that need to be copied in `~/.config/dask/.` (see [README.md](./config/dask/README.md)).

If you are on **Spider**, you can copy the file by:
```shell
cp -r config/dask/spider/* ~/.config/dask/ 
```

Or on **Snellius**, do:
```shell
cp -r config/dask/snellius/* ~/.config/dask/
```


## Running 

### Jupyter

Submit a batch job script based on the provided [template](./scripts/jupyter_dask.bsh) to start the Jupyter server and the Dask scheduler on a compute node (one might want to change the node specifications depending on the requirements of the analysis running on the same node). Also, change the wall time limit according the needs (the Jupyter server will be killed when the limit is reached). 

If you are on **Spider**, run:
```shell
sbatch scripts/jupyter_dask_spider.bsh
```

On **Snellius**, you can run:
```shell
sbatch scripts/jupyter_dask_snellius.bsh
```

Copy the `ssh` command printed in the job stdout (file `slurm-<JOB_ID>.out`). It should look like:
```shell
ssh -i /path/to/private/ssh/key -N -L 8889:NODE:8888 USER@sssssss.surf.nl
``` 

Paste the command in a new terminal window on your local machine (modify the path to the private key used to connect to the supercomputer). You can now access the Jupyter session running on the supercomputer from your browser at `localhost:8889`. Select "File > Shutdown" to kill the server and release resources. 

### Dask 

A Dask cluster (with no worker) is started together with the JupyterLab session (it should be listed in the menu appearing when selecting the Dask tab on the left part of the screen). Workers can be added by clicking the "scale" button on the running cluster instance and by selecting the number of desired workers. Press "shutdown" to kill all workers and the scheduler. If the job running the Jupyter server and the Dask scheduler is killed, the Dask workers will also be killed shortly (configure this using the `death-timeout` key in the config file).  A new cluster based on the default configurations can be created by pressing the "+" button. A cluster with different specifications can be created in a Python notebook/console by instantiating a `SLURMCluster()` object with the desired custom features.  

## Examples

* [Work with STAC Catalogs on the dCache Storage](./examples/01-STAC-on-dCache). 

## Resources

* [Getting Started with Pangeo on HPC](https://pangeo.io/setup_guides/hpc.html)
* [Interactive Use — Dask-jobqueue](http://jobqueue.dask.org/en/latest/interactive.html)
* [Jupyter on the HPC Clusters | Princeton Research Computing](https://researchcomputing.princeton.edu/support/knowledge-base/jupyter)

