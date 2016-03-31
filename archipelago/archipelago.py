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
    
    def __init__(self, database=None):
        if not self._db_url:
            self._db_url = os.getenv('ARCHIPELAGO_DB', 'sqlite:///parl.db')

        if  database != None:
            # effectively a 'reset' & change db. not ideal. this all needs serious rework.
            self._db_url = database
            self._engine = None
        
        if not self._engine:
            self._engine = create_engine(self._db_url, echo=False)
            self._session_factory.configure(bind=self._engine)

        if  not self._engine.has_table(MPCommons.__tablename__) or \
            not self._engine.has_table(Address.__tablename__) or \
            not self._engine.has_table(Office.__tablename__): 
           self._engine, self._session_factory = setup_archipelago(self._db_url)


        self.session = self._session_factory()

    def get_constituencies(self):
        """Return a python list of constituencies in the archipelago database.""" 

        return [constit[0] for constit in self.session.query(MPCommons.Constituency).all()]

    def get_twitter_users(self):
        """Return a python list of constituencies in the archipelago database.""" 
        
        results = self.session.query(MPCommons, Address.Address).\
            join(MPCommons.Addresses).\
            filter(Address.AddressType=='twitter').\
            order_by(MPCommons.Name).all()

        return [
                   {   
                    "name": MP.Name,
                    "party":MP.Party,
                    "constituency":MP.Constituency,
                    "o_id":MP.OfficialId, 
                    "twitter_url":twitter_url, 
                    "handle":twitter_url[20:] 
                    } for MP, twitter_url in results 
                ]

    def get_mps_by_o_id(self, o_id_list):
        return self.session.query(MPCommons).filter(MPCommons.OfficialId.in_(o_id_list)).order_by(MPCommons.Name).all()





