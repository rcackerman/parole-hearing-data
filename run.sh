#!/bin/bash -e

git pull origin master
source .env/bin/activate
python scrape.py data.csv > output.csv 2>log.txt &
mv output.csv data.csv
git add data.csv
git commit -m "Automatically updated data on $(date)"
git push origin master
