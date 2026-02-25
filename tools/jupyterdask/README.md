# JupyterDask

A Python command-line tool to facilitate running Jupyter and Dask on a remote SLURM cluster.

## Installation

Install the tool with its dependencies using pip:

```shell
pip install "git+https://github.com/RS-DAT/JupyterDaskOnSLURM.git#egg=jupyterdask&subdirectory=tools/jupyterdask"
```

Test that you can run the command line tool as:

```shell
jupyterdask -h
```

## Development

If you want to modify/develop the tool, clone this repository and install it in editable mode with the `dev` dependencies:

```shell
git clone git@github.com:RS-DAT/JupyterDaskOnSLURM.git
cd JupyterDaskOnSLURM/tools/jupyterdask
pip install -e .[dev]
```

In order to keep a consistent coding style, we use the [Ruff](https://docs.astral.sh/ruff/) linter and formatter:

```shell
ruff check .
ruff lint .
```

The commands above can be run automatically at every commit via pre-commit hooks, which can be installed by running:

```shell
pre-commit install
```