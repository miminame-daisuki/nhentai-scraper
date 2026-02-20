# nHentai Scraper for macOS

[English](README.md) | 繁體中文

一個專為在macOS上容易使用而設計的[nHentai][nHentai.net]爬蟲／下載器。\
有任何問題或建議歡迎在[這裡][issues]提出～

懶人包請按[這裡](#懶人包)

## 功能

- 下載[nHentai上自己的favorites][favorites]或是使用者給定之本本id/tag/搜尋列表...
- 下載的本本可以儲存成資料夾（直接在macOS的Finder裡看）或是cbz壓縮檔（在伺服器上看）：
  - 以資料夾儲存後：
    - 縮圖和標籤會自動被設定在每本本本的資料夾上
    - 圖片會另存成一個PDF檔以方便閱讀
  - 以cbz壓縮檔儲存後：
    - 可以在[LANraragi][lanraragi]或是[Kavita][kavita]等自架伺服器上閱讀
- 下載時跳過使用者給定之黑名單
- 跳過已經完成下載的本本
- 支援下載相同名字（但id不同）的本本
- 支援在筆電闔上螢幕後繼續運行

## 安裝

### 下載Unix執行檔

1. 從[Releases][releases]下載最新的`.tgz`壓縮檔
1. 解壓縮

### 下載原始碼（會想這麼做的應該也看得懂英文，所以就不翻了（~~其實只是我懶~~））

1. Clone the GitHub repository by running
`git clone https://github.com/ecchi-na-no-wa-dame/nhentai-scraper.git`
in your terminal.
1. Move into the program directory with `cd nhentai-scraper`.
1. Create a virtual environment with `python -m venv venv`.
1. Activate the virtual environment with `source venv/bin/activate`.
1. Install dependencies with `pip install -r requirements.txt`.

## 基本用法

1. 依據你的安裝方法，執行程式的步驟為：
    - 從[Releases][releases]下載`.tgz`壓縮檔的人：
        - 如果你希望只在筆電螢幕掀開時執行，
        請點兩下`nhentai-scraper`執行檔。
        - 如果你希望在macbook闔上螢幕後繼續執行，
        請點兩下`nhentai-scraper_no_sleep.command`執行檔。

    - For people downloading cloning the repository:
        - If you want the program to run only when your computer is not sleeping,
        run `caffeinate -is python src/main.py` in your terminal.
        - If you want the program to continue to run
        even when the lid of your macbook is closed,
        run `python src/main.py`  in your terminal.

1. 第一次執行時會顯示預設設定。如果要改任何設定的話輸入'n'，反之輸入'y'。
1. 匯出包含繞過CloudFlare和Anubis所需要之cookies和headers的`.har`檔後
存在`inputs/`資料夾內。（Safari請參照[這些步驟](#繞過cloudflare和anubis保護)）
1. 依照下方其中一種方法輸入想下載的本本／標籤：
    - 在`inputs/`資料夾裡依照[這個格式](#範例inputs檔)新增一個`download_list.txt`檔
    - 輸入你想下載的本本id/標籤，用'; '來分隔
1. 依照下方其中一種方法輸入**不想**下載的本本／標籤：
    - 在`inputs/`資料夾裡依照[相同格式](#範例inputs檔)新增一個`blacklists.txt`檔
    - 輸入你**不想**下載的本本id/標籤，用'; '來分隔
1. 程式會自動產生一個`Downloaded/`資料夾來存放下載後的本本並開始下載
1. 要結束運行的話，按`Ctrl-c`

## 繞過CloudFlare和Anubis保護

1. 使用Safari打開[nHentai][nHentai.net]
1. 需要時通過CloudFlare CAPTCHA
1. 登入你的帳號
1. 從Safari選單列中的「開發」選單點選「顯示網頁原始碼」
（如果沒有看到「開發」選單的話請參照[這些步驟][Safari-Developer]）
1. 點選「網路」分頁後重新整理網頁
1. 點選右上角的「匯出」後儲存到與`nhentai-scraper`執行檔同位置下的`inputs/`資料夾內
（檔名維持預設之`nhentai.net.har`）

## 範例Inputs檔

`inputs/download_list.txt`和`inputs/blacklist.txt`都是按照相同格式。

```text
artist:<artist>
tag:<tag>
group:<group>
search:<search>
#114514
favorites
```

（':'後面不用加空格）

## 更新

### 更新Unix執行檔

1. 從[Releases][releases]下載最新的`.tgz`壓縮檔
1. 解壓縮
1. 把`nhentai-scraper` 執行檔跟`_internal` 資料夾用新的取代

### Updating the Source code

1. Move into the `nhentai-scraper` directory by `cd nhentai-scraper`.
1. Pull the newest commits by running `git pull`.

## 進階用法

- To run the program periodically, use `crontab` or `launchctl`.
  - For `crontab`, give `Full Disk Access` to `/usr/sbin/cron`
  in `System Preferences` (Or `System Settings` in newer macOS versions).

## 伺服器配合使用方法

### [LANraragi][lanraragi]

1. Go to `Settings` then click `Tags and Thumbnails`
1. Click `Generate Missing Thumbnails`
1. After generating missing thumbnails, click `Return to Library`
1. Go to `Batch Operations`
1. Select `Use Plugin` for `Task` and `ComicInfo` for `Use plugin`
1. Click `Check/Uncheck all` then `Start Task`
(This took around 0.5 seconds per gallery on my machine,
so you may need to wait a bit if you have a large library)
1. (Optional)Repeat the previous two steps, but change the `Use plugin` option to:
    - `Filename Parsing` if you want the filenames
    to only contain the title of the gallery
    - `nHentai` if you want the filenames
    to completely follow the format on [nHentai][nhentai.net]

## 使用程式的一些小技巧

- 如果一直出現'Error 403'的話，試著啟用／更改VPN
- 如果有些本本一直沒在LANraragi裡出現的話，試著重啟Docker container
- 如果要在Finder裡用標題搜尋下載後的本本的話，去掉括弧'[]'裡的部分
例：要搜尋'[artist]title'的話，直接打'title'
- 如果下載時即便某標籤內所有本本都有下載了卻仍然沒有跳過下載的話，
試著[重建Spotlight索引][reindex-spotlight]

## 懶人包

下載[nHentai上自己的favorites][favorites]：

1. 從[Releases][releases]下載最新的`.tgz`檔後解壓縮
1. 點兩下`nhentai-scraper`執行檔（會開啟macOS的終端機）
1. 畫面會顯示預設設定，輸入`y`後按`Enter`
1. 請參照[這些步驟](#繞過cloudflare和anubis保護)來繞過nHentai的CloudFlare和Anubis保護
1. 回到終端機後按`Enter`
1. 輸入`y`後按`Enter`
1. 輸入`favorites`後按`Enter`
1. 輸入`y`後按`Enter`
1. 再按一次`Enter`
1. 如果看到出現'Searching galleries from favorites: '以及後面的進度條就ok了！
1. 下載的本本會存在`Downloaded/`資料夾裡
1. 想停止下載的話按`Ctrl-c`, 之後要繼續下載時再點兩次`nhentai-scraper`執行檔

## FAQ

### Q:為什麼是爬[n站][nHentai.net]而不是[熊貓][ehentai.org]？

這其實有幾個原因（這些只是我個人粗淺的認知，如有錯誤歡迎指正）：

- 有些本本在熊貓被版權砲後還有機會在n站找到
- 對於iOS使用者來說，在不使用Sideloading或越獄等手段的前提下，
n站的存取方便性和UI設計遠優於熊貓
- 對n站用的很久且累積了不少favorites的人來說，要遷移到熊貓可能不太容易

[nHentai.net]: https://nhentai.net
[favorites]: https://nhentai.net/favorites/
[releases]: https://github.com/ecchi-na-no-wa-dame/nhentai-scraper/releases
[issues]: https://github.com/ecchi-na-no-wa-dame/nhentai-scraper-macOS/issues
[Safari-Developer]: https://support.apple.com/zh-tw/guide/safari/sfri20948/mac
[lanraragi]: https://github.com/Difegue/LANraragi
[kavita]: https://github.com/Kareadita/Kavita
[ehentai.org]: https://e-hentai.org
[reindex-spotlight]: https://support.apple.com/zh-tw/102321
