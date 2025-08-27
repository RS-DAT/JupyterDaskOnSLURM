import datetime
import io
import logging
import time
import webbrowser

from contextlib import contextmanager
from typing import Any, ContextManager
from urllib.parse import urlparse, parse_qs

from fabric import Connection
from invoke.exceptions import UnexpectedExit


logger = logging.getLogger(__file__)

TIMESTAMP = datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S')


def submit_and_connect(
        job_script: str,
        host: str,
        identity_file: str | None = None,
        port: int = 8888,
        timeout: int = 60,
        log_dir: str = ".jupyterdask",
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
        with _start_jupyter(conn, job_script, log_dir=log_dir, timeout=timeout) as url:
            url_info = _parse_url(url)
            _forward_port_and_open_browser(
                conn,
                remote_host=url_info["hostname"],
                remote_port=url_info["port"],
                local_port=port,
                token=url_info["token"],
            )


def _get_connect_kwargs(identity_file: str | None) -> dict[str, str | None]:
    return {"key_filename": identity_file} if identity_file is not None else None


def _setup_log_dir(connection: Connection, log_dir: str = ".jupyterdask") -> None:
    connection.run(f"mkdir -p '{log_dir}'", hide=True)


@contextmanager
def _start_jupyter(
        connection: Connection,
        job_script: str,
        log_dir: str = ".jupyterdask",
        timeout: int = 60
) -> ContextManager[str]:
    job_id = _submit_job(connection, job_script, log_dir=log_dir)
    try:
        log_file = _get_log_file(job_id, log_dir=log_dir)
        _wait_for_jupyter_to_start(connection, job_id, log_file, timeout=timeout)
        yield _get_jupyter_url(connection, log_file)
    finally:
        _cancel_job(connection, job_id)


def _submit_job(
        connection: Connection,
        job_script: str,
        log_dir: str = ".jupyterdask"
) -> int:
    job_name = f"jupyter-{TIMESTAMP}"
    remote_path = f"{log_dir}/{job_name}.bsh"
    connection.put(io.StringIO(job_script), remote_path)
    res = connection.run(f"sbatch --job-name {job_name} {remote_path}", hide=True)
    # Parse stdout of the form: "Submitted batch job <JOB_ID>"
    job_id = int(res.stdout.split()[-1])
    return job_id


def _wait_for_jupyter_to_start(
        connection: Connection,
        job_id: str,
        log_file: str,
        timeout: int = 60,
):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if _job_is_active(connection, job_id):
            if _jupyter_is_running(connection, log_file):
                return
        else:
            raise RuntimeError(f"Job {job_id} failed.")
        time.sleep(5)
    raise TimeoutError(f"Failed to start Jupyter in job {job_id}.")


def _cancel_job(connection: Connection, job_id: int) -> None:
    connection.run(f"scancel {job_id}", warn=True, hide=True)


def _get_log_file(job_id: int, log_dir: str = ".jupyterdask") -> str:
    return f"{log_dir}/jupyter-{TIMESTAMP}-{job_id}.out"


def _job_is_active(connection: Connection, job_id: int):
    res = connection.run(f"squeue -j {job_id} --format %T", warn=True, hide=True)
    # If the job is active, squeue will return "STATE\n<SOME_STATE>\n"
    is_active = len(res.stdout.split()) == 2
    return (res.exited == 0) and is_active


def _jupyter_is_running(connection: Connection, log_file: str):
    if not _file_exists(connection, log_file):
        return False
    try:
        _ = _get_jupyter_url(connection, log_file)
    except UnexpectedExit:
        return False
    return True


def _file_exists(connection: Connection, path: str) -> bool:
    res = connection.run(f"test -f {path}", warn=True, hide=True)
    return res.exited == 0


def _get_jupyter_url(connection: Connection, path: str) -> str:
    res = connection.run(f"grep -A 1 'is running at:' {path} | grep -oE 'https?://.*'", hide=True)
    return res.stdout


def _parse_url(url: str) -> dict[str, Any]:
    parsed = urlparse(url)
    hostname, _ = parsed.hostname.split(".", 1)  # Only use short hostname
    token = parse_qs(parsed.query).get("token", [None])[0]
    return {"hostname": hostname, "port": parsed.port, "token": token}


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
        _wait()


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


def _wait():
    while True:
        input()
