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
  return month_array

def generate_baseurl():
  baseurl = 'http://161.11.133.89/ParoleBoardCalendar/interviews.asp?name={letter}&month={month}&year={year}'
  urls = []
  monthsyears = fill_in_the_blanks()
  letters = list(ascii_uppercase)
  for my in monthsyears:
    for l in letters:
      url = baseurl.format(letter = l, month = str(my[1]).zfill(2), year = my[0])
      urls.append(url)
  return urls

def get_general_parolee_keys(url):
  keys = []
  op = s.urlopen(url)
  bs = BeautifulSoup(op)
  keys_th = bs.find('table', class_ = 'intv').find('tr').find_all('th')
  [keys.append(unicode(key.string)) for key in keys_th]
  return keys

def get_headers(list_of_dicts):
  all_keys = [l.keys() for l in list_of_dicts]
  return set().union(*all_keys)


##
# Cycles through all the urls created
# by the month, year, and letter combos
# For example, all the "A"s in June 2013
# Saves each cell by row to the parolees list.
urls_to_visit = generate_baseurl()
parolee_keys = get_general_parolee_keys(urls_to_visit[0])

for url in urls_to_visit[0:5]:
  print url
  op = s.urlopen(url)
  bs = BeautifulSoup(op)

  # All parolees are within the central table.
  parolee_table = bs.find('table', class_ = "intv")

  # Splitting out into one line per parolee.
  try:
    parolee_tr = parolee_table.find_all('tr')
    for pr in parolee_tr:
      tds = pr.find_all('td')
      i = 0
      pl = {}
      while i < len(tds):
        pl[parolee_keys[i]] = tds[i].string.strip()
        i += 1
      pl['scrape date'] = datetime.date.today().isoformat()
      parolees.append(pl)
  except:
    # This usually happens when there are no results
    # (For example, no one with a last name beginning "X" in August 2012)
    print "Unable to split parolee table by TR"
    continue

print "Scraping parolees"
for parolee in parolees:
  if len(parolee) <= 1:
    # Some blank rows sneak in; let's skip them.
    parolees.remove(parolee)
  else:
    print detailurl.format(number = parolee['NYSID'])

    # Checking if the parolee has detailed info already
    if len(parolee) > 11:
      pass
    else:
      try:
        dp = s.urlopen(detailurl.format(number = parolee['NYSID']), timeout=5)
        dbs = BeautifulSoup(dp)
        detail_table = dbs.find('table', class_ = "detl")
        crimes = dbs.find('table', class_ = "intv").find_all('tr')
        crime_titles = ["Crime {} - " + unicode(th.string) for th in dbs.find('table', class_ = "intv").find_all('th')]
        

        for tr in detail_table:
          detail = tr.getText().split(":")
          # we don't need to capture the nysid, name, or din again
          if "nysid" in detail[0].lower() or "name" in detail[0].lower() or "din" in detail[0].lower():
            continue
          else:
            parolee[detail[0]] = detail[1].strip().replace(u'\xa0', u'')

        a = 1
        for c in crimes[1:len(crimes)]:
          c_t = [ct.format(a) for ct in crime_titles]
          i = 0
          while i < len(c):
            parolee[c_t[i]] = c.find_all('td')[i].string.strip()
            i += 1
          a += 1

      except:
        # Most of these errors appear to be caused by the detail page not
        # actually existing.
        print parolee['NYSID'] + ' Could not be parsed', sys.exc_info()[0]
        continue


##
# Save to CSV

headers = get_headers(parolees)

with open('output.csv', 'a') as csvfile:
   w = csv.DictWriter(csvfile, delimiter=',', quoting=csv.QUOTE_ALL, fieldnames = headers)
   w.writeheader()
   w.writerows(parolees)
