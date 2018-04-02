from bs4 import BeautifulSoup
import requests as r
import re
from shapely.geometry import Point
import json
import sqlite3

con = sqlite3.connect("libraries.db")

def setup_table(con=con):
    cur = con.cursor()
    cur.execute("""
    DROP TABLE IF EXISTS libraries;
    """)
    con.commit()
    cur.execute("""
    CREATE TABLE libraries (
        name text,
        lat numeric,
        long numeric,
        website text
    )
    """)
    con.commit()



#lib_page = r.get("http://www.worldcat.org/libraries/12177")

def parse_map_link(map_link):
    parts = map_link.split(sep="@", maxsplit=1)
    float_results = re.findall(r"[-+]?\d*\.\d+|\d+", parts[1])
    p = Point(float(float_results[0]),float(float_results[1]) )
    return p
    
def load_row(row, con=con):
    cur = con.cursor()
    cur.execute("""
    INSERT INTO libraries VALUES (?,?,?,?)
    
    """, (row['name'], row['lat'], row['long'], row['website']))
    con.commit()

def parse_name(name):
    new_name = re.sub(r'[^a-zA-Z ]',r'', name) 
    return new_name

def get_library(lib_url):
    lib_page = r.get(lib_url, "html.parser")
    lib_soup = BeautifulSoup(lib_page.text)
    lib_data = lib_soup.find(id="lib-data")
    if lib_data is None:
        return None
    library_name = lib_data.find("h1")
    library_maps_link = lib_data.find("a", class_="lib-map-sm")
    library_website = lib_soup.find(id="lib-links").find("a", class_="lib-website")
    if library_name and library_maps_link:
        library_maps_link = library_maps_link.get("href")
        library_name = library_name.get_text()
        library_website = library_website.get("href")
    else:
        return None
    library_point = parse_map_link(library_maps_link)
    library_info = {'name':parse_name(library_name),  'lat':library_point.x, "long":library_point.y, "website":library_website}
    return library_info

libraries = []
setup_table()
for x in range(3,300000):
    try:
        lib_data = get_library("http://www.worldcat.org/libraries/{0}".format(x))
    except KeyboardInterrupt:
        raise
    except:
        True
    if lib_data is not None:
        load_row(lib_data)
    if x % 10000 == 0:
        print("{0} rows processed".format(x))



