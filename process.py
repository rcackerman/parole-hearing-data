import re, time, csv, datetime
import os, sys

def format_date(date):
  if int(date) <= 50:
    date = 2000 + int(date)
    return date
  elif int(date) > 50 and int(date) < 100:
    date = 1900 + int(date)
    return date
  else:
    return date

def no_names(x):
  if type(x) == list:
    return x[1:len(x)]

parolees = []

with open('output2.csv', 'r') as csvfile:
  dreader = csv.DictReader(csvfile)
  for p in dreader:
    parolees.append(p)

parolees = 

##
# Cleaning

# get rid of names
ps = parolees
ps = map(no_names, ps)