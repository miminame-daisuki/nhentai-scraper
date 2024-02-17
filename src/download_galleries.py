#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 19:43:58 2024

@author: ball
"""
import os

from nhentai_scraper import Gallery

def load_download_list():
    cur_path = os.path.dirname(__file__)
    inputs_folder_path = os.path.relpath('../inputs/', cur_path)
    filename = f'{inputs_folder_path}/download_list.txt'
    with open(filename) as f:
        download_list = f.read().splitlines()
    download_list = [entry for entry in download_list if not entry == '']

    return download_list

def main():
    
    x = input('Confirm using vpn (y/n)')
    if x != 'y':
        return 
    
    failed_galleries = []
    failed_retry_galleries = []
    
    download_list = load_download_list()
    for count, gallery_id in zip(range(len(download_list)), download_list):
        print(f'Downloading number {count+1} out of {len(download_list)} galleries...')        
        gallery = Gallery(gallery_id)
        gallery.download()
        if gallery.status[:20] != 'Finished downloading':
            failed_galleries.append(f'{gallery_id}')
    
    # write the failed galleries to failed_download_list.txt
    if len(failed_galleries) != 0:
        print('\n\nRetrying failed galleries...')
        print(f"\n\n{'-'*200}")
        for gallery_id in failed_galleries:
            gallery = Gallery(gallery_id)
            gallery.download()
            if gallery.status[:20] != 'Finished downloading':
                failed_retry_galleries.append(f'{gallery_id}, status: {gallery.status}')
        
        if len(failed_retry_galleries) != 0:
            cur_path = os.path.dirname(__file__)
            inputs_folder_path = os.path.relpath('../inputs/', cur_path)
            filename = f'{inputs_folder_path}/failed_download_list.txt'
            with open(filename, 'w') as f:
                for entry in failed_retry_galleries:
                    f.write(entry)
                    f.write('\n')
            print(f'\n\n\nFailed gallery id written to {filename}\n\n')
        else:
            print('\n\n\nFinished all downloads!!!\n\n')
    else:
        print('\n\n\nFinished all downloads!!!\n\n')
        
if __name__ == '__main__':
    main()
