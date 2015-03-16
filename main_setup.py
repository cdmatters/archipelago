import sqlite3
import requests
from lxml import etree
import os
import TWFY_key  #a file; only contains:  key = 'your_key_string'
import parl_init_TWFY as pi_TWFY
import parl_init_GOV as pi_GOV


def create_database():
    if os.path.isfile('parl.db'):
        os.remove('parl.db')
    with sqlite3.connect('parl.db') as connection:
        cur = connection.cursor()
        cur.execute("CREATE TABLE MPCommons (Name Text, Constituency Text, MP Boolean,\
                                            Party Text, ImageUrl Text, MemberId Number,\
                                            PersonId Number, OfficialId Number)")
        cur.execute("CREATE TABLE Offices  (PersonId Number, Office Text,\
                                            StartDate Text, EndDate Text, Name Text)")
        cur.execute("CREATE TABLE Addresses (OfficialId Number, Type Text, Address Text)")


def main_setup():
    create_database()
    pi_TWFY.TWFY_setup()
    pi_GOV.GOV_setup()


if __name__ == '__main__':
    main_setup()