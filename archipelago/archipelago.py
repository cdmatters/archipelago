import sqlite3


def get_constituencies(database='parl.db'):
    """Return a python list of constituencies in the archipelago database.""" 
    # Throw error if database does not exist """
    with sqlite3.connect(database) as connection:
        cur = connection.cursor()
        cur.execute('SELECT Constituency FROM MPCommons')

        constituency_list = [result[0] for result in  cur.fetchall()]
        
    return constituency_list


