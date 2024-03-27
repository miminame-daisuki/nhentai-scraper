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
import yaml
import os
import sys
from PIL import Image
from subprocess import run
import unicodedata
from tqdm import tqdm
from pypdf import PdfReader
from pathlib import Path
import logging
import logging.config


logger = logging.getLogger('__main__.' + __name__)


def set_logging_config(logging_config_filename=''):
    logging_dir = os.path.abspath(f'{get_application_folder_dir()}/log/')
    if not logging_config_filename:
        logging_config_filename = os.path.join(
            logging_dir, 'logging_config.yaml'
        )
    with open(logging_config_filename) as f:
        if 'yaml' in logging_config_filename:
            logging_config = yaml.full_load(f)
        elif 'json' in logging_config_filename:
            logging_config = json.load(f)

    logging_filename = os.path.join(
        logging_dir, f'{__name__}.log'
    )
    logging_config['handlers']['file']['filename'] = logging_filename
    logging.config.dictConfig(logging_config)

    logger.info(f"\n{'-'*os.get_terminal_size().columns}")


def get_application_folder_dir():

    application_folder_dir = ''
    # when running executable
    if getattr(sys, 'frozen', False):
        application_folder_dir = os.path.dirname(sys.executable)
    # when running python script (placed inside ./src/)
    elif __file__:
        application_folder_dir = os.path.abspath(
            f'{os.path.dirname(__file__)}/..'
        )

    return application_folder_dir


def load_input_list(filename):

    application_folder_path = get_application_folder_dir()
    inputs_folder_dir = os.path.abspath(f'{application_folder_path}/inputs/')
    filename = f'{inputs_folder_dir}/{filename}'
    with open(filename) as f:
        id_list = f.read().splitlines()
    id_list = [entry for entry in id_list if not entry == '']

    return id_list


def load_headers(inputs_dir):

    headers_filename = f'{inputs_dir}/headers.json'
    with open(headers_filename) as f:
        headers = json.load(f)

    return headers


def load_cookies(inputs_dir):

    cookies_filename = f'{inputs_dir}/cookies.json'
    with open(cookies_filename) as f:
        cookies = json.load(f)

    return cookies


def get_response(
    url, headers=None, cookies=None,
    sleep_time='default', timeout_time=61
):

    if not headers:
        headers = {}
    if not cookies:
        cookies = {}

    try:
        response = requests.get(
            url, headers=headers, cookies=cookies, timeout=timeout_time
        )
    except Exception as error:
        logger.error(f'An exception occured: {error}')
        response = lambda: None
        response.status_code = 'No_response'

    # sleep for sleep_time after each get_response
    if sleep_time == 'default':
        sleep_time = 3*random.random()+1.5
    logger.info(f'Sleeping for {sleep_time:.3f} seconds...')
    time.sleep(sleep_time)

    return response


def check_tag_fileicon():
    result_tag = run(['which', 'tag'], capture_output=True)
    result_fileicon = run(['which', 'fileicon'], capture_output=True)
    if result_tag.returncode == 0 and result_fileicon.returncode == 0:
        return True
    else:
        return False


def set_download_dir(download_dir=''):

    application_folder_path = get_application_folder_dir()

    if download_dir:
        if os.path.isabs(download_dir):
            pass
        else:
            download_dir = os.path.abspath(
                f'{application_folder_path}/{download_dir}/'
            )
    else:
        download_dir = os.path.abspath(
            f'{application_folder_path}/Downloaded/'
        )

    if not os.path.isdir(download_dir):
        os.mkdir(download_dir)

    return download_dir


class Gallery:

    def __init__(
        self, gallery_id, download_dir='',
        additional_tags=None, headers=None, cookies=None
    ):

        self.id = str(gallery_id).split('#')[-1]
        logger.info(f'Gallery initiated for id: {gallery_id}')

        self.application_folder_path = get_application_folder_dir()
        self.download_dir = set_download_dir(download_dir)
        self.inputs_dir = os.path.abspath(
            f'{self.application_folder_path}/inputs/'
        )
        logger.info(f"Download directory set to: '{self.download_dir}'")

        self.headers = headers
        if not self.headers:
            self.headers = load_headers(self.inputs_dir)
        self.cookies = cookies
        if not self.cookies:
            self.cookies = load_cookies(self.inputs_dir)

        self.status_code = -1

        self.title = ''
        self.downloaded_metadata = {'id': ''}
        self.additional_tags = additional_tags

    def download_metadata(self):

        logger.info('Downloading gallery metadata from nhentai api...')
        api_url = f'https://nhentai.net/api/gallery/{int(self.id)}'

        api_response = get_response(
            api_url, headers=self.headers, cookies=self.cookies
        )
        if api_response.status_code == 403:
            self.status_code = -2

            return

        elif api_response.status_code == 404:
            self.status_code = -3

            return

        # retry for up to 3 times
        tries = 0
        while api_response.status_code != 200:
            logger.error(
                ('Failed to retrieve metadata with status code'
                 f'{api_response.status_code}, retrying...')
            )
            api_response = get_response(
                api_url, headers=self.headers, cookies=self.cookies
            )
            tries += 1

            if tries >= 3 and api_response != 200:
                self.status_code = -4

                return

        self.metadata = api_response.json()
        self.media_id = self.metadata['media_id']
        if self.metadata['title']['japanese']:
            self.title = self.metadata['title']['japanese']
        else:
            self.title = self.metadata['title']['english']
        self.title = self.title.replace('/', '_')
        self.num_pages = self.metadata['num_pages']
        self.tags = [f"{tag['type']}:{tag['name']}"
                     for tag in self.metadata['tags']]

        if self.additional_tags is not None:
            self.tags.append(self.additional_tags)

        logger.info('Metadata downloaded')
        logger.info(f'Title: {self.title}')

        return self.metadata

    def check_blacklist(self, blacklist=None):
        logger.info('Checking blacklist...')
        if not blacklist:
            blacklist = load_input_list('blacklist.txt')
            blacklist_tags = [tag for tag in blacklist if ':' in tag]
        if any(tag in self.tags for tag in blacklist_tags):
            self.status_code = -5
        else:
            logger.info('Clear')

    def get_img_extension(self, img_metadata):

        if img_metadata['t'] == 'j':
            extension = 'jpg'
        elif img_metadata['t'] == 'p':
            extension = 'png'
        elif img_metadata['t'] == 'g':
            extension = 'gif'

        return extension

    def check_folder(self):

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

            # download and set thumbnail if thumbnail file doesn't exist
            if 'thumb.jpg' not in os.listdir(self.folder_dir)\
                    and 'thumb.png' not in os.listdir(self.folder_dir):
                try:
                    self.download_thumb()
                    self.set_thumb()
                except Exception as error:
                    logger.error(
                        ('An exception occured when'
                         f'downloading/setting thumbnail: {error}')
                    )

        else:
            os.mkdir(self.folder_dir)
            self.save_metadata()
            logger.info('Folder created with metadata saved')

            # download and set thumbnail
            try:
                self.download_thumb()
                self.set_thumb()
            except Exception as error:
                logger.error(
                    ('An exception occured when downloading/setting'
                     f'thumbnail: {error}')
                )

    def load_downloaded_metadata(self):

        metadata_filename = f'{self.folder_dir}/metadata.json'
        with open(metadata_filename, 'r') as f:
            self.downloaded_metadata = json.load(f)

        return self.downloaded_metadata

    def save_metadata(self):

        filename = f'{self.folder_dir}/metadata.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=4)

    def download_thumb(self):

        logger.info('Retrieving thumbnail...')
        extension = self.get_img_extension(
            self.metadata['images']['thumbnail']
        )
        thumb_url = (
            'https://t3.nhentai.net/galleries/'
            f'{self.media_id}/thumb.{extension}'
        )
        thumb_response = get_response(
            thumb_url, headers=self.headers, cookies=self.cookies
        )
        if thumb_response.status_code != 200:
            self.status_code = -6
            logger.error(
                ('Something went wrong when retrieving thumbnail:'
                 f'{thumb_response.status_code}')
            )

            return

        self.thumb_filename = f'{self.folder_dir}/thumb.{extension}'
        with open(self.thumb_filename, 'wb') as f:
            f.write(thumb_response.content)

    def check_tags(self):

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

    def set_thumb(self):

        # resizing thumbnail to be square
        thumb = Image.open(self.thumb_filename)
        thumb_width, thumb_height = thumb.size
        thumb_size = max(thumb_width, thumb_height)
        thumb_square = Image.new(
            'RGBA',
            (thumb_size, thumb_size),
            (0, 0, 0, 0)
        )
        thumb_square.paste(
            thumb,
            (int((thumb_size-thumb_width)/2),
             int((thumb_size-thumb_height)/2)
             )
        )
        thumb_rgb = thumb_square.convert('RGB')
        thumb_rgb.save(self.thumb_filename)

        # set thumbnail with filicon
        set_thumb_command = [
            'fileicon',
            'set',
            f"{self.folder_dir}",
            f'{self.thumb_filename}'
        ]
        result = run(set_thumb_command, capture_output=True)
        logger.info(result.stdout.decode('utf-8').split('\n')[0])
        if result.returncode != 0:
            self.status_code = -8
            logger.error(f"{result.stderr.decode('utf-8')}")

    def download_page(self, page):

        logger.info(f'Retrieving Page {page}/{self.num_pages} url...')

        extension = self.get_img_extension(
            self.metadata['images']['pages'][int(page)-1]
        )
        img_url = (
            'https://i5.nhentai.net/galleries/'
            f'{self.media_id}/{int(page)}.{extension}'
        )
        img_response = get_response(
            img_url, headers=self.headers, cookies=self.cookies
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

    def check_missing_pages(self):

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
                    ('Retrying failed pages '
                     f'for the {tries}(th) time...\n')
                )

            self.download_missing_pages(tries, leave_tqdm=leave_tqdm)
            self.load_missing_pages()

            # record missing pages for initial download try
            if tries == 0:
                self.initial_failed_pages = self.load_missing_pages()

            tries += 1
            if tries > 3 and len(self.missing_pages) != 0:
                logger.error(f'Failed pages: {self.missing_pages}')
                self.status_code = -9

                return

    def download_missing_pages(self, tries, leave_tqdm=True):

        t = tqdm(self.missing_pages, leave=leave_tqdm)
        for page in t:
            if tries == 0:
                t.set_description(f"Downloading #{self.id}")
            else:
                t.set_description(
                    f'Retrying failed pages for the {tries}(th) time'
                )
            self.download_page(page)

    def load_missing_pages(self):

        # check whether all page numbers are downloaded against self.num_pages
        self.missing_pages = []
        file_list = os.listdir(self.folder_dir)
        for page in range(1, int(self.num_pages) + 1):
            if str(page) not in [Path(file).stem for file in file_list]:
                self.missing_pages.append(str(page))

        # delete duplicates
        self.missing_pages = list(dict.fromkeys(self.missing_pages))

        return self.missing_pages

    def check_extra_pages(self):

        # check whether there are more pages downloaded than self.num_pages
        # which should not happen
        extra_pages = []
        downloaded_pages = os.listdir(self.folder_dir)
        non_page_files = [
            'Icon\r',
            'metadata.json',
            'thumb.jpg',
            'thumb.png',
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
            if (int(Path(downloaded_page).stem)
                    not in range(int(self.num_pages)+1)):
                extra_pages.append(downloaded_page)

        if len(extra_pages) != 0:
            self.status_code = -10

        return extra_pages

    def check_pdf(self):

        logger.info('Checking PDF...')
        pdf_path = f"{self.folder_dir}/{self.title}.pdf"
        # load all image files and remove unwanted ones
        image_filenames = os.listdir(self.folder_dir)
        exclude_list = [
            'Icon\r',
            'metadata.json',
            '.DS_Store',
            'thumb.jpg',
            'thumb.png'
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

    def status(self):
        # status_code >= -1: Normal
        # status_code < -1: Error
        status_dict = {
            0: f"{self.title} (#{self.id}) download finished",
            1: f"{self.title} (#{self.id}) already downloaded",
            2: (f"{self.title} (#{self.id}) has the same title as "
                f"the already downloaded #{self.downloaded_metadata['id']}"),
            -1: 'Download not finished...',
            -2: 'Error 403 - Forbidden (try updating `cf_clearance`)',
            -3: f'Error 404 - Not Found for #{self.id}',
            -4: ('Error when downloading metadata '
                 f"(failed retry 3 times) for #{self.id}"),
            -5: f"BLACKLISTED #{self.id}",
            -6: ('Error when downloading thmbnail '
                 f"for {self.title} (#{self.id})"),
            -7: ('Error when setting tags '
                 f"for {self.title} (#{self.id})"),
            -8: ('Error when setting thumbnail '
                 f"for {self.title} (#{self.id})"),
            -9: ('Error when downloading missing pages (failed retry 3 times) '
                 f"for {self.title} (#{self.id})"),
            -10: ('There are more pages downloaded than self.num_pages '
                  f"for {self.title} (#{self.id})"),
            -11: ('Error when saving PDF '
                  f"for {self.title} (#{self.id})"),
        }

        return status_dict[self.status_code]

    def download(self):

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

        self.download_metadata()
        if skip_download():
            return self.status_code

        self.check_blacklist()
        if skip_download():
            return self.status_code

        self.check_folder()
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
    set_logging_config()
    logger.info('Program started')
    download_dir = os.path.abspath(f'{get_application_folder_dir()}/test/')
    id_list = input('Input gallery id: ')
    id_list = id_list.split(' ')
    for gallery_id in id_list:
        gallery = Gallery(gallery_id, download_dir=download_dir)
        gallery.download()
