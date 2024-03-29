import os
import sys
import json
import yaml
import logging
import logging.config


logger = logging.getLogger('__main__.' + __name__)


def get_application_folder_dir():

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


def set_download_dir(download_dir=''):

    application_folder_path = get_application_folder_dir()

    if download_dir:
        if os.path.isabs(download_dir):
            pass
        else:
            download_dir = os.path.abspath(
                f'{application_folder_path}/{download_dir}/'
            )
    else:
        download_dir = os.path.abspath(
            f'{application_folder_path}/Downloaded/'
        )

    if not os.path.isdir(download_dir):
        os.mkdir(download_dir)

    return download_dir


def set_logging_config(logging_config_filename=''):
    application_folder_path = get_application_folder_dir()
    logging_dir = os.path.abspath(f'{application_folder_path}/log/')
    if not logging_config_filename:
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


def exit_gracefully(signum, frame):
    logger.info(f"\n{'-'*os.get_terminal_size().columns}")
    logger.info('Program terminated with Ctrl-C')
    sys.exit(0)
