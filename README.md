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

## To-do list
- Add download_favorites
- Put favorites in separate folder or add a `favorite` tag for each favorited gallery?
- Add `.blacklisted_id.txt` in `inputs/` to skip download
- use Path for paths
- Download by author (put galleries with same title in `Repeated downloads` folder?) to automatically update downloaded galleries
- Automatically detect input file contains artist name or gallery id?
- Use only one input `download_list.txt` file and use '#' or 'tag:tag: or 'favorites' to separate different kind of inputs?
- Combine download_author.py and download_galleries.py into one file containing main() and put function definitions in new file
- Fix logger name in .log files
- Overwrite same gallery with newer one (determined from id or upload date)? No, keep all downloaded galleries
- Create new log file every time program is started
- Don't use TimeRotatingFileHandler (Implement automatic deletetion of old logs manually)
- Capture ctrl-c
- Download from mirror sites such as https://www2.hentai2.net/NUMBER_GOES_HERE.html or hitomi.la?
- Write folder name using NFC of NFD?
- Check download_dir settings in every function, and separate it into a new function
- download_list = search_tag() - find_tag()
- Add documentation, comments, ...
- Review entire code

- Add diagnosis? (total slept time, failed url percentage, ...)
- Truncate tqdm.write for long gallery titles with `self.title[:os.get_terminal_size().column] + '...'`?
- Is check_extra_pages needed?
- Is retry failed galleries needed?
- Ask whether to use tag and fileicon when starting program
- Check whether tag and fileicon has been installed
- Logging for confirm_settings()
- Add more settings in confirm_settings()
- Add yaml for each gallery in addition to json
- Log user termination of program
- Add another handler for printing std output (change most of the logger.info to logger.debug?)
- Check logger for unnecessary logs
