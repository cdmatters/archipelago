import sqlite3
import requests
from lxml import etree
import os
import time
import json

###########################
site = 'http://data.parliament.uk/membersdataplatform/services/mnis/'
###########################


def fetch_xml_online(request, api='members/query/', output=''):
    url = site + api + request + output
    
    data_request = requests.get(url)
    data_req_string = data_request.content
    data_xml = etree.fromstring(data_req_string)

    return data_xml

def return_constituency_list(database='parl.db'):
    with sqlite3.connect(database) as connection:
        cur = connection.cursor()
        cur.execute('SELECT Constituency FROM MPCommons')

        constituency_list = [result[0] for result in  cur.fetchall()]
        
    return constituency_list

def populate_addresses_from_constituency(const):
    #note: this function could be used to populate many fields: name, party, etc. can update later
    #      right now, leave the TWFY data in place: INPUT --> Official Id, Address
    const_xml = fetch_xml_online('constituency='+const+'/', output='Addresses/')
    official_ID = const_xml[0].get('Member_Id')
    addresses_xml = const_xml[0].find('Addresses')

    with sqlite3.connect('parl.db') as connection:
        cur = connection.cursor()
        cur.execute('UPDATE MPCommons SET OfficialId=? WHERE Constituency=?', (official_ID,const))

        for address_xml in addresses_xml:
            atype, address = '',''
            if address_xml.get('Type_Id')=='6':  #web info
                atype = 'Website'
                address = address_xml.find('Address1').text
            elif address_xml.get('Type_Id')=='7':  #twitter info
                atype = 'Twitter'
                address = address_xml.find('Address1').text
            #elif... <other address types>
            if atype != '':
                cur.execute('INSERT INTO Addresses VALUES(?,?,?)', (official_ID,atype,address))


def GOV_setup():
    start = time.time()
    constituencies = return_constituency_list()
    for c in constituencies:
        populate_addresses_from_constituency(c)
    print 'GOV Setup in %ds'%(time.time()-start)

    


