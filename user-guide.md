# User guide

## Introduction

The following steps will help you to run a Jupyter server and a Dask cluster on a SLURM compute cluster. This guide has been particularly tailored to the SURF systems [Spider](https://spiderdocs.readthedocs.io) and [Snellius](https://servicedesk.surf.nl/wiki/spaces/WIKI/pages/30660184/Snellius) (find information on how to get access to SURF infrastructure [here](https://www.surf.nl/en/research-it/apply-for-access-to-compute-services)). The procedures described here have also been tested on the [DelftBlue Supercomputer at TU Delft](https://doc.dhpc.tudelft.nl/delftblue/).

The guide discusses two alternative routes:
* the first one involves the usage of the [`jupyterdask`](./tools/jupyterdask/) command-line tool, which represents a convenient method to start and connect to Jupyter and Dask on the remote cluster without having to explicitly logging in to the system. This should be the preferred approach for ease-of-use and when basic configurations are sufficient. See the ["Deployment via the `jupyterdask` command-line tool"](#deployment-via-the-jupyterdask-command-line-tool) section below.
* the second approach involves "manual" steps that can be taken in order to deploy Jupyter and Dask on a compute node of the remote cluster. These are the steps that could be followed when total control on settings is needed and more advanced configurations are required. See the ["Manual deployment"](#manual-deployment) section below.

> [!NOTE]
> This guide assumes the following:
> * you have received credentials to the cluster from SURF (or TU Delft);
> * you are able to access the system via SSH;
> * you have set up a SSH key pair for password-less login, see the dedicated SURF guides for [Snellius](https://servicedesk.surf.nl/wiki/spaces/WIKI/pages/30660216/Connecting+to+the+system), [Spider](https://spiderdocs.readthedocs.io/en/latest/Pages/getting_started.html), or [DelftBlue](https://doc.dhpc.tudelft.nl/delftblue/Remote-access-to-DelftBlue/).

## Table of Contents

- [Deployment via the `jupyterdask` command-line tool](#deployment-via-the-jupyterdask-command-line-tool)
  - [Installation](#installation)
  - [Deployment](#deployment)
  - [Shutting down](#shutting-down)
- [Manual deployment](#manual-deployment)
- [Access to dCache](#access-to-dcache)
- [Recommendations for Python environments](#recommendations-for-python-environments)
  - [Tykky HPC Container Wrapper](#tykky-hpc-container-wrapper)

## Deployment via the `jupyterdask` command-line tool

This repository includes [a Python command-line tool](./tools/jupyterdask/) that allows one to start Jupyter and Dask services on a compute node of a SLURM cluster (Snellius/Spider/etc.) from your local machine and to connect to the system via the execution of a single command.

### Installation

The `jupyterdask` tool only requires installation **on your local machine**. It can be installed with `pip` as:

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

A browser window should open up. **Note that it might take a few seconds for the Jupyter server to start**, after which you should have access to a JupyterLab session. A Dask cluster (with no worker) is started together with the JupyterLab session, and it should be listed in the menu appearing when selecting the Dask tab on the left part of the screen. Workers can be added by clicking the "scale" button on the running cluster instance and by selecting the number of desired workers.

Additional options for the `jupyterdask` command-line tool include:
* `-p`: Set local port where to forward the remote Jupyter server (default is 8888).
* `--timeout`: time (in seconds) waited for the remote Jupyter server to start (default is 120).
* `--template`: use the given custom file as a template for the job script.
* `--log-dir`: path where job scripts and log files are saved on the remote cluster (default is `${HOME}/.jupyterdask`).

See all options with `jupyterdask --help`.

### Shutting down

From the Dask tab in the Jupyter interface, click "shutdown" on a running cluster instance to kill all workers and the scheduler (a new cluster based on the default configurations can be re-created by pressing the "+" button).

From the Jupyter interface, select "File > Shutdown" to stop the Jupyter server and release resources.

If the job running the Jupyter server and the Dask scheduler is killed, the Dask workers will also be killed shortly after.

## Manual deployment

This section describes the "manual" steps that can be taken in order to deploy Jupyter and Dask on a compute node of the remote cluster.

Starting point is to compile a batch job script for the target cluster. The [`scripts/batch-job`](./scripts/batch-job/) folder of this repository contains a number of job scripts that can be used as templates on the various platforms. After having selected the relevant file, login to the cluster, download (and optionally edit) the content of the selected file, and submit the job to the SLURM scheduler. For example, on Spider:

```shell
wget https://raw.githubusercontent.com/RS-DAT/JupyterDaskOnSLURM/refs/heads/main/scripts/batch-job/jupyterdask_spider.bsh
sbatch jupyterdask_spider.bsh
```

As part of the job, a line with the command to set up a SSH tunnel to the remote Jupyter session will be written in the job output file (`slurm-<JOB_ID>.out`). It should look like:

```shell
ssh -i /path/to/ssh/private/key -N -L 8888:node:8888 host
```

Paste the command in a new terminal window **on your local machine** after modifying the path to the private key. Note that the command will hang without printing any output to screen. You will now be able to access the Jupyter session from your browser at the following address: http://localhost:8888 .

Shutting down the Dask and Jupyter sessions from the JupyterLab interface will release resources (see also the section ["Shutting down"](#shutting-down)). The SSH tunnel can then be killed (e.g. with `Ctrl+C`).

## Access to dCache

The scripts and templates described in this guide allow to configure access to [the SURF dCache storage](http://doc.grid.surfsara.nl/en/stable/Pages/Service/system_specifications/dcache_specs.html). In particular, they enable access to dCache via the [fsspec](https://filesystem-spec.readthedocs.io/en/latest/) package (internally used by Dask and several other packages) and our in-house developed fsspec implementation for dCache ([dCacheFS](https://github.com/RS-DAT/dcachefs)).

Access credentials to dCache can be provided either in the form of a username/password pair or as a macaroon for bearer token authentication (preferred option, it is the only strategy supported by the `jupyterdask` command line tool). Information on how to obtain a macaroon can be found as part of [the SURF dCache documentation](https://doc.grid.surfsara.nl/en/latest/Pages/Advanced/storage_clients/webdav.html#sharing-data-with-macaroons).

More information on how to work with the dCache storage via fsspec are provided in the documentation of [dCacheFS](https://dcachefs.readthedocs.io/en/latest/).

## Recommendations for Python environments

The distributed file systems that are used on HPC systems like Spider or Snellius are designed to efficiently read/write large files but suffer severe limitations when dealing with a large number of small files. For this reason, Conda and other (Python) environment managers that involve the creation of many files could become very slow (and additional put strain) on these file systems. The following approaches allow to bypass the issue while still allowing to make use of the convenience of package managers like Conda:

* Containerize the environment using [Apptainer](https://apptainer.org/), a container system analogous to Docker but suitable for execution on HPC systems. By wrapping the environment in a container image, the software installation looks like a single file to the underlying file system, circumventing the many-small-files issue mentioned above. One can automate the process of building a container image with a custom environment via continuous integration, see e.g. [this example repository](https://github.com/RS-DAT/2025-09-03-EO-summer-school), where we build a container image with a Conda environment using GitHub Actions and push the image to [the GitHub Container Registry (GHCR)](https://github.com/RS-DAT/2025-09-03-EO-summer-school/pkgs/container/2025-09-03-eo-summer-school). Note that the Apptainer container can be used together with the `jupyterdask` command-line tool via the `--container-image` option (see also the section above ["Deployment via the `jupyterdask` command line tool"](#deployment-via-the-jupyterdask-command-line-tool)). Similarly, the scripts in [`scripts/batch-job`](./scripts/batch-job/) for manual deployment includes instructions on how to run Jupyter and Dask from containers.
* Alternatively, one can make use of the [Tykky container wrapper for HPC](https://docs.csc.fi/computing/containers/tykky/) developed by the Finnish [IT Center for Science (CSC)](https://csc.fi/en/). This solution is similar to the previous one, since it also uses Apptainer to wrap Conda- or pip-based environments, but it additionally generates wrappers so that the installed software can be used (almost) as if it was not containerized. Note that a few configuration steps need to be carried out in order to set up the HPC container wrapper - see [the section below](#tykky-hpc-container-wrapper). If using the HPC container wrapper, the `jupyterdask` command line tool or the manual deployment scripts can be configured exclusively with the path to the Python installation wrapper (i.e. `--python /path/to/install_dir/bin/python` and `PYTHON=/path/to/install_dir/bin/python`, respectively) - no need to specify the path to the container image.

Advantages of the former approach include the possibility to easily automate the process of building the environment image (for the latter, the steps required to build the image have to be run on the cluster). The latter approach provides instead better tools to update the environment without having to rebuild the container image.

### Tykky HPC Container Wrapper

In order to setup the Tykky HPC container wrapper, one needs to log in to the target cluster, clone and access the [hpc-container-wrapper](https://github.com/CSCfi/hpc-container-wrapper) repository:

```shell
git clone https://github.com/CSCfi/hpc-container-wrapper .
cd hpc-container-wrapper
```

We provide configuration files for Spider and Snellius in [`config/hpc-container-wrapper`](./config/hpc-container-wrapper/). Download the relevant configuration file to the `configs` directory, then run the installation shell script. For example, on Spider:

```shell
wget https://raw.githubusercontent.com/RS-DAT/JupyterDaskOnSLURM/refs/heads/main/config/hpc-container-wrapper/spider.yaml -P ./configs
bash install.sh spider
```

A containerized conda environment can now be created using the following command. Note that we provide [a template environment file](https://github.com/RS-DAT/JupyterDaskOnSLURM/blob/main/config/conda/environment.yaml) that includes Jupyter, Dask and a few other software packages that are relevant for this project.

```shell
mkdir -p /path/to/install_dir/
bash bin/conda-containerize new --mamba --prefix /path/to/install_dir/  environment.yaml
```

Now you are all set! For more advanced configuration options or for information on how to update a containerized environment have a look at the [HCP container wrapper documentation](https://docs.lumi-supercomputer.eu/software/installing/container-wrapper/) or at [the dedicated section in the Spider documentation](https://doc.spider.surfsara.nl/en/latest/Pages/software_on_spider.html#lumi-container-wrapper).


