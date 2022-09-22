# Jupyter and Dask on SLURM

This repository contains instructions to setup and run a JupyterLab server and a Dask cluster on a SLURM system, such as the [Spider data processing platform](https://spiderdocs.readthedocs.io) and the [Snellius supercomputer](https://servicedesk.surf.nl/wiki/display/WIKI/Snellius) hosted by [SURF](https://www.surf.nl).

## Installation 

Clone and access this repository:
```shell
git clone http://github.com/RS-DAT/JupyterDaskOnSLURM.git 
cd JupyterDaskOnSLURM
```

The required packages are most easily installed via the `conda` package manager, and they are available from the `conda-forge` channel. In order to install `conda` (and its faster C++ implementation `mamba`) and to configure `conda-forge` as the default channel, download and run the following install script:
```shell
wget https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-x86_64.sh
chmod +x Mambaforge-Linux-x86_64.sh
./Mambaforge-Linux-x86_64.sh
```
After accepting the license term and selecting the installation location (the default is `${HOME}/mambaforge`), type `yes` to initialize Mambaforge. Logout/login to activate.

Create a new environment with Dask, Dask-Jobqueue, JupyterLab and its Dask extension using the provided environment file:
```shell
mamba env create -f environment.yaml
```

Activate the environment and install additional dependencies using `mamba`/`pip`, as required by each use case:
```shell
conda activate jupyter_dask
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
and make the Jupyter config file that will be created after running the previous step readable by the current user only:
```shell
chmod 400 ~/.jupyter/jupyter_server_config.py 
```

### Dask

The repository folder [`config`](./config) contains the configuration files that need to be copied in `~/.config/dask/.` (see [README.md](./config/dask/README.md)).

If you are on **Spider**, you can copy the files by:
```shell
cp -r config/dask/spider/* ~/.config/dask/ 
```

Or on **Snellius**, do:
```shell
cp -r config/dask/snellius/* ~/.config/dask/
```

### dCache

In order to configure access to [the SURF dCache storage](http://doc.grid.surfsara.nl/en/stable/Pages/Service/system_specifications/dcache_specs.html) using [the Filesystem Spec library](https://filesystem-spec.readthedocs.io/en/latest/) and [dCacheFS](https://github.com/NLeSC-GO-common-infrastructure/dcachefs), you can add the following JSON file to `~/.config/fsspec/.` (replace `<MACAROON>` with the actual [token for authentication](http://doc.grid.surfsara.nl/en/latest/Pages/Advanced/storage_clients/webdav.html#sharing-data-with-macaroons)):
```json
{
    "dcache": {
        "api_url": "https://dcacheview.grid.surfsara.nl:22880/api/v1",
        "webdav_url": "https://webdav.grid.surfsara.nl:2880",
        "token": "<MACAROON>",
        "block_size": 0
    }
}
```
URL-paths starting with the `dcache://...` protocol will then be open via dCacheFS by Filesystem Spec. 

## Running 

### Jupyter

Submit a batch job script based on the provided template to start the Jupyter server and the Dask scheduler on a compute node (one might want to change the node specifications depending on the requirements of the analysis running on the same node). Also, change the wall time limit according the needs (the Jupyter server will be killed when the limit is reached). 

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

See [this repository](https://github.com/RS-DAT/JupyterDask-Examples) for some examples that make use of this deployment. 

## Resources

* [Getting Started with Pangeo on HPC](https://pangeo.io/setup_guides/hpc.html)
* [Interactive Use — Dask-jobqueue](http://jobqueue.dask.org/en/latest/interactive.html)
* [Jupyter on the HPC Clusters | Princeton Research Computing](https://researchcomputing.princeton.edu/support/knowledge-base/jupyter)

