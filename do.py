import mechanize
import cookielib
from bs4 import BeautifulSoup
import re
import csv

# CHANGEME
csvfile = open("books.csv","w")
writer = csv.writer(csvfile)
writer.writerow(["title","author","pub"])

mech = mechanize.Browser()
mech.set_handle_robots(False)

cj = cookielib.LWPCookieJar()
mech.set_cookiejar(cj)

mech.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

theurl = 'https://www1.columbia.edu/pamacea/login.shtml?target=/sec-cgi-bin/cul/prox/ezpwebserv-ezproxy.cgi%3furl=ezp.2aHR0cDovL2ZpcnN0c2VhcmNoLm9jbGMub3JnL2ZzaXA.ZGJuYW1lPVdvcmxkQ2F0JmRvbmU9cmVmZXJlcg--&pamservice=krb&userfile='

mech.open(theurl)

mech.select_form(nr=0)
mech["username"] = "CHANGEME"
mech["password"] = "CHANGEME"
results = mech.submit().read()

mech.select_form(nr=0)

mech.form['term1'] = "fiction"
mech.form['index1'] = ["ge:"]

mech.form['term2'] = "1939-1945"
mech.form['index2'] = ["kw:"]

mech.form['term3'] = "world war"
mech.form['index3'] = ["kw:"]

mech.form["limit-yr:"] = "1940-1955"
mech.form["limit-la="] = ["eng"]
mech.form["limit-dt="] = ["bks"]

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
