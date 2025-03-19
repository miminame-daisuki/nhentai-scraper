# NHentai Scraper
[English](https://github.com/miminame-daisuki/nhentai-scraper/blob/main/README.md) | 繁體中文

一個nhentai的爬蟲。啊啊啊我還沒把這部分翻譯成中文，如果有人急了.jpg的話可以在issues那邊留言，我盡快幫你～

## To-do
- Update README
- Output and print initial_fails when initial_try = False?
- How to download repeats for favorites?
- Replace 'tags' and 'fileicon' with pure python code
- EOF error?

- Package python scripts (into command line scripts?) instead of using pyinstaller
- Use async to send requests to all mirrors (i1, i2, i3, ...) to download with the one that has the fastest response
- Add colors to terminal output
- Continue download pages when error in downloading thumbnail?
- Fix tqdm (progress bar disappearing) when retrying failed pages
- Automatically load blacklist tags from nhentai user page
- Add helper functions (export id of favorites, print id of downloaded galleries, compare difference between favorites (or any tag) on nhentai.com and local downloads, ...)
- Separate settings (ex: download wait time) to another .txt file
- Make thumbnails and tags optional
- Update list of downloaded galleries to txt file
- Print # of new repeats and blacklists not downloaded during this session in write_final_results()?
- Add whether to put gallery id in folder name to settings?
- Release memory after each gallery download?

- Print name of program when starting?
- Replace os with Path
- Add blank after : in tags
- Use async?
- Rewrite logs for more readibility?
- Automatically delete old logs?
- Regenerate `requirements.txt` and `environment.yml`
- Add tests
- Add documentation
