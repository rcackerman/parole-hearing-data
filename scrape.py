"""
Scrape all parole hearing data for NYS.
"""

import csv
import scrapelib
import sys
from bs4 import BeautifulSoup
from string import ascii_uppercase
from time import localtime, mktime

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
            parolees[(row[u"DIN"], row[u"PAROLE BOARD INTERVIEW DATE"])] = row
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
    return set([l.keys() for l in list_of_dicts])


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

        url = DETAIL_URL.format(number=parolee['NYSID'])
        sys.stderr.write(url + '\n')

        soup = BeautifulSoup(scraper.urlopen(url, timeout=5))
        detail_table = soup.find('table', class_="detl")
        if not detail_table:
            continue

        crimes = soup.find('table', class_="intv").find_all('tr')
        crime_titles = [u"Crime {} - " + unicode(th.string) for th in soup.find('table', class_="intv").find_all('th')]

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


def print_data(parolees):
    """
    Prints output data to stdout, from which it can be piped to a file.  Orders
    by parole hearing date and DIN (order is important for version control.)
    """
    headers = get_headers(parolees)

    parolees = sorted(parolees, key=lambda x: (x[u"PAROLE BOARD INTERVIEW DATE"], x[u"DIN"]))
    out = csv.DictWriter(sys.stdout, delimiter=',', quoting=csv.QUOTE_ALL,
                         fieldnames=headers)
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
        key = (parolee[u"DIN"], parolee[u"PAROLE BOARD INTERVIEW DATE"])
        existing_parolees[key] = parolee

    print_data(existing_parolees.values())


if __name__ == '__main__':
    scrape(sys.argv[1] if len(sys.argv) > 1 else None)
