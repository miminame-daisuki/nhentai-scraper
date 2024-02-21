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
import sys
from PIL import Image
import signal
import subprocess
import unicodedata

def get_application_folder_dir():
    
    # when running executable
    if getattr(sys, 'frozen', False):
        application_folder_dir = os.path.dirname(sys.executable)
    # when running python script (placed inside ./src/)
    elif __file__:
        application_folder_dir = os.path.abspath(f'{os.path.dirname(__file__)}/..')
        
    return application_folder_dir

class Gallery:
    
    def __init__(self, gallery_id, download_dir='',
                 headers={} , cookies={}):
        
        self.id = str(gallery_id).split('#')[-1]
        
        self.application_folder_path = get_application_folder_dir()
        
        # set download_dir to the one provided, or use default directory
        if download_dir:
            if os.path.isabs(download_dir):
                self.download_dir = download_dir
            else:
                self.download_dir = os.path.abspath(f'{self.application_folder_path}/{download_dir}/')
        if not download_dir:
            self.downloaded_dir = os.path.abspath(f'{self.application_folder_path}/Downloaded/')
        print(f"\nDownload directory set to: '{self.download_dir}'")
        
        self.inputs_dir = os.path.abspath(f'{self.application_folder_path}/inputs/')
        
        self.headers = headers
        if not self.headers:
            self.load_headers()
        self.cookies = cookies
        if not self.cookies:
            self.load_cookies()
        
        self.status = 'Not finished...'
        
    def load_headers(self):
        
        headers_filename = f'{self.inputs_dir}/headers.json'
        with open(headers_filename) as f:
            self.headers = json.load(f)

        return self.headers
    
    def load_cookies(self):
        
        cookies_filename = f'{self.inputs_dir}/cookies.json'
        with open(cookies_filename) as f:
            self.cookies = json.load(f)
            
        return self.cookies
    
    def get_response(self, url, headers={}, cookies={},
                     sleep_time='default', timeout_time=60):
        
        # register a handler for the timeout
        def handler(signum, frame):
            signame = signal.Signals(signum).name
            print(f'Signal handler called with signal {signame} ({signum})')
            raise OSError("Waited for too long")
            
        if not headers:
            headers = self.headers
        if not cookies:
            cookies = self.cookies
            
        try:
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(timeout_time)
            response = requests.get(url, headers=headers, cookies=cookies)
            signal.alarm(0)
        except Exception as error:
            print(f'An exception occured: {error}')
            response = ''
            
        # sleep for sleep_time after each get_response
        if sleep_time == 'default':
            sleep_time = 3*random.random()+1.5
        print(f'Sleeping for ~ {sleep_time:.1f} seconds...')
        time.sleep(sleep_time)
        
        return response
    
    def get_metadata(self):
        
        print(f"\nRetrieving gallery api for id '{self.id}'...")
        api_url = f'https://nhentai.net/api/gallery/{int(self.id)}'
        
        api_response = self.get_response(api_url)
        
        # try for up to 3 times 
        tries = 0
        while api_response.status_code != 200 or not api_response:
            print('Retrying...')
            api_response = self.get_response(api_url)
            tries += 1
            if tries >= 3:
                break
                
        if tries >= 3:
            self.status = 'Tried more than 5 times when getting metadata, '\
                + 'try updating cf_clearance'
            return 
            
        self.metadata = api_response.json()
        self.media_id = self.metadata['media_id']
        if self.metadata['title']['japanese']:
            self.title = self.metadata['title']['japanese']
        else:
            self.title = self.metadata['title']['english']
        self.title = self.title.replace('/', '_')
        self.tags = [tag['name'] for tag in self.metadata['tags']]
        self.num_pages = self.metadata['num_pages']
        
        print(f'\n\nTitle: {self.title}\n')
        
        return self.metadata
    
    def get_img_extension(self, img_metadata):
        
        if img_metadata['t'] == 'j':
            extension = 'jpg'
        elif img_metadata['t'] == 'p':
            extension = 'png'
        elif img_metadata['t'] == 'g':
            extension = 'gif'
            
        return extension
    
    def make_dir(self):
        
        # replace '/' with '_' for folder directory
        self.folder_dir = os.path.join(self.download_dir, self.title)
            
        # check whether there exists a downloaded gallery with the same name
        if os.path.isdir(self.folder_dir):
            # check whether the gallery was downloaded with a different source
            self.load_downloaded_metadata()
            if int(self.downloaded_metadata['id']) != int(self.id):
                self.status = "Same gallery with different id "\
                    +f"{self.downloaded_metadata['id']} already exists"
                
                return
            
            # download and set thumbnail if thumbnail file doesn't exist
            if 'thumb.jpg' not in os.listdir(self.folder_dir)\
                and 'thumb.png' not in os.listdir(self.folder_dir):
                try:
                    self.download_thumb()
                    self.set_thumb()
                except Exception as error:
                    print(f'An exception occured: {error}')
            
        else:
            os.mkdir(self.folder_dir)
            
            self.save_metadata()
            self.set_tags()
            
            # download and set thumbnail
            try:
                self.download_thumb()
                self.set_thumb()
            except Exception as error:
                print(f'An exception occured: {error}')
                
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
        
        print('\nRetrieving thumbnail...')
        extension = self.get_img_extension(self.metadata['images']['thumbnail'])
        thumb_url = f'https://t3.nhentai.net/galleries/{self.media_id}/thumb.{extension}'
        thumb_response = self.get_response(thumb_url)
        if not thumb_response:
            print('Failed when getting response for thumbnail')
            return
        if thumb_response.status_code != 200:
            print(f'Something went wrong: {thumb_response.status_code}')
            return 
        
        self.thumb_filename = f'{self.folder_dir}/thumb.{extension}'
        with open(self.thumb_filename, 'wb') as f:
            f.write(thumb_response.content)

            
    def set_tags(self):
        
        tags_string = ''.join(f"'{tag}'," for tag in self.tags)[:-1]

        # set tags with tag
        set_tags_command = f"tag -a {tags_string} '{self.folder_dir}'"
        subprocess.call(set_tags_command, shell=True)
                
    def set_thumb(self):
        
        # resizing thumbnail to be square 
        thumb = Image.open(self.thumb_filename)
        thumb_width, thumb_height = thumb.size
        thumb_size = max(thumb_width, thumb_height)
        thumb_square=Image.new('RGBA', (thumb_size, thumb_size), (0,0,0,0))
        thumb_square.paste(thumb ,
                           (int((thumb_size-thumb_width)/2),
                            int((thumb_size-thumb_height)/2)))
        thumb_rgb = thumb_square.convert('RGB')
        thumb_rgb.save(self.thumb_filename)
        
        # set thumbnail with filicon
        set_thumb_command = f"fileicon set '{self.folder_dir}' '{self.thumb_filename}'"
        subprocess.call(set_thumb_command, shell=True)
        
    def download_page(self, page):
        
        print(f'\nRetrieving Page {page}/{self.num_pages} url...')
        
        extension = self.get_img_extension(self.metadata['images']['pages'][int(page)-1])
        img_url = f'https://i5.nhentai.net/galleries/{self.media_id}/{int(page)}.{extension}'
        img_response = self.get_response(img_url)
        if not img_response:
            print(f'Failed when getting response for page {page}')
            return 
        if img_response.status_code != 200:
            print(f'Something went wrong with: {img_response.status_code}')
            return 
        
        print('Image downloaded')
        filename = f'{self.folder_dir}/{str(page)}.{extension}'
        with open(filename, 'wb') as f:
            f.write(img_response.content)
            
    def check_gallery(self):
        
        print('\nChecking downloaded gallery...')
        self.make_dir()
        if not self.status == 'Not finished...': return self.status 
        
        # check for missing and extra pages
        self.load_missing_pages()
        extra_pages = self.check_extra_pages()
        if len(extra_pages) != 0:
            self.status = 'There are more pages downloaded than self.num_pages'
            
            return
        
        # download all missing pages, and retry up to 3 times for failed pages
        tries = 0
        while len(self.missing_pages) != 0:
            if tries != 0:
                print('\n\nRetrying failed downloads '
                      + f'for the {tries}(th) time...\n')
                
            self.download_missing_pages()
            self.load_missing_pages()
            
            # record missing pages for initial download try
            if tries == 0:
                self.initial_failed_pages = self.load_missing_pages()
            
            tries += 1
            if tries > 3 and len(self.missing_pages) != 0:
                print(f'\nFailed pages: {self.missing_pages}')
                self.status = 'Retried 3 times'
                
                return

            
    def download_missing_pages(self):
        
        for page_count in self.missing_pages:
            self.download_page(page_count)
            
    def load_missing_pages(self):
        
        # check whether all page numbers are downloaded against self.num_pages
        self.missing_pages = []
        file_list = os.listdir(self.folder_dir)
        for page in range(int(self.num_pages)):
            page_count = str(page+1)
            if page_count not in [file.split('.')[0] for file in file_list]:
                self.missing_pages.append(page_count)
        
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
                            if unicodedata.normalize('NFC', page) not in non_page_files]
        for file_count in downloaded_pages:
            if int(file_count.split('.')[0]) not in range(int(self.num_pages)+1):
                extra_pages.append(file_count)
                    
        return extra_pages
    
    def img2pdf(self):
        
        print('Converting images to PDF file...')
        pdf_path = f'{self.folder_dir}/{self.title}.pdf'
        
        # load all image files and remove unwanted ones
        image_filenames = os.listdir(self.folder_dir)
        exclude_list = ['Icon\r', 'metadata.json', '.DS_Store',
                        'thumb.jpg', 'thumb.png']
        image_filenames = [file for file in image_filenames if not file in exclude_list]
        
        # check whether pdf already exists
        for filename in image_filenames:
            if 'pdf' in filename:
                print('PDF file already exists')
                self.status = f'Finished downloading {self.title}'
                
                return
        
        # sort according to page number
        sort = [int(page.split('.')[0]) for page in image_filenames]
        image_filenames = [file for _, file in sorted(zip(sort, image_filenames))]
        
        # open all image files and save to pdf
        images = [Image.open(os.path.join(self.folder_dir, img_filename))
                  for img_filename in image_filenames]
        
        try:
            images[0].save(pdf_path, "PDF", resolution=100.0, 
                           save_all=True, append_images=images[1:])
        except Exception as error:
            self.status = f'Error when converting to pdf: {error}'
            return
            
        self.status = f'Finished downloading {self.title}'
        
    def download(self):
            
        def check_status():
            if self.status == 'Not finished...':
                return True
            else:
                print(f'\n\n{self.status}')
                print(f"\n\n{'-'*200}")
                
                return False
        
        try:
            self.get_metadata()
        except Exception as error:
            print(f'An exception occured: {error}')
            self.status = 'Error when retrieving metadata'
            print(f'\n\n{self.status}')
            print(f"\n\n{'-'*200}")
            
            return self.status
        
        if not check_status(): return self.status
        
        self.check_gallery()
        if not check_status(): return self.status
        
        self.img2pdf()
        
        print(f'\n\n{self.status}')
        print(f"\n\n{'-'*200}")
            
        return self.status

    

if __name__ == '__main__':
    download_dir = os.path.abspath(f'{get_application_folder_dir()}/test/')
    gallery_id = input('Input gallery id: ')
    gallery = Gallery(gallery_id, download_dir=download_dir)
    gallery.download()
