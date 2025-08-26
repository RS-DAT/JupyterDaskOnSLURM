import os

from jinja2 import Environment, PackageLoader, FileSystemLoader

from .config import get_config


def setup_job_script(
        host: str,
        template: str | None = None,
        python: str = "python",
        log_dir: str = "~/.jupyterdask",
) -> str:
    """
    Setup the job script to start Jupyter and Dask on the remote cluster.

    :param host: remote cluster destination
    :param template_path: use the given custom file as template for the job script
    :param python: Python executable on the remote cluster
    :param log_dir: path where to save job scripts and log files on the remote cluster
    :return: the text of the batch job script
    """
    if template is None:
        env = Environment(loader=PackageLoader("jupyterdask"))
        temp = env.get_template("template.slurm")
    else:
        dirname, basename = os.path.split(os.path.abspath(template))
        env = Environment(loader=FileSystemLoader(dirname))
        temp = env.get_template(basename)
    return temp.render(
        python=python,
        log_dir=log_dir,
        **vars(get_config(host))
     )
