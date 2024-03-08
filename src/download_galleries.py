#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 19:43:58 2024

@author: ball
"""

import os
import logging

import nhentai_scraper


logger = logging.getLogger('__main__.' + __name__)


def download_id_list(id_list, download_dir):

    failed_galleries = {
        'initial_failed_galleries': [],
        'failed_retry_galleries': [],
        'repeated_galleries': []
    }

    finished_count = 0
    for count, gallery_id in enumerate(id_list, start=1):
        logger.info(f"\n{'-'*200}")
        logger.info((f'Downloading number {count} '
                     f'out of {len(id_list)} galleries...'))
        gallery = nhentai_scraper.Gallery(gallery_id,
                                          download_dir=download_dir)
        gallery.download()
        if gallery.status_code == 0 or gallery.status_code == 1:
            finished_count += 1
            print((f'Finished {finished_count} '
                   f'out of {len(id_list)} gallery downloads.'))
        elif gallery.status_code == 2:
            failed_galleries['repeated_galleries'].append(
                f"{gallery.status()}"
            )
        else:
            failed_galleries['initial_failed_galleries'].append(
                f'{gallery_id}'
            )
            logger.error((f'Failed to download #{gallery_id}, due to '
                          f"{gallery.status()}"))

    # retry failed galleries
    if len(failed_galleries['initial_failed_galleries']) != 0:
        print('\nRetrying failed galleries...')
        for gallery_id in failed_galleries['initial_failed_galleries']:
            gallery = nhentai_scraper.Gallery(gallery_id,
                                              download_dir=download_dir)
            gallery.download()
            if gallery.status_code != 0:
                failed_galleries['failed_retry_galleries'].append(
                    (f'{gallery_id}, status: '
                     f"{gallery.status_list[gallery.status_code]}")
                )
        print(f"\n{'-'*200}")

    print((f"\nFinished {finished_count} out of {len(id_list)} gallery "
           'downloads in total'))
    print((f"{len(failed_galleries['failed_retry_galleries'])} "
           'failed retry galleries'))
    print((f"{len(failed_galleries['repeated_galleries'])} "
           'repeated galleries not downloaded'))

    return failed_galleries


def write_failed_galleries(failed_galleries, filename):

    # write the failed retry galleries to failed_download_id.txt
    application_folder_path = nhentai_scraper.get_application_folder_dir()
    inputs_folder_dir = os.path.abspath((f'{application_folder_path}'
                                         '/inputs/'))
    filename = os.path.join(inputs_folder_dir, filename)
    with open(filename, 'w') as f:
        for entry in failed_galleries:
            f.write(entry)
            f.write('\n')
    print(f'\n\n\nFailed gallery id written to {filename}\n\n')


def confirm_settings():

    while True:
        x = input('Confirm using vpn?(y/n)')
        if x != 'y':
            continue
        else:
            break

    while True:
        x = input('Confirm updated cf_clearance?(y/n)')
        if x != 'y':
            continue
        else:
            break

    # confirm download location
    download_dir = os.path.abspath(
        f'{nhentai_scraper.get_application_folder_dir()}/Downloaded/'
    )
    while True:
        confirm_download_dir = input((f'Download to {download_dir}?(y/n)'))
        if confirm_download_dir != 'y':
            download_dir = str(input('Download directory: '))
        else:
            break

    print(f"\n{'-'*200}")

    return download_dir


def main():

    nhentai_scraper.set_logging_config()
    logger.info(f"\n{'-'*200}")
    logger.info('Program started')
    download_dir = confirm_settings()
    id_list = nhentai_scraper.load_input_list('download_id.txt')
    failed_galleries = download_id_list(id_list, download_dir)
    if len(failed_galleries['repeated_galleries']) != 0:
        write_failed_galleries(
            failed_galleries['repeated_galleries'], 'repeated_galleries.txt'
        )
    if len(failed_galleries['failed_retry_galleries']) != 0:
        write_failed_galleries(
            failed_galleries['failed_retry_galleries'],
            'failed_download_id.txt'
        )
    else:
        print('\n\n\nFinished all downloads!!!\n\n')


if __name__ == '__main__':
    main()
