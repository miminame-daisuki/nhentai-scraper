# nHentai Scraper

English | [繁體中文](README_zh-TW.md)

Scraper/Downloader for [nHentai][1],
designed for ease of use on MacOS.\
Feel free to ask about any difficulties you are facing [here](issues)!

## Features

- Downloads from your [favorites on nhentai.net][2]
or a user-given list of gallery ids/searches/tags/artists/groups/parodies...
- Galleries can be saved either as folders (directly viewed by Finder)
or cbz archives (viewed on servers):
  - By saving as folders:
    - Thumbnail and tags are automatically set to the folder for each gallery.
    - Images are combined into a single PDF file for easier viewing.
  - By saving as cbz archives:
    - Galleries may be viewed on servers such as [LANraragi][5] and [Kavita][6].
- Prevents downloads from user-defined blacklists.
- Skips over already-downloaded galleries.
- Supports skipping over galleries with the same title.
- Supports running while computer is in sleep with lid closed.

## Installation

### Unix executable

1. Download the `.tgz` archive from [Releases][3].
1. Extract the downloaded `.tgz` archive.

### Source code

1. Run `git clone https://github.com/miminame-daisuki/nhentai-scraper` in your terminal.
1. Move into the program directory with `cd nhentai-scraper`.
1. Create a virtual environment with `python -m venv venv`.
1. Activate the virtual environment with `source venv/bin/activate`.
1. Install dependencies with `pip install -r requirements.txt`.

## Basic Usage

1. (For people downloading the unix executable from [Releases][3])
Create a `inputs/` folder at the location of the `main` executable.
1. Export your cookies and headers for bypassing CloudFlare and Anubis
in an `.har` file and save it to the `inputs/` folder.
Example using Safari:
    1. Open [nhentai.net](https://nhentai.net) in Safari.
    1. (Optional) Log in to your account
    (only necessary if you wish to download your [favorites][2]).
    1. Clear the CloudFlare captcha.
    1. From the `Develop` menu, click on `Show Web Inspector`.
    (Follow [these steps][4] if you haven't enabled it.)
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

## Advanced Usage

- To run the program periodically, use cron or launchctl.

## Example `download_list.txt` File

```text
artist:<artist>
tag:<tag>
group:<group>
search:<search>
#114514
```

## Usage with Servers

### [LANraragi][5]

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
    - `nHentai` if you want the filenames to completely follow the format on nHentai

## Some Tips when Using the Program

- Use/Change VPN if constantly getting Error 403.
Ex: To search for `[artist] title`, simply type `title`.
- If some of the archives are not showing in LANraragi, restart the Docker container.
- To search for downloaded galleries by title in Finder,
don't include the parts in the paranthesis `[]`.
- [Reindex spotlight][7] if it is not skipping a praticular tag,
even though all galleries from the tag have already been downloaded.

[1]: https://nhentai.net
[2]: https://nhentai.net/favorites/
[3]: https://github.com/miminame-daisuki/nhentai-scraper/releases
[4]: https://developer.apple.com/documentation/safari-developer-tools/enabling-developer-features
[5]: https://github.com/Difegue/LANraragi
[6]: https://github.com/Kareadita/Kavita
[7]: https://support.apple.com/en-us/102321
