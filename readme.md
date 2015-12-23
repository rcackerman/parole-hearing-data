#Parole Hearing Data

### What is the Parole Hearing Data Project?

The Parole Hearing Data Project pulls records from the <a href= "https://www.parole.ny.gov/calendar.html">New York State Parole Board’s Interview Calendar </a> and dumps them into a spreadsheet, which grows every month as the parole board updates the calendar by adding newly scheduled hearings and newly issued determinations.  The goal of this project is to enable researchers to analyze this data and better understand patterns within parole hearing determinations within New York State.

Data from a sample run is included in `data.csv`. This project is in development.

### Why are we working on this?

Because in New York over 10,000 parole eligible prisoners are denied release every year based on the discretion of a small number of parole commissioners. The consequences of these denials have very real social and financial costs: families remain separated for periods that are arguably longer than necessary, incarcerated individuals who have changed their lives lose hope in a better future, millions of dollars are spent to imprison men and women who have been determined as posing a low risk to society were they to be released (in New York it costs $60,000 annually to incarcerate one individual, and more to incarcerate older individuals with illnesses). 

When we began this project, we wanted to see if we could understand better what the parole board's deicison making patterns were. Since then, we've learned through feedback from academic and nonprofit researchers just how hard it has been to actually analyze the data that the parole board actually publishes without it being reformatted in this way. We're excited for this work to be used and for new insights to result from researchers and criminal justice experts using this project as a resource.

### Setup and run

**Install app requirements**

```bash
$ pip install -r requirements.txt
```

**Running the scraper**

To run the scraper, execute the following python in the base directory of this
repo.

```bash
python scrape.py data.csv > output.csv 2>log.txt &
```

The results of the scraper will be in `output.csv`. Scraper logs will be in
`log.txt`.  The scraper will run in the background, and use the existing
`data.csv` as a source of historical data.

If you're OK with automatically updating the existing data, there is
a convenience script.

    ./run.sh

You can also automate this by specializing the `crontab` file and installing it
in your system by adapting the line and pasting it in to `crontab -e`.

## Team

Nikki Zeichner, <a href= "codeforamerica.org">Code for America</a>

Rebecca Ackerman, <a href="casecommons.org">Case Commons</a> 

John Krauss, <a href= "cartodb.com">CartoDB</a> 

And a special thanks to R. Luke DuBois of <a href= "http://engineering.nyu.edu/user/1797">NYU</a> and Annie Waldman of <a href= "http://www.propublica.org/site/author/annie_waldman">ProPublica</a>.

## Errors / Bugs

If something is not behaving intuitively, it is a bug, and should be reported.
Report it here: https://github.com/rcackerman/parole-hearing-data/issues

## Note on Patches/Pull Requests

* Fork the project.
* Make your feature addition or bug fix.
* Send a pull request. Bonus points for topic branches.
