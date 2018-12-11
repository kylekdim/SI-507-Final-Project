import unittest
from SI507_final_proj import *

class TestMembersPullParse(unittest.TestCase): #Test the data scraped from the MSU EGR directory, parsed by BS4

    def member_is_in_member_list(self, member_name, member_addr, member_list): #Helper function to check if a staff member appears in a request for staff members, called below
        for member in member_list:
            if member_name == member.name and member_addr == member.st_address:
                return True
        return False        

    def get_member_from_list(self, member_name, member_list): #Helper function to get a specific named member in a request for staff members, called below
        for member in member_list:
            if member_name == member.name:
                return member
        return None

    def setUp(self): #member_list makes a request for data with get_egr_data, 
        self.member_list = get_egr_data()
        self.ricardo_ma = self.get_member_from_list('Ricardo Mejia-Alvarez', self.member_list) #check if this name is in the response data

    def test_staff_pull(self):
        self.assertEqual(len(self.member_list), 453) #ensure the len of member list returned from request = 453
        self.assertTrue(self.member_is_in_member_list('Ricardo Mejia-Alvarez',
            '1449 Engineering Research Complex', self.member_list)) #Check if Ricardo is in the list returned from request through his Name and Street Address.

    def test_member(self):
        self.assertEqual(self.ricardo_ma.name, 'Ricardo Mejia-Alvarez') #Check to see if the Richardo instance attributes match what we expect in member_list 
        self.assertEqual(self.ricardo_ma.title, 'Assistant Professor')
        self.assertEqual(self.ricardo_ma.email, 'rimejal@msu.edu')
        self.assertEqual(self.ricardo_ma.phone, '217-649-6583')
        self.assertEqual(self.ricardo_ma.department, 'Mechanical Engineering')
        self.assertEqual(self.ricardo_ma.st_address, '1449 Engineering Research Complex')
        self.assertEqual(self.ricardo_ma.room, 'A117')
        self.assertEqual(self.ricardo_ma.city, 'East Lansing')
        self.assertEqual(self.ricardo_ma.state, 'MI')
        self.assertEqual(self.ricardo_ma.zip_code, '48824')

class TestJsonOutput(unittest.TestCase): #test the content of the formatted json file
    
    def test_read_json_data(self): #reach name 122 on the STAFFJSON file, and compare it to what we'd expect based on the cache content. Here I am checking for the right name and email.

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



class TestDatabase(unittest.TestCase): #these tests are meant to test the SQL database constructed from Json data.

    def test_building_table(self): #test the building table to ensure that a building that we think should be in there is there, also to ensure right number of buildings
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
        self.assertEqual(len(result_list), 2) #Ensure that there are only 2 matches for this zip code, as expected
        self.assertEqual(result_list[1][2], 42.72463) #Check the latitude of the second building

        conn.close()

    def test_staff_table(self): 
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT LastName FROM Staff' #Get all last names

        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Keddle',), result_list) #Test for presence of this name
        self.assertEqual(len(result_list), 452) #Test to ensure that the right amount of people are showing in the staff table

        sql = '''
            SELECT LastName, Department, Title, Email FROM Staff
            WHERE Department="Mechanical Engineering"
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(len(result_list), 81) #Ensure there are 81 members in the ME dept
        self.assertIn(('Toulson', 'Mechanical Engineering', 'Associate Professor', 'toulson@msu.edu',), result_list) #Check for a row tuple in the results list
        self.assertEqual(result_list[45][3], 'modaresh@msu.edu') #Check if staff member at this row has the email address expected 

        conn.close()

    def test_dept_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT DepartmentName FROM Department' #Get departments 

        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Composite Materials and Structures Center',), result_list) #Check for presence of a known dept
        self.assertEqual(len(result_list), 15) #Check for 15 departments as expected
        self.assertEqual(result_list[8][0], 'Engineering Development and Alumni Relations') #Check if the 8th row result is the expected department

        conn.close()

    def test_joins(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        #Join staff and building table and check if a known building name shows up in the results.

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
            self.app = app.test_client() #deploy a test client instance of the website to see if it gets a successful 200 status code; check all routes
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
