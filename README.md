# NHentai Scraper
English | [繁體中文](https://github.com/miminame-daisuki/nhentai-scraper/blob/main/README_zh-TW.md)

Scraper/Downloader for [nhentai](https://nhentai.net), specifically designed for MacOS.

## Features
- Automatically sets thumbnail and tags to folder for each gallery.
- Combines downloaded images into pdf.
- Downloads from a user-given list of gallery ids or searches/tags/artists/groups/parodies...
- Can also download from [Favorites on nhentai](https://nhentai.net/favorites/).
- Prevents downloads from user-defined blacklists.
- Skips already-downloaded galleries.
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
1. Create a file called `download_id.txt` inside the folder `inputs/`, and place the gallery id/ tag name/ artist name ... you wish to download in the file, separated by line breaks.  
Example:
```
artist:
tag:
group:
search:
#
```

2. (Optional) Create another file called `blacklist.txt` inside the `inputs/` folder, and place the list of tags you want to avoid downloading, separated by line breaks.  
Example:
```
tag:yaoi
tag:males only
```

3. Find your cookies and headers with your browser of choice for bypassing CloudFlare.  
Example using Safari:
    1. Go to [nhentai](https://nhentai.net).
    1. (Optional) Log in to your account (only necessary if you wish to download your favorites).
    1. Clear the CloudFlare captcha.
    1. From the `Develop` menu, click on `Show Web Inspector`. (Follow [these steps](https://developer.apple.com/documentation/safari-developer-tools/enabling-developer-features) if you haven't enabled it.)
    1. Select `nhentai.net` in the `Name` column. It should be displaying almost nothing (except for the `https://nhentai.net/` url in the `URL` line under the `Summary` section).
    1. Reload the page.
    1. Repeat Step 3-iv., except that it should be displaying a lot more information this time.
    1. Locate `Cookie` and `User-Agent` under the `Request` section.

4. Depending on your installation, execute the program either by:
    - Double clicking the `main` unix executable file.
    - Running `python main.py` (located in the `src/` folder) in your terminal.  

- If you want the program to continue to run even when the computer is in sleep, do either of the following instead:
    - Double click the `main_no_sleep.command` file in the `src/` folder
    - Run `caffeinate python main.py` inside the `src/` folder.

5. Follow the instructions, and copy-paste your cookies & user agent from Step 3. when prompted.

6. The program will automatically create a `Downloaded/` folder for the downloaded galleries and begin download.

7. To end the program, simply press `Ctrl-c`.

8. The next time you start the program, it will continue to download any unfinished galleries.

## Some Tips when Using the Program
- [Reindex spotlight](https://support.apple.com/en-us/102321) if it is not skipping a praticular tag, even though all galleries from the tag have already been downloaded. 
- Use/Change VPN if constantly getting Error 403.
- To search for downloaded galleries by title, don't include the parts in the paranthesis `[]`. Ex: To search for `[artist] title`, simply type `title`.
