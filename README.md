# NHentai scraper
Scraper/Downloader for [nhentai](https://nhentai.net), specifically designed for MacOS

## Features
- Automatically sets thumbnail and tags to folder for each gallery
- Combines downloaded images into pdf

## Dependencies
- [fileicon](https://github.com/mklement0/fileicon)
- [tag](https://github.com/jdberry/tag)

## Basic Usage
1. Place the id (six digit number) of the galleries you want to download in the file `download_list.txt` inside the folder `inputs/`
2. Open your browser, find the cookies and headers (for bypassing CloudFlare), and put those in the `cookies.txt` and 'headers.txt` files inside `inputs`
3. Double click the `double_click_run.command` file in the `src/` folder

- use logging
- use requests.get(timeout=61)
- use progressbar or tqdm
- use Path for paths
- Failed when retrieving thumbnail
- Add check whether same title, different language has been downloaded or not (using split('[')?)
- Download by author (download all galleries?, even the ones the same title by using title-1, title-2 for example?) to automatically update downloaded galleries

- Confiem cf_clearance before execution
- Use different mirrors (i3, i5, i7, ...) when status code = 404
- Add tmux
- Add diagnosis? (total slept time, failed url percentage, ...)
- Same title already downloaded, different contents?
- Output failed_pages and pages_url for each failed_gallery_url
- Is check_extra_pages needed?
- Show current progress and estimate remaining time

- fileicon: ERROR: Target not found or neither file nor folder: '../Downloaded/[たかやKi] ドキ2 Xmas'
