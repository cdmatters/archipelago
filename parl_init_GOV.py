import sqlite3
import requests
from lxml import etree
import os
import time

###########################
site = 'http://data.parliament.uk/membersdataplatform/services/mnis/'
###########################


def fetch_xml_online(request, api='members/query/', output=''):
    url = site + api + request + output
    
    data_request = requests.get(url)
    data_req_string = data_request.content
    data_xml = etree.fromstring(data_req_string)

    return data_xml



def return_constituency_list():

    with sqlite3.connect('parl.db') as connection:
        cur = connection.cursor()
        cur.execute('SELECT Constituency FROM MPCommons')

        constituency_list = cur.fetchall()
    return constituency_list


print return_constituency_list()