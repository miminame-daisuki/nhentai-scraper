import os
from pathlib import Path
import sys
import json
import yaml
import signal
import logging
import logging.config
from typing import Union, Optional


logger = logging.getLogger('__main__.' + __name__)


def get_application_folder_dir() -> str:

    application_folder_dir = ''
    # when running executable
    if getattr(sys, 'frozen', False):
        application_folder_dir = os.path.dirname(sys.executable)
    # when running python script (placed inside ./src/)
    elif __file__:
        application_folder_dir = os.path.abspath(
            f'{os.path.dirname(__file__)}/..'
        )
    else:
        application_folder_dir = os.path.abspath(
            f'{os.getcwd()}/..'
        )

    return application_folder_dir


def set_download_dir(download_dir: Optional[Union[str, Path]] = None) -> str:

    if download_dir is None:
        application_folder_path = get_application_folder_dir()
        download_dir = os.path.abspath(
            f'{application_folder_path}/Downloaded/'
        )
    else:
        if os.path.isabs(download_dir):
            pass
        else:
            download_dir = os.path.abspath(
                f'{application_folder_path}/{download_dir}/'
            )

    if not os.path.isdir(download_dir):
        os.mkdir(download_dir)

    return download_dir


def set_logging_config(
    logging_config_filename: Optional[Union[str, Path]] = None
):

    if logging_config_filename is None:
        application_folder_path = get_application_folder_dir()
        logging_dir = os.path.abspath(f'{application_folder_path}/log/')
        logging_config_filename = os.path.join(
            logging_dir, 'logging_config.yaml'
        )

    with open(logging_config_filename) as f:
        if 'yaml' in logging_config_filename:
            logging_config = yaml.full_load(f)
        elif 'json' in logging_config_filename:
            logging_config = json.load(f)

    logging_filename = os.path.join(
        logging_dir, f'{__name__}.log'
    )
    logging_config['handlers']['file']['filename'] = logging_filename
    logging.config.dictConfig(logging_config)


def exit_gracefully(signum: signal.Signals, frame):

    logger.info(f"\n{'-'*os.get_terminal_size().columns}")
    logger.info('Program terminated with Ctrl-C')
    print(f"\n{'-'*os.get_terminal_size().columns}")
    print('\nProgram terminated with Ctrl-C')

    sys.exit(0)
