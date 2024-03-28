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
import download_galleries
import load_inputs
import misc
from nhentai_urls import NHENTAI_URL, FAVORITES_URL, API_SEARCH_URL


logger = logging.getLogger('__main__.' + __name__)


def search_url(url, headers=None, cookies=None):
    # retrieves all <=25 gallery ids from a nhentai url

    if not headers:
        headers = {}
    if not cookies:
        cookies = {}

    gallery_id = []

    response = nhentai_scraper.get_response(
        url, headers=headers, cookies=cookies
    )

    if response.status_code == 403:
        return None, 'Error 403'
    elif response.status_code == 404:
        return None, 'Error 404'
    elif response.status_code != 200:
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


def search_api(search: str, headers=None, cookies=None):

    search_url = API_SEARCH_URL + search

    if not headers:
        headers = {}
    if not cookies:
        cookies = {}

    gallery_id = []

    response = nhentai_scraper.get_response(
        search_url, headers=headers, cookies=cookies
    )

    if response.status_code == 403:
        return None, 'Error 403'
    elif response.status_code == 404:
        return None, 'Error 404'
    elif response.status_code != 200:
        return None, None

    api_metadata = response.json()
    page_count = api_metadata['num_pages']
    gallery_id = [f"#{gallery['id']}" for gallery in api_metadata['result']]

    return gallery_id, page_count


# retrieves all gallery ids from a tag or favorites
def search_tag(tag: str):

    logger.info(f"\n{'-'*os.get_terminal_size().columns}")
    logger.info(f"Searching galleries from {tag}")
    print(f"\nSearching galleries from {tag}...\n")

    if ':' in tag:
        tag_type, tag_name = tag.split(':')
        url = f"{NHENTAI_URL}/{tag_type}/{tag_name}/"
    elif tag == 'favorites':
        url = FAVORITES_URL

    headers = load_inputs.load_json('headers.json')
    cookies = load_inputs.load_json('cookies.json')

    page_count = search_url(
        url, headers=headers, cookies=cookies
    )[1]

    id_list = []

    if page_count == 'Error 403':
        print('Error 403 - Forbidden (try updating `cf_clearance`)')
        logger.error('Error 403 - Forbidden (try updating `cf_clearance`)')

        return None

    elif page_count == 'Error 404':
        print(f'Error 404 - Not Found for {tag}')
        logger.error(f'Error 404 - Not Found for {tag}')

        return None

    elif page_count is None:
        logger.error(f'Failed to retrieve {tag}')
        print(f'Failed to retrieve {tag}')
        print(f"\n{'-'*os.get_terminal_size().columns}")

        return None

    for page in tqdm(range(1, page_count+1), leave=False):
        logger.info(f"Searching page {page} from {tag}")
        page_url = url + f'?page={page}'
        gallery_id = search_url(
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
    download_dir = misc.set_download_dir(download_dir)
    # download_dir = download_dir.replace(' ', r'\ ')

    find_tag_command = [
        'tag',
        '--find',
        tag.replace('-', ' '),
        rf'{download_dir}'
    ]
    result = run(find_tag_command, capture_output=True, check=True)

    matched_galleries = result.stdout.decode('utf-8')

    if not matched_galleries:
        find_tag_command = [
            'tag',
            '--find',
            tag,
            rf'{download_dir}'
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


def download_tag(tag, download_dir, skip_downloaded_ids=False):

    id_list = search_tag(tag)

    # Failed to retrieve id_list
    if id_list is None:
        return None

    # only keep not yet finished downloaded ids in id_list
    if skip_downloaded_ids:

        matched_galleries_id = search_finished_downloads(
            tag, download_dir=download_dir
        )
        repeat_ids = load_inputs.load_input_list('repeated_galleries.txt')
        blacklist = load_inputs.load_input_list('blacklist.txt')
        blacklist_ids = [id for id in blacklist if '#' in id]

        id_list = list(
            set(id_list)
            - set(matched_galleries_id)
            - set(repeat_ids)
            - set(blacklist_ids)
        )

    if not id_list:
        print(
            f'All galleries from {tag} have already been downloaded.'
        )
        print(f"\n{'-'*os.get_terminal_size().columns}")
        logger.info(
            f'All galleries from {tag} has already been downloaded.'
        )

        return None

    if tag == 'favorites':
        additional_tags = 'favorites'
    else:
        additional_tags = None

    logger.info(f'Start downloading for {tag}')
    gallery_results = download_galleries.download_id_list(
        id_list, download_dir,
        additional_tags=additional_tags, id_list_name=tag
    )

    return gallery_results
