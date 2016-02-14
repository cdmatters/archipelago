import sqlite3
import os

class Archipelago(object):

    def __init__(self, database="parl.db"):
        if not os.path.isfile(database):
            #maybe this should go elsewhere.
            print """ERROR: no specified db file etc."""

        self.parl_db = database


    def _execute_query(self, sql_command):
        with sqlite3.connect(self.parl_db) as connection:
            cur = connection.cursor()
            cur.execute(sql_command)

            result = cur.fetchall()
        return result 

    def get_constituencies(self):
        """Return a python list of constituencies in the archipelago database.""" 
        # Throw error if database does not exist """
        request_sql = 'SELECT Constituency FROM MPCommons'
        results = self._execute_query(request_sql)

        return [result[0] for result in  results]

    def get_twitter_users(self):
        """Return a python list of constituencies in the archipelago database.""" 
        # Throw error if database does not exist """
        request_sql = '''SELECT mp.Name, mp.Party, mp.OfficialId, ad.Address
                        FROM  Addresses AS ad 
                        INNER JOIN MPCommons as mp
                        ON mp.OfficialId=ad.OfficialId
                        WHERE ad.AddressType="twitter"
                        ORDER BY mp.Name ASC'''
        results = self._execute_query(request_sql)
         
        return [
                   {   
                    "name":r[0],
                    "party":r[1],
                    "o_id":r[2], 
                    "twitter_url":r[3], 
                    "handle":r[3][20:] 
                    } for r in results 
                ]




