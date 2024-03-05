from bs4 import BeautifulSoup
import os
import logging

import nhentai_scraper
import download_galleries


logger = logging.getLogger(__name__)


def get_gallery_id(url, headers={}, cookies={}):
    # retrieves all <=25 gallery ids from a nhentai url

    gallery_id = []

    response = nhentai_scraper.get_response(url,
                                            headers=headers,
                                            cookies=cookies)
    soup = BeautifulSoup(response.content, features='html.parser')
    gallery_count = soup.find('span', {'class': 'count'}).string
    page_count = int(gallery_count)//25 + 1
    gallery_list = soup.find_all('div', {'class': 'gallery'})
    for gallery in gallery_list:
        gallery_id.append(gallery.find('a').get('href').split('/')[2])

    return gallery_id, page_count


# retrieves all gallery ids from a artist
def search_artist(artist: str):

    print(f'\nSearching galleries from artist {artist}')
    artist_url = f'https://nhentai.net/artist/{artist}/'
    application_folder_path = nhentai_scraper.get_application_folder_dir()
    inputs_dir = os.path.abspath(f'{application_folder_path}/inputs/')
    headers = nhentai_scraper.load_headers(inputs_dir)
    cookies = nhentai_scraper.load_cookies(inputs_dir)
    id_list, page_count = get_gallery_id(artist_url,
                                         headers=headers,
                                         cookies=cookies)

    for page in range(2, page_count+1):
        page_url = artist_url + f'?page={page}'
        id_list.extend(get_gallery_id(page_url,
                                      headers=headers,
                                      cookies=cookies)[0])

    return id_list


def load_artist_list():
    application_folder_path = nhentai_scraper.get_application_folder_dir()
    inputs_folder_dir = os.path.abspath(f'{application_folder_path}/inputs/')
    filename = f'{inputs_folder_dir}/download_artist.txt'
    with open(filename) as f:
        artist_list = f.read().splitlines()
    artist_list = [entry for entry in artist_list if not entry == '']

    return artist_list


def main():
    nhentai_scraper.set_logging_config()
    logger.info('Program started')
    download_dir = download_galleries.confirm_settings()
    artist_list = load_artist_list()
    failed_retry_galleries = []
    for artist in artist_list:
        try:
            id_list = search_artist(artist)
        except Exception as error:
            logger.error(f'{error}')
            continue
        failed_retry_galleries.extend(
            download_galleries.download_id_list(id_list, download_dir)
        )
    download_galleries.check_failed_retry_galleries(failed_retry_galleries)


if __name__ == '__main__':
    main()
