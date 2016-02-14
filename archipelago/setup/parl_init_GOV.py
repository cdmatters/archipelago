import sqlite3
import requests
from lxml import etree
import os
import time
import json
from archipelago import Archipelago
from tqdm import tqdm

###########################
site = 'http://data.parliament.uk/membersdataplatform/services/mnis/'
###########################


def fetch_xml_online(request, api='members/query/', output=''):
    url = site + api + request + output

    data_request = requests.get(url)
    data_req_string = data_request.content
    data_xml = etree.fromstring(data_req_string)

    return data_xml

def build_mp_addresses_from_constituency(addresses_request_xml):
    """ Build a python object containing addresses about an MP """
    # print etree.tostring(addresses_request_xml, pretty_print=True)
    #ERROR HANDLING
    mp_address = {}
    mp_address["official_ID"] = addresses_request_xml[0].get('Member_Id')
    mp_address["name"] = addresses_request_xml[0].find('DisplayAs').text
    mp_address["constituency"] = addresses_request_xml[0].find('MemberFrom').text
    mp_address["addresses"] = {}
    addresses_xml = addresses_request_xml[0].find('Addresses')

    for address_xml in addresses_xml:
        a_type = address_xml.get('Type_Id')

        if a_type=='6':
            mp_address["addresses"][ "website" ] = address_xml.find('Address1').text
        elif a_type=='7':
            mp_address["addresses"][ "twitter" ] = address_xml.find('Address1').text

    return mp_address

def load_addresses_from_constituency(constituency, database="parl.db"):
    #note: this function could be used to populate many fields: name, party, etc. can update later
    #      right now, leave the TWFY data in place: INPUT --> Official Id, Address
    addresses_xml = fetch_xml_online('constituency='+constituency+'/', output='Addresses/')
    mp_addresses = build_mp_addresses_from_constituency(addresses_xml)
    official_ID = mp_addresses["official_ID"]

    with sqlite3.connect(database) as connection:
        cur = connection.cursor()
        cur.execute('UPDATE MPCommons SET OfficialId=? WHERE Constituency=?', (official_ID,constituency))
    
        for a_type, address in mp_addresses["addresses"].items():
            cur.execute('INSERT INTO Addresses VALUES(?,?,?)', (official_ID,a_type,address))



def GOV_setup():
    start = time.time()
    arch = Archipelago()
    constituencies = arch.get_constituencies()
    for c in tqdm(constituencies):
        try:
            load_addresses_from_constituency(c)
        except IndexError:
            print "ERROR: Could not load %s! Please check data " % c
            continue
    print 'GOV Setup in %ds'%(time.time()-start)

    


