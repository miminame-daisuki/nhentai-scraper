# NHentai Scraper
[English](https://github.com/miminame-daisuki/nhentai-scraper/blob/main/README.md) | 繁體中文

一個nhentai的爬蟲。啊啊啊我還沒把這部分翻譯成中文，如果有人急了.jpg的話可以在issues那邊留言，我盡快幫你～

## To-do
- Remove #559950 from blacklist after fixing above bug
- Check why error when downloading thumbnail (happens when title contains '"'?)
- Print download failed tags
- Replace 'tags' and 'fileicon' with pure python code
- Download repeated galleries
- Retry Error 500

- Update README
- Use async to send requests to all mirrors (i1, i2, i3, ...) to download with the one that has the fastest response
- Add colors to terminal output
- Continue download pages when error in downloading thumbnail?
- EOF error?
- Fix tqdm (progress bar disappearing) when retrying failed pages
- Automatically load blacklist tags from nhentai user page
- Output ids of successfully downloaded galleries to log?
- Add helper functions (export id of favorites, print id of downloaded galleries, compare difference between favorites (or any tag) on nhentai.com and local downloads, ...)
- Update list of downloaded galleries to txt file?
- Separate internal settings (ex: download wait time) to another .py file
- Print 'N repeadted galleries not downloaded', 'N blacklisted', 'N failed retry galleries' only when N > 0
- Make thumbnails and tags optional
- Automatically add tags to 'already downloaded' galleries

- Print name of program when starting?
- Replace os with Path
- Add blank after : in tags
- Use async?
- Rewrite logs for more readibility?
- Automatically delete old logs
- Regenerate `requirements.txt` and `environment.yml`
- Add tests
- Add documentation
