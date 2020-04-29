# Version 0.2

# Authors
- A Law
- D Farr
- B Wang
- JK Baillie

# Meta-analysis by information content (MAIC)
Data-driven aggregation of ranked and unranked lists

https://baillielab.net/maic

# basic usage

python maic.py -f <inputfilename>

# Input file format

Input is a series of lists of named entities, which may belong to categories. Each line of the input file is a list of entities, separated by tab
The first four columns (tab-separated text strings) in each line specify features of the list in this line:

<category>	<list_label>	RANKED	<unused>	entity1	entity2	entity3	...

<category>	<list_label>	RANKED	<unused>	entity1	entity2	entity3	...

<category>	<list_label>	UNRANKED	<unused>	entity1	entity2	entity3	...

<category>	<list_label>	UNRANKED	<unused>	entity1	entity2	entity3	...

# Options

-f FILENAME, --filename FILENAME
                      path to the file containing data to be analysed

-o, --output-folder 'path to the folder in which to write the '
                             'results files'

-v, --verbose         increase the detail of logging messages.

-q, --quiet           decrease the detail of logging messages (overrides the
                      -v/--verbose flag)

