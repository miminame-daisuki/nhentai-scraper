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
import signal
import subprocess

class Gallery:
    
    def __init__(self, gallery_id, download_dir='',
                 headers={} , cookies={}):
        
        self.id = str(gallery_id).split('#')[-1]
        
        self.download_dir = download_dir
        if not download_dir:
            cur_path = os.path.dirname(__file__)
            self.download_dir = os.path.relpath('../Downloaded/', cur_path)
        
        self.headers = headers
        if not self.headers:
            self.load_headers()
        self.cookies = cookies
        if not self.cookies:
            self.load_cookies()
        
        self.status = 'Not finished...'
        
    def load_headers(self):
        
        cur_path = os.path.dirname(__file__)
        inputs_folder_path = os.path.relpath('../inputs/', cur_path)
        headers_filename = f'{inputs_folder_path}/headers.json'
        with open(headers_filename) as f:
            self.headers = json.load(f)

        return self.headers
    
    def load_cookies(self):
        
        cur_path = os.path.dirname(__file__)
        inputs_folder_path = os.path.relpath('../inputs/', cur_path)
        cookies_filename = f'{inputs_folder_path}/cookies.json'
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
            self.status = 'Tried more than 5 times when getting metadata'
            return 
            
        self.metadata = api_response.json()
        self.media_id = self.metadata['media_id']
        if self.metadata['title']['japanese']:
            self.title = self.metadata['title']['japanese']
        else:
            self.title = self.metadata['title']['english']
        self.tags = [tag['name'] for tag in self.metadata['tags']]
        self.num_pages = self.metadata['num_pages']
        
        print(f'\n\nTitle: {self.title}\n')
        
        return self.metadata
    
    def get_img_extension(self, img_metadata):
        
        if img_metadata['t'] == 'j':
            extension = 'jpg'
        elif img_metadata['t'] == 'p':
            extension = 'png'
            
        return extension
    
    def make_dir(self):
        
        # replace '/' with '_' for folder directory
        self.folder_dir = os.path.join(self.download_dir,self.title.replace('/', '_'))
            
        # check whether there exists a downloaded gallery with the same name
        if os.path.isdir(self.folder_dir):
            # check whether the gallery was downloaded with a different source
            self.load_downloaded_metadata()
            if int(self.downloaded_metadata['id']) != int(self.id):
                self.status = f"Same gallery with different id {self.downloaded_metadata['id']} already exists"
                
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
        thumb_square.paste(thumb ,(int((thumb_size-thumb_width)/2),int((thumb_size-thumb_height)/2)))
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
        
        # download all missing pages, and try for up to 3 times for failed pages
        tries = 0
        while len(self.missing_pages) != 0:
            if tries != 0:
                print(f'\n\nRetrying failed downloads for the {tries}(th) time...\n')
                
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

        self.status = f'Finished downloading {self.title}'
            
    def download_missing_pages(self):
        
        for page_count in self.missing_pages:
            self.download_page(page_count)
            
    def load_missing_pages(self):
        
        # check against self.num_pages to check whether all page numbers are downloaded 
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
        for file_count in [file.split('.')[0] for file in os.listdir(self.folder_dir)]:
            if file_count != 'Icon\r' and file_count != 'metadata'\
                and file_count != 'thumb' and file_count != '':
                if int(file_count) not in range(int(self.num_pages)+1):
                    extra_pages.append(file_count)
                    
        return extra_pages
    
    def download(self):
            
        try:
            self.get_metadata()
        except Exception as error:
            print(f'An exception occured: {error}')
            self.status = 'Error when retrieving metadata'
            print(f'\n\n{self.status}')
            print(f"\n\n{'-'*200}")
            
            return self.status
        
        if self.status != 'Not finished...':
            print(f'\n\n{self.status}')
            print('Try updating cf_clearance')
            print(f"\n\n{'-'*200}")
            
            return self.status
        
        self.check_gallery()
        
        print(f'\n\n{self.status}')
        print(f"\n\n{'-'*200}")
            
        return self.status

if __name__ == '__main__':
    # download_dir = '/Volumes/Transcend/Transcend/untitled folder/nhentai_new/test/'
    gallery_id = input('Input gallery id: ')
    gallery = Gallery(gallery_id)
    gallery.download()
