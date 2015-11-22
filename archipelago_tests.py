import parl_init_TWFY
import main_setup

import unittest
import sqlite3
import json
import os


class TestFetchDataMethods(unittest.TestCase):
    def test_constituencies_json_api(self):
        request_data = []

        request_data = parl_init_TWFY.fetch_data_online('getConstituencies', output='json')

        test_reference = [ 
            {"name" : "Aberavon"},
            {"name" : "Aberconwy"},
            {"name" : "Aberdeen North"},
            {"name" : "Aberdeen South"}
        ]

        # test initial records
        self.assertEqual( request_data[0:4], test_reference ) 
        # test number of responses
        self.assertEqual( len(request_data), 650)
        # test encoding of accents in unicode
        self.assertEqual( request_data[-3]["name"], u'Ynys M\xf4n') #Ynys Mon w circumflex

    def test_mp_and_office_json_api(self):
        request_data = []

        request_data = parl_init_TWFY.fetch_data_online('getMPs', '&party=Liberal')

        test_reference = [
            {
                "name": "Mark Williams",
                "office": 
                    [   
                        {
                        "dept": "Welsh Affairs Committee",
                        "from_date": "2015-07-13", 
                        "to_date": "9999-12-31", 
                        "position": "Member"
                        }
                    ],
                "member_id": "40728", 
                "person_id": "11489", 
                "party": "Liberal Democrat",
                "constituency": "Ceredigion"
            }

        ]

        # test first record
        self.assertEqual( request_data[0:1], test_reference ) 
        # test number of responses
        self.assertEqual( len(request_data), 8)

    def test_build_mp_and_office_tuple_list(self):

        test_data = [ 
            {
                "name": "Mark Williams",
                "office": 
                    [   
                        {
                        "dept": "Welsh Affairs Committee",
                        "from_date": "2015-07-13", 
                        "to_date": "9999-12-31", 
                        "position": "Member"
                        },
                        {
                        "dept": "Foreign Office",
                        "from_date": "2015-07-13", 
                        "to_date": "9999-12-31", 
                        "position": "Foreign Secretary"
                        }
                    ],
                "member_id": "40728", 
                "person_id": "11489", 
                "party": "Liberal Democrat",
                "constituency": "Ceredigion"
            },
            {   
                "name": "William Marks",
                "office": [],
                "member_id": "40730", 
                "person_id": "11491", 
                "party": "Labour",
                "constituency": "York Outer"
            }
        ]
        
        test_reference = (
            [
                (
                    "Mark Williams",
                    "Liberal Democrat", 
                    40728, 
                    11489,
                    "Ceredigion"
                ),(
                    "William Marks",
                    "Labour", 
                    40730, 
                    11491,
                    "York Outer"
                ) 
            ],
            [
                (
                    11489,
                    "Welsh Affairs Committee",
                    "2015-07-13",
                    "9999-12-31",
                    "Mark Williams",
                    "Member"
                ),(
                    11489,
                    "Foreign Office",
                    "2015-07-13", 
                    "9999-12-31", 
                    "Mark Williams",
                    "Foreign Secretary"
                )
            ]
        )

        processed_data = parl_init_TWFY.build_mp_and_office_lists(test_data)

        self.assertEqual(processed_data, test_reference)


class TestDatabaseMethods(unittest.TestCase):
    def setUp(self):
        self.test_db = "test.db"
        main_setup.create_database(self.test_db)

    def tearDown(self):
        os.remove(self.test_db)

    def test_load_constituencies(self):

        parl_init_TWFY.load_constituencies(self.test_db)

        with sqlite3.connect(self.test_db) as connection:
            cur = connection.cursor()
            cur.execute("SELECT * FROM MPCommons")

            loaded_constituencies = cur.fetchall()

            test_reference = [
                (None, u'Worsley and Eccles South', 0, None, None, 0, 0, 0),
                (None, u'Worthing West', 0, None, None, 0, 0, 0),
                (None, u'Wrexham', 0, None, None, 0, 0, 0),
                (None, u'Wycombe', 0, None, None, 0, 0, 0),
                (None, u'Wyre and Preston North', 0, None, None, 0, 0, 0), 
                (None, u'Wyre Forest', 0, None, None, 0, 0, 0),
                (None, u'Wythenshawe and Sale East', 0, None, None, 0, 0, 0),
                (None, u'Yeovil', 0, None, None, 0, 0, 0),
                (None, u'Ynys M\xf4n', 0, None, None, 0, 0, 0),
                (None, u'York Central', 0, None, None, 0, 0, 0), 
                (None, u'York Outer', 0, None, None, 0, 0, 0)
            ]
            
            self.assertEqual( loaded_constituencies[-11:], test_reference)

    def test_load_mp_details(self):

        parl_init_TWFY.load_constituencies(self.test_db) # isolated and tested separately

        parl_init_TWFY.load_mp_details(self.test_db)

        with sqlite3.connect(self.test_db) as connection:
            cur = connection.cursor()
            cur.execute("SELECT * FROM MPCommons")

            loaded_mps = cur.fetchall()
            print loaded_mps
            mp_test_reference = [
                (None, u'Worsley and Eccles South', 0, None, None, 0, 0, 0),
                (None, u'Worthing West', 0, None, None, 0, 0, 0),

            ]

            self.assertEqual( loaded_mps[-4:], mp_test_reference )

            cur.execute("SELECT * FROM Offices")
            loaded_offices = cur.fetchall()

            print loaded_offices
            offices_test_reference = [
            ]

            self.assertEqual( loaded_officess[-4:], offices_test_reference )


if __name__ == '__main__':
    unittest.main(verbosity=2)