#!/bin/bash -e

# Pull most recent remote updates.
git pull origin master

# The line below activates a Python virtualenv.
# Comment out if you use a different environment manager.
source .env/bin/activate

# Scrape to a temp file
python scrape.py data.csv > output.csv 2>log.txt &
# Move to final file
mv output.csv data.csv

git add data.csv
git commit -m "Automatically updated data on $(date)"
git push origin master