'''
Transform raw parolee scrape information.
'''

import os
from datetime import date
import yaml

_CONFIG_DIR = os.path.join(os.path.dirname(
                            os.path.dirname(__file__)
                            ), 'config')
_SECURITY_LEVELS = yaml.load(
                    open(os.path.join(_CONFIG_DIR, 'prisons.yml')))
_SIMPLIFIED_DECISIONS = yaml.load(
                            open(os.path.join(_CONFIG_DIR, 'decisions.yml')))
_FORBIDDEN_HEADERS = [u'name']


def get_year_of_entry(din):
    '''Parses the last 2 digits of the parolee's DIN to a 4 digit year.
    The last 2 digits of the parolee's DIN are the year of entry
    for the current sentence.
    '''
    din_year = int(din[0:2])
    # The maximum year of entry is this year.
    max_year = int(date.today().strftime('%y'))
    return 2000 + din_year if din_year <= max_year else 1900 + din_year


def get_security_level(parolee, facility_columns):
    '''looks up the security level for a particular facility and returns a key/value pair.
    '''
    for i in facilities_columns:
        yield { '{} security level'.format(i): _SECURITY_LEVELS[i] }


def simplify_outcomes(decision):
    """
    Takes a parolee, finds the outcome,
    and creates a key value pair with a simplified outcome.
    """
    decision = parolee['decision']
    return {'interview_decision_category': _SIMPLIFIED_DECISIONS[decision]}


def fix_defective_sentence(sentence):
    """
    Most of the sentences in existing data were erroneously converted from
    "NN-NN" to "Month-NN" or "NN-Month", for example "03-00" to "Mar-00".  This
    fixes these mistakes.
    """
    if not sentence:
        return sentence
    sentence = sentence.split('-')
    month2num = {"jan": "01", "feb": "02", "mar": "03", "apr": "04",
                 "may": "05", "jun": "06", "jul": "07", "aug": "08",
                 "sep": "09", "oct": "10", "nov": "11", "dec": "12"}
    for i, val in enumerate(sentence):
        sentence[i] = month2num.get(val.lower(), ('00' + val)[-2:])
    try:
        # sometimes the min/max is flipped.
        if int(sentence[0]) > int(sentence[1]) and int(sentence[1]) != 0:
            sentence = [sentence[1], sentence[0]]
    except ValueError:
        pass
    return '-'.join(sentence)


def complete_date(date, year, month):
    yield u'{}-{}-*'.format(year, '0{}'.format(month)[-2:])
