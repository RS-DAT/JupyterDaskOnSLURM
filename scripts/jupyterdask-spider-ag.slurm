#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=02:00:00
#SBATCH --partition=normal
#SBATCH --output=.jupyterdask/%x-%j.out


APPTAINER_CMD="apptainer exec --bind /tmp,/scratch,/project,/run,/usr,/etc"
APPTAINER_IMAGE=""oras://ghcr.io/rs-dat/2025-09-03-eo-summer-school:latest""
PYTHON="${APPTAINER_CMD} ${APPTAINER_IMAGE} python"

export DASK_DISTRIBUTED__DASHBOARD__LINK="/proxy/{port}/status"
export DASK_LABEXTENSION__FACTORY__MODULE="dask_jobqueue"
export DASK_LABEXTENSION__FACTORY__CLASS="SLURMCluster"
export DASK_JOBQUEUE__SLURM__DEATH_TIMEOUT=60
export DASK_JOBQUEUE__SLURM__PYTHON=${PYTHON}
export DASK_JOBQUEUE__SLURM__JOB_EXTRA_DIRECTIVES="['--output', '.jupyterdask/%x-%j.out']"
export DASK_JOBQUEUE__SLURM__PROCESSES=1
export DASK_JOBQUEUE__SLURM__CORES=4
export DASK_JOBQUEUE__SLURM__MEMORY="32GiB"
export DASK_JOBQUEUE__SLURM__WALLTIME="01:00:00"
export DASK_JOBQUEUE__SLURM__QUEUE="normal"
export DASK_JOBQUEUE__SLURM__LOCAL_DIRECTORY="\$TMPDIR"

${PYTHON} \
  -m jupyterlab \
  --no-browser \
  --port=`shuf -i 8400-9400 -n 1` \
  --ip=0.0.0.0
