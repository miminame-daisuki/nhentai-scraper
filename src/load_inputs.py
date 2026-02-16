import os
from pathlib import Path
import json
from typing import Union, Optional

import cli
import misc


def load_input_list(
    filename: Union[str, Path], skip_to_tag: Optional[str] = ''
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
        print('Not json file.')
        return {}

    if inputs_dir is None:
        application_folder_path = misc.get_application_folder_dir()
        inputs_dir = os.path.abspath(f'{application_folder_path}/inputs/')

    json_filename = f'{inputs_dir}/{filename}'
    with open(json_filename) as f:
        json_dict = json.load(f)

    return json_dict


def load_nhentai_cookies(inputs_dir: Optional[Path] = None) -> dict:

    if inputs_dir is None:
        application_folder_path = misc.get_application_folder_dir()
        inputs_dir = Path(application_folder_path).absolute() / "inputs/"

    json_filename = inputs_dir / "nhentai.net.har"
    with open(json_filename) as f:
        nhentai_net_jar = json.load(f)

    if nhentai_net_jar["log"]["pages"][0]["title"] != "https://nhentai.net/":
        raise Exception("Please export from 'https://nhentai.net'")

    nhentai_headers = next(
        entry["request"]["headers"]
        for entry in nhentai_net_jar["log"]["entries"]
        if entry["request"]["url"] == "https://nhentai.net/"
    )

    nhentai_Cookie = next(
        item['value'] for item in nhentai_headers if item['name'] == 'Cookie'
    )

    return nhentai_Cookie


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

    # load command line arguments
    args = cli.cli_parser()

    # confirm download location
    application_folder_path = misc.get_application_folder_dir()
    download_dir = str(misc.set_download_dir())
    if args.confirm_settings:
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
    if 'headers.json' not in [file.name for file in inputs_path.iterdir()]:
        write_headers(inputs_path)

    if args.update_cookies:
        write_cookies(inputs_path)

    settings['redownload_downloaded'] = args.redownload_downloaded

    settings['skip_to_tag'] = args.skip_to_tag

    return settings
