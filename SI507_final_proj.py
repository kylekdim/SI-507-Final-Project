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


        # create instance for staff member
        results_list.append(Member(name, title, email, phone, st_address, room))

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
    def __init__(self, name, title, email, phone, st_address, room):
        self.name = name
        self.title = title
        self.email = email
        self.phone = phone
        self.st_address = st_address
        self.room = room


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
        DROP TABLE IF EXISTS 'Address';
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
        CREATE TABLE 'Address' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'StreetAddress' TEXT,
            'Room' TEXT
            );
        '''
    try:
        cur.execute(statement)
    except:
        print("Table creation failed at 'Address'. Please try again.")
        
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



    for name in json_data:
        #print(name)
        Name = name
        Title = json_data[name]["title"]
        #print(Title)
        Email = json_data[name]["email"]
        #print(Email)
        Phone = json_data[name]["phone"]

        insert_statement = '''
            INSERT INTO Staff(Name, Title, Email, Phone) VALUES (?, ?, ?, ?);
        '''

        # execute + commit
        cur.execute(insert_statement, [Name, Title, Email, Phone])
        conn.commit()

    for name in json_data:
        StreetAddress = json_data[name]["st_address"]
        Room = json_data[name]["room"]

        insert_statement = '''
            INSERT INTO Address(StreetAddress, Room) VALUES (?, ?);
        '''

        # execute + commit
        cur.execute(insert_statement, [StreetAddress, Room])
        conn.commit()

    conn.close()

#----------------------------
# Function Calls 
#----------------------------

#### Execute funciton, get_umsi_data, here ####
egr_titles = {}

results = get_history_data()

#print(results) results are class instances

for person in results:
    egr_titles[person.name]  = {
        "title": person.title,
        "email": person.email,
        "phone": person.phone,
        "st_address": person.st_address,
        "room": person.room
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