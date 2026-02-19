# User guide

The following steps will help you to run a Jupyter server and a Dask cluster on a SLURM cluster. This guide has been particularly tailored to the SURF systems [Spider](https://spiderdocs.readthedocs.io) and [Snellius](https://servicedesk.surf.nl/wiki/spaces/WIKI/pages/30660184/Snellius). Find information on how to get access to SURF infrastructure [here](https://www.surf.nl/en/research-it/apply-for-access-to-compute-services). The procedure described here have also been tested to some extent on the [DelftBlue Supercomputer at TU Delft](https://doc.dhpc.tudelft.nl/delftblue/).

The guide discusses two alternative routes:
* the first one involves the usage of the [`jupyterdask`](./tools/jupyterdask/) command-line tool, which represents a convenient method to start and connect to Jupyter and Dask on the remote cluster without having to explicitly logging in to the system. This should be the preferred approach for ease-of-use and when basic configurations are sufficient. See the ["Deployment via the `jupyterdask` command-line tool"](#deployment-via-the-jupyterdask-command-line-tool) section below.
* the second approach describes the "manual" steps that can be taken in order to deploy Jupyter and Dask on a compute node of the remote cluster. These are the steps that could be followed when total control on settings is needed and more advanced configurations are required. See the ["Manual deployment"](#manual-deployment) section below.

> [!NOTE]
> This guide assumes the following:
> * you have received credentials to the cluster from SURF (or TU Delft);
> * you are able to access the system via SSH;
> * you have set up a SSH key pair for password-less login, see the dedicated SURF guides for [Snellius](https://servicedesk.surf.nl/wiki/spaces/WIKI/pages/30660216/Connecting+to+the+system), [Spider](https://spiderdocs.readthedocs.io/en/latest/Pages/getting_started.html), or [DelftBlue](https://doc.dhpc.tudelft.nl/delftblue/Remote-access-to-DelftBlue/).

**Contents:**

- [Deployment via the `jupyterdask` command-line tool](#deployment-via-the-jupyterdask-command-line-tool)
  - [Installation](#installation)
  - [Deployment](#deployment)
  - [Shutting down](#shutting-down)
- [Manual deployment](#manual-deployment)
- [Recommendations for Python environments](#recommendations-for-python-environments)
- [Access to dCache](#access-to-dcache)

## Deployment via the `jupyterdask` command-line tool

We provide [a Python command-line tool](./tools/jupyterdask/) that allows one to start Jupyter and Dask services on a compute node of a SLURM cluster (Snellius/Spider/etc.) from your local machine and to connect to the system via a single command.

### Installation

The `jupyterdask` tool should only be installed **on your local machine**. It can be installed with `pip` as:

```shell
pip install -e "git+https://github.com/RS-DAT/JupyterDaskOnSLURM.git#egg=jupyterdask&subdirectory=tools/jupyterdask"
```

Verify that installation has succeeded by running the following command, which should print out the installed version of `jupyterdask`:

```shell
jupyterdask --version
# jupyterdask 0.3.0
```

### Deployment

After installing `jupyterdask` locally, you can start a remote JupyterLab session with the following command:

```shell
jupyterdask -i /path/to/ssh/private/key --python /path/to/python --run host
```

The following arguments should be provided:
* `-i`: path to the private key used for authentication on the remote cluster.
* `--python`: Python executable on the remote cluster. This may include commands to activate a virtual environment, e.g. `--python='conda activate myenv && python'` or `--python='source /path/to/venv/bin/activate && python'`. See also section on ["Recommendations for Python environments"](#recommendations-for-python-environments).
* `--run`: start Jupyter on the remote cluster and connect to the interface.
* `host`: it can be provided as `USER@HOSTNAME` (where `USER` is you user name on the remote cluster and `HOSTNAME` is e.g. `spider.surf.nl` or `snellius.surf.nl`) or simply as `HOST` (if a host is defined in `~/.ssh/config`).

A browser window should open up. **Note that it might take few seconds for the Jupyter server to start**, after which you should have access to a JupyterLab session. A Dask cluster (with no worker) is started together with the JupyterLab session, and it should be listed in the menu appearing when selecting the Dask tab on the left part of the screen. Workers can be added by clicking the "scale" button on the running cluster instance and by selecting the number of desired workers.

Additional options for the `jupyterdask` command-line tool include:
* `-p`: Set local port where to forward the remote Jupyter server (default is 8888).
* `--timeout`: time (in seconds) waited for the remote Jupyter server to start (default is 120).
* `--template`: use the given custom file as template for the job script.
* `--log-dir`: path where job scripts and log files are saved on the remote cluster (default is `${HOME}/.jupyterdask`).

See all options with `jupyterdask --help`.

### Shutting down

From the Dask tab in the Jupyter interface, click "shutdown" on a running cluster instance to kill all workers and the scheduler (a new cluster based on the default configurations can be re-created by pressing the "+" button).

From the Jupyter interface, select "File > Shutdown" to stop the Jupyter server and release resources.

If the job running the Jupyter server and the Dask scheduler is killed, the Dask workers will also be killed shortly after.

## Manual deployment

This section describes the "manual" steps that can be taken in order to deploy Jupyter and Dask on a compute node of the remote cluster.

Starting point is to compile a batch job script for the target cluster. The [`scripts`](./scripts/) folder of this repository contains a number of job scripts that can be used as templates on the various platforms. After having selected the relevant one, copy (and optionally edit) its content to the remote cluster, then submit it to the SLURM scheduler:

```shell
sbatch jupyterdask_spider.bsh
```

Copy the `ssh` command printed in the job output file (`slurm-<JOB_ID>.out`). It should look like:

```shell
ssh -i /path/to/ssh/private/key -N -L 8888:node:8888 host
```

Paste the command in a new terminal window **on your local machine** after modifying the path to the private key. You can now access the Jupyter session from your browser at the following address: http://localhost:8888 .

## Access to dCache

The scripts and templates described in this guide allow to configure access to [the SURF dCache storage](http://doc.grid.surfsara.nl/en/stable/Pages/Service/system_specifications/dcache_specs.html). In particular, they enable access to dCache via the [fsspec](https://filesystem-spec.readthedocs.io/en/latest/) package (internally used by Dask and several other packages) and our in-house developed fsspec implementation for dCache ([dCacheFS](https://github.com/RS-DAT/dcachefs)).

Access credentials to dCache can be provided either in the form of a username/password pair or as a macaroon for bearer token authentication (preferred option, it is the only strategy supported by the `jupyterdask` command line tool). Information on how to obtain a macaroon can be found as part of [the SURF dCache documentation](https://doc.grid.surfsara.nl/en/latest/Pages/Advanced/storage_clients/webdav.html#sharing-data-with-macaroons).

More information on how to work vith the dCache storage via fsspec are provided in the documentation of [dCacheFS](https://dcachefs.readthedocs.io/en/latest/).

## Recommendations for Python environments

### Container wrapper for Spider system

On Spider, using conda environments will lead to performance issues, due to
conda's nature of many small files. In such cases, one can containerize the
conda environment. One way to do this is to use the
[hpc-container-wrapper](https://github.com/CSCfi/hpc-container-wrapper) tool.
This is a container wrapper tool developed by Finnish IT center for science
(CSC).

To set up the container wrapper, first log in to Spider:

```shell
ssh USER@spider.surf.nl
```

Then, clone the `JupyterDaskOnSLURM` repository in your home directory:

```shell
git clone http://github.com/RS-DAT/JupyterDaskOnSLURM.git
```

change to the `JupyterDaskOnSLURM` directory:

```shell
cd JupyterDaskOnSLURM
```

and execute the `spider_container_deploy.sh` script:

```shell
bash spider_container_deploy.sh
```

This will run the setup and containerization of the `environment.yaml` file
contained in the `JupyterDaskOnSLURM` directory (please modify as needed before
running the script).

Now you are all set!

### Manual installation on Spider using the container wrapper

If you want to manually set up the container wrapper on Spider, follow the steps
below.

First change to your home directory:

```shell
cd ~
```

Then, clone both the `hpc-container-wrapper` and `JupyterDaskOnSLURM` repositories:

```shell
git clone https://github.com/CSCfi/hpc-container-wrapper.git
git clone http://github.com/RS-DAT/JupyterDaskOnSLURM.git
```

Then, copy the container config file `spider.yaml` file from the
`JupyterDaskOnSLURM` to the `.config` file in `hpc-container-wrapper`:

```shell
cp ./JupyterDaskOnSLURM/config/container/spider.yaml ./hpc-container-wrapper/configs/
```

Change to the `hpc-container-wrapper` directory and run the
`install.sh` script to install the container wrapper:

```shell
cd hpc-container-wrapper
bash install.sh spider
```

Next, copy the `environment.yaml` file from the `JupyterDaskOnSLURM`
to the current directory and create a container. In the following example, we
create a container under `jupyter_dask` directory:

```shell
mkdir -p ./jupyter_dask
cp ../JupyterDaskOnSLURM/environment.yaml .
bin/conda-containerize new --prefix ./jupyter_dask ./environment.yaml
```

At the end of the installation, the tool will print the path to the executable
directory (`bin` directory) of the container. For example:

```output
export PATH="/absolute/path/to/the/container/bin:$PATH"
```

```shell
cd ..
mkdir -p ~/.config/dask
cp JupyterDaskOnSLURM/config/dask/config_spider.yml ~/.config/dask/config.yml
```

Then add the following lines to the `~/.config/dask/config.yml` file, under the
`slurm` section of `jobqueue` section, note that you need to replace the `export
PATH` part with the output from the container creation step:

```yaml
    job_script_prologue:
      - 'export PATH="/absolute/path/to/the/container/bin:$PATH"' # Export environment path to
    python: python
```

After adding the lines, the `~/.config/dask/config.yml` file should look like this:

```yaml
  distributed:
    ... Some other configurations ...
  labextension:
    ... Some other configurations ...
  jobqueue:
    slurm:
      ... Some other configurations ...
      job_script_prologue:
        - 'export PATH="/home/caroline-oku/caroline/Public/demo_mobyle/container_wrapper/hpc-container-wrapper/tmp/bin:$PATH"'
      python: python
```

Then also configure the SLURM job file
`JupyterDaskOnSLURM/scripts/jupyter_dask_spider_container.bsh`. Then replace the
following part with the PATH exportaion from the container creation step:

```shell
# CHANGE THIS TO THE ABSOLUTE PATH TO THE CONTAINER BIN
export PATH="/absolute/path/to/the/container/bin:$PATH"
```

Now you have reached the exit point of the deployment script! The Jupyter Server
with Dask plugin can now be started using the
`jupyter_dask_spider_container.bsh` script.

```shell
sbatch JupyterDaskOnSLURM/scripts/jupyter_dask_spider_container.bsh
```

After the job starts, there will be an example `ssh` command printed in the job stdout (file `slurm-<JOB_ID>.out`). It should look like:

```shell
ssh -i /path/to/private/ssh/key -N -L 8889:NODE:8888 USER@sssssss.surf.nl
```

You can execute this command in a new terminal window **on your local machine**
(modify the path to the private key). You can now access the Jupyter session
from your browser at `localhost:8889`.

