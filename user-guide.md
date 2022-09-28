# User guide

The following steps will help you to run a Jupyter server and a Dask cluster on one of the SURF systems running SLURM, such as Spider, Snellius or Lisa (please find information on how to get accesss to SURF infrastructure [here](https://www.surf.nl/en/research-it/apply-for-access-to-compute-services)).

This guide assumes that you have received credentials from SURF, that you are able to access the system via SSH, and that a SSH key pair has been setup for password-less login (see the dedicated SURF guides for [Lisa/Snellius](https://servicedesk.surf.nl/wiki/display/WIKI/SSH#SSH-Bonus2:public-keyauthentication) and [Spider](https://spiderdocs.readthedocs.io/en/latest/Pages/getting_started.html)). 

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

Edit the template job script `scripts/jupyter_dask.bsh`, **uncommenting the block corresponding to the desired SURF system**. The job configuration details can be further customized depending on the specific requirements for the node running the Jupyter server.  

### Dask

The repository `config/dask` directory contains a template Dask configuration file. This file defines the default worker settings in the Dask cluster, and it thus **needs to be edited depending on the SURF system** which we are running on. In particular, **uncomment the correct block in  `config/dask/config.yaml`**, then copy the file to `${HOME}/.config/dask`:
```shell
mkdir -p ~/.config/dask
cp -r config/dask/config.yaml ~/.config/dask/. 
```

The default Dask settings can be further tuned depending on user needs.

### dCache

In order to configure access to [the SURF dCache storage](http://doc.grid.surfsara.nl/en/stable/Pages/Service/system_specifications/dcache_specs.html) via [the Filesystem Spec library](https://filesystem-spec.readthedocs.io/en/latest/) (internally used by Dask and other libraries), you can use the configuration file provided in `config/fsspec`. Edit `config/fsspec/config.json`, **replacing the `<MACAROON>` string with the actual macaroon** (see [this guide](http://doc.grid.surfsara.nl/en/latest/Pages/Advanced/storage_clients/webdav.html#sharing-data-with-macaroons) for information on how to generate it), then copy the file to `${HOME/.config/fsspec}`:
```shell
mkdir -p ~/.config/fsspec
cp -r config/fsspec/config.json ~/.config/fsspec/. 
```

More information on how to read files from the dCache storage are provided in the [documentation of the dCacheFS package](https://dcachefs.readthedocs.io/en/latest/).

## Running 

This repository includes [a Python script](./scripts/runJupyterDaskOnSLURM.py) to start Jupyter and Dask services on a SURF system that has been configured following the steps above. 

Download the script on your local machine by cloning this repository:
```shell
git clone http://github.com/RS-DAT/JupyterDaskOnSLURM.git 
cd JupyterDaskOnSLURM
```

The script requires Python 3 and the [Fabric library](https://www.fabfile.org), which can be installed via `pip`:
```shell
pip install fabric
```

Running the script the first time using the option `--add_platform` queries the user for authentication credentials (username and path to the private ssh-key), storing these in a configuration file for later use:
```shell
python scripts/runJupyterDaskOnSLURM.py --add_platform
```

The script can later be run as:
```shell
python scripts/runJupyterDaskOnSLURM.py --platform <PLATFORM_NAME>
```

A browser window should open up. **Note that it might take few seconds for the Jupyter server to start**, after which you should have access to a JupyterLab interface (login using the password set as above). 

A Dask cluster (with no worker) is started together with the JupyterLab session and it should be listed in the menu appearing when selecting the Dask tab on the left part of the screen. Workers can be added by clicking the "scale" button on the running cluster instance and by selecting the number of desired workers. 

## Shutting down

From the Dask tab in the Jupyter interface, click "shutdown" on a running cluster instance to kill all workers and the scheduler (a new cluster based on the default configurations can be re-created by pressing the "+" button). 

From the Jupyter interface, select "File > Shutdown" to stop the Jupyter server and release resources.

If the job running the Jupyter server and the Dask scheduler is killed, the Dask workers will also be killed shortly after (configure this using the `death-timeout` key in the config file).

## Throubleshooting

### Manual deployment

As an alternative to the deployment script, the Jupyter and Dask services can  be started via the the following "manual" procedure.

Login to the SURF system, then submit a batch job script based on the template provided in `scripts/jupyter_dask.bsh` to start the Jupyter server and the Dask scheduler on a compute node: 
```shell
sbatch scripts/jupyter_dask.bsh
```

Copy the `ssh` command printed in the job stdout (file `slurm-<JOB_ID>.out`). It should look like:
```shell
ssh -i /path/to/private/ssh/key -N -L 8889:NODE:8888 USER@sssssss.surf.nl
``` 

Paste the command in a new terminal window **on your local machine** (modify the path to the private key). You can now access the Jupyter session from your browser at `localhost:8889`.
