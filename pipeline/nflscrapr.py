"""
Python wrapper for the nflscrapr R package.
This module is used to run jobs from the nflscrapr directory in the root of this project.

Example usage:
    from . import nflscrapr

    job_name = 'games'
    nflscrapr.run(job_name, **kwargs)
"""
import logging
import subprocess
import sys

from . import config


def run(job, **kwargs):
    """Runs the nflscrapr job as a subprocess.

    :param season: year of season
    :type season: int
    :param season_type: type of season (pre, reg, post)
    :type season_type: str
    """
    command = _get_command(job, **kwargs)
    try:
        logging.info(f"Running R subprocess with command {command}...")
        output = subprocess.check_output(command).decode()
        logging.info(f"command ran successfully with output:\n{output}")
    except subprocess.CalledProcessError as e:
        logging.info(e.output)
        sys.exit(1)


def _get_command(job, **kwargs):
    """Gets the command to execute the given job.

    :param job: name of the jobb
    :type job: str
    :return: the bash command to run
    :rtype: list
    """
    command_map = {
        'games': _get_games_command
    }

    if job not in command_map:
        raise ValueError(f"{job} job doesn't have an associated command.")

    command_func = command_map[job]
    command = command_func(**kwargs)
    return command


def _get_games_command(**kwargs):
    """Formats the command to run the games nflscrapr job.

    :return: the bash command to run
    :rtype: list
    """
    if "season" not in kwargs:
        raise ValueError("'season' arg missing from kwargs!")

    if "season_type" not in kwargs:
        raise ValueError("'season_type' arg missing from kwargs!")

    command = [
        'Rscript',
        f"{config.NFLSCRAPR_JOBS_PATH}/games.r",
        f"--year={kwargs.get('season')}",
        f"--type={kwargs.get('season_type')}",
        f"--file={config.GAMES_DUMP_CSV_PATH}"
    ]
    return command
