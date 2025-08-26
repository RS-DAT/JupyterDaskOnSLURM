from dataclasses import dataclass

import fabric


@dataclass
class ClusterConfig:
    """ Remote cluster configuration. """
    cores: int | None = None
    memory: str | None = None
    walltime: str | None = None
    partition: str | None = None
    worker_processes: int | None = None
    worker_cores: int | None = None
    worker_memory: str | None = None
    worker_walltime: str | None = None
    worker_partition: str | None = None
    worker_local_directory: str | None = None


DEFAULT_CONFIGS = {
    "spider": ClusterConfig(),
    "snellius": ClusterConfig(),
    "delftblue": ClusterConfig(),
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
    return ClusterConfig()


def _get_host(host: str) -> str:
    """ Resolve host, even if it is defined via the SSH agent. """
    with fabric.Connection(host, forward_agent=True) as c:
        return c.host
