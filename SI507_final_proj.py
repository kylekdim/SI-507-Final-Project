#SI 507 Final Project
#Name: Kyle Chang
#Section: Wed 10 AM

import sys
import requests
import json
import urllib
from bs4 import BeautifulSoup
import sqlite3
import csv
from flask import Flask, render_template, url_for, g
import plotly.plotly as py

app = Flask(__name__)

STAFFJSON = 'staff.json'
DBNAME = 'staff.db'
CACHE_FNAME = 'cache.json'

#=======================================
#-------Function Declarations-----------
#=======================================

#Function that crawls and scrapes data from MSU EGR directory, and individual profile pages
#Returns list of class instances to be imported into Json file

def get_egr_data():    
    base_url = "https://www.egr.msu.edu"
    url_end = "/people/directory/all"
    url = base_url + url_end

    # scrape with Beautiful Soup
    page_content = make_request_using_cache(url) #dictonary with html
    soup_content = BeautifulSoup(page_content, "html.parser") #parsed html content

    person_class = soup_content.find_all("td", class_ = "views-field views-field-title views-align-left") #find all links to individual profiles

    results_list = [] #this will hold class instances returned to main program, and later be converted to a json file
    
    #Examine content and set variables, converting to appropriate data types as needed

    for item in person_class:
        url_person = item.find("a")["href"] # get the folder structure in link
        details_url = base_url + url_person # format the URL
        details_page_text = make_request_using_cache(details_url) #call the request/cache pull function
        details_page_soup = BeautifulSoup(details_page_text, "html.parser") #call beautiful soup function to parse the request data

        # get staff member's name
        name_section = details_page_soup.find(class_ = "profile-title")
        name = name_section.find(class_ = "active").text

        # get staff member's title
        title_section = details_page_soup.find(class_ = "profile-pro-title")
        title = title_section.find(class_ = "field-content").text

        # get staff member's email
        try:
            email_section = details_page_soup.find(class_ = "views-field views-field-field-ep-email")
            email_raw = email_section.find("a")["href"]
            email = email_raw[7:] 
        except:
            email = ""

        # get staff member's phone
        try:
            phone_section = details_page_soup.find(class_ = "views-field views-field-field-ep-phone-number")
            phone = phone_section.find(class_ = "field-content").text
        except:
            phone = ""

        #get staff member's department
        try:
            department_section = details_page_soup.find(class_ = "field field-name-taxonomy-vocabulary-10 field-type-taxonomy-term-reference field-label-hidden")
            department = department_section.find(class_ = "field-item even").text
        except:
            department = ""

        #get the staff member's street address
        try:
            st_address_section = details_page_soup.find(class_ = "views-field views-field-field-ep-address-rm")
            st_address = st_address_section.find(class_ = "field-content").text
        except:
            st_address = ""

        #get the staff member's room number
        try:
            room_section = details_page_soup.find(class_ = "views-field views-field-field-ep-room-number")
            room = room_section.find(class_ = "field-content").text
        except:
            room = ""

        #get the staff member's city
        try:
            city_section = details_page_soup.find(class_ = "views-field views-field-field-ep-city")
            city = city_section.find(class_ = "field-content").text
        except:
            city = ""

        #get the staff member's state
        try:
            state_section = details_page_soup.find(class_ = "views-field views-field-field-ep-state")
            state = state_section.find(class_ = "field-content").text
        except:
            state = ""

        #get the staff member's zip
        try:
            zip_section = details_page_soup.find(class_ = "views-field views-field-field-ep-zip-code")
            zip_code = zip_section.find(class_ = "field-content").text
        except:
            zip_code = ""


        # create instance for staff member, add it to the results_list declared above
        results_list.append(Member(name, title, email, phone, department, st_address, room, city, state, zip_code))

    return results_list

# ---------------------------
# Cache Code:
# ---------------------------

####### IMPORTANT ######### This 'Try/Except' statement is the first thing executed in this program; it is grouped with cache-
#related functions below.

#Open and load the cache if it exists
try:
    cache_file = open(CACHE_FNAME, "r")
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()

# Start a new cache dictionary if no cache yet   
except:
    CACHE_DICTION = {}

# In the cache, add an entry for this unique call based on the URL
def get_unique_key(url):
    return url

# This function looks for a cache, and either refers to existing data, or makes a new call and saves info in cache
def make_request_using_cache(url):
    header = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
    unique_ident = get_unique_key(url)

    if unique_ident in CACHE_DICTION:
        # access the existing data
        print("Getting cached data from: " + url)
        return CACHE_DICTION[unique_ident]
    else:
        print("Making a request for new data from: " + url)
        # make the request and cache the new data
        resp = requests.get(url, headers=header)
        
        #print(resp.content)
        
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]

# Staff Member Class Declaration
class Member:
    def __init__(self, name, title, email, phone, department, st_address, room, city, state, zip_code):
        self.name = name
        self.title = title
        self.email = email
        self.phone = phone
        self.department = department
        self.st_address = st_address
        self.room = room
        self.city = city
        self.state = state
        self.zip_code = zip_code


#==========================================
# ---------- Initial Database Setup -------
#==========================================

def setup_db():
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
    except:
        print("Database creation failed at startup. Please try again.")

    statement = '''
        DROP TABLE IF EXISTS 'Staff';
    '''
    cur.execute(statement)

    statement = '''
        DROP TABLE IF EXISTS 'Building';
    '''
    
    cur.execute(statement)

    statement = '''
        DROP TABLE IF EXISTS 'Department';
    '''
    
    cur.execute(statement)

    conn.commit()

    # ==================================
    # -------- Create Staff Table ------
    # ==================================

    statement = '''
        CREATE TABLE 'Staff' (
            'StaffId' INTEGER PRIMARY KEY AUTOINCREMENT,
            'FirstName' TEXT NOT NULL,
            'LastName' TEXT NOT NULL,
            'Title' TEXT NOT NULL,
            'StreetAddress' TEXT,
            'BuildingId' INTEGER,
            'Room' TEXT,
            'Department' TEXT,
            'DepartmentId' INTEGER,
            'Email' TEXT,
            'Phone' TEXT,
            FOREIGN KEY(BuildingId) REFERENCES Building(BuildingId),
            FOREIGN KEY(DepartmentId) REFERENCES Department(DepartmentId)
            );
        '''
    try:
        cur.execute(statement)
    except:
        print("Table creation failed at 'Staff'. Please try again.")

    conn.commit()

    # ==================================
    # -------- Create Address Table ----
    # ==================================

    statement = '''
        CREATE TABLE 'Building' (
            'BuildingId' INTEGER PRIMARY KEY AUTOINCREMENT,
            'BuildingName' TEXT,
            'StreetAddress' TEXT,
            'City' TEXT,
            'State' TEXT,
            'ZipCode' TEXT,
            'Latitude' DECIMAL,
            'Longitude' DECIMAL
            );
        '''
    try:
        cur.execute(statement)
    except:
        print("Table creation failed at 'Building'. Please try again.")
        
    conn.commit()

    # ==================================
    # -------- Create Department Table -
    # ==================================

    statement = '''
        CREATE TABLE 'Department' (
            'DepartmentId' INTEGER PRIMARY KEY AUTOINCREMENT,
            'DepartmentName' TEXT
            );
        '''
    try:
        cur.execute(statement)
    except:
        print("Table creation failed at 'Department'. Please try again.")

    conn.commit()
            

    #===========================================
    #------------ Load Json Data ---------------
    #===========================================

    json_file = open(STAFFJSON, 'r')
    json_content = json_file.read()
    json_data = json.loads(json_content)

    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
    except:
        print("Failure. Please try again.")

    addresses ="" #string to store processed addresses to extract unique addresses
    departments ="" #string to store processed depts to extract unique depts

    #------------ Load the Staff Table ----------

    for name in json_data:
        #print(name)
        raw_name = name
        non_space_name = raw_name.strip()
        name_list = non_space_name.split()

        if "Jr." in name_list:
            FirstName = "Robert C."
            LastName = "Ferrier, Jr."
        elif "MEng." in name_list:
            FirstName = "Kyle"
            LastName = "Foster, MEng."
        elif "P.E.," in name_list:
            FirstName = "Venkatesh"
            LastName = "Kodur, Ph.D."
        elif "Associate" in name_list:
            FirstName = "Patrick"
            LastName = "Kwon"

        elif len(name_list) == 2:
            FirstName = name_list[0]
            LastName = name_list[1]
        elif len(name_list) == 3:
            FirstName = name_list[0] + " " + name_list[1]
            LastName = name_list[2]
        elif len(name_list) > 3:
            FirstName = name_list[0] + " " + name_list[1] + " " + name_list[2]
            LastName = name_list[3]


        raw_title = json_data[name]["title"]
        Title = raw_title.strip() #get rid of leading whitespace in titles to get rid of dups

        Department = json_data[name]["department"]
        #print(Title)

        #Normalize the formatting of Street Addresses for staff members
        StreetAddress = json_data[name]["st_address"] 
        if "Engineering Research Complex" in StreetAddress: #filter out any entries with this address; it is referring to the main complex
            StreetAddress = "1449 Engineering Research Ct"
        elif "428" in StreetAddress:
            StreetAddress = "428 S Shaw Ln"
        elif "524" in StreetAddress:
            StreetAddress = "524 S Shaw Ln"
        elif "775" in StreetAddress:
            StreetAddress = "775 Woodlot Dr"
        elif "1497" in StreetAddress:
            StreetAddress = "1497 Engineering Research Ct"
        elif "1439" in StreetAddress:
            StreetAddress = "1439 Engineering Research Ct"
        elif "1449" in StreetAddress:
            StreetAddress = "1449 Engineering Research Ct"
        elif "438" in StreetAddress:
            StreetAddress = "438 S Shaw Ln"
        elif "3815" in StreetAddress:
            StreetAddress = "3815 Technology Blvd"
        elif "2857" in StreetAddress:
            StreetAddress = "2857 Jolly Rd"
        elif "248" in StreetAddress: #this is a typo, 248 does not exist
            StreetAddress = "428 S Shaw Ln"
        elif "448" in StreetAddress:
            StreetAddress = "448 Wilson Rd"
        elif "219" in StreetAddress:
            StreetAddress = "219 Wilson Rd"
        elif "208" in StreetAddress: #this is a typo, there was no street address, only building
            StreetAddress = "469 Wilson Rd"
        elif "567" in StreetAddress:
            StreetAddress = "567 Wilson Rd"
        elif "408" in StreetAddress:
            StreetAddress = "408 W Circle Dr"
        elif "469" in StreetAddress:
            StreetAddress = "469 Wilson Rd"
        elif "1439" in StreetAddress:
            StreetAddress = "1439 Engineering Research Ct"
        elif "640" in StreetAddress:
            StreetAddress = "640 S Shaw Ln"
        elif "474" in StreetAddress:
            StreetAddress = "474 S Shaw Ln"
        elif "939" in StreetAddress:
            StreetAddress = "939 Fee Rd"
        elif "427" in StreetAddress:
            StreetAddress = "427 N Shaw Ln"
        elif "578" in StreetAddress:
            StreetAddress = "578 S Shaw Ln"
        elif "423" in StreetAddress:
            StreetAddress = "423 S Shaw Ln"
        elif "2727" in StreetAddress:
            StreetAddress = "2727 Alliance Dr"
        elif "288" in StreetAddress:
            StreetAddress = "288 Farm Ln"
        elif "603" in StreetAddress:
            StreetAddress = "603 Wilson Rd"
        elif "842" in StreetAddress:
            StreetAddress = "842 Chestnut Rd"
        elif "308" in StreetAddress:
            StreetAddress = "308 W Circle Dr"
        elif "480" in StreetAddress:
            StreetAddress = "480 Wilson Rd"
        elif "1129" in StreetAddress:
            StreetAddress = "1129 Farm Ln"
        elif "846" in StreetAddress:
            StreetAddress = "846 Service Rd"
        elif "426" in StreetAddress:
            StreetAddress = "426 Auditorium Rd"
        elif "619" in StreetAddress:
            StreetAddress = "619 Red Cedar Rd"
        elif "Michigan" in StreetAddress:
            StreetAddress = "220 Trowbridge Rd"

        Room = json_data[name]["room"]
        Room = Room.strip()
        Email = json_data[name]["email"]
        temp_num =[]

        #Consistently format phone numbers by removing inconsistent symbols
        RawPhone = json_data[name]["phone"]
        PhoneA = RawPhone.replace('-', '')
        PhoneB = PhoneA.replace(')', '')
        PhoneC = PhoneB.replace('(', '')
        PhoneUnformatted = PhoneC.replace(' ', '')

        for num in PhoneUnformatted:
            temp_num.append(num)
        temp_num.insert(0,"(")
        temp_num.insert(4,") ")
        temp_num.insert(8,"-")
        Phone = ''.join(temp_num)
        if Phone == "() -":
            Phone =''

        #SQL INSERT statement
        insert_statement = '''
            INSERT INTO Staff(FirstName, LastName, Title, Department, StreetAddress, Room, Email, Phone) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        '''

        # execute + commit
        cur.execute(insert_statement, [FirstName, LastName, Title, Department, StreetAddress, Room, Email, Phone])
        conn.commit()

    for name in json_data:
        #Normalize the formatting of Street Addresses and Building Names (I looked the building names up in Google Maps)
        StreetAddress = json_data[name]["st_address"]

        if "428" in StreetAddress:
            BuildingName = "College of Engineering - Main Building"
            StreetAddress = "428 S Shaw Ln"
            Latitude = 42.724560    # Obtained Lat/Long values manually from https://www.latlong.net/convert-address-to-lat-long.html
            Longitude = -84.481490

        elif "524" in StreetAddress:
            BuildingName = "Farrall Agricultural Engineering Hall"
            StreetAddress = "524 S Shaw Ln"
            Latitude = 42.724670
            Longitude = -84.477170

        elif "775" in StreetAddress:
            BuildingName = "Bio Engineering Facility"
            StreetAddress = "775 Woodlot Dr"
            Latitude = 42.717300
            Longitude = -84.467520

        elif "1497" in StreetAddress:
            BuildingName = "Engineering Research Complex - South"
            StreetAddress = "1497 Engineering Research Ct"
            Latitude = 42.716930
            Longitude = -84.470210

        elif "1439" in StreetAddress:
            BuildingName = "Engineering Research Complex - Aux"
            StreetAddress = "1439 Engineering Research Ct"
            Latitude = 42.716120
            Longitude = -84.470260

        elif "1449" in StreetAddress:
            BuildingName = "Engineering Research Complex - Main"
            StreetAddress = "1449 Engineering Research Ct"
            Latitude = 42.716560
            Longitude = -84.468210

        elif "438" in StreetAddress:
            BuildingName = "Biosystems and Agricultural Engineering Building"
            StreetAddress = "438 S Shaw Ln"
            Latitude = 42.725220
            Longitude = -84.480730

        elif "3815" in StreetAddress:
            BuildingName = "Michigan Biotechnology Institute"
            StreetAddress = "3815 Technology Blvd"
            Latitude = 42.693180
            Longitude = -84.500790

        elif "2857" in StreetAddress:
            BuildingName = "MSU Engineering Research Facility"
            StreetAddress = "2857 Jolly Rd"
            Latitude = 42.682780
            Longitude = -84.471320

        elif "248" in StreetAddress: #this is a typo, 248 does not exist
            BuildingName = "College of Engineering - Main Building"
            StreetAddress = "428 S Shaw Ln"
            Latitude = 42.724560
            Longitude = -84.481490

        elif "448" in StreetAddress:
            BuildingName = "School of Packaging"
            StreetAddress = "448 Wilson Rd"
            Latitude = 42.723190
            Longitude = -84.480030

        elif "219" in StreetAddress:
            BuildingName = "Wilson Hall"
            StreetAddress = "219 Wilson Rd"
            Latitude = 42.721940
            Longitude = -84.488980

        elif "208" in StreetAddress: #this is a typo, there was no street address, only building
            BuildingName = "GM Trout Building"
            StreetAddress = "469 Wilson Rd"
            Latitude = 42.723320
            Longitude = -84.480030

        elif "567" in StreetAddress:
            BuildingName = "Biomedical and Physical Science Building"
            StreetAddress = "567 Wilson Rd"
            Latitude = 42.723310
            Longitude = -84.476550

        elif "408" in StreetAddress:
            BuildingName = "Olds Hall"
            StreetAddress = "408 W Circle Dr"
            Latitude = 42.730840
            Longitude = -84.481110

        elif "469" in StreetAddress:
            BuildingName = "GM Trout Building"
            StreetAddress = "469 Wilson Rd"
            Latitude = 42.723320
            Longitude = -84.480030

        elif "1439" in StreetAddress:
            BuildingName = "Engineering Research Complex - West"
            StreetAddress = "1439 Engineering Research Ct"
            Latitude = 42.716122
            Longitude = -84.470261

        elif "640" in StreetAddress:
            BuildingName = "Cyclotron Building"
            StreetAddress = "640 S Shaw Ln"
            Latitude = 42.724450
            Longitude = -84.473450

        elif "474" in StreetAddress:
            BuildingName = "Anthony Hall"
            StreetAddress = "474 S Shaw Ln"
            Latitude = 42.724990
            Longitude = -84.479120

        elif "939" in StreetAddress:
            BuildingName = "West Fee Hall"
            StreetAddress = "939 Fee Rd"
            Latitude = 42.721800
            Longitude = -84.464800

        elif "427" in StreetAddress:
            BuildingName = "International Center"
            StreetAddress = "427 N Shaw Ln"
            Latitude = 42.726520
            Longitude = -84.480610

        elif "578" in StreetAddress:
            BuildingName = "Chemistry Building"
            StreetAddress = "578 S Shaw Ln"
            Latitude = 42.724820
            Longitude = -84.475420

        elif "423" in StreetAddress:
            BuildingName = "Engineering Library"
            StreetAddress = "423 S Shaw Ln"
            Latitude = 42.725220
            Longitude = -84.477900

        elif "2727" in StreetAddress:
            BuildingName = "MSU Foundation Building"
            StreetAddress = "2727 Alliance Dr"
            Latitude = 42.703590
            Longitude = -84.500050

        elif "288" in StreetAddress:
            BuildingName = "Natural Science Building"
            StreetAddress = "288 Farm Ln"
            Latitude = 42.731060
            Longitude = -84.476800

        elif "603" in StreetAddress:
            BuildingName = "Molecular Plant Sciences Building"
            StreetAddress = "603 Wilson Rd"
            Latitude = 42.723310
            Longitude = -84.475290

        elif "842" in StreetAddress:
            BuildingName = "Case Hall"
            StreetAddress = "842 Chestnut Rd"
            Latitude = 42.724630
            Longitude = -84.487770

        elif "308" in StreetAddress:
            BuildingName = "IM Sports Circle"
            StreetAddress = "308 W Circle Dr"
            Latitude = 42.731780
            Longitude = -84.484060

        elif "480" in StreetAddress:
            BuildingName = "Natural Resources Building"
            StreetAddress = "480 Wilson Rd"
            Latitude = 42.723210
            Longitude = -84.478720

        elif "1129" in StreetAddress:
            BuildingName = "Food Safety And Toxicology Building"
            StreetAddress = "1129 Farm Ln"
            Latitude = 42.721310
            Longitude = -84.475140

        elif "846" in StreetAddress:
            BuildingName = "MSU Clinical Center"
            StreetAddress = "846 Service Rd"
            Latitude = 42.717480
            Longitude = -84.466880

        elif "426" in StreetAddress:
            BuildingName = "Hannah Administration Building"
            StreetAddress = "426 Auditorium Rd"
            Latitude = 42.729720
            Longitude = -84.481490

        elif "619" in StreetAddress:
            BuildingName = "Wells Hall"
            StreetAddress = "619 Red Cedar Rd"
            Latitude = 42.727020
            Longitude = -84.481570

        elif "Michigan" in StreetAddress:
            StreetAddress = "220 Trowbridge Rd"
            BuildingName = "Michigan State University - Main"
            Latitude = 42.719560
            Longitude = -84.489100

        City = json_data[name]["city"]
        if City == "EAST LANSING":
            City = "East Lansing"

        #strip trailing whitespace from state entries
        raw_state = json_data[name]["state"]
        State = raw_state.strip()

        ZipCode = json_data[name]["zip_code"]

        if StreetAddress[:5] not in addresses: #added this part to change address table to unique entries only
            addresses= addresses + StreetAddress

            insert_statement = '''
                INSERT INTO Building(BuildingName, StreetAddress, City, State, ZipCode, Latitude, Longitude) VALUES (?, ?, ?, ?, ?, ?, ?);
            '''

            # execute + commit
            cur.execute(insert_statement, [BuildingName, StreetAddress, City, State, ZipCode, Latitude, Longitude])
            conn.commit()


    for name in json_data:

            DepartmentName = json_data[name]["department"]

            if DepartmentName not in departments: #added this part to change address table to unique entries only
                departments= departments + DepartmentName

                insert_statement = '''
                    INSERT INTO Department(DepartmentName) VALUES (?);
                '''

                # execute + commit
                cur.execute(insert_statement, [DepartmentName])
                conn.commit()



    #populate the BuildingId column in the "Staff" table to populate the foreign key field with "Building"
    add_BuildingId = '''
        UPDATE Staff
        SET (BuildingId) = (SELECT Building.BuildingId FROM Building WHERE Staff.StreetAddress = Building.StreetAddress)
    '''

    cur.execute(add_BuildingId)
    conn.commit()

    add_DepartmentId = '''
        UPDATE Staff
        SET (DepartmentId) = (SELECT Department.DepartmentId FROM Department WHERE Staff.Department = Department.DepartmentName)
    '''

    cur.execute(add_DepartmentId)
    conn.commit()

    conn.close()


@app.route('/')
def index():
    #cur = get_db().cursor()
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

    except:
        print("failed to connect database to web output")

    statement= '''
        SELECT FirstName, LastName, Title, Department FROM Staff
        ORDER BY LastName ASC;
        '''
    data= cur.execute(statement).fetchall()
    
    conn.close()

    return render_template('index.html', data=data)



@app.route('/staff')
def staff():
    #cur = get_db().cursor()
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

    except:
        print("failed to connect database to web output")

    statement= '''
        SELECT FirstName, LastName, Title, Department, StaffId FROM Staff
        ORDER BY LastName ASC;
        '''
    members = cur.execute(statement).fetchall()
    conn.close()

    return render_template('staff.html', members=members)

@app.route('/staff/<int:id>')
def profile(id=None):

    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

    except:
        print("failed to connect database to web output")

    statement = '''
        SELECT * FROM Staff WHERE StaffId = {};
    '''.format(id)

    person= cur.execute(statement).fetchall()
    conn.close()

    return render_template('profile.html', person= person, id=id)

@app.route('/buildings')
def buildings():
    #cur = get_db().cursor()

    x_values= []
    y_values= []

    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

    except:
        print("failed to connect database to web output")

    statement= '''
        SELECT Building.BuildingName, Building.StreetAddress, count(Staff.StaffId) as "Staff Count", Building.BuildingId
        FROM Staff
        LEFT JOIN Building ON Staff.BuildingId = Building.BuildingId
        GROUP BY Building.BuildingName
        ORDER BY "Staff Count" DESC;
        '''
    data= cur.execute(statement).fetchall()

    for building in data:
        x_values.append(building[0])
        y_values.append(building[2])

    conn.close()

    return render_template('buildings.html', data=data, x_values=x_values, y_values=y_values)

@app.route('/buildings/<int:id>')
def building_staff(id=None):

    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

    except:
        print("failed to connect database to web output")

    members_statement= '''
        SELECT FirstName, LastName, Title, Department, StaffId, Building.BuildingName, Building.StreetAddress, Building.City, Building.State, Building.ZipCode FROM Staff
        LEFT JOIN Building ON Staff.BuildingId = Building.BuildingId
        WHERE Staff.BuildingId ={}
        ORDER BY LastName ASC;
        '''.format(id)

    building_statement= '''
        SELECT Building.BuildingName, Building.StreetAddress, Building.City, Building.State, Building.ZipCode FROM Building
        WHERE Building.BuildingId ={};
        '''.format(id)

    latlong_statement= '''
        SELECT Building.BuildingName, Building.Latitude, Building.Longitude FROM Building
        WHERE Building.BuildingId ={};
        '''.format(id)

    members = cur.execute(members_statement).fetchall()
    building = cur.execute(building_statement).fetchall()
    latlong = cur.execute(latlong_statement).fetchall()

    conn.close()

    return render_template('buildingstaff.html', members= members, building=building, id=id, latlong=latlong)

@app.route('/depts')
def depts():
    #cur = get_db().cursor()

    x_values= []
    y_values= []

    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

    except:
        print("failed to connect database to web output")

    statement= '''
        SELECT Staff.Department as "Department", COUNT(Staff.StaffId) as "Staff Count", Staff.DepartmentId
        FROM Staff
        GROUP BY "Department"
        ORDER BY "Department";
        '''
    data= cur.execute(statement).fetchall()

    for dept in data:
        x_values.append(dept[0])
        y_values.append(dept[1])

    conn.close()

    return render_template('depts.html', data=data, x_values=x_values, y_values=y_values)

@app.route('/depts/<int:id>')
def dept_staff(id=None):

    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

    except:
        print("failed to connect database to web output")

    members_statement= '''
        SELECT FirstName, LastName, Title, Department, StaffId FROM Staff
        WHERE DepartmentId ={}
        ORDER BY LastName ASC;
        '''.format(id)

    dept_statement= '''
        SELECT DepartmentName FROM Department
        WHERE DepartmentId ={};
        '''.format(id)


    members = cur.execute(members_statement).fetchall()
    dept = cur.execute(dept_statement).fetchall()

    conn.close()

    return render_template('deptstaff.html', members= members, dept=dept, id=id)

#============================
# Main Body w/ Function Calls 
#============================

dc_error = "Connection to flask site interrupted. Closing program. Re-execute program to continue using the 'MSU EGR Directory'." 


try: #try to run the flask app if the db file exists
    if __name__ == '__main__':
        app.run(debug=True)


except: #If no db file exists, try to expedite code when json file already exists:
    try:
        print("Trying to set up database from parsed json file generated with past use.")
        setup_db()
        print("Database has been successfully populated")

        if __name__ == '__main__':
            app.run(debug=True)


    except: #If a parsed json file doesn't exist, start fresh with getting the scraping data (Call to 'get_egr_data' will check for cache data)
        print("Could not instantly create database with json file")

        egr_titles = {}

        results = get_egr_data() #results is a list of class instances filled with parsed scraping information

        for person in results: #format json file for output to create db
            egr_titles[person.name]  = {
                "title": person.title,
                "department": person.department,
                "email": person.email,
                "phone": person.phone,
                "st_address": person.st_address,
                "room": person.room,
                "city": person.city,
                "state": person.state,
                "zip_code": person.zip_code
            }

        #### Write out Json file here ####
        print("Creating a json database source file...")
        egr_staff_file = open("staff.json", "w") # create a json file
        egr_staff_file.write(json.dumps(egr_titles, indent = 4)) # dump the dictionary and format it
        egr_staff_file.close() # close the file
        print("The json file has been created successfully.")

        setup_db()
        print("Database has been successfully populated")
        if __name__ == '__main__':
            app.run(debug=True)


        #------------------------------
        # END OF CODE
        #-----------------------------