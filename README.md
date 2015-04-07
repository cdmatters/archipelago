#*Untitled* Parliament Project

This repository contains code for the creation and 
population of MP's data, both from the GOV.UK and 
THEYWORKFORYOU (TWFY) Websites. 

It also contains a number of interesting projects
that rely on the similar data.

##RUN: 
1. pip install the requirements.txt
2. *parl_init_TWFY* requires an api key. Generate this
on the TWFY website.
3. run *main_setup.py*

This will:
* generate a local database of MPs.
* data included: name, constituency, party, seats/offices,
small official photos of every MP

##PROJECTS:
###Twirps

This project populates a database of tweets from MPs
and provides analysis on them. Read **twirps_README.md**
for further info.


##IDEAS:
* making a map/graph of jobs by committee
* scraping/rss to pick up relevant news articles for mps
* checking blogs of mps and linking to relevant articles
* searching official gov site (not TWFY)

