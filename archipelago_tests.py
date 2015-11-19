import unittest
import parl_init_TWFY

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



if __name__ == '__main__':
    unittest.main()