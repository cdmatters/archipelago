import sqlite3
import requests
from lxml import etree
import os

import parl_init_TWFY as pi_TWFY
import parl_init_GOV as pi_GOV
from models import Base

from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker   

def create_database(dbname='sqlite:///parl.db'):
    db_url = dbname

    engine = create_engine(db_url, echo=False)
    Base.metadata.drop_all(engine, checkfirst=True)
    Base.metadata.create_all(engine)
    return engine

def setup_archipelago():
    try:
        engine = create_database()
        session_factory = sessionmaker(bind=engine) 

        pi_TWFY.TWFY_setup(session_factory)
        pi_GOV.GOV_setup(session_factory)
        return (engine, session_factory)
    except: #bad
        if os.path.isfile('parl.db'):
            os.remove('parl.db')
            raise

def is_arch_setup_local():
    return os.path.isfile('parl.db') 


if __name__ == '__main__':
    if not is_arch_setup():
        setup_archipelago()
