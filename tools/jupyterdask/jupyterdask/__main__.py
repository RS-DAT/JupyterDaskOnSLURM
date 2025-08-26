from .cli import parse_args
from .run import submit_and_connect
from .template import setup_job_script


def main(
        host: str,
        identity_file: str | None = None,
        port: int = 8888,
        timeout: int = 120,
        template: str | None = None,
        python: str = "python",
        log_dir: str = "~/.jupyterdask",
        run: bool = False,
) -> None:
    """
    Setup and run Jupyter and Dask on a compute node of a remote cluster.

    :param host: remote cluster destination
    :param identity_file: path to the private key used for authentication on the remote cluster
    :param port: the local port where to forward the remote Jupyter server
    :param timeout: time (in seconds) waited for the remote Jupyter server to start
    :param template: use the given custom file as template for the job script
    :param python: Python executable on the remote cluster
    :param log_dir: path where to save job scripts and log files on the remote cluster
    :param run: run Jupyter on the remote cluster and connect to the interface
    """
    job_script = setup_job_script(
        host,
        template=template,
        python=python,
        log_dir=log_dir,
    )
    if run:
        submit_and_connect(
            job_script,
            host,
            identity_file=identity_file,
            port=port,
            timeout=timeout,
            log_dir=log_dir,
        )


def __main__() -> None:
    args = parse_args()
    main(**args)
