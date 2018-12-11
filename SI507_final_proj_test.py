import unittest
from SI507_final_proj import *

class TestDatabase(unittest.TestCase):

    def test_building_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT BuildingName FROM Building'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Biomedical and Physical Science Building',), result_list)
        self.assertEqual(len(result_list), 33)

        sql = '''
            SELECT BuildingName, StreetAddress, Latitude, Longitude
            FROM Building
            WHERE ZipCode=48825
            ORDER BY BuildingName DESC
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        #print(result_list)
        self.assertEqual(len(result_list), 2)
        self.assertEqual(result_list[1][2], 42.72463)

        conn.close()

    def test_staff_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT LastName FROM Staff'

        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Keddle',), result_list)
        self.assertEqual(len(result_list), 452)

        sql = '''
            SELECT LastName, Department, Title, Email FROM Staff
            WHERE Department="Mechanical Engineering"
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(len(result_list), 81)
        self.assertIn(('Toulson', 'Mechanical Engineering', 'Associate Professor', 'toulson@msu.edu',), result_list)
        self.assertEqual(result_list[45][3], 'modaresh@msu.edu')

        conn.close()

    def test_dept_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT DepartmentName FROM Department'

        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Composite Materials and Structures Center',), result_list)
        self.assertEqual(len(result_list), 15)
        self.assertEqual(result_list[8][0], 'Engineering Development and Alumni Relations')

        conn.close()

    def test_joins(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = '''
            SELECT BuildingName
            FROM Staff
                JOIN Building
                ON Staff.BuildingId=Building.BuildingId
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Michigan Biotechnology Institute',), result_list)
        conn.close()
'''
class TestBarSearch(unittest.TestCase):

    def test_bar_search(self):
        results = process_command('bars ratings top=1')
        self.assertEqual(results[0][0], 'Chuao')

        results = process_command('bars cocoa bottom=10')
        self.assertEqual(results[0][0], 'Guadeloupe')

        results = process_command('bars sellcountry=CA ratings top=5')
        self.assertEqual(results[0][3], 4.0)

        results = process_command('bars sourceregion=Africa ratings top=5')
        self.assertEqual(results[0][3], 4.0)


class TestCompanySearch(unittest.TestCase):

    def test_company_search(self):
        results = process_command('companies region=Europe ratings top=5')
        self.assertEqual(results[1][0], 'Idilio (Felchlin)')

        results = process_command('companies country=US bars_sold top=5')
        self.assertTrue(results[0][0] == 'Fresco' and results[0][2] == 26)

        results = process_command('companies cocoa top=5')
        self.assertEqual(results[0][0], 'Videri')
        self.assertGreater(results[0][2], 0.79)

class TestCountrySearch(unittest.TestCase):

    def test_country_search(self):
        results = process_command('countries sources ratings bottom=5')
        self.assertEqual(results[1][0],'Uganda')

        results = process_command('countries sellers bars_sold top=5')
        self.assertEqual(results[0][2], 764)
        self.assertEqual(results[1][0], 'France')


class TestRegionSearch(unittest.TestCase):

    def test_region_search(self):
        results = process_command('regions sources bars_sold top=5')
        self.assertEqual(results[0][0], 'Americas')
        self.assertEqual(results[3][1], 66)
        self.assertEqual(len(results), 4)

        results = process_command('regions sellers ratings top=10')
        self.assertEqual(len(results), 5)
        self.assertEqual(results[0][0], 'Oceania')
        self.assertGreater(results[3][1], 3.0)


'''
unittest.main()
