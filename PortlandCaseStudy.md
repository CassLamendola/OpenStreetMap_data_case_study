# OpenStreetMap Case Study
### Cassandra Lamendola

## Portland, Oregon, U.S.

- [openstreetmap.org](https://www.openstreetmap.org/search?query=Portland%2C%20Oregon#map=10/45.5428/-122.6544)
- [mapzen.com](https://mapzen.com/data/metro-extracts/metro/portland_oregon/)

Portland, Oregon is one of my favorite cities. I visit there at least once a year because I love the culture of the city. That's why I chose to use the Portland OpenStreetMap data for this case study.

## Problems Encountered in the Map

* Abbreviated street types ('Ave.',  'St.', 'Blvd.', etc.)
* Abbreviated street directions (S, NE, W)
* Inconsistency in zip codes (some include 4 digit secondary zip code, some zip codes are outside of Portland)
* Unexpected keys in way tag attributes (brand:wikidata, contact:twitter, tiger:source, tiger:upload_uid, tiger:name_type, fixme, FIXME:access)

## Some solutions

### Abbreviated street types

To correct the abbreviated street types, I used the regular expression from an example in the SQL lessons. This is the function from my PortlandCaseStudy.py file that I wrote to do the correction:

```python
def update_name(name, mapping):
	name = name.split(" ")
	old_street_type = name.pop()
	if old_street_type in mapping:
    	name.append(mapping[old_street_type])
    else:
    	name.append(old_street_type)
	name = " ".join(name)
	return name
```

### Abbreviated street directions

In order to correct the abbreviated street directions, I decided to update the function I had written for correcting street types so that it could take care of both jobs. I also updated the mapping dictionary to include possible directions. Here is the updated function from PortlandCaseStudy.py:

```python
def update_name(name, mapping):
	name = name.split()
	for word in range(len(name)):
		if name[word] in mapping.keys():
			name[word] = mapping[name[word]]
	name = " ".join(name)
	return name
```