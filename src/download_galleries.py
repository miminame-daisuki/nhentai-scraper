#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 19:43:58 2024

@author: ball
"""

import os
from pathlib import Path
import sys
from subprocess import run
import json
from tqdm import tqdm
import logging

import nhentai_scraper


logger = logging.getLogger('__main__.' + __name__)


def download_id_list(
    id_list, download_dir,
    additional_tags=None, id_list_name=None
):

    gallery_results = {
        'finished': [],
        'repeats': [],
        'blacklists': [],
        'initial_fails': [],
        'retry_fails': [],
    }

    progress_bar = tqdm(enumerate(id_list, start=1), total=len(id_list))
    for count, gallery_id in progress_bar:
        if id_list_name is not None:
            progress_bar.set_description(
                f"Downloading galleries from {id_list_name}"
            )

        logger.info(f"\n{'-'*os.get_terminal_size().columns}")
        logger.info(
            (f'Downloading number {count} '
             f'out of {len(id_list)} galleries...')
        )
        gallery = nhentai_scraper.Gallery(
            gallery_id, download_dir=download_dir,
            additional_tags=additional_tags
        )
        gallery.download()

        record_gallery_results(gallery_results, gallery, initial_try=True)

    # retry failed galleries
    if gallery_results['initial_fails']:
        print('\nRetrying failed galleries...\n')

        progress_bar = tqdm(
                enumerate(gallery_results['initial_fails'], start=1),
                total=len(gallery_results['initial_fails'])
            )
        for count, gallery_id in progress_bar:
            logger.info(f"\n{'-'*os.get_terminal_size().columns}")
            logger.info(
                (f'Downloading number {count} '
                 f'out of {len(id_list)} galleries...')
            )

            gallery = nhentai_scraper.Gallery(
                gallery_id, download_dir=download_dir,
                additional_tags=additional_tags
            )
            gallery.download()

            record_gallery_results(gallery_results, gallery, initial_try=False)

    print_gallery_results(gallery_results)

    return gallery_results


def record_gallery_results(gallery_results, gallery, initial_try=True):

    if gallery.status_code == 0 or gallery.status_code == 1:
        gallery_results['finished'].append(gallery.id)
    elif gallery.status_code == 2:
        gallery_results['repeats'].append(f'#{gallery.id}')
    elif gallery.status_code == -5:
        gallery_results['blacklists'].append(f'#{gallery.id}')
    else:
        if initial_try:
            gallery_results['initial_fails'].append(f'#{gallery.id}')
        else:
            gallery_results['retry_fails'].append(gallery.status())
        logger.error(gallery.status())

    return gallery_results


def print_gallery_results(gallery_results):

    total_download_counts = 0
    keys = ['finished', 'repeats', 'blacklists', 'retry_fails']
    for id_list in keys:
        total_download_counts += len(id_list)

    print(
        (f"\nFinished {len(gallery_results['finished'])} "
         f'out of {total_download_counts} gallery downloads in total')
    )
    print(
        (f"{len(gallery_results['repeats'])} "
         'repeated galleries not downloaded')
    )
    print(f"{len(gallery_results['blacklists'])} BLACKLISTED")
    print(
        (f"{len(gallery_results['retry_fails'])} "
         'failed retry galleries')
    )
    print(f"\n{'-'*os.get_terminal_size().columns}")


def write_gallery_results(gallery_results, filename):

    # write the failed retry galleries to failed_download_id.txt
    application_folder_path = nhentai_scraper.get_application_folder_dir()
    inputs_folder_dir = os.path.abspath(
        f'{application_folder_path}/inputs/'
    )
    filename = os.path.join(inputs_folder_dir, filename)

    with open(filename, 'w') as f:
        for entry in gallery_results:
            f.write(entry)
            f.write('\n')


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


def confirm_settings():

    settings = {}

    # confirm download location
    application_folder_path = nhentai_scraper.get_application_folder_dir()
    download_dir = os.path.abspath(
        f'{application_folder_path}/Downloaded/'
    )
    while True:
        confirm_download_dir = input((f'Download to {download_dir}?(y/n)'))
        if confirm_download_dir != 'y':
            download_dir = input('Download directory: ')
            download_dir = nhentai_scraper.set_download_dir(download_dir)
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

    # check `fileicon` and `tag` installation
    check_fileicon_command = [
        'which',
        'fileicon'
    ]
    result = run(check_fileicon_command, capture_output=True)
    if result.returncode != 0:
        print(
            "Please install 'fileicon' from "
            "'https://github.com/mklement0/fileicon'"
        )
        sys.exit('fileicon not installed')
    check_tag_command = [
        'which',
        'tag'
    ]
    result = run(check_tag_command, capture_output=True)
    if result.returncode != 0:
        print(
            "Please install 'tag' from "
            "'https://github.com/jdberry/tag'"
        )
        sys.exit('tag not installed')

    skip_downloaded_ids = input('Skip downloaded galleries?(y/n)')
    if skip_downloaded_ids == 'y':
        skip_downloaded_ids = True
    else:
        skip_downloaded_ids = False
    settings['skip_downloaded_ids'] = skip_downloaded_ids

    print('-'*os.get_terminal_size().columns)

    return settings


# def main():

#     nhentai_scraper.set_logging_config()
#     logger.info(f"\n{'-'*os.get_terminal_size().columns}")
#     logger.info('Program started')
#     download_dir = confirm_settings()
#     id_list = nhentai_scraper.load_input_list('download_id.txt')
#     failed_galleries = download_id_list(id_list, download_dir)
#     if len(failed_galleries['repeated_galleries']) != 0:
#         write_failed_galleries(
#             failed_galleries['repeated_galleries'], 'repeated_galleries.txt'
#         )
#     if len(failed_galleries['failed_retry_galleries']) != 0:
#         write_failed_galleries(
#             failed_galleries['failed_retry_galleries'],
#             'failed_download_id.txt'
#         )
#     else:
#         print('\n\n\nFinished all downloads!!!\n\n')


# if __name__ == '__main__':
#     main()
