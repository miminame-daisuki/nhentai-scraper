import os
import logging

import nhentai_scraper
import download_galleries
import download_tags


logger = logging.getLogger(__name__)


def main():

    nhentai_scraper.set_logging_config()
    logger.info('Program started')
    download_dir = download_galleries.confirm_settings()

    tag_list = nhentai_scraper.load_input_list('download_tags.txt')
    failed_galleries = download_tags.download_tags(
        tag_list,
        download_dir
    )

    if len(failed_galleries['repeated_galleries']) != 0:
        download_galleries.write_failed_galleries(
            failed_galleries['repeated_galleries'], 'repeated_galleries.txt'
        )
    if len(failed_galleries['failed_retry_galleries']) != 0:
        download_galleries.write_failed_galleries(
            failed_galleries['failed_retry_galleries'],
            'failed_download_id.txt'
        )
    else:
        print('\n\nFinished all downloads!!!\n\n')
        logger.info(f"\n{'-'*os.get_terminal_size().columns}")
        logger.info('Finished all downloads')


if __name__ == '__main__':
    main()
