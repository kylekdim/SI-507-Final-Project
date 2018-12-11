import unittest
from SI507_final_proj import *

class TestMembersPullParse(unittest.TestCase):

    def member_is_in_member_list(self, member_name, member_addr, member_list):
        for member in member_list:
            if member_name == member.name and member_addr == member.st_address:
                return True
        return False        

    def get_member_from_list(self, member_name, member_list):
        for member in member_list:
            if member_name == member.name:
                return member
        return None

    def setUp(self):
        self.member_list = get_egr_data()
        self.ricardo_ma = self.get_member_from_list('Ricardo Mejia-Alvarez', self.member_list)

    def test_staff_pull(self):
        self.assertEqual(len(self.member_list), 453)
        self.assertTrue(self.member_is_in_member_list('Ricardo Mejia-Alvarez',
            '1449 Engineering Research Complex', self.member_list))

    def test_member(self):
        self.assertEqual(self.ricardo_ma.name, 'Ricardo Mejia-Alvarez')
        self.assertEqual(self.ricardo_ma.title, 'Assistant Professor')
        self.assertEqual(self.ricardo_ma.email, 'rimejal@msu.edu')
        self.assertEqual(self.ricardo_ma.phone, '217-649-6583')
        self.assertEqual(self.ricardo_ma.department, 'Mechanical Engineering')
        self.assertEqual(self.ricardo_ma.st_address, '1449 Engineering Research Complex')
        self.assertEqual(self.ricardo_ma.room, 'A117')
        self.assertEqual(self.ricardo_ma.city, 'East Lansing')
        self.assertEqual(self.ricardo_ma.state, 'MI')
        self.assertEqual(self.ricardo_ma.zip_code, '48824')

class TestJsonOutput(unittest.TestCase):
    
    def test_read_json_data(self):

        json_file = open(STAFFJSON, 'r')
        json_content = json_file.read()
        json_data = json.loads(json_content)
        json_file.close()

        count = 0
        for name in json_data:

            count = count + 1

            if count == 122:
                self.assertEqual(name, "John Foss")
                self.assertEqual(json_data[name]["email"], "foss@egr.msu.edu") 



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
 
 
class FlaskTests(unittest.TestCase):
     
        # executed prior to each test
        def setUp(self):
            self.app = app.test_client()
            self.assertEqual(app.debug, False)
     
        def test_page_index(self):
            response = self.app.get('/', follow_redirects=True)
            self.assertEqual(response.status_code, 200)

        def test_page_staff(self):
            response = self.app.get('/staff', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
        
        def test_page_buildings(self):
            response = self.app.get('/buildings', follow_redirects=True)
            self.assertEqual(response.status_code, 200)

        def test_page_depts(self):
            response = self.app.get('/depts', follow_redirects=True)
            self.assertEqual(response.status_code, 200)

        def test_page_staff_profile(self):
            response = self.app.get('/staff/34', follow_redirects=True)
            self.assertEqual(response.status_code, 200)

        def test_page_building_staff(self):
            response = self.app.get('/buildings/7', follow_redirects=True)
            self.assertEqual(response.status_code, 200)

        def test_page_dept_staff(self):
            response = self.app.get('/depts/4', follow_redirects=True)
            self.assertEqual(response.status_code, 200)

unittest.main()
