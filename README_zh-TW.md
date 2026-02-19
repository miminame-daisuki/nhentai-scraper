# NHentai Scraper for MacOS

[English](README.md) | 繁體中文

一個專為在MacOS上容易使用而設計的[nHentai][nHentai.net]爬蟲／下載器。
有任何問題或建議歡迎在[這裡][issues]提出～

## 懶人包（以下載[nHentai上自己的favorites][favorites]為例）

1. 從[Releases][releases]下載最新的`.tgz`檔後解壓縮
1. 點兩下`main`執行檔（`終端機`會開啟一個新視窗）
1. 畫面會顯示預設設定，輸入`y`後按`Enter`
1. 輸入`favorites`後按`Enter`
1. 再按一次`Enter`
1. 使用Safari登入[nHentai][nHentai.net]
1. 從Safari選單列中的「開發」選單點選「顯示網頁原始碼」
（如果沒有看到「開發」選單的話請參照[這些步驟][Safari-Developer]）
1. 點選「網路」分頁後重新整理網頁
1. 點選右上角的「匯出」後儲存到與`main`執行檔同位置下的`inputs/`資料夾內
（檔名維持預設之`nhentai.net.har`）
1. 回到終端機後按`Enter`
1. 如果看到出現'Searching galleries from favorites: '以及後面之進度條就ok了
1. 下載的本本會存在`Downloaded/`資料夾裡
1. 想停止下載的話按`Ctrl-c`, 之後要繼續下載時再點兩次`main`執行檔

[nHentai.net]: https://nhentai.net
[favorites]: https://nhentai.net/favorites/
[releases]: https://github.com/ecchi-na-no-wa-dame/nhentai-scraper/releases
[issues]: https://github.com/ecchi-na-no-wa-dame/nhentai-scraper-MacOS/issues
[Safari-Developer]: https://support.apple.com/zh-tw/guide/safari/sfri20948/mac
