import string
from datetime import date, timedelta
from functools import wraps

import bs4
import requests
from dateutil.relativedelta import relativedelta
from dateutil import parser


_BASE_URL = 'http://161.11.133.89/ParoleBoardCalendar/'
_DETAIL_URL = ROOT_URL + 'details.asp?nysid={number}'
_CALENDAR_URL = ROOT_URL + 'interviews.asp?'


def validate_requested_month(func):
    '''Interview calendars are only available from 24 months in the past to 6
    months in the future. If the year and month provided fall outside of this
    range, raise an error.
    '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        requested_month = date(args[0], args[1], 1)
        current_month = date.today().replace(day=1)
        if requested_month < current_month + relativedelta(months=-24):
            raise ValueError(
                'Cannot request interviews prior to 24 months ago')
        elif requested_month > current_month + relativedelta(months=+6):
            raise ValueError(
                'Cannot request interviews after 6 months from now')
        return func(*args, **kwargs)
    return wrapper


def construct_url_params(**kwargs):
    params = ['='.join([k, v]) for k, v in kwargs.items()]
    return '&'.join(params)


@validate_requested_month
def construct_urls(year, month, url=_CALENDAR_URL):
    '''Interview calendars are divided by interviewees' last names. Return a
    generator containing parole board calendar URLs for the year and month
    requested for each letter of the alphabet.
    '''
    for letter in string.ascii_uppercase:
        params = construct_url_params(**{
            'year': str(year),
            'month': '{:02d}'.format(month),
            'name': letter
        })
        yield '?'.join([url, params])


def scrape_calendar(url):
    '''Return a generator containing dictionaries representing each interview in
    the calendar at the requested URL.
    '''
    res = requests.get(url)
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    rows = zip(*[iter(soup.findAll('td'))] * 9)
    rows = [[list(elem.stripped_strings)[0] for elem in row] for row in rows]
    for row in rows:
        yield dict(zip(
            ['name', 'din', 'gender', 'birth_date', 'race_ethnicity',
             'facility', 'date', 'type', 'decision'], row))


def scrape_detail(url):
    '''Return a generator containing dictionaries representing the detail for
    each DIN in the calendar.
    '''
    pass
