import os
import sys
from subprocess import run
from pathlib import Path
import json
from typing import Union, Optional

import misc


def load_input_list(filename: str) -> list[str]:

    application_folder_path = misc.get_application_folder_dir()
    inputs_folder_dir = os.path.abspath(f'{application_folder_path}/inputs/')

    filename = f'{inputs_folder_dir}/{filename}'
    with open(filename) as f:
        id_list = f.read().splitlines()

    id_list = [entry for entry in id_list if not entry == '']

    return id_list


def load_json(
    filename: Union[str, Path],
    inputs_dir: Optional[Union[str, Path]] = None
) -> dict:

    if filename.split('.')[-1] != 'json':
        print('Not json file')
        return {}

    if inputs_dir is None:
        application_folder_path = misc.get_application_folder_dir()
        inputs_dir = os.path.abspath(f'{application_folder_path}/inputs/')

    json_filename = f'{inputs_dir}/{filename}'
    with open(json_filename) as f:
        json_dict = json.load(f)

    return json_dict


def write_cookies(inputs_path: Path):
    cookies = {}
    cookies['cf_clearance'] = input('cf_clearance: ')
    cookies['sessionid'] = input('sessionid :')
    with open(inputs_path / 'cookies.json', 'w') as f:
        json.dump(cookies, f, indent=4)


def write_headers(inputs_path: Path):
    headers = {}
    headers['User-Agent'] = input('User-Agent: ')
    with open(inputs_path / 'headers.json', 'w') as f:
        json.dump(headers, f, indent=4)


def confirm_settings() -> dict:

    settings = {}

    # confirm download location
    application_folder_path = misc.get_application_folder_dir()
    download_dir = os.path.abspath(
        f'{application_folder_path}/Downloaded/'
    )
    while True:
        confirm_download_dir = input((f'Download to {download_dir}?(y/n)'))
        if confirm_download_dir != 'y':
            download_dir = input('Download directory: ')
            download_dir = misc.set_download_dir(download_dir)
        else:
            break
    settings['download_dir'] = download_dir

    # create `cookies.json` and `headers.json` if not present in `inputs/`
    inputs_path = Path(f'{application_folder_path}/inputs').absolute()
    if 'cookies.json' not in [file.name for file in inputs_path.iterdir()]:
        write_cookies(inputs_path)
    else:
        x = input('Update cookies? (y/n)')
        if x != 'n':
            write_cookies(inputs_path)
    if 'headers.json' not in [file.name for file in inputs_path.iterdir()]:
        write_headers(inputs_path)

    check_fileicon_tag_install()

    skip_downloaded_ids = input('Skip downloaded galleries?(y/n)')
    if skip_downloaded_ids == 'y':
        skip_downloaded_ids = True
    else:
        skip_downloaded_ids = False
    settings['skip_downloaded_ids'] = skip_downloaded_ids

    print('-'*os.get_terminal_size().columns)

    return settings


def check_fileicon_tag_install():
    check_fileicon_command = ['which', 'fileicon']
    result = run(check_fileicon_command, capture_output=True)
    if result.returncode != 0:
        print(
            "Please install 'fileicon' from "
            "'https://github.com/mklement0/fileicon'"
        )
        sys.exit('fileicon not installed')

    check_tag_command = ['which', 'tag']
    result = run(check_tag_command, capture_output=True)
    if result.returncode != 0:
        print(
            "Please install 'tag' from "
            "'https://github.com/jdberry/tag'"
        )
        sys.exit('tag not installed')
