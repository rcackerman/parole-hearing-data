"""
Scrape all parole hearing data for NYS.
"""

import csv
import scrapelib
import sys
from bs4 import BeautifulSoup
from string import ascii_uppercase
from time import localtime, mktime
from datetime import datetime
from dateutil import parser as dateparser

ROOT_URL = 'http://161.11.133.89/ParoleBoardCalendar'
DETAIL_URL = ROOT_URL + '/details.asp?nysid={number}'
INTERVIEW_URL = ROOT_URL + '/interviews.asp?name={letter}&month={month}&year={year}'


def get_existing_parolees(path):
    """
    Load in existing parole hearing data from provided path.  Turns into a
    dict, indexed by DIN and parole board interview date.
    """
    parolees = {}
    with open(path, 'rU') as csvfile:
        for row in csv.DictReader(csvfile, delimiter=',', quotechar='"'):
            row = dict((k.lower(), v) for k, v in row.iteritems())
            parolees[(row[u"din"], row[u"parole board interview date"])] = row
    return parolees


def baseurls():
    """
    Provide URLs for the calendar going back 24 months and forward 6 months via
    generator
    """
    today = localtime()
    for monthdiff in xrange(-25, 7):
        monthyear = localtime(mktime(
            [today.tm_year, today.tm_mon + monthdiff, 1, 0, 0, 0, 0, 0, 0]))[:2]
        for letter in ascii_uppercase:
            yield INTERVIEW_URL.format(letter=letter,
                                       month=str(monthyear[1]).zfill(2),
                                       year=monthyear[0])


def get_general_parolee_keys(scraper, url):
    """
    Obtains a list of the standard parolee data keys (table headers) from the
    specified URL.
    """
    soup = BeautifulSoup(scraper.urlopen(url))
    keys_th = soup.find('table', class_='intv').find('tr').find_all('th')
    return [unicode(key.string) for key in keys_th]

def get_headers(list_of_dicts):
    """
    Returns a set of every different key in a list of dicts.
    """
    return set().union(*[l.keys() for l in list_of_dicts])


def scrape_interviews(scraper):
    """
    Scrape all interviews.  Returns a list of parolees, with minimal data,
    from these hearings.
    """
    parolees = []
    parolee_keys = None
    for url in baseurls():
        sys.stderr.write(url + '\n')

        if parolee_keys is None:
            parolee_keys = get_general_parolee_keys(scraper, url)

        soup = BeautifulSoup(scraper.urlopen(url))

        # All parolees are within the central table.
        parolee_table = soup.find('table', class_="intv")
        if not parolee_table:
            continue

        # Splitting out into one line per parolee.
        parolee_tr = parolee_table.find_all('tr')
        for row in parolee_tr:
            cells = row.find_all('td')
            if not cells:
                continue
            parolee = {}
            for i, cell in enumerate(cells):
                parolee[parolee_keys[i]] = cell.string.strip()
            parolees.append(parolee)

    return parolees


# pylint: disable=too-many-locals
def scrape_details(scraper, parolee_input):
    """
    Scrape details for specified parolees.  Returns the same list, with
    additional data.
    """
    out = []
    for existing_parolee in parolee_input:
        parolee = existing_parolee.copy()
        if len(parolee) <= 1:
            # Some blank rows sneak in; let's skip them.
            continue

        url = DETAIL_URL.format(number=parolee['nysid'])
        sys.stderr.write(url + '\n')

        soup = BeautifulSoup(scraper.urlopen(url, timeout=5))
        detail_table = soup.find('table', class_="detl")
        if not detail_table:
            continue

        crimes = soup.find('table', class_="intv").find_all('tr')
        crime_titles = [u"crime {} - " + unicode(th.string)
                        for th in soup.find('table', class_="intv").find_all('th')]

        for row in detail_table:
            key, value = row.getText().split(":")
            # we don't need to capture the nysid, name, or din again
            key = key.lower()
            if "nysid" in key or "name" in key or "din" in key:
                continue
            parolee[key] = value.strip().replace(u'\xa0', u'')

        for crime_num, crime in enumerate(crimes[1:]):
            title = [ct.format(crime_num + 1) for ct in crime_titles]
            i = 0
            while i < len(crime):
                parolee[title[i]] = crime.find_all('td')[i].string.strip()
                i += 1

        out.append(parolee)

    return out
# pylint: enable=too-many-locals

def reorder_headers(supplied):
    """
    Takes the supplied headers, and prefers the "expected" order.  Any
    unexpected supplied headers are appended alphabetically to the end.  Any
    expected headers not supplied are not included.
    """
    headers = []
    expected = [
        "scrape date",
        "nysid",
        "din",
        "sex",
        "birth date",
        "race / ethnicity",
        "housing or interview facility",
        "parole board interview date",
        "parole board interview type",
        "interview decision",
        "year of entry",
        "aggregated minimum sentence",
        "aggregated maximum sentence",
        "release date",
        "release type",
        "housing/release facility",
        "parole eligibility date",
        "conditional release date",
        "maximum expiration date",
        "parole me date",
        "post release supervision me date",
        "parole board discharge date",
        "crime 1 - crime of conviction",
        "crime 1 - class",
        "crime 1 - county of commitment",
        "crime 2 - crime of conviction",
        "crime 2 - class",
        "crime 2 - county of commitment",
        "crime 3 - crime of conviction",
        "crime 3 - class",
        "crime 3 - county of commitment",
        "crime 4 - crime of conviction",
        "crime 4 - class",
        "crime 4 - county of commitment",
        "crime 5 - crime of conviction",
        "crime 5 - class",
        "crime 5 - county of commitment",
        "crime 6 - crime of conviction",
        "crime 6 - class",
        "crime 6 - county of commitment",
        "crime 7 - crime of conviction",
        "crime 7 - class",
        "crime 7 - county of commitment",
        "crime 8 - crime of conviction",
        "crime 8 - class",
        "crime 8 - county of commitment"
    ]
    for header in expected:
        if header in supplied:
            supplied.remove(header)
            headers.append(header)
    headers.extend(sorted(supplied))
    return headers

def print_data(parolees):
    """
    Prints output data to stdout, from which it can be piped to a file.  Orders
    by parole hearing date and DIN (order is important for version control.)
    """
    headers = get_headers(parolees)
    headers = reorder_headers(headers)

    # Convert date columns to SQL-compatible date format (like "2014-10-07")
    # when possible
    for parolee in parolees:
        for key, value in parolee.iteritems():
            if "date" in key:
                try:
                    parolee[key] = datetime.strftime(dateparser.parse(value), '%Y-%m-%d')
                except ValueError:
                    pass

    parolees = sorted(parolees, key=lambda x: (x[u"parole board interview date"], x[u"din"]))
    out = csv.DictWriter(sys.stdout, delimiter=',', fieldnames=headers)
    out.writeheader()
    out.writerows(parolees)


def scrape(old_data_path):
    """
    Main function -- read in existing data, scrape new data, merge the two
    sets, and save to the output location.
    """
    scraper = scrapelib.Scraper(requests_per_minute=180,
                                retry_attempts=5, retry_wait_seconds=15)

    if old_data_path:
        existing_parolees = get_existing_parolees(old_data_path)
    else:
        existing_parolees = {}

    new_parolees = scrape_interviews(scraper)
    new_parolees = scrape_details(scraper, new_parolees)

    for parolee in new_parolees:
        key = (parolee[u"din"], parolee[u"parole board interview date"])
        existing_parolees[key] = parolee

    print_data(existing_parolees.values())


if __name__ == '__main__':
    scrape(sys.argv[1] if len(sys.argv) > 1 else None)
