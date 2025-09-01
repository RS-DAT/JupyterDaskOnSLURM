import argparse

from typing import Any

from . import __version__


def parse_args() -> dict[str, Any]:
    """
    Parse command line arguments.

    :return: Input parameter arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "host",
        help="remote cluster destination as `[user@]hostname`.",
    )
    parser.add_argument(
        "--identity_file",
        "-i",
        help="path to the private key used for authentication on the remote cluster.",
        type=str,
        required=False,
    )
    parser.add_argument(
        "--port",
        "-p",
        help="the local port where to forward the remote Jupyter server.",
        type=int,
        default=8888,
    )
    parser.add_argument(
        "--timeout",
        help="time (in seconds) waited for the remote Jupyter server to start.",
        type=int,
        default=120,
    )
    parser.add_argument(
        "--template",
        help="use the given custom file as template for the job script.",
        type=str,
        required=False,
    )
    parser.add_argument(
        "--python",
        help=(
            "Python executable on the remote cluster. This may include commands to activate a "
            "virtual environment, e.g. `--python='conda activate myenv && python'` or "
            "`--python='source /path/to/venv/bin/activate && python'`."
        ),
        type=str,
        default="python",
    )

    parser.add_argument(
        "--log-dir",
        help="path where to save job scripts and log files on the remote cluster.",
        type=str,
        default=".jupyterdask",
    )
    parser.add_argument(
        "--run",
        help="run Jupyter on the remote cluster and connect to the interface.",
        action="store_true",
        default=False
    )
    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version='%(prog)s ' + __version__
    )
    args = parser.parse_args()
    return vars(args)
