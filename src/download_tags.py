#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 22:22:59 2024

@author: ball
"""
from bs4 import BeautifulSoup
import os
from pathlib import Path
import json
import requests
import re
from subprocess import run
from tqdm import tqdm
import logging
from typing import Union, Optional

import nhentai_scraper
import download_galleries
import load_inputs
import misc
from nhentai_urls import NHENTAI_URL, FAVORITES_URL, API_SEARCH_URL


logger = logging.getLogger('__main__.' + __name__)


def search_url(
    url: str,
    session: requests.sessions.Session,
    params: Optional[dict] = None
) -> tuple[list[str], int]:
    # retrieves all <=25 gallery ids from a nhentai url

    if params is None:
        params = {}

    gallery_id = []

    response = nhentai_scraper.get_response(
        url, session, params=params
    )

    if response.status_code != 200:
        return None, f'Error {response.status_code}'

    soup = BeautifulSoup(response.content, features='html.parser')

    if soup.title.string.split(' ')[0] == 'Login':
        raise Exception(
            'Please login to nhentai.net and update the cookies again.'
        )

    gallery_count = soup.find('span', {'class': 'count'}).string
    gallery_count = gallery_count.replace('(', '').replace(')', '')
    gallery_count = gallery_count.replace(',', '')
    page_count = int(gallery_count)//25 + 1

    gallery_list = soup.find_all('div', {'class': 'gallery'})
    for gallery in gallery_list:
        gallery_id.append(f"#{gallery.find('a').get('href').split('/')[2]}")

    return gallery_id, page_count


def search_api(
    search: str,
    session: requests.sessions.Session,
    params: Optional[dict] = None
) -> tuple[Optional[list[str]], Union[int, str]]:

    gallery_id = []

    # query = {'query': search}
    # if params is not None:
    #     query = query | params
    # response = nhentai_scraper.get_response(
    #     API_SEARCH_URL, session, params=query
    # )

    url = API_SEARCH_URL + '?query=' + search
    response = nhentai_scraper.get_response(
        url, session, params=params
    )

    if response.status_code != 200:
        return None, f'Error {response.status_code}'

    api_metadata = response.json()
    page_count = int(api_metadata['num_pages'])
    gallery_id = [f"#{gallery['id']}" for gallery in api_metadata['result']]

    return gallery_id, page_count


# retrieves all gallery ids from a tag or favorites
def search_tag(
    tag: str,
    session: requests.sessions.Session
) -> Optional[Union[list[str], str]]:

    logger.info(f"\n{'-'*os.get_terminal_size().columns}")
    logger.info(f"Searching galleries from {tag}")
    print(f"\nSearching galleries from {tag}...\n")

    id_list = []

    retry_count = 0
    while retry_count < 3:
        retry_count += 1

        if tag.startswith('search: '):
            search = tag.split('search: ')[1]
            page_count = search_api(search, session)[1]
        elif ':' in tag:
            tag_type, tag_name = tag.split(':')

            # replace special characters in tag_name
            tag_name = re.sub('[^0-9a-zA-Z]+', '-', tag_name)
            # drop final non-alphanumerical character in tag_name
            if not tag_name[-1].isalnum():
                tag_name = tag_name[:-1]

            url = f"{NHENTAI_URL}/{tag_type}/{tag_name}/"
            page_count = search_url(url, session)[1]
        elif tag == 'favorites':
            url = FAVORITES_URL
            page_count = search_url(url, session)[1]

        # successfully retrieved page_count for tag
        if type(page_count) is int:
            break
        else:
            logger.error('Retrying...')

    else:
        error = page_count
        if error == 'Error 403':
            error_message = (
                f'Error 403 - Forbidden for {tag} '
                '(try updating cookies)\n'
            )
        elif error == 'Error 404':
            error_message = f'Error 404 - Not Found for {tag}\n'
        elif error == 'Error 500':
            error_message = f'Error 500 - Server error for {tag}\n'
        else:
            error_message = (
                f'Failed to retrieve {tag} due to Error {error}\n'
            )

        logger.error(error_message)
        print(error_message)

        return error_message

    for page in tqdm(range(1, page_count+1), leave=False):
        logger.info(f"Searching page {page} from {tag}")
        params = {'page': page}
        if tag.startswith('search: '):
            gallery_id = search_api(search, session, params=params)[0]
        elif ':' in tag or tag == 'favorites':
            gallery_id = search_url(url, session, params=params)[0]

        if gallery_id is None:
            logger.error(f'Failed to retrieve id_list for page {page}')
            continue
        id_list.extend(gallery_id)

    return id_list


def search_finished_downloads(
    tag: str,
    download_dir: Optional[Union[str, Path]] = None
) -> list[str]:

    # search for finished download galleries in download_dir
    if download_dir is None:
        download_dir = str(misc.set_download_dir(download_dir))

    find_tag_command = [
        'tag',
        '--find',
        tag.replace('-', ' '),
    ]
    result = run(find_tag_command, capture_output=True, check=True)

    matched_galleries = result.stdout.decode('utf-8')

    if not matched_galleries:
        find_tag_command = [
            'tag',
            '--find',
            tag,
        ]
        result = run(find_tag_command, capture_output=True, check=True)

        matched_galleries = result.stdout.decode('utf-8')

    # remove last one (blank stirng)
    matched_galleries = matched_galleries.split('\n')[:-1]

    matched_galleries = [
        gallery for gallery in matched_galleries
        if gallery.startswith(download_dir)
    ]

    matched_galleries_id = []
    for gallery in matched_galleries:
        metadata_filename = f'{gallery}/metadata.json'
        with open(metadata_filename, 'r') as f:
            matched_metadata = json.load(f)
        matched_galleries_id.append(f"#{matched_metadata['id']}")

    return matched_galleries_id


def download_tag(
    tag: str,
    download_dir: Union[str, Path],
    session: requests.sessions.Session,
    skip_downloaded_ids: Optional[bool] = False
) -> Optional[dict[str, list[str]]]:

    id_list = search_tag(tag, session)

    # Failed to retrieve id_list for tag
    if type(id_list) is str:
        error_message = id_list
        gallery_results = {'retry_fails': [error_message]}

        return gallery_results

    # only keep not yet finished downloaded ids in id_list
    if skip_downloaded_ids:

        matched_galleries_id = search_finished_downloads(
            tag, download_dir=download_dir
        )
        repeat_ids = load_inputs.load_input_list('repeated_galleries.txt')
        blacklist = load_inputs.load_input_list('blacklist.txt')
        blacklist_ids = [id for id in blacklist if '#' in id]

        id_list_to_download = list(
            set(id_list)
            - set(matched_galleries_id)
            - set(repeat_ids)
            - set(blacklist_ids)
        )

    if not id_list_to_download:
        print(
            f'All galleries from {tag} have already been downloaded.\n'
        )
        logger.info(
            f'All galleries from {tag} has already been downloaded.'
        )

        return None

    if tag == 'favorites':
        additional_tags = ['favorites']
    else:
        additional_tags = None

    logger.info(f'Start downloading for {tag}')
    gallery_results = download_galleries.download_id_list(
        id_list_to_download,
        download_dir,
        session,
        additional_tags=additional_tags,
        id_list_name=tag
    )

    return gallery_results
