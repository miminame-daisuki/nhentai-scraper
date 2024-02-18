# NHentai scraper
Scraper/Downloader for [nhentai](https://nhentai.net), specifically designed for MacOS

## Features
- Automatically sets thumbnail and tags to folder for each gallery
- Combines downloaded images into pdf

## Dependencies
- [fileicon](https://github.com/mklement0/fileicon)
- [tag](https://github.com/jdberry/tag)

## Usage
1. Place the id of the galleries you want to download in the file `download_list.txt` inside the folder `inputs/`
2. Double click the `double_click_run.command` file in the `src/` folder


- Failed when retrieving thumbnail
- Use different mirrors (i3, i5, i7, ...) when status code = 404
- Add tmux
- Add diagnosis? (total slept time, failed url percentage, ...)
- Same title already downloaded, different contents?
- Output failed_pages and pages_url for each failed_gallery_url
- Is check_extra_pages needed?
- Show current progress and estimate remaining time

- fileicon: ERROR: Target not found or neither file nor folder: '../Downloaded/[たかやKi] ドキ2 Xmas'
- Can't search ssd by tag (because of file system not being MacOS Extended?)
- Add img2pdf to Gallery class (and check the part separated by alot of blank lines)
