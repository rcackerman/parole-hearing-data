import urllib
from bs4 import BeautifulSoup
import re

url = "http://161.11.133.89/ParoleBoardCalendar/details.asp?nysid="

data = open("parole.csv").readlines()
data = [d.strip() for d in data]

for d in data[1:]:

   d = d.split(",")[2]
   urlfinal = url+d

   response = urllib.urlopen(urlfinal)
 
   bs = BeautifulSoup(response.read())
   
   tables = bs.find_all("table")

   if not tables: continue

   head = []
   body = []

   for tr in tables[0].find_all("tr"):

      out = tr.getText()
      out = out.split(":")

      head.append(out[0].strip())
      body.append(out[1].strip())

   for tr in tables[1].find_all("tr"):

      for th in tr.find_all("th"):
         head.append(th.getText().strip())
      
      for td in tr.find_all("td"):
         body.append(td.getText().strip())

      print tr.prettify()

   print ",".join(head)
   print ",".join(body)

   exit()


