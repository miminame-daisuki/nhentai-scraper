import os
import datetime
from pathlib import Path
import sys
import json
import yaml
import logging
import logging.config
from typing import Union, Optional

from print_colored_text import bcolors

logger = logging.getLogger("__main__." + __name__)


def create_gallery_results_dict(repeat_ids: list, blacklist: list) -> dict:

    gallery_results = {
        "finished": [],
        "already_downloaded": [],
        "repeats": repeat_ids,
        "blacklists": blacklist,
        "updated_tags": [],
        "initial_fails": [],
        "retry_fails": [],
    }
    return gallery_results


def print_start_message(download_dir) -> None:

    message = (
        f"\n{bcolors.HEADER}NHENTAI SCRAPER{bcolors.ENDC}\n\n"
        f"Downloading to: {download_dir}\n"
    )

    print('\u2500'*os.get_terminal_size().columns)
    print(message)
    print('\u2500'*os.get_terminal_size().columns)


def get_application_folder_dir() -> str:

    application_folder_dir = ""
    # when running executable
    if getattr(sys, "frozen", False):
        application_folder_dir = os.path.dirname(sys.executable)
    # when running python script (placed inside ./src/)
    elif __file__:
        application_folder_dir = os.path.abspath(
            f"{os.path.dirname(__file__)}/.."
        )
    else:
        application_folder_dir = os.path.abspath(f"{os.getcwd()}/..")

    return application_folder_dir


def set_download_dir(download_dir: Optional[Union[str, Path]] = None) -> Path:

    application_folder_path = get_application_folder_dir()
    if download_dir is None:
        download_dir = Path(application_folder_path) / "Downloaded"
    if not Path(download_dir).is_absolute():
        download_dir = Path(application_folder_path) / download_dir
    download_dir = Path(download_dir).absolute()

    if not download_dir.is_dir():
        download_dir.mkdir()

    return download_dir


def set_logging_config(
    logging_config_filename: Optional[Union[str, Path]] = None,
) -> None:

    application_folder_path = get_application_folder_dir()
    logging_dir = os.path.abspath(f"{application_folder_path}/logs/")
    if logging_config_filename is None:
        logging_config_filename = os.path.join(
            logging_dir, "logging_config.yaml"
        )

    logging_config_filename = Path(logging_config_filename)
    with open(logging_config_filename) as f:
        if logging_config_filename.suffix == ".yaml":
            logging_config = yaml.full_load(f)
        elif logging_config_filename.suffix == ".json":
            logging_config = json.load(f)

    logging_filename = os.path.join(
        logging_dir, f"{str(datetime.date.today())}.log"
    )
    logging_config["handlers"]["file"]["filename"] = logging_filename
    logging.config.dictConfig(logging_config)
