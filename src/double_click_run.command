#!/bin/bash
cd "$(dirname "$0")"
time caffeinate -is python download_galleries.py
