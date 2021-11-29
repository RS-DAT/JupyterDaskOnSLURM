# Dask config files

* [`distributed.yaml`](./distributed.yaml) includes options to forward the Dask dashboard through Jupyter.
* [`jobqueue.yaml`](./jobqueue.yaml) contains the default arguments to `SLURMCluster()`, describing the configuration of a worker in a new Dask SLURMCluster (e.g. how much memory, cores, etc. per worker). 
* [`labextension.yaml`](./labextension.yaml) contains the default configuration of the Dask Cluster in a new JupyterLab session (e.g. use SLURMCluster, how many nodes initially).
