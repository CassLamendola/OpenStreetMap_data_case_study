import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

osm_file = open("portland_oregon.osm", "r")

# Find out if any 'tags' have problem characters.

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

def key_type(element, keys):
    if element.tag == "tag":
        if lower.match(element.attrib['k']):
            keys["lower"] += 1
        elif lower_colon.match(element.attrib['k']):
            keys["lower_colon"] += 1
        elif problemchars.match(element.attrib['k']):
            keys["problemchars"] += 1
        else:
            keys["other"] += 1
    return keys

def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys

pprint.pprint(process_map(osm_file))