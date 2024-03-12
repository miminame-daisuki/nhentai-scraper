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
        logging_config_filename = os.path.join(logging_dir,
                                               'logging_config.yaml')
    with open(logging_config_filename) as f:
        if 'yaml' in logging_config_filename:
            logging_config = yaml.full_load(f)
        elif 'json' in logging_config_filename:
            logging_config = json.load(f)

    logging_filename = os.path.join(logging_dir,
                                    f'{__name__}.log')
    logging_config['handlers']['file']['filename'] = logging_filename

    logging.config.dictConfig(logging_config)


def get_application_folder_dir():

    application_folder_dir = ''
    # when running executable
    if getattr(sys, 'frozen', False):
        application_folder_dir = os.path.dirname(sys.executable)
    # when running python script (placed inside ./src/)
    elif __file__:
        application_folder_dir = os.path.abspath(
            f'{os.path.dirname(__file__)}/..')

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


def get_response(url, headers=None, cookies=None,
                 sleep_time='default', timeout_time=61):

    if not headers:
        headers = {}
    if not cookies:
        cookies = {}

    try:
        response = requests.get(url, headers=headers, cookies=cookies,
                                timeout=timeout_time)
    except Exception as error:
        logger.error(f'An exception occured: {error}')
        response = lambda: None
        response.status_code = 'No_response'

    # sleep for sleep_time after each get_response
    if sleep_time == 'default':
        sleep_time = 3*random.random()+1.5
    logger.info(f'Sleeping for ~ {sleep_time:.1f} seconds...')
    time.sleep(sleep_time)

    return response


class Gallery:

    def __init__(self, gallery_id, download_dir='',
                 headers=None, cookies=None):

        self.id = str(gallery_id).split('#')[-1]
        logger.info(f'Gallery initiated for id: {gallery_id}')

        self.application_folder_path = get_application_folder_dir()

        # set download_dir to the one provided, or use default directory
        if download_dir:
            if os.path.isabs(download_dir):
                self.download_dir = download_dir
            else:
                self.download_dir = os.path.abspath(
                    f'{self.application_folder_path}/{download_dir}/')
        else:
            self.downloaded_dir = os.path.abspath(
                f'{self.application_folder_path}/Downloaded/')
            if not os.path.isdir(self.download_dir):
                os.mkdir(self.download_dir)
        logger.info(f"Download directory set to: '{self.download_dir}'")

        self.inputs_dir = os.path.abspath(
            f'{self.application_folder_path}/inputs/')

        self.headers = headers
        if not self.headers:
            self.headers = load_headers(self.inputs_dir)
        self.cookies = cookies
        if not self.cookies:
            self.cookies = load_cookies(self.inputs_dir)

        self.status_code = -1

        self.title = ''
        self.downloaded_metadata = {'id': ''}

    def download_metadata(self):

        logger.info('Downloading gallery metadata from nhentai api...')
        api_url = f'https://nhentai.net/api/gallery/{int(self.id)}'

        api_response = get_response(api_url,
                                    headers=self.headers,
                                    cookies=self.cookies)
        if api_response.status_code == 403:
            self.status_code = -2

            return

        elif api_response.status_code == 404:
            self.status_code = -3

            return

        # retry for up to 3 times
        tries = 0
        while api_response.status_code != 200:
            logger.error(('Failed to retrieve metadata with status code'
                          f'{api_response.status_code}, retrying...'))
            api_response = get_response(api_url,
                                        headers=self.headers,
                                        cookies=self.cookies)
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
        self.tags = [f"{tag['type']}:{tag['name']}"
                     for tag in self.metadata['tags']]
        self.num_pages = self.metadata['num_pages']

        return self.metadata

    def check_blacklist(self, blacklist=None):
        logger.info('Checking blacklist...')
        if not blacklist:
            blacklist = load_input_list('blacklist.txt')
        for tag in self.metadata['tags']:
            if any(tag in self.tags for tag in blacklist):
                self.status_code = -5

    def get_img_extension(self, img_metadata):

        if img_metadata['t'] == 'j':
            extension = 'jpg'
        elif img_metadata['t'] == 'p':
            extension = 'png'
        elif img_metadata['t'] == 'g':
            extension = 'gif'

        return extension

    def check_dir(self):

        logger.info('Checking folder...')
        # replace '/' with '_' for folder directory
        self.folder_dir = os.path.join(self.download_dir, self.title)

        # check whether there exists a downloaded gallery with the same name
        if os.path.isdir(self.folder_dir):
            # check whether the gallery was downloaded with a different source
            self.load_downloaded_metadata()
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
                    logger.error(('An exception occured when'
                                  f'downloading/setting thumbnail: {error}'))

        else:
            os.mkdir(self.folder_dir)

            self.save_metadata()
            self.set_tags()

            # download and set thumbnail
            try:
                self.download_thumb()
                self.set_thumb()
            except Exception as error:
                logger.error(('An exception occured when downloading/setting'
                              f'thumbnail: {error}'))

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
            self.metadata['images']['thumbnail'])
        thumb_url = ('https://t3.nhentai.net/galleries/'
                     f'{self.media_id}/thumb.{extension}')
        thumb_response = get_response(thumb_url,
                                      headers=self.headers,
                                      cookies=self.cookies)
        if thumb_response.status_code != 200:
            self.status_code = -6
            logger.error(('Something went wrong when retrieving thumbnail:'
                          f'{thumb_response.status_code}'))
            return

        self.thumb_filename = f'{self.folder_dir}/thumb.{extension}'
        with open(self.thumb_filename, 'wb') as f:
            f.write(thumb_response.content)

    def set_tags(self):

        tags_string = ''.join(f'{tag},' for tag in self.tags)
        tags_string = tags_string[:-1]  # to exclude the final ','

        # set tags with tag
        set_tags_command = ['tag',
                            '-a',
                            f'{tags_string}',
                            f"{self.folder_dir}"
                            ]
        result = run(set_tags_command, capture_output=True, check=True)
        logger.info(f'{result.stdout}')
        if result.returncode != 0:
            self.status_code = -7
            logger.error(f"{result.stderr}")

    def set_thumb(self):

        # resizing thumbnail to be square
        thumb = Image.open(self.thumb_filename)
        thumb_width, thumb_height = thumb.size
        thumb_size = max(thumb_width, thumb_height)
        thumb_square = Image.new(
            'RGBA', (thumb_size, thumb_size), (0, 0, 0, 0))
        thumb_square.paste(thumb,
                           (int((thumb_size-thumb_width)/2),
                            int((thumb_size-thumb_height)/2)))
        thumb_rgb = thumb_square.convert('RGB')
        thumb_rgb.save(self.thumb_filename)

        # set thumbnail with filicon
        set_thumb_command = ['fileicon',
                             'set',
                             f"{self.folder_dir}",
                             f'{self.thumb_filename}'
                             ]
        result = run(set_thumb_command, capture_output=True, check=True)
        logger.info(f'{result.stdout}')
        if result.returncode != 0:
            self.status_code = -8
            logger.error(f"{result.stderr}")

    def download_page(self, page):

        logger.info(f'Retrieving Page {page}/{self.num_pages} url...')

        extension = self.get_img_extension(
            self.metadata['images']['pages'][int(page)-1])
        img_url = ('https://i5.nhentai.net/galleries/'
                   f'{self.media_id}/{int(page)}.{extension}')
        img_response = get_response(img_url,
                                    headers=self.headers,
                                    cookies=self.cookies)
        if img_response.status_code != 200:
            logger.error(('Something went wrong with when getting response'
                          f'for page {page}: {img_response.status_code}'))
            return

        logger.info('Image downloaded')
        filename = f'{self.folder_dir}/{str(page)}.{extension}'
        with open(filename, 'wb') as f:
            f.write(img_response.content)

    def check_gallery(self):

        logger.info('Checking downloaded gallery...')

        # check for missing and extra pages
        self.load_missing_pages()
        self.check_extra_pages()

        if self.status_code != -1:
            return self.status_code

        # download all missing pages, and retry up to 3 times for failed pages
        tries = 0
        while len(self.missing_pages) != 0:
            if tries == 0:
                print(f'\nDownloading {self.title} (#{self.id})')
                logger.info(f'Title: {self.title}')
            if tries != 0:
                logger.info(('Retrying failed downloads '
                             f'for the {tries}(th) time...\n'))
                print(('Retrying failed downloads '
                       f'for the {tries}(th) time...'))

            self.download_missing_pages()
            self.load_missing_pages()

            # record missing pages for initial download try
            if tries == 0:
                self.initial_failed_pages = self.load_missing_pages()

            tries += 1
            if tries > 3 and len(self.missing_pages) != 0:
                logger.error(f'Failed pages: {self.missing_pages}')
                self.status_code = -9
                return

    def download_missing_pages(self):

        for page in tqdm(self.missing_pages):
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
        non_page_files = ['Icon\r', 'metadata.json', 'thumb.jpg', 'thumb.png',
                          '.DS_Store', f'{self.title}.pdf']
        downloaded_pages = [unicodedata.normalize('NFC', page)
                            for page in downloaded_pages
                            if unicodedata.normalize('NFC', page)
                            not in non_page_files]
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
        exclude_list = ['Icon\r', 'metadata.json', '.DS_Store',
                        'thumb.jpg', 'thumb.png']
        image_filenames = [
            unicodedata.normalize('NFC', file) for file in image_filenames if file not in exclude_list
        ]

        # check whether pdf already exists
        if f"{self.title}.pdf" in image_filenames:
            reader = PdfReader(pdf_path)
            if len(reader.pages) == self.num_pages:
                logger.info('PDF file already exists with matching page count')
                self.status_code = 1

                return

        logger.info('Converting images to PDF file...')
        # sort according to page number
        sort = [int(Path(page).stem) for page in image_filenames]
        image_filenames = [file for _, file in sorted(
            zip(sort, image_filenames))]

        # open all image files and save to pdf
        try:
            images = [Image.open(os.path.join(self.folder_dir, img_filename))
                      for img_filename in image_filenames]
            images[0].save(pdf_path, "PDF", resolution=100.0,
                           save_all=True, append_images=images[1:])
        except Exception as error:
            logger.error(f"{error}")
            self.status_code = -11

    def status(self):
        # status_code >=0: Normal
        # status_code <0: Error
        status_dict = {
            0: f"Finished downloading {self.title} (#{self.id})",
            1: f"{self.title} (#{self.id}) already downloaded",
            2: (f"{self.title} (#{self.id}) has the same title as "
                f"the already downloaded #{self.downloaded_metadata['id']}"),
            -1: 'Download not finished...',
            -2: 'Error 403 - Forbidden (try updating `cf_clearance`)',
            -3: f'Error 404 - Not Found for #{self.id}',
            -4: ('Error when downloading metadata '
                 f"(failed retry 3 times) for #{self.id}"),
            -5: f"BLACKLISTED #{self.id}",
            -6: 'Error when downloading thmbnail',
            -7: 'Error when setting tags',
            -8: 'Error when setting thumbnail',
            -9: 'Error when downloading missing pages (failed retry 3 times)',
            -10: 'There are more pages downloaded than self.num_pages',
            -11: 'Error when saving PDF',
        }

        return status_dict[self.status_code]

    def download(self):

        def check_status():
            logger.info(self.status())
            if self.status_code == -1:

                return True

            elif self.status_code == 0:
                logger.info(f'\n\n{self.status()}')
                logger.info(f"\n{'-'*200}")

                return True

            elif self.status_code > 0:
                print(self.status())

                return False

            else:
                print(self.status())
                logger.error(f'Status: {self.status()}')
                logger.error(f"\n{'-'*200}")

                return False

        self.download_metadata()
        if not check_status():
            return self.status_code

        self.check_blacklist()
        if not check_status():
            return self.status_code

        self.check_dir()
        if not check_status():
            return self.status_code

        self.check_gallery()
        if not check_status():
            return self.status_code

        self.check_pdf()
        if not check_status():
            return self.status_code

        self.status_code = 0
        check_status()


if __name__ == '__main__':
    set_logging_config()
    logger.info(f"\n{'-'*200}")
    logger.info('Program started')
    download_dir = os.path.abspath(f'{get_application_folder_dir()}/test/')
    id_list = input('Input gallery id: ')
    id_list = id_list.split(' ')
    for gallery_id in id_list:
        gallery = Gallery(gallery_id, download_dir=download_dir)
        gallery.download()
        if gallery.status_code == 0:
            print(gallery.status())
