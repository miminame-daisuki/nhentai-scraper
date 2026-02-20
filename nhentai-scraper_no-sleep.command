#!/bin/bash
# cd to the directory where this script is located at.
cd "$(dirname "$0")" || exit
time caffeinate -is ./nhentai-scraper
