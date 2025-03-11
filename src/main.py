import os
import logging
import signal
from functools import partial

import nhentai_scraper
import download_galleries
import download_tags
import load_inputs
import misc


logger = logging.getLogger(__name__)


def main():

    misc.set_logging_config()
    logger.info(f"\n{'-'*os.get_terminal_size().columns}")
    logger.info('Program started')

    settings = load_inputs.confirm_settings()
    download_dir = settings['download_dir']
    skip_downloaded_ids = settings['skip_downloaded_ids']
    skip_to_tag = settings['skip_to_tag']

    download_list = load_inputs.load_input_list(
        'download_list.txt', skip_to_tag=skip_to_tag
    )
    blacklist = load_inputs.load_input_list('blacklist.txt')
    repeat_ids = load_inputs.load_input_list('repeated_galleries.txt')

    session = nhentai_scraper.create_session()

    gallery_results = {
        'finished': [],
        'repeats': repeat_ids,
        'blacklists': blacklist,
        'initial_fails': [],
        'retry_fails': [],
    }

    signal.signal(
        signal.SIGINT,
        partial(download_galleries.exit_gracefully, gallery_results)
    )

    for entry in download_list:

        additional_tags = []
        if 'repeats' in download_list:
            additional_tags.append('repeats')

        # entry is `favorites`, `repeats`, or a tag
        if entry == 'favorites' or entry == 'repeats' or ':' in entry:

            if entry == 'favorites':
                additional_tags.append('favorites')

            gallery_results_extend = download_tags.download_tag(
                entry, download_dir,
                session,
                skip_downloaded_ids=skip_downloaded_ids,
                additional_tags=additional_tags,
            )

            if gallery_results_extend is None:
                print(f"{'-'*os.get_terminal_size().columns}")
                continue

            for key in gallery_results_extend:
                gallery_results[key].extend(gallery_results_extend[key])

        # entry is a gallery id
        elif '#' in entry:
            logger.info(f"\n{'-'*os.get_terminal_size().columns}")

            gallery = nhentai_scraper.Gallery(
                entry, session=session, download_dir=download_dir,
                additional_tags=additional_tags,
            )
            gallery.download()

            download_galleries.record_gallery_results(
                gallery_results, gallery, initial_try=True
            )

        else:
            logger.info(f"\n{'-'*os.get_terminal_size().columns}")
            logger.error(f'{entry} is neither a tag nor a gallery id')
            print(f'{entry} is neither a tag nor a gallery id')

        if gallery_results['repeats']:
            download_galleries.write_gallery_results(
                gallery_results['repeats'], 'repeated_galleries.txt'
            )
        if gallery_results['blacklists']:
            download_galleries.write_gallery_results(
                gallery_results['blacklists'], 'blacklist.txt'
            )

        print(f"{'-'*os.get_terminal_size().columns}")

    download_galleries.write_final_results(gallery_results)


if __name__ == '__main__':
    main()
