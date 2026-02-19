# nHentai Scraper for MacOS

English | [繁體中文](README_zh-TW.md)

Scraper/Downloader for [nHentai][nHentai.net],
designed for ease of use on MacOS.\
Feel free to ask about any difficulties you are facing
(or offer any suggestions) [here][issues]!

## Features

- Downloads from your [favorites on nhentai.net][favorites]
or a user-given list of gallery ids/searches/tags/artists/groups/parodies...
- Galleries can be saved either as folders (directly viewed by Finder)
or cbz archives (viewed on servers):
  - By saving as folders:
    - Thumbnail and tags are automatically set to the folder for each gallery.
    - Images are combined into a single PDF file for easier viewing.
  - By saving as cbz archives:
    - Galleries may be viewed on servers such as [LANraragi][lanraragi] and [Kavita][kavita].
- Prevents downloads from user-defined blacklists.
- Skips over already-downloaded galleries.
- Supports skipping over galleries with the same title.
- Supports running while computer is in sleep with lid closed.

## Installation

### Downloading the Unix executable

1. Download the newest `.tgz` archive from [Releases][releases].
1. Extract the downloaded `.tgz` archive.

### Downloading the Source code

1. Clone the GitHub repository by running
`git clone https://github.com/ecchi-na-no-wa-dame/nhentai-scraper.git`
in your terminal.
1. Move into the program directory with `cd nhentai-scraper`.
1. Create a virtual environment with `python -m venv venv`.
1. Activate the virtual environment with `source venv/bin/activate`.
1. Install dependencies with `pip install -r requirements.txt`.

## Basic Usage

1. (For people downloading the unix executable from [Releases][releases])
Create a `inputs/` folder at the location of the `main` executable.
1. Export your cookies and headers for bypassing CloudFlare and Anubis
in an `.har` file and save it to the `inputs/` folder.
Example using Safari:
    1. Open [nhentai.net](https://nhentai.net) in Safari.
    1. (Optional) Log in to your account
    (only necessary if you wish to download your [favorites][favorites]).
    1. Clear the CloudFlare captcha.
    1. From the `Develop` menu, click on `Show Web Inspector`.
    (Follow [these steps][Safari-Developer] if you haven't enabled it.)
    1. Select the `Network` tab, and refresh the page.
    1. Click on the `Export` option in the upper right hand corner,
    and save it inside the `inputs/` folder where the program is located at.

1. Depending on your installation, execute the program either by:
    - If you want the program to only run when your computer is awake:
        - Double click the `main` file.
        - Run `python main.py` (located in the `src/` folder) in your terminal.

    - If you want the program to continue to run even when the computer is in sleep:
        - Double click the `main_no_sleep.command` file.
        - Run `caffeinate -is python main.py`
        (located inside the `src/` folder) in your terminal.

1. For the first run, the program will print out the default settings.
Enter 'n' if you want to change any of the settings. Otherwise, enter 'y'.

1. The program will automatically create a `Downloaded/` folder
for the downloaded galleries and begin download.

1. To terminate the program, simply press `Ctrl-c`.

## Updating

### Updating the Unix executable

1. Download the newest `.tgz` archive from [Releases][releases].
1. Extract the downloaded `.tgz` archive.
1. Replace the `main` executable and the `_internal` folder with the new ones

### Updating the Source code

1. Move into the `nhentai-scraper` directory by `cd nhentai-scraper`.
1. Pull the newest commits by running `git pull`.

## Advanced Usage

- To run the program periodically, use cron or launchctl.
  - For `cron`, give `Full Disk Access` to `/usr/sbin/cron`
  in `System Preferences` (Or `System Settings` in newer MacOS versions).

## Example `download_list.txt` File

```text
artist:<artist>
tag:<tag>
group:<group>
search:<search>
#114514
```

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
    to completely follow the format on [nHentai][nHentai.net]

## Some Tips when Using the Program

- Use/Change VPN if constantly getting Error 403.
Ex: To search for `[artist] title`, simply type `title`.
- If some of the archives are not showing in LANraragi, restart the Docker container.
- To search for downloaded galleries by title in Finder,
don't include the parts in the paranthesis `[]`.
- [Reindex spotlight][reindex-spotlight] if it is not skipping a praticular tag,
even though all galleries from the tag have already been downloaded.

[nHentai.net]: https://nhentai.net
[favorites]: https://nhentai.net/favorites/
[issues]: https://github.com/ecchi-na-no-wa-dame/nhentai-scraper-MacOS/issues
[releases]: https://github.com/ecchi-na-no-wa-dame/nhentai-scraper/releases
[Safari-Developer]: https://developer.apple.com/documentation/safari-developer-tools/enabling-developer-features
[lanraragi]: https://github.com/Difegue/LANraragi
[kavita]: https://github.com/Kareadita/Kavita
[reindex-spotlight]: https://support.apple.com/en-us/102321
