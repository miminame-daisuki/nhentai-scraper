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
    logger.info(f"\n{'-'*80}")
    logger.info("Program started")

    settings = load_inputs.generate_runtime_settings()
    download_dir = settings["downloads"]["download_dir"]
    check_downloaded = settings["runtime"]["check-downloaded"]
    skip_to_tag = settings["runtime"]["skip-to-tag"]

    download_list = load_inputs.load_input_list(
        "download_list.txt", skip_to_tag=skip_to_tag
    )
    blacklist = load_inputs.load_input_list("blacklist.txt")
    repeat_ids = load_inputs.load_input_list("repeated_galleries.txt")

    misc.print_start_message(download_dir)

    session = nhentai_scraper.create_session(
        cookie_dict=load_inputs.load_nhentai_Cookie(),
        headers_dict=load_inputs.load_nhentai_headers(),
    )

    gallery_results = misc.create_gallery_results_dict(repeat_ids, blacklist)

    signal.signal(
        signal.SIGINT,
        partial(download_galleries.exit_gracefully, gallery_results),
    )

    for entry in download_list:

        additional_tags = []

        # entry is `favorites`, `repeats`, or a tag
        if entry == "favorites" or entry == "repeats" or ":" in entry:

            if entry in blacklist:
                print(f"\nBLACKLISTED {entry}.\n")
                print("\u2500" * misc.get_separation_line_width())
                continue

            if entry == "favorites":
                additional_tags.append("favorites")

            gallery_results_extend = download_tags.download_tag(
                entry,
                download_dir,
                session,
                filetype=settings["downloads"]["filetype"],
                server=settings["downloads"]["server"],
                check_downloaded=check_downloaded,
                additional_tags=additional_tags,
                gallery_results=gallery_results,
            )

            if gallery_results_extend is None:
                continue

        # entry is a gallery id
        elif "#" in entry:
            logger.info(f"\n{'-'*80}")

            gallery = nhentai_scraper.Gallery(
                entry,
                filetype=settings["downloads"]["filetype"],
                server=settings["downloads"]["server"],
                session=session,
                download_dir=download_dir,
                additional_tags=additional_tags,
            )
            gallery.download()

            download_galleries.record_gallery_results(
                gallery_results, gallery, initial_try=True
            )

        else:
            logger.info(f"\n{'-'*80}")
            logger.error(f"{entry} is neither a tag nor a gallery id")
            print(f"{entry} is neither a tag nor a gallery id.")

        if gallery_results["repeats"]:
            download_galleries.write_gallery_results(
                gallery_results["repeats"], "repeated_galleries.txt"
            )
        if gallery_results["blacklists"]:
            download_galleries.write_gallery_results(
                gallery_results["blacklists"], "blacklist.txt"
            )

        print("\u2500" * misc.get_separation_line_width())

    download_galleries.write_final_results(gallery_results)


if __name__ == "__main__":
    main()
