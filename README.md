# *Archipelago*


Archipelago is a library that creates an interface to obtain parliamentary information quickly and easily in Python, for use in other open source politics related projects. 

It quickly creates a complete local database of parliamentary information for the UK, by querying the both GOV.UK and TheyWorkForYou.com websites, and provides an easy api to query this database, whilst also exposing the database itself.



## RUN: 
1. pip install archipelago
2. *parl_init_TWFY* requires an api key. Generate this
on the TWFY website.
3. the first time you run after import archipelago, it will ask for your key.

## DATA:

* **House of Commons**: name, constituency, party, seats/offices, websites, twitter handles, small official photos of every MP
* **House of Lords**: *incomplete*

## IDEAS:

* making a map/graph of jobs by committee
* scraping/rss to pick up relevant news articles for mps
* checking blogs of mps and linking to relevant articles
* searching official gov site (not TWFY)

## PROJECTS:

#### Twirps

This project populates a database of tweets from MPs
and provides analysis on them.

*All work for Twirps has migrated from the subdirectory here to the repo [here](https://github.com/condnsdmatters/twirps)*



