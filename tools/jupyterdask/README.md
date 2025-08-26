# JupyterDask

A Python command-line tool to facilitate running Jupyter and Dask on a remote SLURM cluster.

## Installation

Install the tool with its dependencies using pip:

```shell
pip install -e "git+https://github.com/RS-DAT/JupyterDaskOnSLURM.git#egg=jupyterdask&subdirectory=tools/jupyterdask"
```

If you want to modify/develop the tool, clone this repository and install it in development mode:

```shell
git clone git@github.com:RS-DAT/JupyterDaskOnSLURM.git
cd JupyterDaskOnSLURM/tools/jupyterdask
pip install -e .
```

Test that you can run the command line tool as:

```shell
jupyterdask -h
```

## Examples

Examples here