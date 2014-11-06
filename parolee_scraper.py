#--------------
# Gets all pages we need to scrape
#--------------

import scrapelib
from bs4 import BeautifulSoup
import re, time, csv
from string import ascii_uppercase
import sys

class ParoleeScraper(scrapelib.Scraper):

	def __init__(self,
	             raise_errors=True,
               requests_per_minute=60,
               follow_robots=True,
               retry_attempts=5,
               retry_wait_seconds=15,
               header_func=None,
               url_pattern=None,
               string_on_page=None):
		self.base_url = 'http://161.11.133.89/ParoleBoardCalendar/'
		self.'interviews.asp?name={letter}&month={month}&year={year}'

	def get_last_scrape_date(self):