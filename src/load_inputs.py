import os
import argparse
import copy
from pathlib import Path
import json
import yaml
from typing import Union, Optional

import cli
import misc


def load_input_list(
    filename: Union[str, Path], skip_to_tag: Optional[str] = ""
) -> list[str]:

    application_folder_path = misc.get_application_folder_dir()
    filename = Path(filename)
    if not filename.is_absolute():
        inputs_folder_dir = os.path.abspath(
            f"{application_folder_path}/inputs/"
        )
        filename = Path(f"{inputs_folder_dir}/{filename}")
    else:
        filename = Path(filename)

    if not filename.exists():
        raise Exception("'download_list.txt' doesn't exist in inputs/ folder!")

    with open(filename) as f:
        download_list = f.read().splitlines()

    download_list = [entry for entry in download_list if not entry == ""]

    if skip_to_tag:
        skip_to_index = download_list.index(skip_to_tag)
        download_list = download_list[skip_to_index:]

    return download_list


def create_config_yaml(inputs_path: Optional[Path] = None) -> None:

    if inputs_path is None:
        application_folder_path = misc.get_application_folder_dir()
        inputs_path = Path(f"{application_folder_path}/inputs").absolute()

    # create config.yaml from config_template.yaml
    config_template_filename = inputs_path / "config_template.yaml"
    with open(config_template_filename, "r") as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    with open(inputs_path / "config.yaml", "w") as f:
        yaml.dump(config, f)


def load_config_yaml(
    inputs_path: Optional[Path] = None,
    args: Optional[argparse.Namespace] = None,
) -> dict:

    if inputs_path is None:
        application_folder_path = misc.get_application_folder_dir()
        inputs_path = Path(f"{application_folder_path}/inputs").absolute()

    config_filename = inputs_path / "config.yaml"
    if not config_filename.exists():
        create_config_yaml()
    with open(config_filename, "r") as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    config["downloads"]["download_dir"] = str(
        misc.set_download_dir(config["downloads"]["download_dir"])
    )

    # populate missing values with default settings
    if config["downloads"]["download_dir"] is None:
        config["downloads"]["download_dir"] = str(misc.set_download_dir())
    if config["downloads"]["filetype"] is None:
        config["downloads"]["filetype"] = "folder"
    if config["downloads"]["set-thumbnail"] is None:
        config["downloads"]["set-thumbnail"] = True
    if config["downloads"]["set-tags"] is None:
        config["downloads"]["set-tags"] = True
    if config["headers"]["User-Agent"] is None:
        config["headers"] = input_headers()
    if not any([value for value in config["cookies"].values()]):
        config["cookies"] = input_cookies()

    if args is not None:
        if args.update_cookies:
            config["headers"] = input_headers()
            config["cookies"] = input_cookies()

    with open(config_filename, "w") as f:
        yaml.dump(config, f)

    return config


def input_cookies() -> dict:

    cookies = input("Cookie: ")
    cookies = {
        line.split("=")[0]: line.split("=")[1] for line in cookies.split("; ")
    }

    return cookies


def input_headers() -> dict:

    headers = {}
    headers["User-Agent"] = input("User-Agent: ")

    return headers


def generate_runtime_settings(inputs_path: Optional[Path] = None) -> dict:

    # load command line arguments and config.yaml
    args = cli.cli_parser()
    config = load_config_yaml(inputs_path=inputs_path, args=args)

    settings = copy.deepcopy(config)

    if args.download_dir:
        settings["downloads"]["download_dir"] = str(
            misc.set_download_dir(args.download_dir)
        )
    if args.filetype:
        settings["downloads"]["filetype"] = args.filetype
    if args.server:
        settings["downloads"]["server"] = args.server
    if args.set_thumbnail:
        settings["downloads"]["set-thumbnail"] = args.set_thumbnail
    if args.set_tags:
        settings["downloads"]["set-tags"] = args.set_tags

    settings["runtime"] = {}
    settings["runtime"]["check-downloaded"] = args.check_downloaded
    settings["runtime"]["skip-to-tag"] = args.skip_to_tag

    # confirm settings
    if args.confirm_settings:
        print(f"{'-'*os.get_terminal_size().columns}")
        print("Runtime settings:")
        print(json.dumps(settings, indent=4))
        print(f"{'-'*os.get_terminal_size().columns}")
        if input("Are these settings correct?(y/n)") != "y":
            raise SystemExit(
                "Please modify these settings in 'inputs/config.yaml'"
                " or set the cli arguments."
            )
        print(f"{'-'*os.get_terminal_size().columns}")

    return settings


if __name__ == "__main__":
    config = load_config_yaml()
    settings = generate_runtime_settings()
