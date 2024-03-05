# NHentai scraper
Scraper/Downloader for [nhentai](https://nhentai.net), specifically designed for MacOS

## Features
- Automatically sets thumbnail and tags to folder for each gallery
- Combines downloaded images into pdf
- Downloads from a user-given list of gallery ids or tags/artists/groups/parodies...

## Dependencies
- [fileicon](https://github.com/mklement0/fileicon)
- [tag](https://github.com/jdberry/tag)

## Basic Usage
1. Place the id (six digit number) of the galleries you want to download in the file `download_id.txt` inside the folder `inputs/`
1. 
Example:
```
artist/
tag/
group/
```
2. Open your browser, find the cookies and headers (for bypassing CloudFlare), and put those in the `cookies.txt` and `headers.txt` files inside `inputs/`
3. Double click the `double_click_run.command` file in the `src/` folder

## To-do list
- use progressbar or tqdm to show current progress and estimate remaining time
- use Path for paths
- Failed when retrieving thumbnail
- Download by author (download all galleries?, even the ones the same title by using title-1, title-2 for example?) to automatically update downloaded galleries
- Automatically detect input file contains artist name or gallery id?
- Combine download_author.py and download_galleries.py into one file containing main() and put function definitions in new file
- Separate galleries with same title already downloaded from failed_galleries

- Add diagnosis? (total slept time, failed url percentage, ...)
- Same title already downloaded, different contents?
- Is check_extra_pages needed?
- Ask whether to use tag and fileicon when starting program
- Add error handling for galleries that have been deleted from nhentai
- Logging for confirm_settings()
- Add more settings in confirm_settings()
- Add yaml for each gallery in addition to json

- fileicon: ERROR: Target not found or neither file nor folder: '../Downloaded/[たかやKi] ドキ2 Xmas'
