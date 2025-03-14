# NHentai Scraper
English | [繁體中文](https://github.com/miminame-daisuki/nhentai-scraper/blob/main/README_zh-TW.md)

Scraper/Downloader for [nhentai](https://nhentai.net), designed for ease of use on MacOS.\
Feel free to ask about any difficulties you are facing [here](https://github.com/miminame-daisuki/nhentai-scraper/issues)!

## Features
- Automatically sets thumbnail and tags to folder for each gallery.
- Combines downloaded images into a single PDF file.
- Downloads from a user-given list of gallery ids or searches/tags/artists/groups/parodies...
- Can also download from [Favorites on nhentai](https://nhentai.net/favorites/).
- Prevents downloads from user-defined blacklists.
- Skips already-downloaded galleries.
- Can also skip over galleries with the same title.
- Supports running while computer is in sleep.

## Dependencies
### CLI Dependencies
- [fileicon](https://github.com/mklement0/fileicon)
- [tag](https://github.com/jdberry/tag)

### Python Dependencies
- [Requests](https://pypi.org/project/requests/)
- [Beautiful Soup 4](https://pypi.org/project/beautifulsoup4/)
- [Pillow](https://pypi.org/project/pillow/)
- [pypdf](https://pypi.org/project/pypdf/)
- [tqdm](https://github.com/tqdm/tqdm)
-

## Installation
### Unix executable (only requires the [CLI dependencies](#cli-dependencies))
- Download the unix executable from [Releases](https://github.com/miminame-daisuki/nhentai-scraper/releases).
### Source code (requires both the [CLI](#cli-dependencies) and the [Python dependencies](#python-dependencies))
- Run `git clone https://github.com/miminame-daisuki/nhentai-scraper` in your terminal.

## Basic Usage
1. (For people downloading from [Releases](https://github.com/miminame-daisuki/nhentai-scraper/releases)) Create a folder with the name `inputs/` at the location of the `main` unix executable file.

1. Create a file called `download_list.txt` inside the folder `inputs/`, and place the gallery id/tag name/artist name ... you wish to download in the file, separated by line breaks.\
Example `download_list.txt`:
    ```
    artist:
    tag:
    group:
    search:
    #114514
    ```

1. (Optional) Add `repeats` to `download_list.txt` if you wish to download repeated galleries (i.e. galleries with the same title as the already downloaded ones, but with different ids)

1. (Optional) Create another file called `blacklist.txt` inside the `inputs/` folder, and place the list of tags you want to avoid downloading, separated by line breaks.\
Example `blacklist.txt`:
    ```
    tag:yaoi
    tag:males only
    ```

1. Find your cookies and headers with your browser of choice for bypassing CloudFlare.
Example using Safari:
    1. Go to [nhentai](https://nhentai.net).
    1. (Optional) Log in to your account (only necessary if you wish to download your favorites).
    1. Clear the CloudFlare captcha.
    1. From the `Develop` menu, click on `Show Web Inspector`. (Follow [these steps](https://developer.apple.com/documentation/safari-developer-tools/enabling-developer-features) if you haven't enabled it.)
    1. Select `nhentai.net` in the `Name` column. It should be displaying almost nothing (except for the `https://nhentai.net/` url in the `URL` line under the `Summary` section).
    1. Reload the page.
    1. Repeat Step 3-iv. This time it should be displaying a lot more information.
    1. Locate `Cookie` and `User-Agent` under the `Request` section.

1. Depending on your installation, execute the program either by:
    - Double clicking the `main` unix executable file.
    - Running `python main.py` (located in the `src/` folder) in your terminal.

    - (Do either of the following instead if you want the program to continue to run even when the computer is in sleep):
        - Double click the `main_no_sleep.command` file. 
        - Run `caffeinate python main.py` inside the `src/` folder.

1. Follow the instructions, and copy-paste your cookies & user agent from Step 3. when prompted.

1. The program will automatically create a `Downloaded/` folder for the downloaded galleries and begin download.

1. Confirm the download folder location when asked `Download to /your/download/folder/location?(y/n)` by either typing `y` or `n` then `Enter`.

1. To end the program, simply press `Ctrl-c`.

1. The next time you start the program, it will prompt the folloing questions:
    1. `Download to /your/download/folder/location?(y/n)`: Confirm download location by typing `y` or `n` then `Enter`.
    1. `Update cookies?(y/n)`: Go to [nhentai](https://nhentai.net) and see if you need to update your cookies for bypassing CloudFlare.
    1. `Skip downloaded galleries?(y/n)`: If `y`, the program will skip over entries in the `download_list.txt` if every gallery belonging to the entry is already downloaded.
    1. `Skip to tag?(Press Enter for no skip)`: If you wish to start downloading from where your last session ended, enter the name of the last unfinished entry from your last session (ex: if you stopped the program while it was downloading 'tag:aaa', then type 'tag:aaa' then `Enter`). The program should resume the download process.

## Some Tips when Using the Program
- [Reindex spotlight](https://support.apple.com/en-us/102321) if it is not skipping a praticular tag, even though all galleries from the tag have already been downloaded. 
- Use/Change VPN if constantly getting Error 403.
- To search for downloaded galleries by title in Finder, don't include the parts in the paranthesis `[]`. Ex: To search for `[artist] title`, simply type `title`.
