# User guide

The following steps will help you to run a Jupyter server and a Dask cluster on one of the SURF systems running SLURM, such as Spider, Snellius or Lisa (please find information on how to get accesss to SURF infrastructure [here]()).

This guide assumes that you have received credentials from SURF, and that you are able to access the system via SSH (see the dedicated SURF guides for [Lisa/Snellius]() and [Spider]()). 

## Installation 

Login to the SURF system from your terminal, then clone and access this repository:
```shell
git clone http://github.com/RS-DAT/JupyterDaskOnSLURM.git 
cd JupyterDaskOnSLURM
```

The required packages are most easily installed via the `conda` package manager, and they are available from the `conda-forge` channel. In order to install `conda` (and its faster C++ implementation `mamba`) and to configure the `conda-forge` channel as the default channel, download and run the following install script:
```shell
wget https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-x86_64.sh
chmod +x Mambaforge-Linux-x86_64.sh
./Mambaforge-Linux-x86_64.sh
```
After accepting the license term and selecting the installation location (the default is `${HOME}/mambaforge`), type `yes` to initialize Mambaforge. Logout/login to activate.

Create a new environment using the conda environment file provided in this repository:
```shell
mamba env create -f environment.yaml
```

Activate the environment and install additional dependencies using `mamba`/`pip`, as required by each use case:
```shell
mamba activate jupyter_dask
mamba install ...
pip install ...
```

## Configuration

After having created the environment, we need to configure few settings.

### Jupyter

Configure the password to access Jupyter:
```shell
jupyter server --generate-config
jupyter server password
```
and make the Jupyter config file that is created after running the previous step readable by the current user only:
```shell
chmod 400 ~/.jupyter/jupyter_server_config.py 
```

### Dask

The repository `config/dask` directory contains a template Dask configuration file. This file defines the default worker settings in the Dask cluster, and it thus **needs to be edited depending on the SURF system** which we are running on. In particular, **uncomment the correct block in  `config/dask/config.yaml`**, then copy the file to `${HOME}/.config/dask`:
```shell
mkdir -p ~/.config/dask
cp -r config/dask/config.yaml ~/.config/dask/. 
```

[This README file](./config/dask/README.md) provides more information on the Dask default settings, which can be further tuned depending on user needs.

### dCache

In order to configure access to [the SURF dCache storage](http://doc.grid.surfsara.nl/en/stable/Pages/Service/system_specifications/dcache_specs.html) via [the Filesystem Spec library](https://filesystem-spec.readthedocs.io/en/latest/) (internally used by Dask and other libraries), you can use the configuration file provided in `config/fsspec`. Edit `config/fsspec/config.json`, **replacing the `<MACAROON>` string with the actual macaroon** (see [this guide](http://doc.grid.surfsara.nl/en/latest/Pages/Advanced/storage_clients/webdav.html#sharing-data-with-macaroons) for information on how to generate it), then copy the file to `${HOME/.config/fsspec}`:
```shell
mkdir -p ~/.config/fsspec
cp -r config/fsspec/config.json ~/.config/fsspec/. 
```

More information on how to read files from the dCache storage are provided in the [documentation of the dCacheFS package](https://dcachefs.readthedocs.io/en/latest/).

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
