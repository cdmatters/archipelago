from archipelago import parl_init_TWFY, main_setup, parl_init_GOV


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
                "member_id": "40730", 
                "person_id": "11491", 
                "party": "Labour",
                "constituency": "York Outer"
            }
        ]

        processed_data = parl_init_TWFY.build_mp_and_office_lists(test_data)
        
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
            mp_test_reference = [
                (u'Mike Kane', u'Wythenshawe and Sale East', 1, u'Labour', None, 40912, 25220, 0), 
                (u'Marcus Fysh', u'Yeovil', 1, u'Conservative', None, 41102, 25384, 0), 
                (u'Albert Owen', u'Ynys M\xf4n', 1, u'Labour', None, 40873, 11148, 0), 
                (u'Rachael Maskell', u'York Central', 1, u'Labour/Co-operative', None, 41325, 25433, 0), 
                (u'Julian Sturdy', u'York Outer', 1, u'Conservative', None, 41326, 24853, 0)
            ]

            self.assertEqual( loaded_mps[-5:], mp_test_reference )

            cur.execute("SELECT * FROM Offices WHERE Name='John Bercow'")
            loaded_offices = cur.fetchall()

            offices_test_reference = [
                (10040, u"Speaker's Committee for the Independent Parliamentary Standards Authority", u'2015-05-18', u'9999-12-31', u'John Bercow', u'Chair'), 
                (10040, u"Speaker's Committee on the Electoral Commission", u'2015-03-30', u'9999-12-31', u'John Bercow', u'Member'), 
                (10040, u'', u'2009-06-22', u'9999-12-31', u'John Bercow', u'Speaker of the House of Commons'), 
                (10040, u'House of Commons Commission', u'2009-06-22', u'9999-12-31', u'John Bercow', u'Member')
            ]

            self.assertEqual( loaded_offices[-4:], offices_test_reference )

    def test_populate_constitency(self):
        pass

    def test_populate_addresses_from_constituency(self):
        pass


if __name__ == '__main__':
    unittest.main(verbosity=2)