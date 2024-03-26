import os
import logging

import nhentai_scraper
import download_galleries
import download_tags


logger = logging.getLogger(__name__)


def main():

    nhentai_scraper.set_logging_config()
    logger.info('Program started')

    settings = download_galleries.confirm_settings()
    download_dir = settings['download_dir']
    skip_downloaded_ids = settings['skip_downloaded_ids']

    download_list = nhentai_scraper.load_input_list('download_list.txt')
    blacklist_list = nhentai_scraper.load_input_list('blacklist_id.txt')
    repeats_list = nhentai_scraper.load_input_list('repeated_galleries.txt')

    gallery_results = {
        'finished': [],
        'repeats': repeats_list,
        'blacklists': blacklist_list,
        'initial_fails': [],
        'retry_fails': [],
    }

    for entry in download_list:

        # entry is `favorites` or a tag
        if entry == 'favorites' or ':' in entry:
            id_list = download_tags.search_tag(entry)
            matched_galleries_id = download_tags.search_finished_downloads(
                entry, download_dir=download_dir
            )

            # only keep not yet finished downloaded ids in id_list
            if skip_downloaded_ids:
                id_list = list(
                    set(id_list)
                    - set(matched_galleries_id)
                    - set(blacklist_list)
                    - set(repeats_list)
                )

            # Failed to retrieve id_list
            if id_list is None:
                continue

            elif not id_list:
                print(
                    f'All galleries from {entry} have already been downloaded.'
                )
                print(f"\n{'-'*os.get_terminal_size().columns}")
                logger.info(
                    f'All galleries from {entry} has already been downloaded.'
                )
                continue

            if entry == 'favorites':
                additional_tags = 'favorites'
            else:
                additional_tags = None

            logger.info(f'Start downloading for {entry}')
            gallery_results_extend = download_galleries.download_id_list(
                id_list, download_dir,
                additional_tags=additional_tags, id_list_name=entry
            )

            for key in gallery_results:
                gallery_results[key].extend(gallery_results_extend[key])

        # entry is a gallery id
        elif '#' in entry:
            logger.info(f"\n{'-'*os.get_terminal_size().columns}")
            gallery = nhentai_scraper.Gallery(
                entry, download_dir=download_dir
            )
            gallery.download()

            download_galleries.record_gallery_results(
                gallery_results, gallery, initial_try=True
            )

        else:
            print(f'{entry} is neither a tag nor a gallery id')
            print(f"\n{'-'*os.get_terminal_size().columns}")
            logger.error(f'{entry} is neither a tag nor a gallery id')

        if gallery_results['repeats']:
            download_galleries.write_gallery_results(
                gallery_results['repeats'], 'repeated_galleries.txt'
            )
        if gallery_results['blacklists']:
            download_galleries.write_gallery_results(
                gallery_results['blacklists'], 'blacklist_id.txt'
            )

    if gallery_results['retry_fails']:
        download_galleries.write_gallery_results(
            gallery_results['retry_fails'],
            'failed_download_id.txt'
        )
    else:
        print('\n\nFinished all downloads!!!\n\n')
        logger.info(f"\n{'-'*os.get_terminal_size().columns}")
        logger.info('Finished all downloads')


if __name__ == '__main__':
    main()
