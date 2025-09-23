import os
import sys
from subprocess import run
from pathlib import Path
import json
from typing import Union, Optional

import misc


def load_input_list(
    filename: str, skip_to_tag: Optional[str] = ''
) -> list[str]:

    application_folder_path = misc.get_application_folder_dir()
    if filename[0] != '/':
        inputs_folder_dir = os.path.abspath(f'{application_folder_path}/inputs/')
        filename = Path(f'{inputs_folder_dir}/{filename}')
    else:
        filename = Path(filename)

    filename.touch(exist_ok=True)
    with open(filename) as f:
        download_list = f.read().splitlines()

    download_list = [entry for entry in download_list if not entry == '']

    if skip_to_tag:
        skip_to_index = download_list.index(skip_to_tag)
        download_list = download_list[skip_to_index:]

    return download_list


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


def write_cookies(inputs_path: Path) -> None:
    # cookies = {}
    # cookies['cf_clearance'] = input('cf_clearance: ')
    # cookies['sessionid'] = input('sessionid :')
    cookies = input('Cookie: ')
    cookies = {
        line.split('=')[0]: line.split('=')[1] for line in cookies.split('; ')
    }
    with open(inputs_path / 'cookies.json', 'w') as f:
        json.dump(cookies, f, indent=4)


def write_headers(inputs_path: Path) -> None:
    headers = {}
    headers['User-Agent'] = input('User-Agent: ')
    with open(inputs_path / 'headers.json', 'w') as f:
        json.dump(headers, f, indent=4)


def confirm_settings() -> dict:

    settings = {}

    # confirm download location
    application_folder_path = misc.get_application_folder_dir()
    download_dir = str(misc.set_download_dir())
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

    skip_downloaded_ids = input('Skip downloaded galleries?(y/n)')
    if skip_downloaded_ids == 'y':
        skip_downloaded_ids = True
    else:
        skip_downloaded_ids = False
    settings['skip_downloaded_ids'] = skip_downloaded_ids

    settings['skip_to_tag'] = input('Skip to tag?(Press Enter for no skip)')

    print('-'*os.get_terminal_size().columns)

    return settings
