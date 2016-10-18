import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

osm_file = open("portland_oregon.osm", "r")

# Find out if any 'tags' have problem characters.

#lower = re.compile(r'^([a-z]|_)*$')
#lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
#problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

#def key_type(element, keys):
#    if element.tag == "tag":
#        if lower.match(element.attrib['k']):
#            keys["lower"] += 1
#        elif lower_colon.match(element.attrib['k']):
#            keys["lower_colon"] += 1
#        elif problemchars.match(element.attrib['k']):
#            keys["problemchars"] += 1
#        else:
#            keys["other"] += 1
#    return keys

#def process_map(filename):
#    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
#    for _, element in ET.iterparse(filename):
#        keys = key_type(element, keys)
#    return keys

#pprint.pprint(process_map(osm_file))

#########################################

# Search for all unexpected street types

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
street_types = defaultdict(set)

expected_street_names = ["Street", "Avenue", "Boulevard", "Place", "Drive", "Court", "Way", "Road", "Parkway", "Square", "Lane", "Trail", "Commons", "Terrace", "Run", "Circle", "Path", "Loop", "Highway", "Broadway"]

def audit_street_type(street_types, street_name):
	m = street_type_re.search(street_name)
	if m:
		street_type = m.group()
		if street_type not in expected_street_names:
			street_types[street_type].add(street_name)

def print_sorted_dict(d):
	keys = d.keys()
	keys = sorted(keys, key=lambda s: s.lower())
	for k in keys:
		v = d[k]
		print "%s: %s" % (k, v)

def is_street_name(elem):
	return (elem.attrib['k'] == "addr:street")

def audit(osmfile):
	for event, elem in ET.iterparse(osmfile, events=("start",)):
		if elem.tag == "way":
			for tag in elem.iter("tag"):
				if is_street_name(tag):
					audit_street_type(street_types, tag.attrib['v'])
	return street_types

#audit(osm_file)
#print_sorted_dict(street_types)

#########################################

# Look for problematic zip codes

zip_codes = []

def is_zip_code(elem):
	return (elem.attrib['k'] == "addr:postcode")

def audit_zip_codes(zip_code):
	if zip_code[:3] != "972":
		zip_codes.append(zip_code)

def audit_zip(osmfile):
	for event, elem in ET.iterparse(osmfile, events=("start",)):
		if elem.tag == "node":
			for tag in elem.iter("tag"):
				if is_zip_code(tag):
					audit_zip_codes(tag.attrib['v'])
	return zip_codes

#audit_zip(osm_file)
#zip_codes = set(zip_codes)
#print zip_codes

#########################################

# "Fix" abbreviated street names

mapping = { "Ave.": "Avenue",
            "Ave" : "Avenue",
            "AVE": "Avenue",
            "Blvd": "Boulevard",
            "Blvd.": "Boulevard",
            "Dr": "Drive",
            "Dr.": "Drive",
            "Hwy": "Highway",
            "Ln": "Lane",
            "Pkwy": "Parkway",
            "Pky": "Parkway",
            "Rd.": "Road",
            "Rd": "Road",
			"St": "Street",
            "St.": "Street",
            "st.": "Street",
            "street": "Street"
            }

def update_name(name, mapping):
	name = name.split()
	for word in name:
		if word in mapping.keys():
			name.append(mapping[word])
		else:
			name.append(word)
	name = " ".join(name)
	return name

#st_types = audit(osm_file)
#for st_types, ways in st_types.iteritems():
#	for name in ways:
#		better_name = update_name(name, mapping)
		
osm_file.close()