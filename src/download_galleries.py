#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 19:43:58 2024

@author: ball
"""

import os
from pathlib import Path
import requests
from tqdm import tqdm
import logging
from typing import Union, Optional

import nhentai_scraper
import misc


logger = logging.getLogger('__main__.' + __name__)


def download_id_list(
    id_list: list[str],
    download_dir: Union[str, Path],
    session: requests.sessions.Session,
    additional_tags: Optional[list[str]] = None,
    id_list_name: Optional[str] = None
) -> dict:

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
            gallery_id, session, download_dir=download_dir,
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
                gallery_id, session, download_dir=download_dir,
                additional_tags=additional_tags
            )
            gallery.download()

            record_gallery_results(gallery_results, gallery, initial_try=False)

    print_gallery_results(gallery_results)

    return gallery_results


def record_gallery_results(
    gallery_results: dict,
    gallery: nhentai_scraper.Gallery,
    initial_try: Optional[bool] = True
) -> dict:

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


def print_gallery_results(gallery_results: dict):

    total_download_counts = 0
    keys = ['finished', 'repeats', 'blacklists', 'retry_fails']
    for key in keys:
        total_download_counts += len(gallery_results[key])

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


def write_gallery_results(
    gallery_results: dict,
        filename: Union[str, Path]
):

    # write the failed retry galleries to failed_download_id.txt
    application_folder_path = misc.get_application_folder_dir()
    inputs_folder_dir = os.path.abspath(
        f'{application_folder_path}/inputs/'
    )
    filename = os.path.join(inputs_folder_dir, filename)

    with open(filename, 'w') as f:
        for entry in gallery_results:
            f.write(entry)
            f.write('\n')


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
