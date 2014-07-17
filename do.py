#--------------
# Gets all pages we need to scrape
#--------------

import mechanize
from bs4 import BeautifulSoup
import re, time, csv, sys
from string import ascii_uppercase

baseurl = 'http://161.11.133.89/ParoleBoardCalendar/interviews.asp?name={letter}&month={month}&year={year}'
detailurl = 'http://161.11.133.89/ParoleBoardCalendar/details.asp?nysid={number}'
urls_to_visit = []
parolees = []
parolee_urls = []

# The parole calendar goes 24 months back
# and 6 months forward (add an extra month to account for current month)
today = time.localtime()
month_array = [time.localtime(time.mktime([today.tm_year, today.tm_mon + n, 1, 0, 0, 0, 0, 0, 0]))[:2] for n in range(-24, 7)]
letters = list(ascii_uppercase)

mech = mechanize.Browser()
mech.set_handle_robots(False)

mech.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

for monthyear in month_array:
   monthvar = str(monthyear[1]).zfill(2)
   for l in letters:
      url = baseurl.format(letter = l, month = monthvar, year = monthyear[0])
      urls_to_visit.append(url)

##
# Cycles through all the urls created
# by the month, year, and letter combos
#
# TODO
#   * add detail page info for each person
#   * don't grab the table headers

for url in urls_to_visit:
   print url

   op = mech.open(url)

   bs = BeautifulSoup(op.read())

   # All parolees are within the central table.
   parolee_table = bs.find('table', class_ = "intv")

   # Splitting out into one line per parolee.
   try:
      parolee_line = parolee_table.find_all('tr')

      for pl in parolee_line:
         pl_list = []

         # Get all info
         for td in pl.find_all(['td', 'th']):
            pl_list.append(td.string.strip())
         parolees.append(pl_list)

         # Get details page url
         parolee_url = detailurl.format(number = pl_list[1])
         parolee_urls.append(parolee_url)
   except:
      continue

##
# Clean up
# TODO:
#   * drop names column
#   * get first 2 digits of DIN number for year of entry; format it into 19__ / 20__ (if <20, then 19__; otherwise 20__?)

with open('output.csv', 'a') as csvfile:
   w = csv.writer(csvfile, delimiter=',')
   w.writerows(parolees)
