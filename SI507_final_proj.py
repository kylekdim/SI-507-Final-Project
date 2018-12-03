#SI 507 Final Project
#Name: Kyle Chang
#Section: Wed 10 AM


import requests
import json
import urllib
from bs4 import BeautifulSoup
import sqlite3
import csv

def get_history_data():    
    base_url = "https://www.egr.msu.edu/"
    url_end = "people/directory/all"
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
        url_person = item.find("a")["href"] # get the node
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
            email = email_section.find("a")["href"]
        except:
            email = ""

        # create instance for staff member
        results_list.append(Member(name, title, email))

    return results_list

# ---------------------------
# Cache Code:
# ---------------------------

CACHE_FNAME = "cache.json"
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
        print("Getting cached data from..." + url)
        return CACHE_DICTION[unique_ident]
    else:
        print("Making a request for new data from..." + url)
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
    def __init__(self, name, title, email):
        self.name = name
        self.title = title
        self.email = email


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

    #statement = '''
        #DROP TABLE IF EXISTS 'Countries';
    #'''
    
    #cur.execute(statement)
    conn.commit()

    # ==================================
    # -------- Create Staff Table -------
    # ==================================

    statement = '''
        CREATE TABLE 'Staff' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Name' TEXT NOT NULL,
            'Title' TEXT NOT NULL,
            'Email' TEXT,
            'Street Address' TEXT,
            'Room' REAL,
            'City' TEXT,
            'State' INTEGER,
            'Zip' REAL,
            'Phone' TEXT,
            );
        '''
    try:
        cur.execute(statement)
    except:
        print("Table creation failed at 'Staff'. Please try again.")
        
    conn.commit()


#----------------------------
# Function Calls 
#----------------------------

#### Execute funciton, get_umsi_data, here ####
history_titles = {}

results = get_history_data()

for person in results:
    history_titles[person.name]  = {
        "title": person.title,
        "email": person.email
    }

#### Write out file here ####
print("Creating a file...")
history_staff_file = open("directory_dict.json", "w") # create a json file
history_staff_file.write(json.dumps(history_titles, indent = 4)) # dump the dictionary and format it
history_staff_file.close() # close the file
print("The file has been created successfully.")

#-----------------------------
# END OF CODE
#-----------------------------