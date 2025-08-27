from dataclasses import dataclass

import fabric


@dataclass
class ClusterConfig:
    """ Remote cluster configuration. """
    cores: int
    memory: str
    walltime: str
    partition: str
    worker_processes: int
    worker_cores: int
    worker_memory: str
    worker_walltime: str
    worker_partition: str
    worker_local_directory: str


DEFAULT_CONFIGS = {
    "spider": ClusterConfig(
        cores=1,
        memory="8GiB",
        walltime="01:00:00",
        partition="normal",
        worker_processes=1,
        worker_cores=4,
        worker_memory="32GiB",
        worker_walltime="01:00:00",
        worker_partition="normal",
        worker_local_directory=r"\$TMPDIR",
    ),
    "snellius": ClusterConfig(
        cores=16,
        memory="28GiB",
        walltime="01:00:00",
        partition="thin",
        worker_processes=1,
        worker_cores=16,
        worker_memory="28GiB",
        worker_walltime="01:00:00",
        worker_partition="thin",
        worker_local_directory=r"\$TMPDIR",
    ),
    "delftblue": ClusterConfig(
        cores=1,
        memory="4G",
        walltime="01:00:00",
        partition="compute",
        worker_processes=1,
        worker_cores=2,
        worker_memory="8G",
        worker_walltime="01:00:00",
        worker_partition="compute",
        worker_local_directory=r"/scratch/\$USER",
    ),
}


def get_config(host: str) -> ClusterConfig:
    """
    Find out a suitable configuration for the given host.

    :param host: remote cluster destination
    :return: default remote cluster configuration
    """
    host = _get_host(host)
    for k, v in DEFAULT_CONFIGS.items():
        if k in host:
            return v
    raise ValueError(f"Cannot find configuration for the host: {host}")


def _get_host(host: str) -> str:
    """ Resolve host, even if it is defined via the SSH agent. """
    with fabric.Connection(host, forward_agent=True) as c:
        return c.host
