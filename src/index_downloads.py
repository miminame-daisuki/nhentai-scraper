import csv
import json

import misc


def index_downloads():

    downloads = []

    download_dir = misc.set_download_dir()

    for child in download_dir.iterdir():
        if child.name == '.DS_Store' or child.name == 'index.csv':
            continue
        with open(child / "metadata.json", "r") as f:
            metadata = json.load(f)
        if metadata["title"]["japanese"]:
            metadata["title"] = metadata["title"]["japanese"]
        else:
            metadata["title"] = metadata["title"]["english"]
        metadata.pop("tags", None)
        metadata.pop("images", None)
        downloads.append(metadata)

    keys = downloads[0].keys()
    with open(download_dir / "index.csv", "w") as f:
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writeheader()
        dict_writer.writerows(downloads)

    return downloads


if __name__ == "__main__":
    downloads = index_downloads()
