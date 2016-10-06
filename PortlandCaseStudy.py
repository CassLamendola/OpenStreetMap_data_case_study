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

expected = ["Street", "Avenue", "Boulevard", "Place", "Drive", "Court", "Way", "Road", "Parkway", "Square", "Lane", "Trail", "Commons", "Terrace", "Run", "Circle", "Path", "Loop", "Highway"]

def audit_street_type(street_types, street_name):
	m = street_type_re.search(street_name)
	if m:
		street_type = m.group()
		if street_type not in expected:
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
	for event, elem in ET.iterparse(osm_file, events=("start",)):
		if elem.tag == "way":
			for tag in elem.iter("tag"):
				if is_street_name(tag):
					audit_street_type(street_types, tag.attrib['v'])
	pprint.pprint(dict(street_types))
	return street_types

audit(osm_file)
print_sorted_dict(street_types)

osm_file.close()