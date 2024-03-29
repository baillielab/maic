# Version 0.2

# Authors

- A Law
- D Farr
- B Wang
- JK Baillie

# Meta-analysis by information content (MAIC)

Data-driven aggregation of ranked and unranked lists

https://baillielab.net/maic

# Code availability

This branch of the maic repository contains the original code, designed to be run as a python script from the command line. it also includes a variety of supplemntary files, including example input and output.

A refactored, functionally identical, version of the code, which can be run from the command line or incorporated into other python scripts, is available from PyPI at https://pypi.org/project/pymaic/0.2/, and on github at https://github.com/baillielab/maic/tree/packaging

# basic usage

python maic.py -f `<inputfilename>`

# Input file format

Input is a series of lists of named entities, which may belong to categories. Each line of the input file is a list of entities, separated by tab
The first four columns (tab-separated text strings) in each line specify features of the list in this line:

\<category>	<list_label>	RANKED	\<unused>	entity1	entity2	entity3	...

\<category>	<list_label>	RANKED	\<unused>	entity1	entity2	entity3	...

\<category>	<list_label>	UNRANKED	\<unused>	entity1	entity2	entity3	...

\<category>	<list_label>	UNRANKED	\<unused>	entity1	entity2	entity3	...

# Options

-f , --filename

path to the file containing data to be analysed

-o, --output-folder

path to the folder in which to write the results files

-p, --plot

draw plots for each list at each iteration

-d, --dump-scores

dump maic scores at each iteration

-l, --max_input_len

maximum list length (default:2000)

-v, --verbose

increase the detail of logging messages

-q, --quiet

decrease the detail of logging messages (overrides the -v/--verbose flag)

# Dataset analysis for methods selection

The dataset features including ranking information, the number of sources included and the heterogeneity of quslity will be explored to show the estimation of the best performed ranking aggregation method for the given dataset. See Wang et al [https://doi.org/10.1093/bioinformatics/btac621] for an explanation of how we evaluated this.

Examples are included in the folder example_input_and_result with simulated input data and output of MAIC.

  When MixLarge data with high heterogeneity (See Wang et al [https://doi.org/10.1093/bioinformatics/btac621]) is used, the algorithm will output:

  "Based on the characteristics of your dataset, we have estimated that MAIC is the best algorithm for this analysis! See Wang et al [https://doi.org/10.1093/bioinformatics/btac621] for an explanation of how we evaluated this."

  When RankLarge data with high heterogeneity (See Wang et al [https://doi.org/10.1093/bioinformatics/btac621]) is used, the algorithm will output:

  "Warning! Your dataset has the unusual combination of ranked-only data, high heterogeneity and a relatively large number of sources (11) included. Based on these features we think you'd get better results from running BIRRA [http://www.pitt.edu/~mchikina/BIRRA/]. See Wang et al [https://doi.org/10.1093/bioinformatics/btac621] for an explanation of how we evaluated this."
