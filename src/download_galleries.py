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
import signal
import sys
from typing import Union, Optional

import nhentai_scraper
import misc
from print_colored_text import bcolors


logger = logging.getLogger('__main__.' + __name__)


def download_id_list(
    id_list: list[str],
    id_list_name: str,
    download_dir: Union[str, Path],
    session: requests.sessions.Session,
    additional_tags: Optional[list[str]] = None,
    download_repeats: Optional[bool] = False,
    gallery_results: Optional[dict[str, list[str]]] = None,
) -> dict[str, list[str]]:

    gallery_results_extend = {
        'finished': [],
        'already_downloaded': [],
        'repeats': [],
        'blacklists': [],
        'initial_fails': [],
        'retry_fails': [],
    }

    print()  # blank line between seapration and progress bar for each gallery
    progress_bar = tqdm(
        enumerate(id_list, start=1),
        total=len(id_list),
        desc=f"Downloading galleries from {id_list_name}",
        leave=False,
    )
    for count, gallery_id in progress_bar:

        logger.info(f"\n{'-'*os.get_terminal_size().columns}")
        logger.info(
            (f'Downloading number {count} '
             f'out of {len(id_list)} galleries...')
        )
        gallery = nhentai_scraper.Gallery(
            gallery_id, session=session, download_dir=download_dir,
            additional_tags=additional_tags,
            download_repeats=download_repeats,
        )
        gallery.download()

        record_gallery_results(
            gallery_results_extend,
            gallery,
            initial_try=True
        )

        if gallery_results:
            record_gallery_results(
                gallery_results,
                gallery,
                initial_try=True
            )

    # retry failed galleries
    if gallery_results_extend['initial_fails']:
        print('\nRetrying failed galleries...\n')

        progress_bar_retry = tqdm(
                enumerate(gallery_results_extend['initial_fails'], start=1),
                total=len(gallery_results_extend['initial_fails']),
                leave=False
            )
        for count, gallery_id in progress_bar_retry:
            logger.info(f"\n{'-'*os.get_terminal_size().columns}")
            logger.info(
                (f'Downloading number {count} '
                 f'out of {len(id_list)} galleries...')
            )

            gallery = nhentai_scraper.Gallery(
                gallery_id, session=session, download_dir=download_dir,
                additional_tags=additional_tags,
                download_repeats=download_repeats,
            )
            gallery.download()

            record_gallery_results(
                gallery_results_extend,
                gallery,
                initial_try=False
            )

            if gallery_results:
                record_gallery_results(
                    gallery_results,
                    gallery,
                    initial_try=False
                )

    elapsed = progress_bar.format_dict['elapsed']
    elapsed_time = progress_bar.format_interval(elapsed)

    print_gallery_results(
        gallery_results_extend,
        id_list_name,
        elapsed_time,
    )

    return gallery_results_extend


def record_gallery_results(
    gallery_results: dict[str, list[str]],
    gallery: nhentai_scraper.Gallery,
    initial_try: Optional[bool] = True
) -> dict[str, list[str]]:

    if gallery.status_code == 0:
        gallery_results['finished'].append(f'#{gallery.id}')
    elif gallery.status_code == 1:
        gallery_results['already_downloaded'].append(f'#{gallery.id}')
    elif gallery.status_code == 2:
        gallery_results['repeats'].append(f'#{gallery.id}')
    elif gallery.status_code == 3:
        gallery_results['blacklists'].append(f'#{gallery.id}')

    if initial_try and gallery.status_code < -1:
        gallery_results['initial_fails'].append(f'#{gallery.id}')
        gallery_results['retry_fails'].append(gallery.status())
    elif not initial_try and gallery.status_code >= -1:
        # remove from retry_fails if download successful during retry
        for result in gallery_results['retry_fails']:
            if f'#{gallery.id}' in result:
                gallery_results['retry_fails'].remove(result)

    return gallery_results


def print_gallery_results(
    gallery_results: dict[str, list[str]],
    id_list_name: str,
    elapsed_time: str,
) -> None:

    total_download_counts = 0
    keys = ['finished', 'repeats', 'blacklists', 'retry_fails']
    for key in keys:
        total_download_counts += len(gallery_results[key])

    print()
    if total_download_counts > 0:
        print(
            f"Finished downloading {len(gallery_results['finished'])} "
            f'out of {total_download_counts} galleries from {id_list_name} '
            f'in {elapsed_time}.'
        )
    if len(gallery_results['repeats']) > 0:
        print(
            'Skipped download of '
            f"{len(gallery_results['repeats'])} repeated galleries."
        )
    if len(gallery_results['blacklists']) > 0:
        print(f"{len(gallery_results['blacklists'])} galleries BLACKLISTED.")
    if len(gallery_results['retry_fails']) > 0:
        print(
            f'{bcolors.FAIL}'
            "Failed to download "
            f"{len(gallery_results['retry_fails'])} galleries."
            f'{bcolors.ENDC}'
        )
    print()


def write_gallery_results(
    gallery_results: dict[str, list[str]],
    filename: Union[str, Path]
) -> None:

    # write the failed retry galleries to failed_downloads.txt
    application_folder_path = misc.get_application_folder_dir()
    inputs_folder_dir = os.path.abspath(
        f'{application_folder_path}/inputs/'
    )
    filename = os.path.join(inputs_folder_dir, filename)

    with open(filename, 'w') as f:
        for entry in gallery_results:
            f.write(entry)
            f.write('\n')


def write_final_results(gallery_results: dict):
    if gallery_results['retry_fails']:
        write_gallery_results(
            gallery_results['retry_fails'],
            'failed_downloads.txt'
        )
        print(
            f"\n\nFinished {len(gallery_results['finished'])} "
            'gallery downloads in total.'
        )
        print(
            f'{bcolors.FAIL}'
            f"{len(gallery_results['retry_fails'])} failed downloads "
            "written to 'failed_downloads.txt'\n\n"
            f'{bcolors.ENDC}'
        )
        print(f"{'-'*os.get_terminal_size().columns}")
        logger.info(
            '\n\nFailed downloads written to failed_downloads.txt\n\n'
        )

    else:
        print(
            f"\n\nFinished all {len(gallery_results['finished'])} "
            'gallery downloads!!!\n\n'
        )
        print(f"{'-'*os.get_terminal_size().columns}")
        logger.info(f"\n{'-'*os.get_terminal_size().columns}")
        logger.info('Finished all downloads')


def exit_gracefully(
    gallery_results: dict,
    signum: signal.Signals,
    frame
) -> None:

    logger.info(f"\n{'-'*os.get_terminal_size().columns}")
    logger.info('Program terminated with Ctrl-C')
    print(f"\n{'-'*os.get_terminal_size().columns}")
    print('\nProgram terminated with Ctrl-C.')
    write_final_results(gallery_results)

    sys.exit(0)
