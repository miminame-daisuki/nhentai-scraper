#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 10 22:54:33 2024

@author: ball
"""

import requests
import random
import time
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from PIL import Image
import unicodedata
from tqdm import tqdm
from pypdf import PdfReader
import shutil
from pathlib import Path
import xattr
import Cocoa
import plistlib
import logging
from typing import Union, Optional

import load_inputs
import misc
from nhentai_urls import (
    API_GALLERY_URL,
    THUMB_BASE_URL_t1,
    THUMB_BASE_URL_t2,
    THUMB_BASE_URL_t4,
    THUMB_BASE_URL_t9,
    IMG_BASE_URL_i2,
    IMG_BASE_URL_i3,
    IMG_BASE_URL_i5,
    IMG_BASE_URL_i7,
)
from print_colored_text import bcolors

# Fix for 'IOError: image file is truncated (nn bytes not processed).'
# See https://stackoverflow.com/questions/12984426/
# pil-ioerror-image-file-truncated-with-big-images
from PIL import ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True


logger = logging.getLogger("__main__." + __name__)


class Session(requests.Session):
    def __init__(
        self, cookies: Optional[dict] = None, headers: Optional[dict] = None
    ):

        config = load_inputs.load_config_yaml()

        if cookies is None:
            cookies = config["cookies"]
            cookiejar = requests.cookies.cookiejar_from_dict(cookies)
            self.cookies = cookiejar

        if headers is None:
            headers = config["headers"]
            if type(headers) is dict:
                self.headers.update(headers)

    def __repr__(self):
        return f"Session(cookies={self.cookies}, headers={self.headers})"

    def get_response(
        self,
        url: str,
        params: Optional[dict] = None,
        sleep_time: Optional[float] = None,
        timeout_time: Optional[float] = 60.0,
    ):

        if params is None:
            params = {}

        try:
            response = self.get(url, params=params, timeout=timeout_time)
        except Exception as error:
            logger.error(f"An exception occured: {error}")
            response = lambda: None
            response.status_code = "No_response"

        # sleep for sleep_time after each get_response
        if sleep_time is None:
            sleep_time = 1 * random.random()
        logger.info(f"Sleeping for {sleep_time:.3f} seconds...")
        time.sleep(sleep_time)

        return response


def create_session(
    cookies: Optional[dict] = None, headers: Optional[dict] = None
) -> requests.sessions.Session:

    session = requests.Session()

    config = load_inputs.load_config_yaml()

    if cookies is None:
        cookies = config["cookies"]
        cookiejar = requests.cookies.cookiejar_from_dict(cookies)
        session.cookies = cookiejar

    if headers is None:
        headers = config["headers"]
        if type(headers) is dict:
            session.headers.update(headers)

    return session


def get_response(
    url: str,
    session: requests.sessions.Session,
    params: Optional[dict] = None,
    sleep_time: Optional[float] = None,
    timeout_time: Optional[float] = 60.0,
) -> requests.Response:

    if params is None:
        params = {}

    try:
        response = session.get(url, params=params, timeout=timeout_time)
    except Exception as error:
        logger.error(f"An exception occured for {url}: {error}")
        response = lambda: None
        response.status_code = "No_response"

    # sleep for sleep_time after each get_response
    if sleep_time is None:
        sleep_time = 0.0
    logger.info(f"Sleeping for {sleep_time:.3f} seconds...")
    time.sleep(sleep_time)

    return response


class Gallery:

    def __init__(
        self,
        id_: Union[int, str],
        filetype: Optional[str] = None,
        server: Optional[str] = None,
        download_dir: Optional[Union[str, Path]] = None,
        session: Optional[requests.sessions.Session] = None,
        additional_tags: Optional[list[str]] = None,
        download_repeats: Optional[bool] = False,
    ):

        self.id = id_
        self.download_dir = download_dir
        self.filetype = filetype
        if self.filetype is None:
            self.filetype = "folder"
        self.server = server
        if self.filetype == "cbz" and self.server is None:
            self.server = "LANraragi"

        if session is None:
            session = create_session()
        self.session = session

        if additional_tags:
            self.additional_tags = additional_tags
        else:
            self.additional_tags = []

        self.download_repeats = download_repeats
        if download_repeats:
            self.additional_tags.append("repeats")

        if self.filetype != "folder":
            self.download_repeats = True

        self.status_code = -1

        self.title = ""
        self.downloaded_metadata = {"id": ""}

        self.get_metadata()

    def __str__(self) -> str:
        return f"{self.title} (#{self.id})"

    def __repr__(self) -> str:
        return (
            f"Gallery(#{self.id}, {self.session}, "
            f"download_dir={self.download_dir}, "
            f"additional_tags={self.additional_tags})"
        )

    @property
    def id(self) -> str:
        return self.__id

    @id.setter
    def id(self, id_: Union[str, int]):
        id_ = str(id_).split("#")[-1]
        logger.info(f"Gallery initialized for id: #{id_}")
        self.__id = id_

    @property
    def download_dir(self):
        return self.__download_dir

    @download_dir.setter
    def download_dir(self, dir: Optional[Union[str, Path]] = None):
        if dir is None:
            dir = str(misc.set_download_dir())
        logger.info(f"Download directory set to: '{dir}'")
        self.__download_dir = dir

    def get_metadata(self) -> dict:

        logger.info("Retreiving gallery metadata from nhentai api...")
        api_url = f"{API_GALLERY_URL}/{int(self.id)}"

        api_response = get_response(api_url, self.session)
        if api_response.status_code == 403:
            self.status_code = -2

            return {}

        elif api_response.status_code == 404:
            self.status_code = -3

            return {}

        # retry for up to 3 times
        tries = 0
        while api_response.status_code != 200:
            logger.error(
                (
                    "Failed to retrieve metadata with status code "
                    f"{api_response.status_code}, retrying..."
                )
            )
            api_response = get_response(api_url, self.session)
            tries += 1

            if tries >= 3 and api_response != 200:
                self.status_code = -4

                return {}

        self.metadata = api_response.json()
        self._parse_metadata()
        self._parse_ComicInfo_xml()

        logger.info("Metadata retrieved")
        logger.info(f"Title: {self.title}")

        return self.metadata

    def _parse_metadata(self) -> None:

        self.media_id = self.metadata["media_id"]
        if self.metadata["title"]["japanese"]:
            self.title = self.metadata["title"]["japanese"]
        else:
            self.title = self.metadata["title"]["english"]
        self.title = self.title.replace("/", "_")

        # trim filenames that are too long (max length = 255 for MacOS)
        if len(self.title) > 240:
            self.title = self.title[:240] + "..."

        self.num_pages = self.metadata["num_pages"]
        self.tags = [
            f"{tag['type']}:{tag['name']}" for tag in self.metadata["tags"]
        ]

        self.thumb_extension = self.get_img_extension(
            self.metadata["images"]["thumbnail"]
        )

        if self.additional_tags:
            self.tags.extend(self.additional_tags)

    def check_blacklist(self, blacklist: Optional[list[str]] = None) -> None:

        logger.info("Checking blacklist...")
        if blacklist is None:
            blacklist = load_inputs.load_input_list("blacklist.txt")
        blacklist_tags = [tag for tag in blacklist if ":" in tag]

        if any(tag in self.tags for tag in blacklist_tags):
            self.status_code = 3
        else:
            logger.info("Clear")

    def get_img_extension(self, img_metadata: dict[str, str]) -> str:

        if img_metadata["t"] == "j":
            return "jpg"
        elif img_metadata["t"] == "p":
            return "png"
        elif img_metadata["t"] == "g":
            return "gif"
        elif img_metadata["t"] == "w":
            return "webp"
        else:
            return ""

    def check_folder(self) -> None:

        logger.info("Checking folder...")
        # replace '/' with '_' for folder directory
        if self.download_repeats:
            self.folder_dir = os.path.join(self.download_dir, str(self))
        else:
            self.folder_dir = os.path.join(self.download_dir, self.title)

        # check whether there exists a downloaded gallery with the same name
        if self.filetype == "cbz" and self.server == "LANraragi":
            cbz_path = self.download_dir / Path(str(self)).with_suffix(".cbz")
            if cbz_path.exists():
                self.status_code = 1

                return

        if os.path.isdir(self.folder_dir):
            self.load_downloaded_metadata()
            logger.info("Folder exists with metadata loaded")

            # check whether the gallery was downloaded with a different source
            if int(self.downloaded_metadata["id"]) != int(self.id):
                self.status_code = 2

                return

            elif self.downloaded_metadata != self.metadata:
                self.save_metadata()
                logger.info("Metadata updated.")

        else:
            os.mkdir(self.folder_dir)
            self.save_metadata()
            logger.info("Folder created with metadata saved")

    def load_downloaded_metadata(self) -> dict:

        metadata_filename = f"{self.folder_dir}/metadata.json"
        with open(metadata_filename, "r") as f:
            self.downloaded_metadata = json.load(f)

        return self.downloaded_metadata

    def save_metadata(self) -> None:

        json_filename = f"{self.folder_dir}/metadata.json"
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=4)

        xml_filename = f"{self.folder_dir}/ComicInfo.xml"
        self.ComicInfo_tree.write(
            xml_filename, xml_declaration=True, encoding="utf-8"
        )

    def _parse_ComicInfo_xml(self) -> None:

        self.ComicInfo_tree = ET.parse(
            f"{misc.get_application_folder_dir()}/src/ComicInfo_template.xml"
        )

        if self.server == "Kavita":
            self.ComicInfo_tree.find("Series").text = self.title
            self.ComicInfo_tree.find("LocalizedSeries").text = self.metadata[
                "title"
            ]["english"]
            self.ComicInfo_tree.find("Number").text = str(self.id)

            parodies_list = []
            characters_list = []
            tags_list = []
            artists_list = []
            languages_list = []
            categories_list = []

            for tag in self.metadata["tags"]:
                if tag["type"] == "parody":
                    parodies_list.append(tag["name"])
                elif tag["type"] == "character":
                    characters_list.append(tag["name"])
                elif tag["type"] == "tag":
                    tags_list.append(tag["name"])
                elif tag["type"] == "artist" or tag["type"] == "group":
                    artists_list.append(tag["name"])
                elif tag["type"] == "language":
                    languages_list.append(tag["name"])
                elif tag["type"] == "category":
                    categories_list.append(tag["name"])

            self.ComicInfo_tree.find("SeriesGroup").text = ",".join(
                parodies_list
            )
            self.ComicInfo_tree.find("Characters").text = ",".join(
                characters_list
            )
            self.ComicInfo_tree.find("Tags").text = ",".join(tags_list)
            self.ComicInfo_tree.find("Writer").text = ",".join(artists_list)
            self.ComicInfo_tree.find("LanguageISO").text = ",".join(
                languages_list
            )
            self.ComicInfo_tree.find("Genre").text = ",".join(categories_list)

            for page in self.metadata["images"]["pages"]:
                # convert image width & height from int to str
                for key, value in page.items():
                    page[key] = str(value)

                ET.SubElement(
                    self.ComicInfo_tree.find("Images"), "pages", page
                )

            ET.SubElement(
                self.ComicInfo_tree.find("Images"),
                "cover",
                {
                    key: str(value)
                    for key, value in self.metadata["images"]["cover"].items()
                },
            )
            ET.SubElement(
                self.ComicInfo_tree.find("Images"),
                "thumbnail",
                {
                    key: str(value)
                    for key, value in self.metadata["images"][
                        "thumbnail"
                    ].items()
                },
            )

            self.ComicInfo_tree.find("PageCount").text = str(
                self.metadata["num_pages"]
            )

            dt = datetime.fromtimestamp(self.metadata["upload_date"])
            self.ComicInfo_tree.find("Year").text = str(dt.year)
            self.ComicInfo_tree.find("Month").text = str(dt.month)
            self.ComicInfo_tree.find("Day").text = str(dt.day)

            self.ComicInfo_tree.find("Translator").text = self.metadata[
                "scanlator"
            ]

        elif self.server == "LANraragi":
            self.ComicInfo_tree.find("Title").text = str(self)
            self.ComicInfo_tree.find("Web").text = f"nhentai.net/g/{self.id}"

            parodies_list = []
            characters_list = []
            tags_list = []
            artists_list = []
            groups_list = []
            languages_list = []

            for tag in self.metadata["tags"]:
                if tag["type"] == "parody":
                    parodies_list.append(tag["name"])
                elif tag["type"] == "character":
                    characters_list.append(tag["name"])
                elif tag["type"] == "tag":
                    tags_list.append(tag["name"])
                elif tag["type"] == "artist":
                    artists_list.append(tag["name"])
                elif tag["type"] == "group":
                    groups_list.append(tag["name"])
                elif tag["type"] == "language":
                    languages_list.append(tag["name"])

            parodies_list.append(self.title)

            ComicInfo_namespace_correspond = [
                ("Series", parodies_list),
                ("Characters", characters_list),
                ("Tags", tags_list),
                ("Penciller", artists_list),
                ("Writer", groups_list),
                ("LanguageISO", languages_list),
            ]
            for namespace, tag_list in ComicInfo_namespace_correspond:
                self.ComicInfo_tree.find(namespace).text = ",".join(tag_list)

            for page in self.metadata["images"]["pages"]:
                # convert image width & height from int to str
                for key, value in page.items():
                    page[key] = str(value)

                ET.SubElement(
                    self.ComicInfo_tree.find("Images"), "pages", page
                )

            ET.SubElement(
                self.ComicInfo_tree.find("Images"),
                "cover",
                {
                    key: str(value)
                    for key, value in self.metadata["images"]["cover"].items()
                },
            )
            ET.SubElement(
                self.ComicInfo_tree.find("Images"),
                "thumbnail",
                {
                    key: str(value)
                    for key, value in self.metadata["images"][
                        "thumbnail"
                    ].items()
                },
            )

            self.ComicInfo_tree.find("PageCount").text = str(
                self.metadata["num_pages"]
            )

    def check_thumb(self) -> None:

        logger.info("Checking thumbnail...")
        if os.path.exists(f"{self.folder_dir}/Icon\r"):
            logger.info("Thumbnail already set")

            return

        # set thumbnail if thumbnail file exists
        self.thumb_filename = f"{self.folder_dir}/thumb.{self.thumb_extension}"
        if f"thumb.{self.thumb_extension}" in os.listdir(self.folder_dir):
            self.set_thumb()

            return

        # download and set thumbnail if thumbnail file doesn't exist
        response_code = self.download_thumb()
        if response_code != 200:
            self.status_code = -5

            return

        self.resize_thumb()
        self.set_thumb()

    def download_thumb(self) -> int:

        logger.info("Retrieving thumbnail...")
        thumb_base_urls = [
            THUMB_BASE_URL_t1,
            THUMB_BASE_URL_t2,
            THUMB_BASE_URL_t4,
            THUMB_BASE_URL_t9,
        ]
        thumb_base_url = random.choice(thumb_base_urls)
        thumb_url = (
            f"{thumb_base_url}/{self.media_id}/thumb.{self.thumb_extension}"
        )

        thumb_response = get_response(thumb_url, self.session)

        # retry for up to 3 times
        tries = 0
        while thumb_response.status_code != 200:
            logger.error(
                "Something went wrong when retrieving thumbnail:"
                f"{thumb_response.status_code}, retrying..."
            )
            thumb_extensions = ["jpg", "webp"]
            thumb_base_url = random.choice(thumb_base_urls)
            thumb_random_extension = random.choice(thumb_extensions)
            # Sometimes the thumbnail webpage on nhentai has two extensions
            thumb_url = (
                f"{thumb_base_url}/{self.media_id}/"
                f"thumb.{thumb_random_extension}.{self.thumb_extension}"
            )
            thumb_response = get_response(thumb_url, self.session)
            tries += 1

            if tries >= 3 and thumb_response.status_code != 200:

                return thumb_response.status_code

        with open(self.thumb_filename, "wb") as f:
            f.write(thumb_response.content)

        return thumb_response.status_code

    def resize_thumb(self) -> None:
        # resizing thumbnail to be square
        with Image.open(self.thumb_filename) as thumb:
            thumb_width, thumb_height = thumb.size
            thumb_size = max(thumb_width, thumb_height)
            thumb_square = Image.new(
                "RGBA", (thumb_size, thumb_size), (0, 0, 0, 0)
            )
            thumb_square.paste(
                thumb,
                (
                    int((thumb_size - thumb_width) / 2),
                    int((thumb_size - thumb_height) / 2),
                ),
            )
            thumb_rgb = thumb_square.convert("RGB")
            thumb_rgb.save(self.thumb_filename)

    def set_thumb(self) -> None:

        logger.info("Setting thumbnail...")

        try:
            thumb_image = Cocoa.NSImage.alloc().initWithContentsOfFile_(
                self.thumb_filename
            )
            workspace = Cocoa.NSWorkspace.sharedWorkspace()
            workspace.setIcon_forFile_options_(thumb_image, self.folder_dir, 0)
            logger.info("Thumbnail set")

        except Exception as error:
            self.status_code = -7
            logger.error(
                f"Something went wrong when setting thumbnail: {error}"
            )

    def check_tags(self) -> None:

        logger.info("Checking tags...")

        tag_attribute = "com.apple.metadata:_kMDItemUserTags"
        if tag_attribute in xattr.xattr(self.folder_dir):
            raw_current_tags = xattr.getxattr(self.folder_dir, tag_attribute)
            current_tags = plistlib.loads(raw_current_tags)
            # Remove the trailing "\n0" that appears
            # when using 'tag save tags
            current_tags = [tag.split("\n")[0] for tag in current_tags]

            if set(self.tags) == set(current_tags):
                self.status_code = 1

                return

            else:
                self.set_tags()
                self.status_code = 4

                return

        logger.info("Tags not found, setting tags...")
        self.set_tags()

    def set_tags(self) -> None:

        tag_attribute = "com.apple.metadata:_kMDItemUserTags"
        tags_data = plistlib.dumps(self.tags, fmt=plistlib.FMT_BINARY)
        try:
            xattr.setxattr(self.folder_dir, tag_attribute, tags_data)
            logger.info("Tags set.")
        except Exception as error:
            self.status_code = -6
            logger.error(f"Something went wrong when setting tags: {error}")

    def download_page(
        self,
        page: Union[str, int],
        img_base_url: Optional[str] = IMG_BASE_URL_i2,
    ) -> None:

        logger.info(f"Retrieving Page {page}/{self.num_pages} url...")

        extension = self.get_img_extension(
            self.metadata["images"]["pages"][int(page) - 1]
        )
        img_url = f"{img_base_url}/{self.media_id}/{int(page)}.{extension}"
        img_response = get_response(img_url, self.session)

        if img_response.status_code != 200:
            logger.error(
                (
                    "Something went wrong with when getting response"
                    f"for page {page}: {img_response.status_code}"
                )
            )

            return

        logger.info("Image downloaded")
        filename = f"{self.folder_dir}/{str(page)}.{extension}"
        with open(filename, "wb") as f:
            f.write(img_response.content)

    def check_missing_pages(self) -> None:

        logger.info("Checking missing pages...")
        self.load_missing_pages()

        if not self.missing_pages:
            logger.info("Downloaded all pages")

            return

        # download all missing pages, and retry up to 3 times for failed pages
        tries = 0
        leave_tqdm = True
        while len(self.missing_pages) != 0:
            if tries != 0:
                leave_tqdm = False
                logger.info(
                    f"Retrying failed pages for the {tries}(th) time..."
                )

            self.download_pages(tries=tries, leave_tqdm=leave_tqdm)
            self.load_missing_pages()

            # record missing pages for initial download try
            if tries == 0:
                self.initial_failed_pages = self.load_missing_pages()

            tries += 1
            if tries > 3 and len(self.missing_pages) != 0:
                logger.error(f"Failed pages: {self.missing_pages}")
                self.status_code = -8

                return

    def download_pages(
        self,
        tries: Optional[int] = 0,
        leave_tqdm: Optional[bool] = True,
    ) -> None:

        bar_format = (
            "{desc}: {percentage:3.0f}%|"
            "{bar}"
            "| {n_fmt:>3}/{total_fmt:<3} [{elapsed}<{remaining}, {rate_fmt}{postfix}]"
        )
        t = tqdm(self.missing_pages, bar_format=bar_format, leave=leave_tqdm)
        for page in t:

            if tries == 0:
                t.set_description(f"Downloading #{self.id}")
                img_base_url = IMG_BASE_URL_i2

            else:
                t.set_description(
                    f"Retrying failed pages for the {tries}(th) time"
                )

                img_base_urls = [
                    IMG_BASE_URL_i2,
                    IMG_BASE_URL_i3,
                    IMG_BASE_URL_i5,
                    IMG_BASE_URL_i7,
                ]
                img_base_url = random.choice(img_base_urls)

            self.download_page(page, img_base_url=img_base_url)

    def load_missing_pages(self) -> list[str]:

        # check whether all page numbers are downloaded against self.num_pages
        self.missing_pages = []
        file_list = os.listdir(self.folder_dir)
        for page in range(1, int(self.num_pages) + 1):
            if str(page) not in [Path(file).stem for file in file_list]:
                self.missing_pages.append(str(page))

        # delete duplicates
        self.missing_pages = list(dict.fromkeys(self.missing_pages))

        return self.missing_pages

    def check_extra_pages(self) -> list[str]:

        # check whether there are more pages downloaded than self.num_pages
        # which should not happen
        extra_pages = []
        downloaded_pages = os.listdir(self.folder_dir)

        non_page_files = [
            "._Icon\r",
            "Icon\r",
            "metadata.json",
            "ComicInfo.xml",
            f"thumb.{self.thumb_extension}",
            ".DS_Store",
            f"{self.title}.pdf",
        ]

        downloaded_pages = [
            unicodedata.normalize("NFC", page)
            for page in downloaded_pages
            if unicodedata.normalize("NFC", page) not in non_page_files
        ]

        for downloaded_page in downloaded_pages:
            if Path(downloaded_page).stem not in [
                str(i) for i in range(1, int(self.num_pages) + 1)
            ]:
                extra_pages.append(downloaded_page)

        if len(extra_pages) != 0:
            self.status_code = -9

        return extra_pages

    def check_pdf(self) -> None:

        logger.info("Checking PDF...")
        self.pdf_path = f"{self.folder_dir}/{self.title}.pdf"
        # load all image files and remove unwanted ones
        image_filenames = os.listdir(self.folder_dir)
        exclude_list = [
            "Icon\r",
            "._Icon\r",
            "metadata.json",
            ".DS_Store",
            f"thumb.{self.thumb_extension}",
        ]
        self.image_filenames = [
            unicodedata.normalize("NFC", file)
            for file in image_filenames
            if file not in exclude_list
        ]

        # check whether pdf already exists
        if f"{self.title}.pdf" in self.image_filenames:
            reader = PdfReader(self.pdf_path)
            if len(reader.pages) == self.num_pages:
                logger.info("PDF file already exists with matching page count")

                return

        self.save2pdf()

    def save2pdf(self) -> None:

        logger.info("Converting images to PDF file...")
        # sort according to page number
        sort = [int(Path(page).stem) for page in self.image_filenames]
        self.image_filenames = [
            file for _, file in sorted(zip(sort, self.image_filenames))
        ]

        # open all image files and save to pdf
        images = []
        try:
            for img_filename in self.image_filenames:
                image_path = os.path.join(self.folder_dir, img_filename)
                with Image.open(image_path) as img:
                    img_copy = img.copy()
                # fix for 'ValueError: cannot save mode I'
                if img_copy.mode == "I" or img_copy.mode == "RGBA":
                    img_copy = img_copy.convert("RGB")
                images.append(img_copy)
            images[0].save(
                self.pdf_path,
                "PDF",
                resolution=100.0,
                save_all=True,
                append_images=images[1:],
            )
        except Exception as error:
            logger.error(f"{error}")
            self.status_code = -10

    def zip(self) -> None:
        shutil.make_archive(self.folder_dir, "zip", self.folder_dir)

        for file in Path(self.folder_dir).iterdir():
            file.unlink()

        # ensure that filenames with '.' within don't have
        # part of the names replaced with '.zip' and '.cbz'
        folder_path = Path(self.folder_dir)
        zip_path = folder_path.with_suffix(folder_path.suffix + ".zip")
        cbz_filename = Path(str(self)).with_suffix(
            Path(str(self)).suffix + ".cbz"
        )

        if self.server == "Kavita":
            zip_path.rename(self.folder_dir / cbz_filename)
        elif self.server == "LANraragi":
            zip_path.rename(self.download_dir / cbz_filename)
            Path(self.folder_dir).rmdir()

    def status(self) -> str:
        # status_code >= 0: Normal
        # status_code = 0: Still downloading
        # status_code < -1: Error

        status_dict = {
            0: f"{str(self)} download finished.",
            1: f"{str(self)} already downloaded.",
            2: (
                f"{str(self)} has the same title as "
                f"the already downloaded #{self.downloaded_metadata['id']}."
            ),
            3: f"BLACKLISTED {str(self)}.",
            4: f"Updated tags for {str(self)}.",
            -1: "Download not finished...",
            -2: (
                f"Error 403 - Forbidden for #{self.id} "
                "(try updating `cf_clearance`)."
            ),
            -3: f"Error 404 - Not Found for #{self.id}.",
            -4: (
                "Error when downloading metadata "
                f"(failed retry 3 times) for #{self.id}."
            ),
            -5: f"Error when downloading thumbnail for {str(self)}.",
            -6: f"Error when setting tags for {str(self)}.",
            -7: f"Error when setting thumbnail for {str(self)}.",
            -8: (
                "Error when downloading missing pages (failed retry 3 times) "
                f"for {str(self)}."
            ),
            -9: (
                "There are more pages downloaded than self.num_pages "
                f"for {str(self)}."
            ),
            -10: f"Error when saving PDF for {str(self)}.",
        }

        return status_dict[self.status_code]

    def download(self) -> int:

        def skip_download():
            if self.status_code < -1:
                tqdm.write(f"{bcolors.FAIL}{self.status()}{bcolors.ENDC}")
                logger.error(self.status())

                return True

            elif self.status_code > 0:
                logger.info(self.status())
                tqdm.write(self.status())

                return True

            else:
                return False

        if skip_download():
            return self.status_code

        self.check_blacklist()
        if skip_download():
            return self.status_code

        self.check_folder()
        if skip_download():
            return self.status_code

        if self.filetype == "folder":
            self.check_thumb()
            if skip_download():
                return self.status_code

        self.check_extra_pages()
        if skip_download():
            return self.status_code

        self.check_missing_pages()
        if skip_download():
            return self.status_code

        if self.filetype == "folder":
            self.check_pdf()
            if skip_download():
                return self.status_code

            # set tags after finishing download
            self.check_tags()
            if skip_download():
                return self.status_code

        elif self.filetype == "cbz":
            self.zip()

        self.status_code = 0
        logger.info(f"{self.status()}")
        tqdm.write(self.status())

        return self.status_code


if __name__ == "__main__":
    misc.set_logging_config()
    logger.info(f"\n{'-'*os.get_terminal_size().columns}")
    logger.info("Program started")

    application_folder_path = misc.get_application_folder_dir()
    download_dir = os.path.abspath(f"{application_folder_path}/test/")

    session = create_session()

    id_list = input("Input gallery id: ").split(" ")
    filetype = input("Download as (cbz/folder): ")
    if filetype not in ["cbz", "folder"]:
        raise Exception("Please enter either 'cbz' or 'folder'.")

    for gallery_id in id_list:
        gallery = Gallery(
            gallery_id,
            filetype=filetype,
            download_dir=download_dir,
        )
        gallery.download()
