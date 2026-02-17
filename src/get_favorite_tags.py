#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 22:22:59 2024

@author: ball
"""
from tqdm import tqdm
from pathlib import Path
from typing import Optional
from bs4 import BeautifulSoup
import json

import nhentai_scraper
import nhentai_urls
import download_tags
import misc


def get_favorites_tags(
    type: Optional[list] = ["artist", "group"],
    save_filename: Optional[Path] = None,
):
    # automatically generates download_list.txt
    # from artists/ids of favorited galleries
    download_list = []

    download_dir = misc.set_download_dir()
    session = nhentai_scraper.create_session()

    id_list = download_tags.search_tag("favorites", session)

    for gallery_id in tqdm(id_list):
        gallery = nhentai_scraper.Gallery(
            gallery_id, session=session, download_dir=download_dir
        )
        tag_list = [
            tag for tag in gallery.metadata["tags"] if (tag["type"] in type)
        ]
        download_list.extend(
            [f"{tag['type']}:{tag['name']}" for tag in tag_list]
        )
        if not tag_list:
            download_list.append(gallery_id)

    download_list = list(set(download_list))

    if save_filename is None:
        save_filename = download_dir.parent / "inputs/download_list.txt"
    with open(save_filename, "w") as f:
        for line in download_list:
            f.write(f"{line}\n")

    return download_list


def get_blacklist_tags(save_filename: Optional[Path] = None):

    blacklist = []

    download_dir = misc.set_download_dir()
    session = nhentai_scraper.create_session()

    response = nhentai_scraper.get_response(nhentai_urls.NHENTAI_URL, session)
    soup = BeautifulSoup(response.text, "html.parser")

    menu_right = soup.find("ul", {"class": "menu right"})
    user_url = (
        menu_right.find_all("li")[1].find("a").get("href")  # type:ignore
    )

    blacklist_url = nhentai_urls.NHENTAI_URL + user_url + "/blacklist"
    response = nhentai_scraper.get_response(blacklist_url, session)
    soup = BeautifulSoup(response.text, "html.parser")

    blacklist_script = soup.find_all("script")[2].contents[0]
    blacklist_json = blacklist_script.split('"')[1]
    blacklist_dict = json.loads(
        blacklist_json.encode("utf-8").decode("unicode-escape")
    )

    for tag in blacklist_dict:
        blacklist.append(f"{tag['type']}:{tag['name']}")

    if save_filename is None:
        save_filename = download_dir.parent / "inputs/blacklist.txt"
    with open(save_filename, "w") as f:
        for line in blacklist:
            f.write(f"{line}\n")

    return blacklist


if __name__ == "__main__":
    get_favorites_tags()
