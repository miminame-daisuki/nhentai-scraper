import argparse


def cli_parser():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--update-cookies",
        help="Update cookies used for bypassing Cloudflare protection.",
        action="store_true",
    )

    parser.add_argument(
        "--confirm-settings",
        help="Confirm various settings: download location, ...",
        action="store_true",
    )

    parser.add_argument(
        "--skip-to-tag",
        help=(
            "Start download at the specified tag, "
            "skipping all previous tags in 'download_list.txt'"
        ),
    )

    parser.add_argument(
        "--redownload-downloaded",
        help=(
            "Start download at the specified tag, "
            "skipping all previous tags in 'download_list.txt'"
        ),
        action="store_true",
    )

    parser.add_argument(
        "--thumbnail",
        help="Set thumbnails to each downloaded gallery.",
        action="store_true",
        default=True,
    )

    parser.add_argument(
        "--tags",
        help="Set tags to each downloaded gallery.",
        action="store_true",
        default=True,
    )

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = cli_parser()
    print(args)
