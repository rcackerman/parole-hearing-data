#--------------
# Gets all pages we need to scrape
#--------------

import scrapelib
from bs4 import BeautifulSoup
import re, time, csv, datetime
from string import ascii_uppercase
import os, sys

s = scrapelib.Scraper(requests_per_minute=180, retry_attempts=5, retry_wait_seconds=15)
detailurl = 'http://161.11.133.89/ParoleBoardCalendar/details.asp?nysid={number}'
parolees = []
parolee_urls = []

def output_exists(file):
  if os.path.isfile(file):
    return True
  else:
    return False

def get_last_scrape_date(the_file):
  # Get last scrape date
  dates = []
  with open(the_file, 'rU') as csvfile:
    r = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    i = r.fieldnames.index('Scrape_Date')
    for row in r:
      dates.append(row['Scrape_Date'])
  max_date = max(dates)
  return max_date

def fill_in_the_blanks():
# The parole calendar goes 24 months back
# and 6 months forward (add an extra month to account for current month)
# We scrape every month, so only need the next 6 months
  if output_exists('data.csv'):
    last_scrape = get_last_scrape_date('data.csv') 
    last_scrape = datetime.datetime.strptime(last_scrape, '%Y-%M-%d')
    month_array = [time.localtime(time.mktime([last_scrape.year, last_scrape.month + n, 1, 0, 0, 0, 0, 0, 0]))[:2] for n in range(0, 7)]
  else:
    today = time.localtime()
    month_array = [time.localtime(time.mktime([today.tm_year, today.tm_mon + n, 1, 0, 0, 0, 0, 0, 0]))[:2] for n in range(0, 7)]
  letters = list(ascii_uppercase)
  yield month_array, letters

def generate_baseurl():
  baseurl = 'http://161.11.133.89/ParoleBoardCalendar/interviews.asp?name={letter}&month={month}&year={year}'
  urls = []
  monthsyears = fill_in_the_blanks().next()[0]
  letters = fill_in_the_blanks().next()[1]
  for my in monthsyears:
    for l in letters:
      url = baseurl.format(letter = l, month = str(my[1]).zfill(2), year = my[0])
      urls.append(url)
  return urls


##
# Cycles through all the urls created
# by the month, year, and letter combos
# For example, all the "A"s in June 2013
# Saves each cell by row to the parolees list.
urls_to_visit = generate_baseurl()

for url in urls_to_visit:
  print url
  op = s.urlopen(url)
  bs = BeautifulSoup(op)

  # All parolees are within the central table.
  parolee_table = bs.find('table', class_ = "intv")

  # Splitting out into one line per parolee.
  try:
    parolee_tr = parolee_table.find_all('tr')
    # print parolee_tr
    for pl in parolee_tr:
      pl_list = []
      for td in pl.find_all('td'):
        pl_list.append(td.string.strip())
      parolees.append(pl_list)
  except:
    # This usually happens when there are no results
    # (For example, no one with a last name beginning "X" in August 2012)
    print "Unable to split parolee table by TR"
    continue


print "Checking parolees"
for parolee in parolees:
  if not parolee:
    # Some blank rows sneak in; let's skip them.
    parolees.remove(parolee)

  else:
    print detailurl.format(number = parolee[1])

    # Checking if the parolee has detailed info already
    if len(parolee) > 10:
      pass
    else:
      try:
        dp = s.urlopen(detailurl.format(number = parolee[1]), timeout=5)
        dbs = BeautifulSoup(dp)
        detail_table = dbs.find('table', class_ = "detl")
        crimes = dbs.find('table', class_ = "intv").find_all('td')
        for tr in detail_table:
          detail = tr.getText().split(":")
          if "nysid" in detail[0].lower() or "name" in detail[0].lower():
            continue
          elif "din" in detail[0].lower():
            parolee.append(detail[1].strip().replace(u'\xa0', u'')[0:2])
          else:
            parolee.append(detail[1].strip().replace(u'\xa0', u''))
        for c in crimes:
          parolee.append(c.string.strip())
      except:
        # Most of these errors appear to be caused by the DIN detail page not
        # actually existing.
        print parolee[1] + ' Could not be parsed', sys.exc_info()[0]
        continue

# And now we clean
for parolee in parolees:
  parolee = parolee[1:len(parolee)]

#####
# TODO
# * Get crime info

headers = ["NYSID", "DIN", "SEX", "BIRTH DATE",  "RACE / ETHNICITY",
           "HOUSING OR INTERVIEW FACILITY", "PAROLE BOARD INTERVIEW DATE",
          "PAROLE BOARD INTERVIEW TYPE", "INTERVIEW DECISION", "Year of Entry",
          "Aggregated Minimum Sentence", "Aggregated Maximum Sentence", "Release Date",
          "Release Type", "Housing/Release Facility", "Parole Eligibility Date", "Conditional Release Date",
          "Maximum Expiration Date", "Parole ME Date", "Post Release Supervision ME Date", "Parole Board Discharge Date"]

with open('output.csv', 'a') as csvfile:
   w = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_ALL)
   w.writerows(parolees)