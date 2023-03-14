# Version 0.2

# Authors
- JK Baillie
- A Law
- B Wang
- D Farr

# Meta-analysis by information content (MAIC)
Data-driven aggregation of ranked and unranked lists

https://baillielab.net/maic

# Code repositories

Original implementation: https://github.com/baillielab/maic
Refactored package code: https://github.com/baillielab/maic/tree/packaging

# basic usage

## installation:

`pip install pymaic`

## from the command line:

pymaic installs a shell script that allows you to run a MAIC analysis directly from the command line as simply as:

`maic -f <inputfilename>`

### Options

-f FILENAME, --filename FILENAME
                      path to the file containing data to be analysed

-t TYPE, --type TYPE
                      format of the file specified with -f (see below).

-o FOLDER, --output-folder FOLDER
                      path to the folder in which to write the results files

-v, --verbose         increase the detail of logging messages.

-q, --quiet           decrease the detail of logging messages (overrides the
                      -v/--verbose flag)


### Input file format

Input is a series of lists of named entities, which may belong to categories. 
pymaic supports three input formats: 

#### MAIC - a tab-separated format (-t MAIC)

Each line of the input file describes a list of entities. The first four columns in each line specify features of the list in this line, and the fifth is a space-separated list of entity names, e.g.

\<category>	<list_label>	RANKED	\<unused>	entity1	entity2	entity3	...

\<category>	<list_label>	RANKED	\<unused>	entity1	entity2	entity3	...

\<category>	<list_label>	UNRANKED	\<unused>	entity1	entity2	entity3	...

\<category>	<list_label>	UNRANKED	\<unused>	entity1	entity2	entity3	...

#### JSON/YAML (-t JSON, -t YAML)

Files can also be provided as semi-structured data in either JSON or YAML format:

```{json}
[
  {
    "name": <list_label>,
    "category": <category>,
    "ranked": true|false,
    "entities": ["entity1", "entity2", "entity3", ...]
  },
  ...
]
```

```{yaml}
-
  name: <list_label>
  category: <category>
  ranked: true|false
  entities:
    - entity1
    - entity2
    - entity3
    - ...
-
  ...
```

## from a python script:

You can instantiate a MAIC analysis in python if you want greater control over the output of results, would like to do some additional processing after analysis, or need to use data in a format not supported by the command-line script.

### Constructing a MAIC analysis object from a file to give programmatic access to the results:

```{python}
from maic import MAIC

app = MAIC.fromfile("/path/to/inputfile")
app.run()

for result in app.sorted_results():
...

```

### Constructing a MAIC analysis from sources other than a file:

```{python}
from maic import MAIC
from maic.models import EntityListModel

models = []

# prepare the data:
for list in mydata:
    models.append(EntityListModel(name=list.name, category=list.category, ranked=True if list.type == "RANKED" else False, entities=list.entities))

app = MAIC(modellist = models)
...

```

# Dataset analysis for methods selection
  
The dataset features including ranking information, the number of sources included and the heterogeneity of quality will be explored to show the estimation of the best performed ranking aggregation method for the given dataset. See Wang et al [https://doi.org/10.1093/bioinformatics/btac621] for an explanation of how we evaluated this. 

  When MixLarge data with high heterogeneity (See Wang et al [https://doi.org/10.1093/bioinformatics/btac621]) is used, the algorithm will output:
  
  "Based on the characteristics of your dataset, we have estimated that MAIC is the best algorithm for this analysis! See Wang et al [https://doi.org/10.1093/bioinformatics/btac621] for an explanation of how we evaluated this."

  When RankLarge data with high heterogeneity (See Wang et al [https://doi.org/10.1093/bioinformatics/btac621]) is used, the algorithm will output:
  
  "Warning! Your dataset has the unusual combination of ranked-only data, high heterogeneity and a relatively large number of sources (11) included. Based on these features we think you'd get better results from running BIRRA [http://www.pitt.edu/~mchikina/BIRRA/]. See Wang et al [https://doi.org/10.1093/bioinformatics/btac621] for an explanation of how we evaluated this."
