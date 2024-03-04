#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 19:43:58 2024

@author: ball
"""
import os

from nhentai_scraper import Gallery, get_application_folder_dir


def load_download_list():

    application_folder_path = get_application_folder_dir()
    inputs_folder_dir = os.path.abspath(f'{application_folder_path}/inputs/')
    filename = f'{inputs_folder_dir}/download_list.txt'
    with open(filename) as f:
        download_list = f.read().splitlines()
    download_list = [entry for entry in download_list if not entry == '']

    return download_list


def download_id_list(id_list, download_dir):

    failed_galleries = []
    failed_retry_galleries = []
    for count, gallery_id in enumerate(id_list, start=1):
        print(f'Downloading number {count} out of {len(id_list)} galleries...')
        gallery = Gallery(gallery_id, download_dir=download_dir)
        gallery.download()
        if gallery.status[:20] != 'Finished downloading':
            failed_galleries.append(f'{gallery_id}')

    # retry failed galleries
    if len(failed_galleries) != 0:
        print('\n\nRetrying failed galleries...')
        print(f"\n\n{'-'*200}")
        for gallery_id in failed_galleries:
            gallery = Gallery(gallery_id, download_dir=download_dir)
            gallery.download()
            if gallery.status[:20] != 'Finished downloading':
                failed_retry_galleries.append(f'{gallery_id}, status: {gallery.status}')

    return failed_retry_galleries


def write_failed_retry_galleries(failed_retry_galleries):

    application_folder_path = get_application_folder_dir()
    inputs_folder_dir = os.path.abspath(f'{application_folder_path}/inputs/')
    filename = f'{inputs_folder_dir}/failed_download_list.txt'
    with open(filename, 'w') as f:
        for entry in failed_retry_galleries:
            f.write(entry)
            f.write('\n')
    print(f'\n\n\nFailed gallery id written to {filename}\n\n')


def main():

    x = input('Confirm using vpn (y/n)')
    if x != 'y':
        return

    # confirm download location
    download_dir = os.path.abspath(f'{get_application_folder_dir()}/Downloaded/')
    while True:
        confirm_download_dir = input((f'Download to {download_dir}?(y/n)'))
        if confirm_download_dir != 'y':
            download_dir = str(input('Download directory: '))
        else:
            break

    id_list = load_download_list()
    failed_retry_galleries = download_id_list(id_list, download_dir)

    # write the failed retry galleries to failed_download_list.txt
    if len(failed_retry_galleries) != 0:
        write_failed_retry_galleries(failed_retry_galleries)
    else:
        print('\n\n\nFinished all downloads!!!\n\n')


if __name__ == '__main__':
    main()
