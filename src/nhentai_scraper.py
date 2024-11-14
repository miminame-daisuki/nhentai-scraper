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
from PIL import Image
from subprocess import run
import unicodedata
from tqdm import tqdm
from pypdf import PdfReader
from pathlib import Path
import signal
import logging
from typing import Union, Optional

import load_inputs
import misc
from nhentai_urls import (
    API_GALLERY_URL,
    THUMB_BASE_URL_t2,
    THUMB_BASE_URL_t3,
    THUMB_BASE_URL_t5,
    THUMB_BASE_URL_t7,
    IMG_BASE_URL_i2,
    IMG_BASE_URL_i3,
    IMG_BASE_URL_i5,
    IMG_BASE_URL_i7
)


logger = logging.getLogger('__main__.' + __name__)


class Session(requests.Session):
    def __init__(
        self,
        cookies: Optional[dict] = None,
        headers: Optional[dict] = None
    ):

        if cookies is None:
            cookies = load_inputs.load_json('cookies.json')
        if headers is None:
            headers = load_inputs.load_json('headers.json')

        cookiejar = requests.cookies.cookiejar_from_dict(cookies)

        self.cookies = cookiejar
        self.headers.update(headers)

    def __repr__(self):
        return f'Session(cookies={self.cookies}, headers={self.headers})'

    def get_response(
        self,
        url: str,
        params: Optional[dict] = None,
        sleep_time: Optional[float] = None,
        timeout_time: Optional[float] = 60.
    ):

        if params is None:
            params = {}

        try:
            response = self.get(
                url, params=params, timeout=timeout_time
            )
        except Exception as error:
            logger.error(f'An exception occured: {error}')
            response = lambda: None
            response.status_code = 'No_response'

        # sleep for sleep_time after each get_response
        if sleep_time is None:
            sleep_time = 1*random.random()
        logger.info(f'Sleeping for {sleep_time:.3f} seconds...')
        time.sleep(sleep_time)

        return response


def create_session(
    cookies: Optional[dict] = None,
    headers: Optional[dict] = None
) -> requests.sessions.Session:

    session = requests.Session()

    if cookies is None:
        cookies = load_inputs.load_json('cookies.json')
    if headers is None:
        headers = load_inputs.load_json('headers.json')

    cookiejar = requests.cookies.cookiejar_from_dict(cookies)

    session.cookies = cookiejar
    session.headers.update(headers)

    return session


def get_response(
    url: str,
    session: requests.sessions.Session,
    params: Optional[dict] = None,
    sleep_time: Optional[float] = None,
    timeout_time: Optional[float] = 60.
) -> requests.Response:

    if params is None:
        params = {}

    try:
        response = session.get(
            url, params=params, timeout=timeout_time
        )
    except Exception as error:
        logger.error(f'An exception occured: {error}')
        response = lambda: None
        response.status_code = 'No_response'

    # sleep for sleep_time after each get_response
    if sleep_time is None:
        sleep_time = 0.
    logger.info(f'Sleeping for {sleep_time:.3f} seconds...')
    time.sleep(sleep_time)

    return response


class Gallery:

    def __init__(
        self,
        id_: Union[int, str],
        session: Optional[requests.sessions.Session] = None,
        download_dir: Optional[Union[str, Path]] = None,
        additional_tags: Optional[list[str]] = None,
    ):

        self.id = id_
        if session is None:
            session = create_session()
        self.session = session
        self.download_dir = download_dir
        self.additional_tags = additional_tags

        self.status_code = -1

        self.title = ''
        self.downloaded_metadata = {'id': ''}

        self.get_metadata()

    def __str__(self) -> str:
        return f'{self.title} (#{self.id})'

    def __repr__(self) -> str:
        return (
            f'Gallery(#{self.id}, {self.session}, '
            f'download_dir={self.download_dir}, '
            f'additional_tags={self.additional_tags})'
        )

    @property
    def id(self) -> str:
        return self.__id

    @id.setter
    def id(self, id_: Union[str, int]):
        id_ = str(id_).split('#')[-1]
        logger.info(f'Gallery initialized for id: #{id_}')
        self.__id = id_

    @property
    def download_dir(self):
        return self.__download_dir

    @download_dir.setter
    def download_dir(self, dir: Union[str, Path]):
        if dir is None:
            dir = str(misc.set_download_dir())
        logger.info(f"Download directory set to: '{dir}'")
        self.__download_dir = dir

    def get_metadata(self) -> dict:

        logger.info('Retreiving gallery metadata from nhentai api...')
        api_url = f'{API_GALLERY_URL}/{int(self.id)}'

        api_response = get_response(
            api_url, self.session
        )
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
                ('Failed to retrieve metadata with status code '
                 f'{api_response.status_code}, retrying...')
            )
            api_response = get_response(
                api_url, self.session
            )
            tries += 1

            if tries >= 3 and api_response != 200:
                self.status_code = -4

                return {}

        self.metadata = api_response.json()
        self._parse_metadata()

        logger.info('Metadata retrieved')
        logger.info(f'Title: {self.title}')

        return self.metadata

    def _parse_metadata(self) -> None:

        self.media_id = self.metadata['media_id']
        if self.metadata['title']['japanese']:
            self.title = self.metadata['title']['japanese']
        else:
            self.title = self.metadata['title']['english']
        self.title = self.title.replace('/', '_')
        self.num_pages = self.metadata['num_pages']
        self.tags = [
            f"{tag['type']}:{tag['name']}" for tag in self.metadata['tags']
        ]

        self.thumb_extension = self.get_img_extension(
            self.metadata['images']['thumbnail']
        )

        if self.additional_tags is not None:
            self.tags.extend(self.additional_tags)

    def check_blacklist(self, blacklist: Optional[list[str]] = None) -> None:

        logger.info('Checking blacklist...')
        if not blacklist:
            blacklist = load_inputs.load_input_list('blacklist.txt')
            blacklist_tags = [tag for tag in blacklist if ':' in tag]

        if any(tag in self.tags for tag in blacklist_tags):
            self.status_code = -5
        else:
            logger.info('Clear')

    def get_img_extension(self, img_metadata: dict[str, str]) -> str:

        if img_metadata['t'] == 'j':
            return 'jpg'
        elif img_metadata['t'] == 'p':
            return 'png'
        elif img_metadata['t'] == 'g':
            return 'gif'
        elif img_metadata['t'] == 'w':
            return 'webp'

    def check_folder(self) -> None:

        logger.info('Checking folder...')
        # replace '/' with '_' for folder directory
        self.folder_dir = os.path.join(self.download_dir, self.title)

        # check whether there exists a downloaded gallery with the same name
        if os.path.isdir(self.folder_dir):
            self.load_downloaded_metadata()
            logger.info('Folder exists with metadata loaded')

            # check whether the gallery was downloaded with a different source
            if int(self.downloaded_metadata['id']) != int(self.id):
                self.status_code = 2

                return

        else:
            os.mkdir(self.folder_dir)
            self.save_metadata()
            logger.info('Folder created with metadata saved')

    def load_downloaded_metadata(self) -> dict:

        metadata_filename = f'{self.folder_dir}/metadata.json'
        with open(metadata_filename, 'r') as f:
            self.downloaded_metadata = json.load(f)

        return self.downloaded_metadata

    def save_metadata(self) -> None:

        filename = f'{self.folder_dir}/metadata.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=4)

    def check_thumb(self) -> None:

        logger.info('Checking thumbnail...')
        check_thumb_command = [
            'fileicon',
            'test',
            f"{self.folder_dir}"
        ]
        result = run(check_thumb_command, capture_output=True)
        if result.returncode == 0:
            logger.info('Thumbnail already set')

            return

        # download and set thumbnail if thumbnail file doesn't exist
        self.thumb_filename = f'{self.folder_dir}/thumb.{self.thumb_extension}'
        if f'thumb.{self.thumb_extension}' not in os.listdir(self.folder_dir):
            response_code = self.download_thumb()
            if response_code != 200:
                self.status_code = -6
                return
            self.resize_thumb()

        self.set_thumb()

    def download_thumb(self) -> None:

        logger.info('Retrieving thumbnail...')
        thumb_base_url = THUMB_BASE_URL_t3
        thumb_url = (
            f'{thumb_base_url}/{self.media_id}/thumb.{self.thumb_extension}'
        )

        thumb_response = get_response(thumb_url, self.session)

        # retry for up to 3 times
        tries = 0
        while thumb_response.status_code != 200:
            logger.error(
                'Something went wrong when retrieving thumbnail:'
                f'{thumb_response.status_code}, retrying...'
            )
            thumb_base_urls = [
                THUMB_BASE_URL_t2,
                THUMB_BASE_URL_t3,
                THUMB_BASE_URL_t5,
                THUMB_BASE_URL_t7
            ]
            thumb_base_url = random.choice(thumb_base_urls)
            thumb_url = (
                f'{thumb_base_url}/{self.media_id}/thumb.{self.thumb_extension}'
            )
            thumb_response = get_response(thumb_url, self.session)
            tries += 1

            if tries >= 3 and thumb_response.status_code != 200:

                return thumb_response.status_code

        with open(self.thumb_filename, 'wb') as f:
            f.write(thumb_response.content)

        return thumb_response.status_code

    def resize_thumb(self) -> None:
        # resizing thumbnail to be square
        with Image.open(self.thumb_filename) as thumb:
            thumb_width, thumb_height = thumb.size
            thumb_size = max(thumb_width, thumb_height)
            thumb_square = Image.new(
                'RGBA',
                (thumb_size, thumb_size),
                (0, 0, 0, 0)
            )
            thumb_square.paste(
                thumb,
                (
                    int((thumb_size-thumb_width)/2),
                    int((thumb_size-thumb_height)/2)
                )
            )
            thumb_rgb = thumb_square.convert('RGB')
            thumb_rgb.save(self.thumb_filename)

    def set_thumb(self) -> None:

        logger.info('Setting thumbnail...')
        set_thumb_command = [
            'fileicon',
            'set',
            f"{self.folder_dir}",
            f"{self.thumb_filename}"
        ]
        result = run(set_thumb_command, capture_output=True)
        logger.info(result.stdout.decode('utf-8').split('\n')[0])
        if result.returncode != 0:
            self.status_code = -8
            logger.error(f"{result.stderr.decode('utf-8')}")

    def check_tags(self) -> None:

        logger.info('Checking tags...')

        show_tags_command = [
            'tag',
            '--list',
            '--no-name',
            self.folder_dir
        ]

        result = run(show_tags_command, capture_output=True)

        if result.stdout:
            self.status_code = 1

            return

        logger.info('Setting tags...')

        tags_string = ''.join(f'{tag},' for tag in self.tags)
        tags_string = tags_string[:-1]  # to exclude the final ','

        # set tags with tag
        set_tags_command = [
            'tag',
            '--set',
            f'{tags_string}',
            f"{self.folder_dir}"
        ]
        result = run(set_tags_command, capture_output=True)
        if result.returncode != 0:
            self.status_code = -7
            logger.error(f"{result.stderr.decode('utf-8')}")

    def download_page(
        self, page: Union[str, int],
        img_base_url: Optional[str] = IMG_BASE_URL_i3
    ) -> None:

        logger.info(f'Retrieving Page {page}/{self.num_pages} url...')

        extension = self.get_img_extension(
            self.metadata['images']['pages'][int(page)-1]
        )
        img_url = f'{img_base_url}/{self.media_id}/{int(page)}.{extension}'
        img_response = get_response(
            img_url, self.session
        )

        if img_response.status_code != 200:
            logger.error(
                ('Something went wrong with when getting response'
                 f'for page {page}: {img_response.status_code}')
            )

            return

        logger.info('Image downloaded')
        filename = f'{self.folder_dir}/{str(page)}.{extension}'
        with open(filename, 'wb') as f:
            f.write(img_response.content)

    def check_missing_pages(self) -> None:

        logger.info('Checking missing pages...')
        self.load_missing_pages()

        if not self.missing_pages:
            logger.info('Downloaded all pages')

            return

        # download all missing pages, and retry up to 3 times for failed pages
        tries = 0
        leave_tqdm = True
        while len(self.missing_pages) != 0:
            if tries != 0:
                leave_tqdm = False
                logger.info(
                    f'Retrying failed pages for the {tries}(th) time...'
                )

            self.download_pages(
                self.missing_pages,
                tries=tries, leave_tqdm=leave_tqdm
            )
            self.load_missing_pages()

            # record missing pages for initial download try
            if tries == 0:
                self.initial_failed_pages = self.load_missing_pages()

            tries += 1
            if tries > 3 and len(self.missing_pages) != 0:
                logger.error(f'Failed pages: {self.missing_pages}')
                self.status_code = -9

                return

    def download_pages(
        self,
        pages: list[str],
        tries: Optional[int] = 0,
        leave_tqdm: Optional[bool] = True
    ) -> None:

        t = tqdm(self.missing_pages, leave=leave_tqdm)
        for page in t:

            if tries == 0:
                t.set_description(f"Downloading #{self.id}")
                img_base_url = IMG_BASE_URL_i5

            else:
                t.set_description(
                    f'Retrying failed pages for the {tries}(th) time'
                )

                img_base_urls = [
                    IMG_BASE_URL_i2,
                    IMG_BASE_URL_i3,
                    IMG_BASE_URL_i5,
                    IMG_BASE_URL_i7
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
            '._Icon\r',
            'Icon\r',
            'metadata.json',
            f'thumb.{self.thumb_extension}',
            '.DS_Store',
            f'{self.title}.pdf'
        ]

        downloaded_pages = [
            unicodedata.normalize('NFC', page)
            for page in downloaded_pages
            if unicodedata.normalize('NFC', page)
            not in non_page_files
        ]

        for downloaded_page in downloaded_pages:
            if (Path(downloaded_page).stem
                    not in [str(i) for i in range(1, int(self.num_pages)+1)]):
                extra_pages.append(downloaded_page)

        if len(extra_pages) != 0:
            self.status_code = -10

        return extra_pages

    def check_pdf(self) -> None:

        logger.info('Checking PDF...')
        pdf_path = f"{self.folder_dir}/{self.title}.pdf"
        # load all image files and remove unwanted ones
        image_filenames = os.listdir(self.folder_dir)
        exclude_list = [
            'Icon\r',
            '._Icon\r',
            'metadata.json',
            '.DS_Store',
            f'thumb.{self.thumb_extension}',
        ]
        image_filenames = [
            unicodedata.normalize('NFC', file) for file in image_filenames
            if file not in exclude_list
        ]

        # check whether pdf already exists
        if f"{self.title}.pdf" in image_filenames:
            reader = PdfReader(pdf_path)
            if len(reader.pages) == self.num_pages:
                logger.info('PDF file already exists with matching page count')

                return

        logger.info('Converting images to PDF file...')
        # sort according to page number
        sort = [int(Path(page).stem) for page in image_filenames]
        image_filenames = [
            file for _, file in sorted(zip(sort, image_filenames))
        ]

        # open all image files and save to pdf
        images = []
        try:
            for img_filename in image_filenames:
                image_path = os.path.join(self.folder_dir, img_filename)
                with Image.open(image_path) as img:
                    img_copy = img.copy()
                images.append(img_copy)
            images[0].save(
                pdf_path, "PDF", resolution=100.0,
                save_all=True, append_images=images[1:]
            )
        except Exception as error:
            logger.error(f"{error}")
            self.status_code = -11

    def status(self) -> str:
        # status_code >= -1: Normal
        # status_code < -1: Error

        status_dict = {
            0: f"{str(self)} download finished",
            1: f"{str(self)} already downloaded",
            2: (f"{str(self)} has the same title as "
                f"the already downloaded #{self.downloaded_metadata['id']}"),
            -1: 'Download not finished...',
            -2: 'Error 403 - Forbidden (try updating `cf_clearance`)',
            -3: f'Error 404 - Not Found for #{self.id}',
            -4: ('Error when downloading metadata '
                 f"(failed retry 3 times) for #{self.id}"),
            -5: f"BLACKLISTED #{self.id}",
            -6: f'Error when downloading thmbnail for {str(self)}',
            -7: f'Error when setting tags for {str(self)}',
            -8: f'Error when setting thumbnail for {str(self)}',
            -9: ('Error when downloading missing pages (failed retry 3 times) '
                 f"for {str(self)}"),
            -10: ('There are more pages downloaded than self.num_pages '
                  f"for {str(self)}"),
            -11: f'Error when saving PDF for {str(self)}',
        }

        return status_dict[self.status_code]

    def download(self) -> int:

        def skip_download():
            if self.status_code < -1:
                tqdm.write(self.status())
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

        self.check_thumb()
        if skip_download():
            return self.status_code

        self.check_extra_pages()
        if skip_download():
            return self.status_code

        self.check_missing_pages()
        if skip_download():
            return self.status_code

        self.check_pdf()
        if skip_download():
            return self.status_code

        # set tags after finishing download
        self.check_tags()
        if skip_download():
            return self.status_code

        self.status_code = 0
        logger.info(f'{self.status()}')
        tqdm.write(self.status())

        return self.status_code


if __name__ == '__main__':
    misc.set_logging_config()
    logger.info(f"\n{'-'*os.get_terminal_size().columns}")
    logger.info('Program started')

    application_folder_path = misc.get_application_folder_dir()
    download_dir = os.path.abspath(f'{application_folder_path}/test/')

    session = create_session()

    id_list = input('Input gallery id: ').split(' ')

    for gallery_id in id_list:
        gallery = Gallery(gallery_id, download_dir=download_dir)
        gallery.download()
