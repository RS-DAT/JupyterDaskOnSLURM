# Work with STAC Catalogs on the dCache Storage

This example includes two Jupyter notebooks that illustrate how to:
* search for scenes from [the Sentinel-2 mission](https://sentinel.esa.int/web/sentinel/missions/sentinel-2) as part of [a open dataset on AWS](https://registry.opendata.aws/sentinel-2-l2a-cogs/)
* save the metadata in the form of a [SpatioTemporal Asset Catalog](https://stacspec.org) on the [SURF dCache storage system](http://doc.grid.surfsara.nl/en/latest/Pages/Advanced/grid_storage.html).
* retrieve some of the scenes' assets.
* doing some simple processing on the retrieved assets using a Dask cluster to distribute workload.

## Additional dependencies 

Activate the environment where Jupyter/Dask are installed and install the following dependencies (**NOTE**: the python version should be >= 3.8): 

```shell
conda activate jupyter_dask

# conda deps 
conda install -c conda-forge \
    gdal \
    xarray \
    rioxarray \
    matplotlib \

# pip deps
pip install \
    stackstac \
    pystac-client \
    stac2dcache \

```


