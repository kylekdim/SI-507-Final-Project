#SI 507 Final Project
#Name: Kyle Chang
#Section: Wed 10 AM


import requests
import json
import urllib
from bs4 import BeautifulSoup
import sqlite3
import csv

STAFFJSON = 'staff.json'
DBNAME = 'staff.db'
CACHE_FNAME = 'cache.json'

def get_history_data():    
    base_url = "https://www.egr.msu.edu"
    url_end = "/people/directory/all"
    url = base_url + url_end

    # scrape with Beautiful Soup
    page_content = make_request_using_cache(url) #dictonary with html
    soup_content = BeautifulSoup(page_content, "html.parser")

    #print(soup_content) 

    #get the Contact details
    #div_content = soup_content.find(class_ = "view-content")

    #print(div_content)
    #table_body = div_content.find("tbody")
    #table_rows = table_body.find_all("tr")

    person_class = soup_content.find_all("td", class_ = "views-field views-field-title views-align-left")
    #print(person_class)

    results_list = []
    
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


        # create instance for staff member
        results_list.append(Member(name, title, email, phone, department, st_address, room, city, state, zip_code))

    return results_list

# ---------------------------
# Cache Code:
# ---------------------------

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
    conn.commit()

    # ==================================
    # -------- Create Staff Table ------
    # ==================================

    statement = '''
        CREATE TABLE 'Staff' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Name' TEXT NOT NULL,
            'Title' TEXT NOT NULL,
            'StreetAddress' TEXT,
            'Room' TEXT,
            'Department' TEXT,
            'Email' TEXT,
            'Phone' TEXT
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
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'BuildingName' TEXT,
            'StreetAddress' TEXT,
            'City' TEXT,
            'State' TEXT,
            'ZipCode' TEXT
            );
        '''
    try:
        cur.execute(statement)
    except:
        print("Table creation failed at 'Building'. Please try again.")
        
    conn.commit()
            
            #'Street Address' TEXT,
            #'Room' REAL,
            #'City' TEXT,
            #'State' INTEGER,
            #'Zip' REAL,
            #'Phone' TEXT,

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

    addresses =""

    for name in json_data:
        #print(name)
        Name = name
        Title = json_data[name]["title"]
        Department = json_data[name]["department"]
        #print(Title)
        StreetAddress = json_data[name]["st_address"] 
        if "Engineering Research Complex" in StreetAddress: #filter out any entries with this address; it is referring to the main complex
            StreetAddress = "1449 Engineering Research Ct."

        Room = json_data[name]["room"]
        Email = json_data[name]["email"]
        #print(Email)
        Phone = json_data[name]["phone"]

        insert_statement = '''
            INSERT INTO Staff(Name, Title, Department, StreetAddress, Room, Email, Phone) VALUES (?, ?, ?, ?, ?, ?, ?);
        '''

        # execute + commit
        cur.execute(insert_statement, [Name, Title, Department, StreetAddress, Room, Email, Phone])
        conn.commit()

    for name in json_data:
        StreetAddress = json_data[name]["st_address"]
        if "428" in StreetAddress:
            BuildingName = "College of Engineering - Main Building"
        elif "524" in StreetAddress:
            BuildingName = "Farrall Agricultural Engineering Hall"
        elif "775" in StreetAddress:
            BuildingName = "Bio Engineering Facility"
        elif "1497" in StreetAddress:
            BuildingName = "Engineering Research Complex - South"
        elif "1449" in StreetAddress:
            BuildingName = "Engineering Research Complex - Main"
        elif "438" in StreetAddress:
            BuildingName = "Biosystems and Agricultural Engineering Building"
        elif "3815" in StreetAddress:
            BuildingName = "Michigan Biotechnology Institute"
        elif "2857" in StreetAddress:
            BuildingName = "MSU Engineering Research Facility"
        elif "248" in StreetAddress:
            BuildingName = "College of Engineering - Building 2"
        elif "448" in StreetAddress:
            BuildingName = "School of Packaging"
        elif "219" in StreetAddress:
            BuildingName = "Wilson Hall"
        elif "208" in StreetAddress:
            BuildingName = "Trout Building"
        elif "567" in StreetAddress:
            BuildingName = "Biomedical and Physical Science Building"
        elif "408" in StreetAddress:
            BuildingName = "Olds Hall"
        elif "469" in StreetAddress:
            BuildingName = "FSHN Buiding"
        elif "1439" in StreetAddress:
            BuildingName = "Engineering Research Complex - West"
        elif "640" in StreetAddress:
            BuildingName = "Cyclotron Building"
        elif "474" in StreetAddress:
            BuildingName = "Anthony Hall"
        elif "939" in StreetAddress:
            BuildingName = "West Fee Hall"
        elif "427" in StreetAddress:
            BuildingName = "International Center"
        elif "578" in StreetAddress:
            BuildingName = "Chemistry Building"
        elif "423" in StreetAddress:
            BuildingName = "Engineering Library"
        elif "2727" in StreetAddress:
            BuildingName = "MSU Foundation Building"
        elif "288" in StreetAddress:
            BuildingName = "Natural Science Building"
        elif "603" in StreetAddress:
            BuildingName = "Molecular Plant Sciences Building"
        elif "842" in StreetAddress:
            BuildingName = "Case Hall"
        elif "308" in StreetAddress:
            BuildingName = "IM Sports Circle"
        elif "480" in StreetAddress:
            BuildingName = "Natural Resources Building"
        elif "1129" in StreetAddress:
            BuildingName = "Food Safety And Toxicology Building"
        elif "846" in StreetAddress:
            BuildingName = "MSU Clinical Center"
        elif "426" in StreetAddress:
            BuildingName = "Hannah Administration Building"
        elif "619" in StreetAddress:
            BuildingName = "Wells Hall"
        elif "Michigan" in StreetAddress:
            StreetAddress = "220 Trowbridge Rd"
            BuildingName = "Michigan State University - Main"


        City = json_data[name]["city"]
        State = json_data[name]["state"]
        ZipCode = json_data[name]["zip_code"]

        if StreetAddress[:3] not in addresses: #added this part to change address table to unique entries only
            addresses= addresses + StreetAddress

            insert_statement = '''
                INSERT INTO Building(BuildingName, StreetAddress, City, State, ZipCode) VALUES (?, ?, ?, ?, ?);
            '''

            print(StreetAddress[:2])

            # execute + commit
            cur.execute(insert_statement, [BuildingName, StreetAddress, City, State, ZipCode])
            conn.commit()

        else:
            print("will not add address:" + StreetAddress)

    conn.close()

#----------------------------
# Function Calls 
#----------------------------

#Try to expedite code when json file already exists:
try:
    setup_db()
    print("Database has been successfully populated")

except:

    print("Could not instantly create database with json file")
    #### Execute funciton, get_umsi_data, here ####
    egr_titles = {}

    results = get_history_data()

    #print(results) results are class instances

    for person in results:
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

    #### Write out file here ####
    print("Creating a file...")
    egr_staff_file = open("staff.json", "w") # create a json file
    egr_staff_file.write(json.dumps(egr_titles, indent = 4)) # dump the dictionary and format it
    egr_staff_file.close() # close the file
    print("The file has been created successfully.")

    setup_db()
    print("Database has been successfully populated")

    #-----------------------------
    # END OF CODE
    #-----------------------------