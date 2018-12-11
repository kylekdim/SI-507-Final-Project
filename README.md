# SI-507-Final-Project
Fall 2018 SI 507 Final Project

<p><U>MSU Engineering Staff Database</U></p>

<p><b>Data Extraction Method:</b> Crawling and Scraping</p>
<p><b>Data Source:</b> https://www.egr.msu.edu/people/directory/all/</p>
<p><b>External credit:</b> base.html template with bootstrap navbar code used from template provided in SI664, creator/instructor: Anthony Whyte

<p><b>Cached Data:</b> cache.json<br>
<b>Formatted Scraping Data:</b> staff.json<br>
<b>SQL Database:</b> staff.db</p>

<b>Program purpose:</b>
1. Crawl and Scrape MSU's Engineering Staff Directory <a href="https://www.egr.msu.edu/people/directory/all/">Data Source</a>
2. Insert scraping data into SQL database
3. Generate a flask website with SQL database query results populating the website's content

<b>How to run:</b> 
1. Clone this repository or duplicate the files and directories contained within it.
2. Launch a virtual machine in your terminal.
3. Install Requirements.txt
4. Decide how quickly you'd like the flask website to deploy, based on how much data this program is processing.

    - Slow (~18 minutes), with new crawling and scraping requests: delete cache.json AND staff.json from the project directory.

    - Medium (~2 minutes), with retrieving crawling and scraping data from cache: delete staff.json

    - Fast (~ 5 seconds), with immediately generating the database from json and deploying flask app with query info fed to routes: KEEP BOTH cache.json AND staff.json

5. Launch SI507_final_proj.py.
6. Navigate to http://127.0.0.1:5000/ in your browser when prompted.

(No need to sign up for Plotly, as the graphs inserted into the site use plotly's javascript CDN)

<b>Detailed Workflow:</b> (More granular comments in SI507_final_proj.py and SI507_final_proj_test.py)
1. Check for cache, and open it for future processing if it exists. Create a new dictionary that will hold contents for a cache of a request.get from the Data Source.
2. Try to set up a SQL database based on a parsed Json file generated from a previous request. If that Json file doesn't exist, causing the database setup to fail, then the program will call a function that is meant to:
3. Get the contents of the Engineering directory website. If a page has already been cached, retrieve the page contents from the cache. Parse the page contents with Beautiful Soup to get data points tied to a Staff Member: first name, last name, title, email address, etc. Store these data points as class attributes for staff members, and return a list of these class instances to the program body.
4. Format each class instance for a staff member for writing to a json file. This Json file is a consolidated record of all of the data points we were looking for about a Staff Member.
5. Set up a SQL database based on the formatted Json file produced earlier. Data is normalized with if/elif statements due to inconsistent manual entry from the Data Source. The database is split into 3 tables: Staff, Buildings, and Departments. The Staff Table has foreign key relationships with Building's and Department's primary keys.
6. Based on the information loaded into the SQL database, deploy a flask app locally to http://127.0.0.1:5000/.

<b>Final Product Overview:</b>

The flask website I have created contains the following routes:

1. index: A simple homepage with a basic description of the website.
2. staff: An exhaustive list of all Engineering staff members with their departments next to their name. The number of staff members is shown at the top header.
3. profile: Contains a staff member's detailed information. Name, Phone, Email, etc.
4. building: This is a list of buildings where Engineering staff members have offices. A plotly bar chart shows how many staff members are in each building. A number of buildings is shown above the list.
5. building staff: This is a list of staff members in a building. It features a plotly map with the location of the building noted. The MapBox key exposed in the template is a read-only-privileged, public-facing key.
6. dept: This is a list of all departments that Engineering staff members are employed under. A plotly bar chart shows the distribution of staff members to departments. The number of departments is also displayed.
7. dept staff: This is a list of all of the staff members aligned to a specific department. The name of the department featured is also displayed.


