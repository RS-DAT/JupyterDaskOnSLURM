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
APPTAINER_CMD="apptainer exec --bind /tmp,/scratch,/project,/run,/usr,/etc"
APPTAINER_IMAGE="{{ image }}"
PYTHON="${APPTAINER_CMD} ${APPTAINER_IMAGE} {{ python }}"
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
  --ip=0.0.0.0
