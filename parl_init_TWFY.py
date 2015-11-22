#create all required databases (if not existent)
#populate the databases with information drawn from TWFY API
import sqlite3
import requests
from lxml import etree
import os
import TWFY_key  #a file; only contains:  key = 'your_key_string'
import time
import json


##############
key = TWFY_key.key
output = 'xml'
site= 'http://www.theyworkforyou.com/'
base = 'api/%s?key=%s&output=%s' % ('%s', key, output)
base_template = 'api/%s?key=%s&output=%s'
##############


def fetch_xml_online(base_arg, bonus_arg=''):
    url = site + base%base_arg + bonus_arg
    
    data_request = requests.get(url)
    data_req_string = data_request.content
    data_xml = etree.fromstring(data_req_string)

    return data_xml

def fetch_data_online(request_type, bonus_arg='', output='json'):
    url = site + base_template%(request_type, key, output) + bonus_arg

    data_request = requests.get(url)
    data_req_string = data_request.text
    
    fetched_data = None
    if output == 'json':
        fetched_data = json.loads(data_req_string, 'unicode')
    # add functionality for xml if necessary & time 
    return fetched_data


def load_constituencies(database='parl.db'):
    constituencies_json = fetch_data_online('getConstituencies')
    constituencies = [(c["name"],) for c in constituencies_json] #tuple for 'executemany' statement
    
    with sqlite3.connect(database) as connection:
        cur = connection.cursor()
        cur.execute('DELETE from MPCommons')
        cur.executemany("INSERT INTO MPCommons \
                        VALUES(null,?, 0, null,null,0,0,0)", constituencies)
        connection.commit()

def build_mp_and_office_lists(mp_details_json):
    # this could be a one liner fn. don't.
    mp_details = [
        (
            mp["name"],
            mp["party"],
            int(mp["member_id"]),
            int(mp["person_id"]),
            mp["constituency"]
        ) 
        for mp in mp_details_json
    ]

    office_details = [
        (
            int(mp["person_id"]),
            office["dept"],
            office["from_date"],
            office["to_date"],
            mp["name"],
            office["position"]
        ) 
        for mp in mp_details_json 
        if "office" in mp.keys()
        for office in mp["office"] ]

    return (mp_details, office_details)
    


def return_mp_and_office_details_from_xml(mp_xml):
    mps_list = []
    offices_list = []

    name_xml = mp_xml.find('name')
    if name_xml is None:
        name_xml = mp_xml.find('full_name')

    mps_list.append((
                    name_xml.text, 
                    mp_xml.find('party').text,
                    int(mp_xml.find('member_id').text),
                    int(mp_xml.find('person_id').text),
                    mp_xml.find('constituency').text,
                    ))

    if mp_xml.find('office') is not None:
        jobs = mp_xml.find('office')
        for job in jobs.findall('match'):
            title = job.find('position').text
            if title == None:
                title = job.find('dept').text
                
            offices_list.append((
                                int(mp_xml.find('person_id').text),
                                title,
                                job.find('from_date').text,
                                job.find('to_date').text,
                                name_xml.text,
                                ))
    return (mps_list, offices_list)


def load_mp_details(database='parl.db'):  
    mps_list = []
    offices_list = []

    parties = ['conservative', 'labour', 'liberal', 'green', 'independent', 'ukip',
                    'DUP', 'sinn fein', 'sdlp', 'plaid', 'scottish']
    
    #collate details from major parties & insert names into db
    for party in parties:
        mps_and_offices_json = fetch_data_online("getMPs", "&party=%s"%party)
        party_mps, party_offices = build_mp_and_office_lists(mps_and_offices_json)

        mps_list.extend(party_mps)
        offices_list.extend(party_offices)
      
    with sqlite3.connect(database) as connection:
        cur = connection.cursor()
        cur.executemany('UPDATE MPCommons SET Name=?,Party=?,MP=1,MemberId=?,PersonId=?\
                        WHERE Constituency=?', mps_list)  
        mps_list = []

    #collate details from minor parties 
        cur.execute('SELECT Constituency FROM MPCommons WHERE MP=0')
        empty_seats = cur.fetchall()
        
        for seat in empty_seats:
            seat_json = fetch_data_online('getMP', '&constituency=%s'%seat)
            
            if "error" in seat_json.keys():
                print seat_json["error"]
                print "***WARNING***: Check by-election for: %s" % seat[0]
                continue
            seat_json["name"] = seat_json["full_name"]
            mp, office = build_mp_and_office_lists([seat_json])

            mps_list.extend(mp)
            offices_list.extend(office)

    #input remaining data and offices into databases
        cur.executemany('INSERT INTO Offices VALUES(?,?,?,?,?,?)', offices_list)
        cur.executemany('UPDATE MPCommons SET Name=?,Party=?,MP=1,MemberId=?,PersonId=?\
                        WHERE Constituency=?', mps_list)
        connection.commit()

def download_images_from_person_id(person_id):
    image_req = requests.get(site+'images/mps/%d.jpg'%person_id)
    with open('profile_images/%d.jpg'%person_id, 'w') as img:
        img.write(image_req.content)
        img.close()

def load_images_for_imageless_mps():
    if not os.path.exists('profile_images'):
        os.makedirs('profile_images')
    with sqlite3.connect('parl.db') as connection:
        cur = connection.cursor()
        cur.execute('SELECT PersonId FROM MPCommons WHERE ImageUrl IS NULL')
        
        mps_missing_images = cur.fetchall()
        for mp_tuple in mps_missing_images:
            person_id = mp_tuple[0]
            download_images_from_person_id(person_id)
            #insert in for loop incase interrupted
            cur.execute('UPDATE MPCommons SET ImageUrl=? WHERE PersonId=?',
                           ('images/mps/%s.jpg'%person_id, person_id)) 
            connection.commit()

def TWFY_setup():
    start = time.time()
    load_constituencies()
    load_mp_details()
    load_images_for_imageless_mps()
    print 'TWFY Setup in %ds'%(time.time()-start)

if __name__ == '__main__':
    TWFY_setup()



