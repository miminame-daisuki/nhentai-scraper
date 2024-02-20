#!/bin/bash
cd "$(dirname "$0")"
eval "$(conda shell.bash hook)"
conda activate scraper
time caffeinate -is python download_galleries.py
