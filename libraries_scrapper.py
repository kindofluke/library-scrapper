from bs4 import BeautifulSoup
import requests as r
import re
from shapely.geometry import Point
import json


#lib_page = r.get("http://www.worldcat.org/libraries/12177")

def parse_map_link(map_link):
    parts = map_link.split(sep="@", maxsplit=1)
    float_results = re.findall(r"[-+]?\d*\.\d+|\d+", parts[1])
    p = Point(float(float_results[0]),float(float_results[1]) )
    return p
    

def parse_name(name):
    new_name = re.sub(r'[^a-zA-Z ]',r'', name) 
    return new_name

def get_library(lib_url):
    lib_page = r.get(lib_url, "html.parser")
    lib_soup = BeautifulSoup(lib_page.text)
    lib_data = lib_soup.find(id="lib-data")
    if lib_data is None:
        raise SystemError
    library_name = lib_data.find("h1").get_text()
    library_maps_link = lib_data.find("a", class_="lib-map-sm").get("href")

    library_website = lib_soup.find(id="lib-links").find("a", class_="lib-website").get("href")
    library_point = parse_map_link(library_maps_link)
    library_info = {'name':parse_name(library_name),  'lat':library_point.x, "long":library_point.y, "website":library_website}
    return library_info

libraries = []
for x in range(3,300000):
    try:
        lib_data = get_library("http://www.worldcat.org/libraries/{0}".format(x))
        libraries.append(lib_data)
    except KeyboardInterrupt:
        raise
    except:
        True
    if len(libraries) % 10000 == 0:
        print(len(libraries))


with open('libraries.json', 'w') as jsonfile:
    json.dump(libraries, jsonfile)

