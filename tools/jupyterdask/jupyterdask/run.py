import datetime
import io
import logging
import time
import webbrowser

from contextlib import contextmanager
from typing import Any, Generator
from urllib.parse import urlparse, parse_qs

from fabric import Connection


logger = logging.getLogger(__file__)

TIMESTAMP = datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S')


def submit_and_connect(
        job_script: str,
        host: str,
        identity_file: str | None = None,
        port: int = 8888,
        timeout: int = 60,
        log_dir: str = "~/.jupyterdask",
) -> None:
    """
    Start Jupyter on the remote cluster and connect to the server.

    :parma job_script: the text of the batch job script
    :param host: remote cluster destination
    :param identity_file: path to the private key used for authentication on the remote cluster
    :param port: the local port where to forward the remote Jupyter server
    :param timeout: time (in seconds) waited for the remote Jupyter server to start
    :param log_dir: path where to save job scripts and log files on the remote cluster
    """
    connect_kwargs = _get_connect_kwargs(identity_file)
    with Connection(host=host, connect_kwargs=connect_kwargs, forward_agent=True) as conn:
        _setup_log_dir(conn, log_dir)
        with _running_job(conn, job_script, log_dir=log_dir, timeout=timeout) as job:
            job_info = _retrieve_job_info(conn, job, log_dir=log_dir)
            _forward_port_and_open_browser(
                conn,
                remote_host=job_info["remote_host"],
                remote_port=job_info["remote_port"],
                local_port=port,
                token=job_info["token"],
            )


def _get_connect_kwargs(identity_file: str | None) -> dict[str, str | None]:
    return {"key_filename": identity_file} if identity_file is not None else None


def _setup_log_dir(connection: Connection, log_dir: str = "~/.jupyterdask") -> None:
    connection.run(f"mkdir -p '{log_dir}'")


@contextmanager
def _running_job(
        connection: Connection,
        job_script: str,
        log_dir: str = "~/.jupyterdask",
        timeout: int = 60
) -> Generator[int]:
    job_id = _submit_job(connection, job_script, log_dir=log_dir)
    _wait_for_job_to_start(connection, job_id, log_dir=log_dir, timeout=timeout)
    try:
        yield job_id
    finally:
        _cancel_job(connection, job_id)


def _submit_job(
        connection: Connection,
        job_script: str,
        log_dir: str = "~/.jupyterdask"
) -> int:
    job_name = f"jupyter-{TIMESTAMP}"
    remote_path = f"{log_dir}/{job_name}.bsh"
    connection.put(io.StringIO(job_script), remote_path)
    res = connection.run(f"sbatch --job-name {job_name} {remote_path}")
    # Parse stdout of the form: "Submitted batch job <JOB_ID>"
    job_id = int(res.stdout.split()[-1])
    return job_id


def _wait_for_job_to_start(
        connection: Connection,
        job_id: str,
        log_dir: str = "~/.jupyterdask",
        timeout: int = 60,
):
    stdout_path = _get_stdout_path(job_id, log_dir=log_dir)
    start_time = time.time()
    while time.time() - start_time < timeout:
        if _remote_file_exists(connection, stdout_path):
            return
        time.sleep(2)
    raise TimeoutError(f"Job {job_id} failed to start.")


def _cancel_job(connection: Connection, job_id: int) -> None:
    connection.run(f"scancel {job_id}")


def _get_stdout_path(job_id: int, log_dir: str = "~/.jupyterdask") -> str:
    return f"{log_dir}/jupyter-{TIMESTAMP}-{job_id}.out"


def _remote_file_exists(connection: Connection, path: str) -> bool:
    res = connection.run(f"test -f {path} && echo True || echo False")
    return bool(res.stdout)


def _retrieve_job_info(
        connection: Connection,
        job_id: int,
        log_dir: str = "~/.jupyterdask",
        timeout: int = 120,
) -> dict[str, Any]:
    stdout_path = _get_stdout_path(job_id, log_dir=log_dir)
    start_time = time.time()
    while time.time() - start_time < timeout:
        res = connection.run(f"grep -A 1 'is running at:' {stdout_path} | grep -oE 'https?://.*'")
        if res.stdout:
            return _parse_url(res.stdout)
        time.sleep(2)
    raise TimeoutError("Jupyter failed to start.")


def _parse_url(url: str) -> dict[str, Any]:
    parsed = urlparse(url)
    token = parse_qs(parsed.query).get("token", [None])[0]
    return {"hostname": parsed.hostname, "port": parsed.port, "token": token}


def _forward_port_and_open_browser(
        connection: Connection,
        local_port: int,
        remote_port: int,
        remote_host: str,
        token: str | None = None
) -> None:
    with connection.forward_local(
        local_port=local_port,
        remote_port=remote_port,
        remote_host=remote_host
    ):
        time.sleep(1)
        _open_browser(port=local_port, token=token)


def _open_browser(port: int = 8888, token: str | None = None) -> None:
    """
    Launch web browser (system default) and open JupyterLab interface.
    """
    url = f"http://localhost:{port}"
    if token is not None:
        url = f"{url}/?token={token}"
    logger.info("JupyterLab URL: %s", url)
    try:
        controller = webbrowser.get()
        controller.open(url)
        logger.info("Web browser launched.")
    except webbrowser.Error:
        logger.info("Failed to open web browser.")
