import argparse


def cli_parser():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--update-cookies",
        help="Update cookies used for bypassing Cloudflare protection",
        action="store_true",
    )
    parser.add_argument(
        "--confirm-settings",
        help="Confirm various settings: download location, ...",
        action="store_true",
    )

    args = parser.parse_args()

    return args

if __name__ == '__main__':
    args = cli_parser()
