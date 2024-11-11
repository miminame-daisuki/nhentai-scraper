#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 22:22:59 2024

@author: ball
"""
from tqdm import tqdm
from pathlib import Path
from typing import Optional

import nhentai_scraper
import download_tags
import load_inputs
import misc


def get_favorite_id_artist(save_filename: Optional[Path] = None):
    # automatically generates download_list.txt
    # from artists/ids of favorited galleries
    download_list = []

    settings = load_inputs.confirm_settings()
    download_dir = misc.set_download_dir()
    session = nhentai_scraper.create_session()

    id_list = download_tags.search_tag('favorites', session)

    for gallery_id in tqdm(id_list):
        gallery = nhentai_scraper.Gallery(
            gallery_id, session=session, download_dir=download_dir
        )
        tag_list = [
            tag for tag in gallery.metadata['tags']
            if (tag['type'] == 'artist' or tag['type'] == 'group')
        ]
        download_list.extend(
            [f"{tag['type']}:{tag['name']}" for tag in tag_list]
        )
        if not tag_list:
            download_list.append(gallery_id)

    download_list = list(set(download_list))

    if save_filename is None:
        save_filename = download_dir.parent / 'inputs/download_list.txt'
    with open(save_filename, 'w') as f:
        for line in download_list:
            f.write(f'{line}\n')


if __name__ == '__main__':
    get_favorite_id_artist()
