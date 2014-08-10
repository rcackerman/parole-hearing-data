#--------------
# Gets all pages we need to scrape
#--------------

import scrapelib
from bs4 import BeautifulSoup
import re, time, csv
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

s = scrapelib.Scraper(requests_per_minute=60, retry_attempts=5, retry_wait_seconds=15)

for monthyear in month_array:
  monthvar = str(monthyear[1]).zfill(2)
  for l in letters:
    url = baseurl.format(letter = l, month = monthvar, year = monthyear[0])
    urls_to_visit.append(url)

##
# Cycles through all the urls created
# by the month, year, and letter combos

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
    continue

for parolee in parolees:
  if not parolee:
    parolees.remove(parolee)
  else:
    print detailurl.format(number = parolee[1])

    #checking if the parolee has detail info already
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
        print parolee[1] + ' did not work'
        continue



#####
# TODO
# * Get crime info
# * split names

headers = ["INMATE NAME", "NYSID", "DIN", "SEX", "BIRTH DATE",  "RACE / ETHNICITY",
           "HOUSING OR INTERVIEW FACILITY", "PAROLE BOARD INTERVIEW DATE",
          "PAROLE BOARD INTERVIEW TYPE", "INTERVIEW DECISION", "Year of Entry",
          "Aggregated Minimum Sentence", "Aggregated Maximum Sentence", "Release Date",
          "Release Type", "Housing/Release Facility", "Parole Eligibility Date", "Conditional Release Date",
          "Maximum Expiration Date", "Parole ME Date", "Post Release Supervision ME Date", "Parole Board Discharge Date"]

with open('output.csv', 'a') as csvfile:
   w = csv.writer(csvfile, delimiter=',')
   w.writerows(parolees)
