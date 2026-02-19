# To-do

- Dynamically create ComicInfo.xml and config.yaml instead of loading from templates
- Update README
- Output and print initial_fails when initial_try = False?
- How to download repeats for favorites
(with additional_tags = ['favorites', 'repeats'])?
- 'EOFError' happening at the end of terminal output?
- Add print result when # of downloaded galleries
= # of repeats = # blacklists = 0
- Make sure metadata.json exists when running Gallery.load_downloaded_metadata()
- Add warning for empty download_list.txt
- Add Docker container
- Add doc for nhentai api

- Check pyright errors
- Add ability to toggle thumbnail and tags
- How to detect individual corrupted images in a gallery
and automatically redownload them?
- Add tqdm for total progress?
- Release memory after each gallery download?
- Package python scripts (into command line scripts?) instead of using pyinstaller
- Use async to send requests to all mirrors (i1, i2, i3, ...)
to download with the one that has the fastest response
- Add colors to terminal output
- Continue download pages when error in downloading thumbnail?
- Fix tqdm (progress bar disappearing) when retrying failed pages
- Automatically load blacklist tags from nhentai user page
- Add helper functions
(export id of favorites,
print id of downloaded galleries,
compare difference between favorites (or any tag) on nhentai.com and local downloads,
tags statistics for downloaded galleries, ...)
- Separate settings (ex: download wait time) to another .txt file
- Make thumbnails and tags optional
- Update list of downloaded galleries to txt file
- Print # of new repeats and blacklists not downloaded during this session
in write_final_results()?
- Add whether to put gallery id in folder name to settings?
- Add periods and () around plural s
- Add line number to logs

- Replace os with Path
- Add blankspace after : in tags
- Use async?
- Rewrite logs for more readibility?
- Regenerate `requirements.txt` and `environment.yml`
- Add tests
- Add documentation
