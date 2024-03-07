#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 22:22:59 2024

@author: ball
"""
from bs4 import BeautifulSoup

import os
import logging

import nhentai_scraper
import download_galleries


logger = logging.getLogger(__name__)


def get_gallery_id(url, headers={}, cookies={}):
    # retrieves all <=25 gallery ids from a nhentai url

    gallery_id = []

    response = nhentai_scraper.get_response(url,
                                            headers=headers,
                                            cookies=cookies)
    soup = BeautifulSoup(response.content, features='html.parser')
    gallery_count = soup.find('span', {'class': 'count'}).string
    page_count = int(gallery_count)//25 + 1
    gallery_list = soup.find_all('div', {'class': 'gallery'})
    for gallery in gallery_list:
        gallery_id.append(gallery.find('a').get('href').split('/')[2])

    return gallery_id, page_count


# retrieves all gallery ids from a tag
def search_tag(tag: str):

    print(f"\nSearching galleries from {tag}")
    tag_url = f"https://nhentai.net/{tag.split(':')[0]}/{tag.split(':')[1]}/"
    application_folder_path = nhentai_scraper.get_application_folder_dir()
    inputs_dir = os.path.abspath(f'{application_folder_path}/inputs/')
    headers = nhentai_scraper.load_headers(inputs_dir)
    cookies = nhentai_scraper.load_cookies(inputs_dir)
    id_list, page_count = get_gallery_id(tag_url,
                                         headers=headers,
                                         cookies=cookies)

    for page in range(2, page_count+1):
        page_url = tag_url + f'?page={page}'
        id_list.extend(get_gallery_id(page_url,
                                      headers=headers,
                                      cookies=cookies)[0])

    return id_list


def main():

    nhentai_scraper.set_logging_config()
    logger.info('Program started')
    download_dir = download_galleries.confirm_settings()
    tag_list = nhentai_scraper.load_input_list('download_tags.txt')
    failed_galleries = {
        'failed_galleries': [],
        'failed_retry_galleries': [],
        'repeated_galleries': []
    }
    for tag in tag_list:
        try:
            id_list = search_tag(tag)
        except Exception as error:
            logger.error(f'{error}')
            continue
        logger.info(f'Start downloading for {tag}')
        failed_galleries_extend = download_galleries.download_id_list(
            id_list, download_dir
        )
        for key in failed_galleries:
            failed_galleries[key].extend(
                failed_galleries_extend[key]
            )
    if len(failed_galleries['repeated_galleries']) != 0:
        download_galleries.write_failed_galleries(
            failed_galleries['repeated_galleries'], 'repeated_galleries.txt'
        )
    if len(failed_galleries['failed_retry_galleries']) != 0:
        download_galleries.write_failed_galleries(
            failed_galleries['failed_retry_galleries'],
            'failed_download_id.txt'
        )
    else:
        print('\n\n\nFinished all downloads!!!\n\n')


if __name__ == '__main__':
    main()
