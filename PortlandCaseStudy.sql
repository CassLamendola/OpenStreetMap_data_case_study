# Create tables for each element

CREATE TABLE nodes (
    id INTEGER PRIMARY KEY NOT NULL,
    lat REAL,
    lon REAL,
    user TEXT,
    uid INTEGER,
    version INTEGER,
    changeset INTEGER,
    time_stamp TEXT
);

CREATE TABLE nodes_tags (
    id INTEGER,
    key TEXT,
    value TEXT,
    type TEXT,
    FOREIGN KEY (id) REFERENCES nodes(id)
);

CREATE TABLE ways (
    id INTEGER PRIMARY KEY NOT NULL,
    user TEXT,
    uid INTEGER,
    version TEXT,
    changeset INTEGER,
    time_stamp TEXT
);

CREATE TABLE ways_tags (
    id INTEGER NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    type TEXT,
    FOREIGN KEY (id) REFERENCES ways(id)
);

CREATE TABLE ways_nodes (
    id INTEGER NOT NULL,
    node_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    FOREIGN KEY (id) REFERENCES ways(id),
    FOREIGN KEY (node_id) REFERENCES nodes(id)
);

# Import csv data into tables

.mode csv
.import nodes.csv nodes
.import ways.csv ways
.import node_tags.csv nodes_tags
.import ways_tags.csv ways_tags
.import ways_nodes.csv ways_nodes

#########################################

# Database queries

# Find number of unique users

SELECT COUNT(DISTINCT(subq.uid))
FROM (
    SELECT uid
    FROM nodes
    UNION
    SELECT uid
    FROM ways)
AS subq;

# Find number of nodes and ways

SELECT COUNT(*)
FROM nodes;

SELECT COUNT(*)
FROM ways;

# Find number of cafes in Portland area

SELECT COUNT(*)
FROM nodes_tags
WHERE value = 'cafe'
OR value = 'coffee_shop';

# Find number of bus stops

SELECT COUNT(*)
FROM nodes_tags
WHERE value = 'bus_stop';

# Find number of streets with a dedicated bike path

SELECT COUNT(*)
FROM (
    SELECT *
    FROM (ways_tags JOIN ways
        ON ways_tags.id = ways.id)
    WHERE ways_tags.key = 'bicycle'
    AND ways_tags.value = 'yes' 
    OR ways_tags.value = 'designated');

# Find the top 5 amenities in Portland

SELECT value, COUNT(*) AS num
FROM nodes_tags
WHERE key = 'amenity'
GROUP BY value
ORDER BY num DESC
LIMIT 5;

# Find number of non-highway streets

SELECT COUNT(DISTINCT(subq.id))
FROM (
    SELECT *
    FROM ways JOIN ways_tags
    ON ways.id = ways_tags.id
    WHERE ways_tags.key != 'highway')
AS subq;
