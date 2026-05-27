#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task={{ cores }}
#SBATCH --time={{ walltime }}
#SBATCH --partition={{ partition }}
#SBATCH --output={{ log_dir }}/%x-%j.out
{% if mem_per_cpu -%}
#SBATCH --mem-per-cpu={{ mem_per_cpu }}
{% endif -%}
{% if account -%}
#SBATCH --account={{ account }}
{% endif -%}
{% if image %}
# Bind all host paths
_DIRS=`/usr/bin/ls -1 / | /usr/bin/awk '!/dev/' | /usr/bin/sed 's/^/\//g' `
export APPTAINER_BIND=`echo ${_DIRS} | /usr/bin/sed 's/ /,/g' `
# Use Python interpreter from the container image
PYTHON="apptainer run {{ image }} {{ python }}"
{% else %}
PYTHON="{{ python }}"
{% endif %}
export DASK_DISTRIBUTED__DASHBOARD__LINK="/proxy/{port}/status"
export DASK_LABEXTENSION__FACTORY__MODULE="dask_jobqueue"
export DASK_LABEXTENSION__FACTORY__CLASS="SLURMCluster"
export DASK_JOBQUEUE__SLURM__DEATH_TIMEOUT=60
export DASK_JOBQUEUE__SLURM__PYTHON=${PYTHON}
export DASK_JOBQUEUE__SLURM__JOB_EXTRA_DIRECTIVES="['--output', '{{ log_dir }}/%x-%j.out']"
export DASK_JOBQUEUE__SLURM__PROCESSES={{ worker_processes }}
export DASK_JOBQUEUE__SLURM__CORES={{ worker_cores }}
export DASK_JOBQUEUE__SLURM__MEMORY="{{ worker_memory }}"
export DASK_JOBQUEUE__SLURM__WALLTIME="{{ worker_walltime }}"
export DASK_JOBQUEUE__SLURM__QUEUE="{{ worker_partition }}"
export DASK_JOBQUEUE__SLURM__LOCAL_DIRECTORY="{{ worker_local_directory }}"

${PYTHON} \
  -m jupyterlab \
  --no-browser \
  --port=`shuf -i 8400-9400 -n 1` \
  --ip=`hostname -s`
