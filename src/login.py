import os
import nhentai_scraper
from tqdm import tqdm

from download_tags import get_gallery_ids


def get_favorites():
    favorites_url = 'https://nhentai.net/favorites/'

    application_folder_path = nhentai_scraper.get_application_folder_dir()
    inputs_dir = os.path.abspath(f'{application_folder_path}/inputs/')
    headers = nhentai_scraper.load_headers(inputs_dir)
    cookies = nhentai_scraper.load_cookies(inputs_dir)

    page_count = get_gallery_ids(
        favorites_url, headers=headers, cookies=cookies
    )[1]

    id_list = []

    if page_count is None:
        # logger.error(f'Failed to retrieve favorites')
        print(f'Failed to retrieve favorites')

        return id_list

    for page in tqdm(range(1, page_count+1), leave=False):
        # logger.info(f"Searching page {page} from favorites")
        page_url = favorites_url + f'?page={page}'
        gallery_id = get_gallery_ids(
            page_url,
            headers=headers, cookies=cookies
        )[0]

        if not gallery_id:
            # logger.error(f'Failed to retrieve id_list for page {page}')
            continue
        id_list.extend(gallery_id)


    return id_list

if __name__ == '__main__':
    get_favorites()
