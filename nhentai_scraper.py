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

wait_time = 60

# register a handler for the timeout
def handler(signum, frame):
    signame = signal.Signals(signum).name
    print(f'Signal handler called with signal {signame} ({signum})')
    raise OSError("Waited for too long")

def load_download_list():
    filename = 'download_list.txt'
    with open(filename) as f:
        download_list = f.read().splitlines()
    download_list = [entry for entry in download_list if not entry == '']
    
    return download_list

class Download_gallery:
    
    def __init__(self, gallery_id, download_dir='./Downloaded/',
                 headers={}, cookies={}):
        
        self.gallery_id = gallery_id.split('#')[-1]
        self.download_dir = download_dir
        self.headers = headers
        self.cookies = cookies
        
        self.status_code = 'Not finished...'
    
    def sleep(self, sleep_time='default'):
        if sleep_time == 'default':
            sleep_time = 3*random.random()+1.5
        print(f'Sleeping for ~ {sleep_time:.1f} seconds...')
        time.sleep(sleep_time)
        
    def load_headers(self):
        
        headers_filename = 'headers.json'
        with open(headers_filename) as f:
            self.headers = json.load(f)

        return self.headers
    
    def load_cookies(self):
        
        cookies_filename = 'cookies.json'
        with open(cookies_filename) as f:
            self.cookies = json.load(f)
            
        return self.cookies
    
    def get_response(self, url, headers={}, cookies={}):
        
        if not headers:
            headers = self.headers
        if not cookies:
            cookies = self.cookies
            
        try:
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(wait_time)
            response = requests.get(url, headers=self.headers, cookies=self.cookies)
            signal.alarm(0)
        except Exception as error:
            print(f'An exception occured: {error}')
        self.sleep()
        
        return response
    
    def get_metadata(self):
        
        print(f"\nRetrieving gallery api for id '{self.gallery_id}'...")
        api_url = f'https://nhentai.net/api/gallery/{int(self.gallery_id)}'
        
        try:
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(wait_time)
            api_response = requests.get(api_url, headers=self.headers, cookies=self.cookies)
            signal.alarm(0)
        except Exception as error:
            print(f'An exception occured: {error}')
        self.sleep()
        tries = 0
        while api_response.status_code != 200:
            print('Retrying...')
            try:
                signal.signal(signal.SIGALRM, handler)
                signal.alarm(wait_time)
                api_response = requests.get(api_url, headers=self.headers, cookies=self.cookies)
                signal.alarm(0)
            except Exception as error:
                print(f'An exception occured: {error}')
            self.sleep()
            tries += 1
            if tries >= 5:
                break
                
        if tries >= 5:
            self.status_code = 'Tried more than 5 times when getting metadata'
            return 
            
        self.metadata = api_response.json()
        self.media_id = self.metadata['media_id']
        if self.metadata['title']['japanese']:
            self.title = self.metadata['title']['japanese']
        else:
            self.title = self.metadata['title']['english']
        self.tags = self.metadata['tags']
        self.num_pages = self.metadata['num_pages']
        
        print(f'\n\nTitle: {self.title}\n')
        
        return self.metadata
    
    def make_dir(self):
        
        # replace '/' with '_' for folder directory
        self.folder_dir = self.download_dir+self.title.replace('/', '_')
            
        # if there exists downloaded gallery with same name
        if os.path.isdir(self.folder_dir):
            # download and set thumbnail
            if 'thumb.jpg' not in os.listdir(self.folder_dir)\
                or 'thumb.png' not in os.listdir(self.folder_dir):
                try:
                    self.download_thumb()
                    self.set_thumb()
                except Exception as error:
                    print(f'An exception occured: {error}')
                    
            # check whether same source
            self.load_downloaded_metadata()
            self.extension = os.listdir(self.folder_dir)[-1].split('.')[-1]
            if int(self.downloaded_metadata['id']) != int(self.gallery_id):
                self.status_code = -2
                
                return
            
        else:
            os.mkdir(self.folder_dir)
            
            self.save_metadata()
            self.set_tags()
            
            # download and thumbnail
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
        # check if extension is jpg or png
        self.extension = 'jpg'
        self.thumb = f'https://t3.nhentai.net/galleries/{self.media_id}/thumb.{self.extension}'
        try:
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(wait_time)
            thumb_response = requests.get(self.thumb, headers=self.headers)
            signal.alarm(0)
        except Exception as error:
            print(f'An exception occured: {error}')
            return
        if thumb_response.status_code != 200:
            self.extension = 'png'
            self.thumb = f'https://t3.nhentai.net/galleries/{self.media_id}/thumb.{self.extension}'
            try:
                signal.signal(signal.SIGALRM, handler)
                signal.alarm(wait_time)
                thumb_response = requests.get(self.thumb, headers=self.headers)
                signal.alarm(0)
            except Exception as error:
                print(f'An exception occured: {error}')
                return
        self.sleep()
        
        thumb_extension = self.thumb.split('.')[-1]
        thumb_data = thumb_response.content
        
        self.thumb_filename = f'{self.folder_dir}/thumb.{thumb_extension}'
        with open(self.thumb_filename, 'wb') as f:
            f.write(thumb_data)

            
    def set_tags(self):
        
        tags = ''.join(f"'{tag['name']}'," for tag in self.tags)
        tags = tags[:-1]
        set_tags_command = f"tag -a {tags} '{self.folder_dir}'"
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
        
        # img_urls = [f'https://i5.nhentai.net/galleries/{self.media_id}/{int(page)}.{self.extension}',
        #             f'https://i5.nhentai.net/galleries/{self.media_id}/{int(page)}.jpg',
        #             f'https://i5.nhentai.net/galleries/{self.media_id}/{int(page)}.png'
        #             ]
        
        # for img_url in img_urls:
        #     img_response = self.get_response(img_url)
        #     if img_response.status_code == 200:
        #         break
        # if img_response.status_code != 200:
        #     print(f'Something went wrong with status code {img_response.status_code}')
        #     return 
        
        img_url = f'https://i5.nhentai.net/galleries/{self.media_id}/{int(page)}.{self.extension}'
        try:
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(wait_time)
            img_response = requests.get(img_url, headers=self.headers)
            signal.alarm(0)
        except Exception as error:
            print(f'\nAn exception occured for page {page}: {error}')
            return
        if img_response.status_code != 200:
            print(f'Something went wrong with status code {img_response.status_code}')
            return 
        
        print('Image downloaded')
        self.sleep()
        filename = f'{self.folder_dir}/{str(page)}.{self.extension}'
        with open(filename, 'wb') as f:
            f.write(img_response.content)
            
    def check_gallery(self):
        
        print('\nChecking downloaded gallery...')
        self.load_missing_pages()
        
        # check for extra pages
        extra_pages = self.find_extra_pages()
        if len(extra_pages) != 0:
            print('There are more pages downloaded than self.num_pages')
            self.status_code = -1
            
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
                print('\nTried more than 3 times')
                print(f'\nFailed pages: {self.missing_pages}')
                print(f"\n{'-'*200}")
                self.status_code = 'Retried for more than 3 times'
                
                return

        self.status_code = 0
            
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
        
    def find_extra_pages(self):
        
        # check whether there are more pages downloaded than self.num_pages
        # which should not happen
        extra_pages = []
        for file_count in [file.split('.')[0] for file in os.listdir(self.folder_dir)]:
            if file_count != 'Icon\r' and file_count != 'metadata' and file_count != 'thumb':
                if int(file_count) not in range(int(self.num_pages)+1):
                    extra_pages.append(file_count)
                    
        return extra_pages
    
    def download_gallery(self):
        
        if not self.headers:
            self.load_headers()
        if not self.cookies:
            self.load_cookies()
            
        try:
            self.get_metadata()
        except Exception as error:
            print(f'An exception occured: {error}')
            self.status_code = 'Error when retrieving metadata'
            print(f'\n\nStatus code: {self.status_code}')
            print(f"\n\n{'-'*200}")
            
            return self.status_code
        
        if self.status_code != 'Not finished...':
            print(f'\n\nStatus code: {self.status_code}')
            print('Try updating cf_clearance')
            print(f"\n\n{'-'*200}")
            
            return self.status_code
        
        self.make_dir()
        if self.status_code == -2:
            print(f"Same gallery with different id {self.downloaded_metadata['id']} already downloaded")
            print(f"\n\n{'-'*200}")
            
            return self.status_code
        
        self.check_gallery()
        
        if self.status_code == 0:
            print(f'\n\nFinished downloading {self.title}')
            print(f"\n\n{'-'*200}")
        
        return self.status_code

if __name__ == '__main__':
    failed_galleries = []
    for gallery_id in load_download_list():
        Download = Download_gallery(gallery_id)
        Download.download_gallery()
        if Download.status_code != 0 and Download.status_code != -1:
            failed_galleries.append(f'{gallery_id}, status_code: {Download.status_code}')
    
    # write the remaining uncessful ones after retrying to file
    if len(failed_galleries) != 0:
        filename = 'failed_download_list.txt'
        with open(filename, 'w') as f:
            for entry in failed_galleries:
                f.write(entry)
                f.write('\n')
        print(f'\n\nFailed gallery id written to {filename}')
    else:
        print('\n\n\n\n\nFinished all downloads!!!\n\n\n\n\n')