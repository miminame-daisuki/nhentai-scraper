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
import logging

import nhentai_scraper
import download_galleries


logger = logging.getLogger(__name__)


def get_gallery_id(url, headers=None, cookies=None):
    # retrieves all <=25 gallery ids from a nhentai url

    if not headers:
        headers = {}
    if not cookies:
        cookies = {}

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

    logger.info(f"Searching galleries from {tag}")
    print(f"\n\nSearching galleries from {tag}...\n\n")
    tag_type, tag_name = tag.split(':')
    tag_url = f"https://nhentai.net/{tag_type}/{tag_name}/"

    application_folder_path = nhentai_scraper.get_application_folder_dir()
    inputs_dir = os.path.abspath(f'{application_folder_path}/inputs/')
    headers = nhentai_scraper.load_headers(inputs_dir)
    cookies = nhentai_scraper.load_cookies(inputs_dir)

    id_list, page_count = get_gallery_id(tag_url,
                                         headers=headers,
                                         cookies=cookies)

    for page in range(2, page_count+1):
        logger.info(f"Searching page {page} from {tag}")
        page_url = tag_url + f'?page={page}'
        id_list.extend(get_gallery_id(page_url,
                                      headers=headers,
                                      cookies=cookies)[0])

    return id_list


def find_tag(tag, download_dir=''):

    application_folder_path = nhentai_scraper.get_application_folder_dir()

    if download_dir:
        if os.path.isabs(download_dir):
            download_dir = download_dir
        else:
            download_dir = os.path.abspath(
                f'{application_folder_path}/{download_dir}/')
    else:
        download_dir = os.path.abspath(
            f'{application_folder_path}/Downloaded/')

    find_tag_command = [
        'tag',
        '--find',
        tag
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


def download_tags(tag_list, download_dir):

    failed_galleries = {
        'initial_failed_galleries': [],
        'failed_retry_galleries': [],
        'repeated_galleries': []
    }

    for tag in tag_list:
        try:
            id_list = search_tag(tag)
        except Exception as error:
            logger.error(f'{error}')
            continue

        # if sorted(find_tag(tag)) == sorted(id_list):
        #     print(f'All galleries from {tag} has already been downloaded.')
        #     logger.info(
        #         f'All galleries from {tag} has already been downloaded.'
        #     )
        #     continue

        logger.info(f'Start downloading for {tag}')
        failed_galleries_extend = download_galleries.download_id_list(
            id_list, download_dir
        )
        for key in failed_galleries:
            failed_galleries[key].extend(
                failed_galleries_extend[key]
            )

    return failed_galleries
