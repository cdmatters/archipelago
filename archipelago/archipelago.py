import sqlite3
import os

from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker  

from setup.models import MPCommons, Address, Office
from setup import setup_archipelago


class Archipelago(object):

    # totally run into problems if more than one db
    _db_url = None 
    _engine = None 
    _session_factory = sessionmaker()
    
    def __init__(self, database="sqlite:///parl.db"):
        if not self._engine:
            self._engine = create_engine(database, echo=False)
            self._session_factory.configure(bind=self._engine)

        if  not self._engine.has_table(MPCommons.__tablename__) or \
            not self._engine.has_table(Address.__tablename__) or \
            not self._engine.has_table(Office.__tablename__): 
           self._engine, self._session_factory = setup_archipelago()


        self.session = self._session_factory()
        self.parl_db = database


    def _execute_query(self, sql_command):
        with sqlite3.connect(self.parl_db) as connection:
            cur = connection.cursor()
            cur.execute(sql_command)

            result = cur.fetchall()
        return result 

    def get_constituencies(self):
        """Return a python list of constituencies in the archipelago database.""" 

        return [constit[0] for constit in self.session.query(MPCommons.Constituency).all()]

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




