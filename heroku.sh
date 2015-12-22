#!/bin/bash

rm -rf * # whoa
rm -f .gitignore

mkdir -p .ssh
echo "$SSH_PRIVATE_KEY" > .ssh/id_rsa
chmod 600 .ssh/id_rsa
echo "$SSH_PUBLIC_KEY" > .ssh/id_rsa.pub
echo -e "Host github.com\n\tStrictHostKeyChecking no\n" >> ~/.ssh/config

git init
git config --global user.email 'nikzei@gmail.com'
git config --global user.name 'Nikki Zeichner'

git remote add origin git@github.com:talos/parole-hearing-data.git
git pull origin master

python scrape.py data.csv > output.csv

mv output.csv data.csv
git add data.csv
git commit -m 'auto update'
git push origin master
