import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
import csv
import codecs
import cerberus
import schema

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

# Look for problematic zip codes. Portland zip codes begin with 972

zip_codes = []

def is_zip_code(elem):
	return (elem.attrib['k'] == "addr:postcode")

def audit_zip_codes(zip_code):
	if zip_code[:3] != "972":
		zip_codes.append(zip_code)
	if len(zip_code) > 5:
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
            "street": "Street",
    		"S.": "South",
			"S": "South",
			"s.": "South",
			"s": "South",
			"south": "South",
			"SE": "Southeast",
			"southeast": "Southeast",
			"SW": "Southwest",
			"southwest": "Southwest",
			"N.": "North",
			"N": "North",
			"n.": "North",
			"n": "North",
			"north": "North",
			"NE": "Northeast",
			"northeast": "Northeast",
			"NW": "Northwest",
			"northwest": "Northwest",
			"E.": "East",
			"E": "East",
			"e.": "East",
			"e": "East",
			"east": "East",
			"W.": "West",
			"W": "West",
			"w.": "West",
			"w": "West",
			"west": "West"
            }

def update_name(name, mapping):
	name = name.split(" ")
	for word in range(len(name)):
		if name[word] in mapping.keys():
			name[word] = mapping[name[word]]
	name = " ".join(name)
	return name

#st_types = audit(osm_file)
#for st_types, ways in st_types.iteritems():
#	for name in ways:
#		better_name = update_name(name, mapping)
#		print name, "->", better_name

#########################################

# "Fix" abbreviated street directions

#for st_types, ways in st_types.iteritems():
#	for name in ways:
#		better_name = update_name(name, mapping)
#		print name, "->", better_name

#########################################

# Look for unexpected keys in way tags

way_keys = set()

def audit_tags(osmfile):
	for event, elem in ET.iterparse(osmfile, events=("start",)):
		if elem.tag == "way":
			for tag in elem.iter():
				if 'k' in tag.attrib:
					way_keys.add(tag.attrib['k'])
	return way_keys

#way_tag_keys = audit_tags(osm_file)
#print way_tag_keys

osm_file.close()

#########################################

# Prepare data for SQL database

osm_path = "portland_oregon.osm"
nodes_path = "nodes.csv"
node_tags_path = "node_tags.csv"
ways_path = "ways.csv"
way_tags_path = "ways_tags.csv"
way_nodes_path = "ways_nodes.csv"

SCHEMA = {
    'node': {
        'type': 'dict',
        'schema': {
            'id': {'required': True, 'type': 'integer', 'coerce': int},
            'lat': {'required': True, 'type': 'float', 'coerce': float},
            'lon': {'required': True, 'type': 'float', 'coerce': float},
            'user': {'required': True, 'type': 'string'},
            'uid': {'required': True, 'type': 'integer', 'coerce': int},
            'version': {'required': True, 'type': 'string'},
            'changeset': {'required': True, 'type': 'integer', 'coerce': int},
            'timestamp': {'required': True, 'type': 'string'}
        }
    },
    'node_tags': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'id': {'required': True, 'type': 'integer', 'coerce': int},
                'key': {'required': True, 'type': 'string'},
                'value': {'required': True, 'type': 'string'},
                'type': {'required': True, 'type': 'string'}
            }
        }
    },
    'way': {
        'type': 'dict',
        'schema': {
            'id': {'required': True, 'type': 'integer', 'coerce': int},
            'user': {'required': True, 'type': 'string'},
            'uid': {'required': True, 'type': 'integer', 'coerce': int},
            'version': {'required': True, 'type': 'string'},
            'changeset': {'required': True, 'type': 'integer', 'coerce': int},
            'timestamp': {'required': True, 'type': 'string'}
        }
    },
    'way_nodes': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'id': {'required': True, 'type': 'integer', 'coerce': int},
                'node_id': {'required': True, 'type': 'integer', 'coerce': int},
                'position': {'required': True, 'type': 'integer', 'coerce': int}
            }
        }
    },
    'way_tags': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'id': {'required': True, 'type': 'integer', 'coerce': int},
                'key': {'required': True, 'type': 'string'},
                'value': {'required': True, 'type': 'string'},
                'type': {'required': True, 'type': 'string'}
            }
        }
    }
}

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

##########################################################
# Helper Functions from "Preparing for Database" problem #
##########################################################

# Yield element if it is the right type of tag
def get_element(osm_file, tags=('node', 'way', 'relation')):
    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

# Raise ValidationError if element does not match schema
def validate_element(element, validator, schema=SCHEMA):
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_strings = (
            "{0}: {1}".format(k, v if isinstance(v, str) else ", ".join(v))
            for k, v in errors.iteritems()
        )
        raise cerberus.ValidationError(
            message_string.format(field, "\n".join(error_strings))
        )

# Extend csv.DictWriter to handle Unicode input
class UnicodeDictWriter(csv.DictWriter, object):

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

# Iteratively process each XML element and write to csv
def process_map(file_in, validate):
    with codecs.open(nodes_path, 'w') as nodes_file, \
         codecs.open(node_tags_path, 'w') as nodes_tags_file, \
         codecs.open(ways_path, 'w') as ways_file, \
         codecs.open(way_nodes_path, 'w') as way_nodes_file, \
         codecs.open(way_tags_path, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

# Clean and shape node or way XML element to Python dict
def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    if element.tag == 'node':
        for attribute in element.attrib:
            if attribute in NODE_FIELDS:
                node_attribs[attribute] = element.attrib[attribute]
        for child in element:
            node_tag = {}
            if PROBLEMCHARS.match(child.attrib["k"]):
                continue
            elif LOWER_COLON.match(child.attrib["k"]):
                node_tag["type"] = child.attrib["k"].split(":",1)[0]
                node_tag["key"] = child.attrib["k"].split(":",1)[1]
                node_tag["id"] = element.attrib["id"]
                node_tag["value"] = child.attrib["v"]
                tags.append(node_tag)
            else:
                node_tag["type"] = "regular"
                node_tag["key"] = child.attrib["k"]
                node_tag["id"] = element.attrib["id"]
                node_tag["value"] = child.attrib["v"]
                tags.append(node_tag)
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        position = 0
        for attrib in element.attrib:
            if attrib in WAY_FIELDS:
                way_attribs[attrib] = element.attrib[attrib]
        for child in element:
            way_tag = {}
            way_node = {}
            if child.tag == "nd":
                way_node["id"] = element.attrib["id"]
                way_node["node_id"] = child.attrib["ref"]
                way_node["position"] = position
                print way_node
                way_nodes.append(way_node)
                position += 1
            if child.tag == "tag":
                if PROBLEMCHARS.match(child.attrib["k"]):
                    continue
                elif LOWER_COLON.match(child.attrib["k"]):
                    way_tag["type"] = child.attrib["k"].split(":",1)[0]
                    way_tag["key"] = child.attrib["k"].split(":",1)[1]
                    way_tag["id"] = element.attrib["id"]
                    way_tag["value"] = child.attrib["v"]
                    tags.append(way_tag)
                else:
                    way_tag["type"] = "regular"
                    way_tag["key"] = child.attrib["k"]
                    way_tag["id"] = element.attrib["id"]
                    way_tag["value"] = child.attrib["v"]
                    tags.append(way_tag)
    return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}

process_map(osm_path, validate=True)
