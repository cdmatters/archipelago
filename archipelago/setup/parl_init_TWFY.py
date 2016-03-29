#create all required databases (if not existent)
#populate the databases with information drawn from TWFY API
import sqlite3
import requests
from lxml import etree
import os
import time
import json
from tqdm import tqdm

from models import Office, Address, MPCommons


def load_TWFY_key():
    TWFY_help = '''
    Archipelago requires an API key to collect data from TheyWorkForYou:
    This can be obtained at http://www.theyworkforyou.com/api/key
    Please enter key here: '''

    if not os.environ.get('TWFY_KEY'):
        
        if os.path.isfile('twfy.key'):
            with open('twfy.key', 'r') as f:
                os.environ['TWFY_KEY'] = f.read()
        else:
            TWFY_key = raw_input( TWFY_help )
            os.environ['TWFY_KEY'] = TWFY_key
            with open('twfy.key', 'w') as f:
                f.write(TWFY_key)

load_TWFY_key()
##############
key = os.environ['TWFY_KEY']
output = 'json'
site= 'http://www.theyworkforyou.com/'
base = 'api/%s?key=%s&output=%s' % ('%s', key, output)
base_template = 'api/%s?key=%s&output=%s'
##############

def fetch_data_online(request_type, bonus_arg='', output='json'):
    url = site + base_template%(request_type, key, output) + bonus_arg

    data_request = requests.get(url)
    data_req_string = data_request.text
    
    fetched_data = None
    if output == 'json':
        fetched_data = json.loads(data_req_string, 'unicode')
    # add functionality for xml if necessary & time 
    return fetched_data


def load_constituencies(session):
    constituencies_json = fetch_data_online('getConstituencies')
    mp_list = [MPCommons(Constituency=c["name"]) for c in constituencies_json]

    session.add_all(mp_list)
    

def build_mp_and_office_lists(mp_details_json):
    # this could be a one liner fn. don't.
    mp_details = [
        {
            'name':mp["name"],
            'party':mp["party"],
            'member_id':int(mp["member_id"]),
            'person_id':int(mp["person_id"]),
            'constituency':mp["constituency"]
        } 
        for mp in mp_details_json
    ]

    office_details = [
        {
            'person_id':int(mp["person_id"]),
            'department':office["dept"],
            'start_date':office["from_date"],
            'end_date':office["to_date"],
            'name':mp["name"],
            'title':office["position"]
        } 
        for mp in mp_details_json 
        if "office" in mp.keys()
        for office in mp["office"] ]

    return (mp_details, office_details)

def load_mp_details(session):  
    mps_list = []
    offices_list = []

    parties = ['conservative', 'labour', 'liberal', 'green', 'independent',
        'ukip', 'DUP', 'sinn fein', 'sdlp', 'plaid', 'scottish']
    
    #collate details from major parties & insert names into db
    for party in parties:
        mps_and_offices_json = fetch_data_online("getMPs", "&party=%s"%party)
        party_mps, party_offices = build_mp_and_office_lists(mps_and_offices_json)

        mps_list.extend(party_mps)
        offices_list.extend(party_offices)

    for mp in mps_list:
        session.query(MPCommons).filter(MPCommons.Constituency==mp['constituency']).\
            update({
                MPCommons.Name:mp['name'], 
                MPCommons.Party:mp['party'],
                MPCommons.MP:1,  
                MPCommons.MemberId:mp['member_id'],
                MPCommons.PersonId:mp['person_id']
            })


    remaining_mp_list = []

    for seat in session.query(MPCommons.Constituency).filter(MPCommons.MP==0):
        seat_json = fetch_data_online('getMP', '&constituency=%s'%seat)
        
        if "error" in seat_json.keys():
            print seat_json["error"]
            print "***WARNING***: Check by-election for: %s" % seat
            continue
        seat_json["name"] = seat_json["full_name"]
        mp, office = build_mp_and_office_lists([seat_json])

        remaining_mp_list.extend(mp)
        offices_list.extend(office)

    for mp in remaining_mp_list:
        session.query(MPCommons).filter(MPCommons.Constituency==mp['constituency']).\
            update({
                MPCommons.Name:mp['name'], 
                MPCommons.Party:mp['party'],
                MPCommons.MP:1,  
                MPCommons.MemberId:mp['member_id'],
                MPCommons.PersonId:mp['person_id']
            })

    # filter unique list of offices
    unique_office_tuple_set = set([ tuple(o_dict.items()) for o_dict in offices_list])
    unique_offices = [dict(unique_tuple) for unique_tuple in unique_office_tuple_set]


    offices= [ Office(PersonId=o['person_id'], Office=o['department'], 
                    StartDate=o['start_date'], EndDate=o['end_date'],
                    Name=o['name'], Title=o['title']
                      ) for o in unique_offices ]   

    session.add_all(set(offices))

def download_images_from_person_id(person_id):
    image_req = requests.get(site+'images/mps/%d.jpg'%person_id)
    with open('profile_images/%d.jpg'%person_id, 'w') as img:
        img.write(image_req.content)
        img.close()

def load_images_for_imageless_mps(session):
    if not os.path.exists('profile_images'):
        os.makedirs('profile_images')
    
    for no_image_mp in tqdm(session.query(MPCommons).filter(MPCommons.ImageUrl==None)):
        download_images_from_person_id(no_image_mp.PersonId)
        no_image_mp.ImageUrl = 'images/mps/%s.jpg'%no_image_mp.PersonId


def TWFY_setup(session_factory):
    start = time.time()
    session = session_factory()
    load_constituencies(session)
    load_mp_details(session)
    # load_images_for_imageless_mps(session)
    session.commit()
    session.close()
    print 'TWFY Setup in %ds'%(time.time()-start)


if __name__ == '__main__':
    TWFY_setup()



