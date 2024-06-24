# User guide

The following steps will help you to run a Jupyter server and a Dask cluster on
one of the SURF systems running SLURM, such as Spider, Snellius or Lisa. Find
information on how to get access to SURF infrastructure
[here](https://www.surf.nl/en/research-it/apply-for-access-to-compute-services).
Or on the [DelftBlue Supercomputer at TU
Delft](https://doc.dhpc.tudelft.nl/delftblue/).

This guide assumes that you have received credentials from SURF or TU Delft,
that you are able to access the system via SSH, and that an SSH key pair has
been set up for password-less login, see the dedicated SURF guides for
[Lisa/Snellius](https://servicedesk.surf.nl/wiki/display/WIKI/SSH#SSH-Bonus2:public-keyauthentication),
[Spider](https://spiderdocs.readthedocs.io/en/latest/Pages/getting_started.html),
and
[DelftBlue](https://doc.dhpc.tudelft.nl/delftblue/Remote-access-to-DelftBlue/).

**Contents:**

- [Local Set-up](#local-set-up)
  - [Installation on platform](#installation-on-platform)
    - [Configuring dCache](#configuring-dcache)
  - [Running](#running)
  - [Shutting down](#shutting-down)
  - [Uninstallation on platform](#uninstallation-on-platform)
- [Manual Installation](#manual-installation)
  - [Configuration](#configuration)
    - [Jupyter](#jupyter)
    - [Dask](#dask)
    - [dCache](#dcache)
- [Container wrapper for Spider system](#container-wrapper-for-spider-system)
- [Troubleshooting](#troubleshooting)
  - [Manual deployment](#manual-deployment)
- [Delft Blue](#delft-blue)
  - [Installation](#installation)
  - [Configuration](#configuration-1)
  - [Deployment](#deployment)

## Local Set-up

This repository includes [a Python script](./scripts/runJupyterDaskOnSLURM.py)
to install the components remotely on a SURF platform (Snellius/Spider/etc.),
and to start Jupyter and Dask services on that platform from a local machine.

**On your local machine**, download the script by cloning this repository:

```shell
git clone http://github.com/RS-DAT/JupyterDaskOnSLURM.git
cd JupyterDaskOnSLURM
```

The script requires Python 3 and the [Fabric library](https://www.fabfile.org)
and, currently, [decorator](https://github.com/micheles/decorator) as well,
which can be installed via `pip`:

```shell
pip install fabric decorator
```

Running the script the first time using the option `--add_platform` queries the
user for a few infomation about the platform e.g. username and path to the
private ssh-key, and stores these in a configuration file at
`.config/platforms/platforms.ini` for later use:

```shell
python runJupyterDaskOnSLURM.py --add_platform
```

> NOTE: Don't use `~` for entering a path.

### Installation on platform

Before installing on the platform, edit the `environment.yaml` file in the
folder to include all conda/pip packages that are needed to run your proposed
workflow.

After editing the `environment.yaml` file, installing the components on the
platform can be done on the platform as:

```shell
python runJupyterDaskOnSLURM.py --uid <UID> --mode install
```

> NOTE: that installation can take a while and requires user input to complete.

#### Configuring dCache

In order to configure access to [the SURF dCache
storage](http://doc.grid.surfsara.nl/en/stable/Pages/Service/system_specifications/dcache_specs.html)
via [the Filesystem Spec
library](https://filesystem-spec.readthedocs.io/en/latest/) (internally used by
Dask and other libraries), you can use the configuration file provided in
`config/fsspec`. Edit `config/fsspec/config.json`, **replacing the `<MACAROON>`
string with the actual macaroon** (see [this
guide](http://doc.grid.surfsara.nl/en/latest/Pages/Advanced/storage_clients/webdav.html#sharing-data-with-macaroons)
for information on how to generate it), then copy the file to
`${HOME/.config/fsspec}`:

```shell
mkdir -p ~/.config/fsspec
cp ./config/fsspec/config.json ~/.config/fsspec/
```

More information on how to read files from the dCache storage are provided in
the [documentation of the dCacheFS
package](https://dcachefs.readthedocs.io/en/latest/).

### Running

You can run Jupyter Lab on the remote server using:

```shell
python runJupyterDaskOnSLURM.py --uid <UID> --mode run
```

A browser window should open up. **Note that it might take few seconds for the
Jupyter server to start**, after which you should have access to a JupyterLab
interface (login using the password set as above).

A Dask cluster (with no worker) is started together with the JupyterLab session,
and it should be listed in the menu appearing when selecting the Dask tab on the
left part of the screen. Workers can be added by clicking the "scale" button on
the running cluster instance and by selecting the number of desired workers.

### Shutting down

From the Dask tab in the Jupyter interface, click "shutdown" on a running
cluster instance to kill all workers and the scheduler (a new cluster based on
the default configurations can be re-created by pressing the "+" button).

From the Jupyter interface, select "File > Shutdown" to stop the Jupyter server
and release resources.

If the job running the Jupyter server and the Dask scheduler is killed, the Dask
workers will also be killed shortly after (configure this using the
`death-timeout` key in the config file).

### Uninstallation on platform

Uninstalling the components on the platform can be done as:

```shell
python runJupyterDaskOnSLURM.py --uid <UID> --mode uninstall
```

This will remove all associated files and folders. However, mamba will remain
installed on the platform and needs to be removed manually, if needed.

## Manual Installation

> NOTE: Follow these instructions if <MODE> = 'install' does not work.

> NOTE: if you work on Spider, follow the instruction[Container wrapper for Spider system](#container-wrapper-for-spider-system).

Login to the SURF system from your terminal, then clone and access this repository:

```shell
git clone http://github.com/RS-DAT/JupyterDaskOnSLURM.git
cd JupyterDaskOnSLURM
```

Alternatively copy the local copy of `JupyterDaskOnSLURM` which has the modified
`environment.yaml` file with the updated packages to the platform using the
`scp` command. For usage of the `scp` command, you can refer to this [blog
post](https://www.howtogeek.com/804179/scp-command-linux/).

The required packages are most easily installed via the `conda` package manager,
and they are available from the `conda-forge` channel. In order to install
`conda` (and its faster C++ implementation `mamba`) and to configure the
`conda-forge` channel as the default channel, download and run the following
installation script (you can skip this step if `conda` is already installed):

```shell
wget https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-x86_64.sh
chmod +x Mambaforge-Linux-x86_64.sh
./Mambaforge-Linux-x86_64.sh
```

After accepting the license term and selecting the installation location (the
default is `${HOME}/mambaforge`), type `yes` to initialize Mambaforge.
Logout/login to activate.

Create a new environment using the conda environment file in this repository -
note that the base version of this file has been provided but can be updated to
include relevant packages for your workflow:

```shell
mamba env create -f environment.yaml
```

Activate the environment and install additional dependencies using
`mamba`/`pip`, as required by each use case:

```shell
mamba activate jupyter_dask
mamba install ...
pip install ...
```

### Configuration

After having created the environment, we need to configure few settings.

#### Jupyter

Configure the password to access Jupyter:

```shell
jupyter server --generate-config
jupyter server password
```

and make the Jupyter config file that is created after running the previous step
readable by the current user only:

```shell
chmod 400 ~/.jupyter/jupyter_server_config.py
```

The repository directory `scripts` contains template job scripts for Spider and
Snellius. These scripts define the requirements of the SLURM job running the
Jupyter server, they can be customized depending on the specific user needs.

#### Dask

The repository directory `config/dask` contains a template Dask configuration
file. This file defines the default worker settings in the Dask cluster, and it
thus **needs to be edited depending on the SURF system or other system** which
we are running on. In particular, **uncomment the correct block in
`config/dask/config.yaml`**, then copy the file to `${HOME}/.config/dask`:

```shell
mkdir -p ~/.config/dask
cp config/dask/config.yaml ~/.config/dask/
```

The default Dask settings can be further tuned depending on user needs.

#### dCache

In order to configure access to [the SURF dCache
storage](http://doc.grid.surfsara.nl/en/stable/Pages/Service/system_specifications/dcache_specs.html)
via [the Filesystem Spec
library](https://filesystem-spec.readthedocs.io/en/latest/) (internally used by
Dask and other libraries), you can use the configuration file provided in
`config/fsspec`. Edit `config/fsspec/config.json`, **replacing the `<MACAROON>`
string with the actual macaroon** (see [this
guide](http://doc.grid.surfsara.nl/en/latest/Pages/Advanced/storage_clients/webdav.html#sharing-data-with-macaroons)
for information on how to generate it), then copy the file to
`${HOME/.config/fsspec}`:

```shell
mkdir -p ~/.config/fsspec
cp config/fsspec/config.json ~/.config/fsspec/
```

More information on how to read files from the dCache storage are provided in
the [documentation of the dCacheFS
package](https://dcachefs.readthedocs.io/en/latest/).

## Troubleshooting

### Manual deployment

As an alternative to the deployment script, the Jupyter and Dask services can
be started via the following "manual" procedure.

Login to the SURF system, then submit a batch job script based on the template
provided in `scripts/jupyter_dask_<PLATFORM_NAME>.bsh` to start the Jupyter
server and the Dask scheduler on a platform, for example:

```shell
sbatch scripts/jupyter_dask_snellius.bsh
```

Copy the `ssh` command printed in the job stdout (file `slurm-<JOB_ID>.out`). It
should look like:

```shell
ssh -i /path/to/private/ssh/key -N -L 8889:NODE:8888 USER@sssssss.surf.nl
```

Paste the command in a new terminal window **on your local machine** (modify the
path to the private key). You can now access the Jupyter session from your
browser at `localhost:8889`.

## Container wrapper for Spider system

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

Then, clone the `JupyterDaskOnSLURM` repository:

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

### manual installation on Spider using container

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

## Delft Blue

Follow the steps bellow to install and configure

### Installation

1. Use `module` to load `miniconda`:

```shell
module load miniconda3/4.12.0
```

2. Clone the repository:

```shell
git clone http://github.com/RS-DAT/JupyterDaskOnSLURM.git
cd JupyterDaskOnSLURM
```

3. If required, modify the `environment.yaml` to include relevant packages for your workflow. Then, create an environment using conda":

```shell
conda env create -f environment.yaml
```

4. Activate the environment and install additional dependencies using
   `conda`/`pip`, as required by each use case:

```shell
conda activate jupyter_dask
conda install ...
pip install ...
```

### Configuration

1. Configure the password to access **Jupyter**:

```shell
jupyter server --generate-config
jupyter server password
```

and make the Jupyter config file that is created after running the previous step
readable by the current user only:

```shell
chmod 400 ~/.jupyter/jupyter_server_config.py
```

The repository directory `scripts` contains template job scripts for Spider,
Snellius and DelftBlue. These scripts define the requirements of the SLURM job
running the Jupyter server, they can be customized depending on the specific
user needs.

```shell
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
```

2. Configure the **Dask** settings. The repository directory `config/dask`
   contains templates for the Dask configuration files. The cofiguration file
   defines the default worker settings in the Dask cluster, and it thus **needs
   to be edited depending on the SURF system or other system** which we are
   running on. In particular, the  **file corresponding to DelftBlue
   `config/dask/config_delftblue.yml`**. Copy the file to
   `${HOME}/.config/dask`:

```shell
mkdir -p ~/.config/dask
cp -r config/dask/config_delftblue.yml ~/.config/dask/config.yml
```

The default Dask settings can be further tuned depending on user needs.

### Deployment

On DelftBlue, you need to start the the Jupyter and Dask services manually using this procedure.

1. Login to DelftBlue, then submit a SLURM job based using the template provided
   in `scripts/jupyter_dask_delftblue.bsh` to start the Jupyter server and the
   Dask scheduler on the login node:

```shell
sbatch scripts/jupyter_dask_delftblue.bsh
```

Copy the `ssh` command printed in the job stdout (file `slurm-<JOB_ID>.out`). It
should look like:

```shell
ssh -i /path/to/private/ssh/key -N -L 8889:NODE:8888 USER@sssssss.tudelft.nl
```

Paste the command in a new terminal window **on your local machine** (modify the
path to the private key). You can now access the Jupyter session from your
browser at `localhost:8889`.
