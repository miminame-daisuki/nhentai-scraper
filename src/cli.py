import argparse


def cli_parser():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--update-cookies",
        action="store_true",
        help=(
            "Update headers and cookies used for "
            "bypassing Cloudflare and Anubis protection."
        ),
    )

    parser.add_argument(
        "--download_dir",
        type=str,
        help=(
            "Set the directory for the folder "
            "containing all the downloaded galleries."
        ),
    )

    parser.add_argument(
        "--filetype",
        choices=['folder', 'cbz'],
        help=(
            "Set the filetype for the downloaded galleries "
        ),
    )

    parser.add_argument(
        "--server",
        choices=['LANraragi', 'Kavita'],
        help=(
            "Set the server name for viewing the downloaded galleries, "
            "only valid with '--filetype cbz' "
        ),
    )

    parser.add_argument(
        "--set-thumbnail",
        action="store_true",
        help=(
            "Set thumbnail to the folders of the downloaded galleries, "
            "only valid with '--filetype folder'."
        ),
    )

    parser.add_argument(
        "--set-tags",
        action="store_true",
        help=(
            "Set tags to the folders of the downloaded gallery, "
            "only valid with '--filetype folder'."
        ),
    )

    parser.add_argument(
        "--check-downloaded",
        action="store_true",
        help="Recheck all downloaded galleries for missing pages.",
    )

    parser.add_argument(
        "--skip-to-tag",
        type=str,
        help=(
            "Start download at the specified tag, "
            "skipping all previous tags in 'download_list.txt'."
        ),
    )

    parser.add_argument(
        "--confirm-settings",
        action="store_true",
        help="Prints all runtime settings for confirmation.",
    )

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = cli_parser()
    print(f'{args = }')
