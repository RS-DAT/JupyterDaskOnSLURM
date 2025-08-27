#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --cpus-per-task={{ cores }}
#SBATCH --mem={{ memory }}
#SBATCH --time={{ walltime }}
#SBATCH --partition={{ partition }}
#SBATCH --output={{ log_dir }}/%x-%j.out
#SBATCH --error={{ log_dir }}/%x-%j.err

export DASK_DISTRIBUTED__DASHBOARD__LINK="/proxy/{port}/status"
export DASK_LABEXTENSION__FACTORY__MODULE="dask_jobqueue"
export DASK_LABEXTENSION__FACTORY__CLASS="SLURMCluster"
export DASK_JOBQUEUE__SLURM__DEATH_TIMEOUT=60
export DASK_JOBQUEUE__SLURM__PYTHON="{{ python }}"
export DASK_JOBQUEUE__SLURM__JOB_EXTRA_DIRECTIVES="['--output', '{{ log_dir }}/%x-%j.out', '--error', '{{ log_dir }}/%x-%j.err']"
export DASK_JOBQUEUE__SLURM__PROCESSES={{ worker_processes }}
export DASK_JOBQUEUE__SLURM__CORES={{ worker_cores }}
export DASK_JOBQUEUE__SLURM__MEMORY="{{ worker_memory }}"
export DASK_JOBQUEUE__SLURM__WALLTIME="{{ worker_walltime }}"
export DASK_JOBQUEUE__SLURM__QUEUE="{{ worker_partition }}"
export DASK_JOBQUEUE__SLURM__LOCAL_DIRECTORY="{{ worker_local_directory }}"

{{ python }} \
  -m jupyterlab \
  --no-browser \
  --port=`shuf -i 8400-9400 -n 1` \
  --ip=`hostname -f`
