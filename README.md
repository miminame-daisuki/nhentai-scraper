# NHentai scraper
Scraper/Downloader for [nhentai](https://nhentai.net), specifically designed for MacOS

## Features
- Automatically sets thumbnail and tags to folder for each gallery
- Combines downloaded images into pdf
- Downloads from a user-given list of gallery ids or tags/artists/groups/parodies...
- Supports user-defined blacklists for downloads
- Supports running when in sleep

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
2. Open your browser, find the cookies and headers (for bypassing CloudFlare), and put those in the `cookies.json` and `headers.json` files inside `inputs/`
3. Double click the `no_sleep.command` file in the `src/` folder

## Tips
- To search for downloaded galleries by title, don't include the parts in the paranthesis `[]`. Ex: To search for `[artist] title`, simply type `title`.
