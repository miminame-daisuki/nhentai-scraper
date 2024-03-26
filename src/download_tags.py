#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 22:22:59 2024

@author: ball
"""
from bs4 import BeautifulSoup
import os
import json
from subprocess import run
from tqdm import tqdm
import logging

import nhentai_scraper


logger = logging.getLogger('__main__.' + __name__)


def get_gallery_ids(url, headers=None, cookies=None):
    # retrieves all <=25 gallery ids from a nhentai url

    if not headers:
        headers = {}
    if not cookies:
        cookies = {}

    gallery_id = []

    response = nhentai_scraper.get_response(
        url, headers=headers, cookies=cookies
    )
    if response.status_code != 200:
        return None, None

    soup = BeautifulSoup(response.content, features='html.parser')
    gallery_count = soup.find('span', {'class': 'count'}).string
    gallery_count = gallery_count.replace('(', '').replace(')', '')
    gallery_count = gallery_count.replace(',', '')
    page_count = int(gallery_count)//25 + 1
    gallery_list = soup.find_all('div', {'class': 'gallery'})
    for gallery in gallery_list:
        gallery_id.append(f"#{gallery.find('a').get('href').split('/')[2]}")

    return gallery_id, page_count


# retrieves all gallery ids from a tag or favorites
def search_tag(tag: str):

    logger.info(f"\n{'-'*os.get_terminal_size().columns}")
    logger.info(f"Searching galleries from {tag}")
    print(f"\nSearching galleries from {tag}...\n")

    if ':' in tag:
        tag_type, tag_name = tag.split(':')
        url = f"https://nhentai.net/{tag_type}/{tag_name}/"
    elif tag == 'favorites':
        url = 'https://nhentai.net/favorites/'

    application_folder_path = nhentai_scraper.get_application_folder_dir()
    inputs_dir = os.path.abspath(f'{application_folder_path}/inputs/')
    headers = nhentai_scraper.load_headers(inputs_dir)
    cookies = nhentai_scraper.load_cookies(inputs_dir)

    page_count = get_gallery_ids(
        url, headers=headers, cookies=cookies
    )[1]

    id_list = []

    if page_count is None:
        logger.error(f'Failed to retrieve {tag}')
        print(f'Failed to retrieve {tag}')

        return None

    for page in tqdm(range(1, page_count+1), leave=False):
        logger.info(f"Searching page {page} from {tag}")
        page_url = url + f'?page={page}'
        gallery_id = get_gallery_ids(
            page_url,
            headers=headers, cookies=cookies
        )[0]

        if not gallery_id:
            logger.error(f'Failed to retrieve id_list for page {page}')
            continue
        id_list.extend(gallery_id)

    return id_list


def search_finished_downloads(tag, download_dir=''):

    # search for finished download galleries in download_dir
    download_dir = nhentai_scraper.set_download_dir(download_dir)

    find_tag_command = [
        'tag',
        '--find',
        tag.replace('-', ' '),
        download_dir
    ]
    result = run(find_tag_command, capture_output=True, check=True)

    matched_galleries = result.stdout.decode('utf-8')

    if not matched_galleries:
        find_tag_command = [
            'tag',
            '--find',
            tag,
            download_dir
        ]
        result = run(find_tag_command, capture_output=True, check=True)

        matched_galleries = result.stdout.decode('utf-8')

    # remove last one (blank stirng)
    matched_galleries = matched_galleries.split('\n')[:-1]

    matched_galleries_id = []
    for gallery in matched_galleries:
        metadata_filename = f'{gallery}/metadata.json'
        with open(metadata_filename, 'r') as f:
            matched_metadata = json.load(f)
        matched_galleries_id.append(f"#{matched_metadata['id']}")

    return matched_galleries_id


def download_tag():
    pass


# def download_tags(tag_list, download_dir, skip_downloaded_ids=False):

#     failed_galleries = {
#         'initial_failed_galleries': [],
#         'failed_retry_galleries': [],
#         'repeated_galleries': []
#     }

#     for tag in tag_list:

#         id_list = search_type(tag)
#         matched_galleries_id = search_finished_downloads(
#             tag, download_dir=download_dir
#         )

#         if sorted(matched_galleries_id) == sorted(id_list):
#             print(f'All galleries from {tag} have already been downloaded.')
#             print(f"\n{'-'*os.get_terminal_size().columns}")
#             logger.info(
#                 f'All galleries from {tag} has already been downloaded.'
#             )
#             continue

#         # only keep not yet finished downloaded ids in id_list
#         if skip_downloaded_ids:
#             id_list = list(set(id_list) - set(matched_galleries_id))

#         if not id_list:
#             continue

#         logger.info(f'Start downloading for {tag}')
#         failed_galleries_extend = download_galleries.download_id_list(
#             id_list, download_dir, id_list_name=tag
#         )
#         for key in failed_galleries:
#             failed_galleries[key].extend(
#                 failed_galleries_extend[key]
#             )

#     return failed_galleries
