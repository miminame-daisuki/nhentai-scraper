import requests
from bs4 import BeautifulSoup
import time
import random


# retrieves all <=25 gallery ids from a nhentai url
def get_gallery_id(url):

    gallery_id = []
    cookies = {'cf_clearance': 'wNF01bqaKxeqf.V9wQw8vrtqp6iCGKv05HtfTjTMFSM-1709480007-1.0.1.1-.d3ir9ZGw7UajznShf2db60wRKZsCAEL76Bz__zw8EtPIE6Gq3ZFz49tX75rkmmW1gACiCAVFPuDRcQcXEja7w'}
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15'}

    response = requests.get(url, headers=headers, cookies=cookies, timeout=60)
    time.sleep(3*random.random()+1.5)
    soup = BeautifulSoup(response.content, features='html.parser')
    gallery_count = soup.find('span', {'class': 'count'}).string
    page_count = int(gallery_count)//25 + 1
    gallery_list = soup.find_all('div', {'class': 'gallery'})
    for gallery in gallery_list:
        gallery_id.append(gallery.find('a').get('href').split('/')[2])

    return gallery_id, page_count


# retrieves all gallery ids from a artist
def search_artist(artist: str):

    artist_url = f'https://nhentai.net/artist/{artist}/'
    print('Loading page 1')
    download_list, page_count = get_gallery_id(artist_url)

    for page in range(2, page_count+1):
        print(f'Loading page {page}')
        page_url = artist_url + f'?page={page}'
        download_list.extend(get_gallery_id(page_url)[0])

    return download_list


def load_artist():
    with open(filename) as f:
        artist_list = f.read().splitlines()
    artist_list = [entry for entry in artist_list if not entry == '']

    for artist in artist_list:
        download_list.extend(search_artist(artist))

    return download_list


if __name__ == '__main__':
    artist = 'ichiri'
    download_list = search_artist(artist)
