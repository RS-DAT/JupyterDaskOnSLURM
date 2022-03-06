# Dask config files

Depends on the infrastructure you are working on, you can choose from the "spider" or "snellius" configuration. On either system, you should copy the `.yaml` files to `~/.config/dask/`.

* `distributed.yaml` includes options to forward the Dask dashboard through Jupyter.
* `jobqueue.yaml` contains the default arguments to `SLURMCluster()`, describing the configuration of a worker in a new Dask SLURMCluster (e.g. how much memory, cores, etc. per worker). 
* `labextension.yaml` contains the default configuration of the Dask Cluster in a new JupyterLab session (e.g. use SLURMCluster, how many nodes initially).
