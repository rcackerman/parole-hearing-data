'''
Transform raw parolee scrape information.
'''

import os
import yaml

_CONFIG_DIR = os.path.join(os.path.dirname(
                            os.path.dirname(__file__)
                            ), 'config')
_SECURITY_LEVELS = yaml.load(
                    open(os.path.join(_CONFIG_DIR, 'prisons.yml')))
_SIMPLIFIED_DECISIONS = yaml.load(
                            open(os.path.join(_CONFIG_DIR, 'decisions.yml')))
_FORBIDDEN_HEADERS = [u'inmate name']


def format_date(date):
    if int(date) <= 50:
        date = 2000 + int(date)
        return date
    elif int(date) > 50 and int(date) < 100:
        date = 1900 + int(date)
        return date
    else:
        return date


def get_year_of_entry(parolee):
    year_of_entry = format_date(parolee['din'][0:2])
    parolee['year of entry'] = year_of_entry
    return parolee


def set_security_level(parolee):
    """
    Takes a dictionary, finds the facility keys,
    and creates a key value pair with the security for that facility.
    """

    h_i_facility = parolee['housing or interview facility']
    h_r_facility = parolee['housing/release facility']

    h_i_sec_level = prison_list.PRISONS[h_i_facility]
    h_r_sec_level = prison_list.PRISONS[h_r_facility]

    parolee['housing/interview facility security level'] = h_i_sec_level
    parolee['housing/release facility security level'] = h_r_sec_level
    return parolee


def simplify_outcomes(parolee):
    """
    Takes a parolee, finds the outcome,
    and creates a key value pair with a simplified outcome.
    """
    decision = parolee['interview decision']
    parolee['interview decision category'] = SIMPLIFIED_DECISIONS[decision]
    return parolee


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
