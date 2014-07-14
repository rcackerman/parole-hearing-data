#--------------
# Gets all pages we need to scrape
#--------------

import mechanize
import cookielib
from bs4 import BeautifulSoup
import re
import time
import csv


# CHANGEME
csvfile = open("books.csv","w")
writer = csv.writer(csvfile)
writer.writerow(["title","author","pub"])

baseurl = 'http://161.11.133.89/ParoleBoardCalendar/interviews.asp?month={month}&year={year}'
urls_to_visit = []

# The parole calendar goes 12 months back
# and 6 months forward (add an extra month to account for current month)
today = time.localtime()
month_array = [time.localtime(time.mktime([now.tm_year, now.tm_mon + n, 1, 0, 0, 0, 0, 0, 0]))[:2] for n in range(-24, 7)]

mech = mechanize.Browser()
mech.set_handle_robots(False)

mech.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

for monthyear in month_array:
   url = baseurl.format(month = monthyear[1], year = monthyear[0])
   urls_to_visit.append(url)

mech.open(theurl)

results = mech.submit().read()
bs = BeautifulSoup(results)

baseurl = mech.geturl()
baseurl = re.sub("(http://[^/]+)/.*","\\1",baseurl)

i = 0

while i < 1000:

   init = False
   
   for td in bs.find_all("td"):
   
      t = td.getText(" ")
      t = re.sub("\n"," ",t)
      t = t.strip()
   
      if re.match("^[0-9]+\..*",t): 
   
         init = True
         continue
   
      if t and init:
   
         title = re.sub("(.*)Author:.*","\\1", t)
         title = title.strip()
         title = title.encode("ascii","ignore")
         author = re.sub(".*Author:(.*)Publication:.*","\\1", t)
         author = author.strip()
         author = author.encode("ascii","ignore")
         pub = re.sub(".*Publication:(.*)Document:.*","\\1", t)
         pub = pub.strip()
         pub = pub.encode("ascii","ignore")
   
         writer.writerow([title,author,pub])      
         init = False
   
      else: continue
  
   n = bs.find("img",attrs={"src":"/images/nfs_next.gif"}) 

   if n.parent.name == "a":

      theurl = baseurl+n.parent["href"]
      print theurl
      results = mech.open(theurl).read()
      bs = BeautifulSoup(results)

   else: break

   i += 1
