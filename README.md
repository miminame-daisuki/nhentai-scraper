# nHentai Scraper for macOS

English | [繁體中文](README_zh-TW.md)

Scraper/Downloader for [nHentai][nhentai.net],
designed for ease of use on macOS.\
Feel free to ask about any difficulties you are facing
or offer any suggestions [here][issues]!

Click [here](#tldr) for TL;DR.

## Features

- Downloads from [your favorites on nhentai.net][favorites]
or a user-given list of gallery ids/tags/searches...
- Galleries can be saved either as folders (directly viewed by macOS Finder)
or cbz archives (viewed on servers):
  - By saving as folders:
    - Thumbnail and tags are automatically set to the folder for each gallery.
    - Images are combined into a single PDF file for easier viewing.
  - By saving as cbz archives:
    - Galleries may be viewed on servers
    such as [LANraragi][lanraragi] and [Kavita][kavita].
- Prevents downloads from user-defined blacklists.
- Skips over already-downloaded galleries.
- Supports skipping over galleries with the same title (but with different ids).
- Supports running while computer is in sleep with lid closed.

## Installation

### Downloading the Unix Executable File

1. Download the newest `.tgz` archive from [Releases][releases].
1. Extract the downloaded `.tgz` archive.

### Downloading the Source Code

1. Clone the GitHub repository by running
`git clone https://github.com/ecchi-na-no-wa-dame/nhentai-scraper.git`
in your terminal.
1. Move into the program directory with `cd nhentai-scraper`.
1. Create a virtual environment with `python -m venv venv`.
1. Activate the virtual environment with `source venv/bin/activate`.
1. Install dependencies with `pip install -r requirements.txt`.

## Basic Usage

1. Depending on your installation, execute the program either by:
    - For people downloading the Unix executable file:
        - If you want the program to only run when your computer is awake,
        double click the `nhentai-scraper` executable.
        - If you want the program to continue to run
        even when the lid of your macbook is closed,
        double click the `nhentai-scraper.command` file.
    - For people cloning the repository:
        - If you want the program to only run when your computer is awake,
        run `python src/main.py`  in your terminal.
        - If you want the program to continue to run
        even when the lid of your macbook is closed,
        run `caffeinate -is python src/main.py` in your terminal.
1. For the first run, the program will print out the default settings.
Enter 'n' if you want to change any of the settings. Otherwise, enter 'y'.
1. Export your cookies and headers for bypassing Cloudflare and Anubis
in an `.har` file and save it to the `inputs/` folder.
(Follow [these steps](#bypassing-cloudflare-and-anubis-protections)
for Safari.)
1. Specify the galleries you wish to download either by:
    - Enter `y` then press `Enter`,
    then enter the gallery ids/tags that you want to download,
    separated by '; '.
    Press `Enter` after finishing.
    - Enter `n` then press `Enter`,
    then create a `download_list.txt` file in [this format](#example-inputs-file)
    and place it in the `inputs/`folder.
    Go back to the Terminal app, press `Enter`.
1. Specify the galleries/tags you wish to **NOT** download either by:
    - Enter `y` then press `Enter`,
    then enter the gallery ids/tags that you **DO NOT** want to download,
    separated by '; '.
    Press `Enter` after finishing.(If nothing, press `Enter` directly.)
    - Enter `n` then press `Enter`,
    then create a `blacklists.txt` file in [the same format](#example-inputs-file)
    and place it in the `inputs/`folder (A blank file is also acceptable).
    Go back to the Terminal app, press `Enter`.
1. The program will automatically create a `Downloaded/` folder
for the downloaded galleries and begin download.
1. To terminate the program, simply press `Ctrl-c`.

## Bypassing Cloudflare and Anubis Protections

1. Open [nHentai][nhentai.net] in Safari.
1. Clear the Cloudflare CAPTCHA if necessary.
1. Login to your account.
1. Select "Show Page Source" from the "Develop" menu in Safari's menu bar.
(Follow [these steps][Safari-Developer] if you don't see the "Develop" menu.)
1. Select the "Network" tab, then refresh the webpage.
1. Click "Export" in the upper-right-hand corner and save it to the `inputs/` folder
located in the same directory as the `nhentai-scraper` executable.
(Keep the filename as its default value `nhentai.net.har`.)

## Example Inputs File

Same format applies to both `inputs/download_list.txt` and `inputs/blacklist.txt`.

```text
artist:<artist>
tag:<tag>
group:<group>
search:<search>
#114514
favorites
```

(No empty space after ':'.)

## Updating

### Updating the Unix executable

1. Download the newest `.tgz` archive from [Releases][releases].
1. Extract the downloaded `.tgz` archive.
1. Replace the `nhentai-scraper` executable
and the `_internal` folder with the new ones

### Updating the Source code

1. Move into the `nhentai-scraper` directory by `cd nhentai-scraper`.
1. Pull the newest commits by running `git pull`.

## Advanced Usage

- To run the program periodically, use `crontab` or `launchctl.`
  - For `crontab`, give `Full Disk Access` to `/usr/sbin/cron`
  in `System Preferences` (Or `System Settings` in newer macOS versions).

## Usage with Servers

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

## Some Minor Tips when Using the Program

- Try using/changing VPN if constantly getting 'Error 403'.
- If some of the archives are not showing in LANraragi,
try restarting the Docker container.
- To search for downloaded galleries by title in Finder,
don't include the parts in the paranthesis '[]'.
Ex: To search for '[artist] title', simply type 'title'.
- Try to [reindex spotlight][reindex-spotlight] if it is not skipping
the download for a praticular tag,
even though all galleries from the tag have already been downloaded.

## TL;DR

To download [your favorites on nHentai][favorites]:

1. Download the newest `.tgz` file from [Releases][releases] and extract it
1. Double click on the `nhentai-scraper` executable (macOS's Terminal will open)
1. The default settings will be printed on screen, press `y` then `Enter`
1. Follow [these steps](#bypassing-cloudflare-and-anubis-protections)
to bypass Cloudflare and Anubis protections on nHentai
1. Go back to the Terminal application, then press `Enter`
1. Press `y` then `Enter`
1. Enter `favorites` then press `Enter`
1. Press `y` then `Enter`
1. Press `Enter` again
1. If you see the words 'Searching galleries from favorites: '
and the progress bar behind it, then everything should be working as intended!
1. The downloaded galleries will be placed inside the `Downloaded` folder
1. Press `Ctrl-c` if you want to stop downloading;
Double-click on the `nhentai-scraper` executable again to resume downloading

[nhentai.net]: https://nhentai.net
[favorites]: https://nhentai.net/favorites/
[issues]: https://github.com/ecchi-na-no-wa-dame/nhentai-scraper-macOS/issues
[releases]: https://github.com/ecchi-na-no-wa-dame/nhentai-scraper/releases
[Safari-Developer]: https://developer.apple.com/documentation/safari-developer-tools/enabling-developer-features
[lanraragi]: https://github.com/Difegue/LANraragi
[kavita]: https://github.com/Kareadita/Kavita
[reindex-spotlight]: https://support.apple.com/en-us/102321
