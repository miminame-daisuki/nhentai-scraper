import os
import logging
import signal

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

    download_list = load_inputs.load_input_list('download_list.txt')
    blacklist = load_inputs.load_input_list('blacklist.txt')
    repeat_ids = load_inputs.load_input_list('repeated_galleries.txt')

    gallery_results = {
        'finished': [],
        'repeats': repeat_ids,
        'blacklists': blacklist,
        'initial_fails': [],
        'retry_fails': [],
    }

    for entry in download_list:

        # entry is `favorites` or a tag
        if entry == 'favorites' or ':' in entry:
            gallery_results_extend = download_tags.download_tag(
                entry, download_dir,
                skip_downloaded_ids=skip_downloaded_ids
            )

            if gallery_results_extend is None:
                continue

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
            logger.info(f"\n{'-'*os.get_terminal_size().columns}")
            logger.error(f'{entry} is neither a tag nor a gallery id')
            print(f'{entry} is neither a tag nor a gallery id')
            print(f"\n{'-'*os.get_terminal_size().columns}")

        if gallery_results['repeats']:
            download_galleries.write_gallery_results(
                gallery_results['repeats'], 'repeated_galleries.txt'
            )
        if gallery_results['blacklists']:
            download_galleries.write_gallery_results(
                gallery_results['blacklists'], 'blacklist.txt'
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
    signal.signal(signal.SIGINT, nhentai_scraper.exit_gracefully)
    main()
