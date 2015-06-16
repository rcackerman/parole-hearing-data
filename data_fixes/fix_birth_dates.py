import pandas as pd
import numpy as np

# tell pandas how to process data type for each column
data_types = {'parole board interview date': 'object', "din": 'object', "scrape date": 'object', "nysid": 'object',
    "sex": 'object', "birth date": 'object', "race / ethnicity": 'object', "housing or interview facility": 'object',
    "parole board interview type": 'object', "interview decision": 'object', "year of entry": 'int',
    "aggregated minimum sentence": 'object', "aggregated maximum sentence": 'object',
    "release date": 'object', "release type": 'object', "housing/release facility": 'object',
    "parole eligibility date": 'object', "conditional release date": 'object', "maximum expiration date": 'object',
    "parole me date": 'object', "post release supervision me date": 'object', "parole board discharge date": 'object',
    "crime 1 - crime of conviction": 'object', "crime 1 - class": 'object', "crime 1 - county of commitment": 'object',
    "crime 2 - crime of conviction": 'object', "crime 2 - class": 'object', "crime 2 - county of commitment": 'object',
    "crime 3 - crime of conviction": 'object', "crime 3 - class": 'object', "crime 3 - county of commitment": 'object',
    "crime 4 - crime of conviction": 'object', "crime 4 - class": 'object', "crime 4 - county of commitment": 'object',
    "crime 5 - crime of conviction": 'object', "crime 5 - class": 'object', "crime 5 - county of commitment": 'object',
    "crime 6 - crime of conviction": 'object', "crime 6 - class": 'object', "crime 6 - county of commitment": 'object',
    "crime 7 - crime of conviction": 'object', "crime 7 - class": 'object', "crime 7 - county of commitment": 'object',
    "crime 8 - crime of conviction": 'object', "crime 8 - class": 'object', "crime 8 - county of commitment": 'object'
}

# picking out date columns for parsing
date_columns = ["scrape date", "birth date", "year of entry",
            "release date", "parole eligibility date",
            "conditional release date",
            "post release supervision me date",
            "parole board discharge date"]

##
# Parolees are all parolees scraped as of 6/16/2015
parolees = pd.read_csv('data.csv', na_values = ['*','**********', 'UNKNOWN'],
    parse_dates=date_columns, dtype=data_types)

def fix_year(x):
    if x.year > 2015:
        new_year = x.year - 100
        return x.replace(year = new_year)
    else:
        return x


# fix years of birth
parolees['birth date'] = parolees['birth date'].apply(lambda x: fix_year(x))

parolees.to_csv('data.csv', index=False)
