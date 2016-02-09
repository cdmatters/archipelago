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


