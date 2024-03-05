#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 19:43:58 2024

@author: ball
"""

import os
import logging

import nhentai_scraper


logger = logging.getLogger(__name__)


def load_id_list():

    application_folder_path = nhentai_scraper.get_application_folder_dir()
    inputs_folder_dir = os.path.abspath(f'{application_folder_path}/inputs/')
    filename = f'{inputs_folder_dir}/download_id.txt'
    with open(filename) as f:
        id_list = f.read().splitlines()
    id_list = [entry for entry in id_list if not entry == '']

    return id_list


def download_id_list(id_list, download_dir):

    failed_galleries = []
    failed_retry_galleries = []
    finished_count = 0
    for count, gallery_id in enumerate(id_list, start=1):
        logger.info((f'Downloading number {count} '
                     f'out of {len(id_list)} galleries...'))
        gallery = nhentai_scraper.Gallery(gallery_id,
                                          download_dir=download_dir)
        gallery.download()
        if gallery.status[:20] == 'Finished downloading':
            finished_count += 1
            print((f'Finished {finished_count} '
                   f'out of {len(id_list)} gallery downloads.'))
        else:
            failed_galleries.append(f'{gallery_id}')
            logger.error((f'Failed to download id {gallery_id}, '
                          f'status: {gallery.status}'))

    # retry failed galleries
    if len(failed_galleries) != 0:
        print('\nRetrying failed galleries...')
        for gallery_id in failed_galleries:
            gallery = nhentai_scraper.Gallery(gallery_id,
                                              download_dir=download_dir)
            gallery.download()
            if gallery.status[:20] != 'Finished downloading':
                failed_retry_galleries.append((f'{gallery_id}, '
                                               f'status: {gallery.status}'))
        print(f"\n{'-'*200}")

    return failed_retry_galleries


def check_failed_retry_galleries(failed_retry_galleries):

    if len(failed_retry_galleries) != 0:
        # write the failed retry galleries to failed_download_id.txt
        application_folder_path = nhentai_scraper.get_application_folder_dir()
        inputs_folder_dir = os.path.abspath((f'{application_folder_path}'
                                             '/inputs/'))
        filename = f'{inputs_folder_dir}/failed_download_id.txt'
        with open(filename, 'w') as f:
            for entry in failed_retry_galleries:
                f.write(entry)
                f.write('\n')
        print(f'\n\n\nFailed gallery id written to {filename}\n\n')
    else:
        print('\n\n\nFinished all downloads!!!\n\n')


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
    logger.info('Program started')
    download_dir = confirm_settings()
    id_list = load_id_list()
    failed_retry_galleries = download_id_list(id_list, download_dir)
    check_failed_retry_galleries(failed_retry_galleries)


if __name__ == '__main__':
    main()
