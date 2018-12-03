#SI 507 Final Project
#Name: Kyle Chang
#Section: Wed 10 AM

#P26 is last page

import requests
import json
import urllib
from bs4 import BeautifulSoup

def get_history_data(page):    
    base_url = "https://lsa.umich.edu/"
    url_end = "history/people.html#page=" + str(page)
    url = "https://www.egr.msu.edu/people/directory/all"

    # scrape with Beautiful Soup
    page_content = make_request_using_cache(url) #dictonary with html
    soup_content = BeautifulSoup(page_content, "html.parser")

    print(soup_content) 

    # get the Contact details
    div_content = soup_content.find(id = "people-list")

    #print(div_content)

    person_class = div_content.find_all(class_ = "person")

    results_list = []
    
    #Examine content and set variables, converting to appropriate data types as needed

    for item in person_class:
        url_person = item.find("a")["href"] # get the node
        details_url = base_url + url_person # format the URL
        details_page_text = make_request_using_cache(details_url) #call the request/cache pull function
        details_page_soup = BeautifulSoup(details_page_text, "html.parser") #call beautiful soup function to parse the request data

        # get staff member's name
        name_section = details_page_soup.find(class_ = "pageTitle")
        name = name_section.find("h1").text

        # get staff member's title
        title_section = details_page_soup.find(class_ = "info")
        title = title_section.find(class_ = "title").text

        # get staff member's email
        email_section = details_page_soup.find(class_ = "info")
        email = email_section.find("a")["href"]

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
        print("Getting cached data from file...")
        return CACHE_DICTION[unique_ident]
    else:
        print("Making a request for new data...")
        # make the request and cache the new data
        resp = requests.get(url, headers=header)
        print(resp.content)
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

#----------------------------
# Function Calls 
#----------------------------

#### Execute funciton, get_umsi_data, here ####
history_titles = {}

for i in range(1, 26):
    for person in get_history_data(i):
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