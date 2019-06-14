# Version 0.2

# Authors
A Law
D Farr
B Wang
JK Baillie

# Meta-analysis by information content (MAIC)
Data-driven aggregation of ranked and unranked lists

https://baillielab.net/maic

# basic usage

python maic.py -f <inputfilename>

# Input file format

Input is a series of lists of named entities, which may belong to categories.
Each line of the input file is a list of entities, separated by tab
The first four columns (tab-separated text strings) in each line specify features of the list in this line:
<category>	<list_label>	RANKED	<unused>	entity1	entity2	entity3	...
<category>	<list_label>	RANKED	<unused>	entity1	entity2	entity3	...
<category>	<list_label>	UNRANKED	<unused>	entity1	entity2	entity3	...
<category>	<list_label>	UNRANKED	<unused>	entity1	entity2	entity3	...

# Options
  -f FILENAME, --filename FILENAME
                        path to the file containing data to be analysed
  -z, --z               default=False. Use a z-score from permuted lists
  -t,                   Transform method
  -b [BASELINE], --baseline [BASELINE]
                        Correct scores using a baseline calculated from random
                        data matching the input data set. Optionally specify
                        the path to a file in which pre-calculated baselines
                        are stored (default is ${HOME}/.maic-baselines.txt.
  -g [GENE_SCORE_OUTPUT_FILE], --gene-score-output-file [GENE_SCORE_OUTPUT_FILE]
  -c {0.0..1.0}, --chop-threshold {0.0..1.0}
                        0.0 < chop-threshold < 1.0
  -m MAX_INPUT_LEN, --max-input-len MAX_INPUT_LEN
                        maximum list length to include
  -n NUM_PERMS, --num-perms NUM_PERMS
                        number of permutations (to generate z score)
  -e, --exclude-current-gene
                        default=False. Less biased but much much slower. Does
                        not significantly affect results.
  -w {none,knn,polynomial,exponential,svr}, --weight-function {none,knn,polynomial,exponential,svr}
                        weighting function to use for ranked lists
  -v, --verbose         increase the detail of logging messages.
  -q, --quiet           decrease the detail of logging messages (overrides the
                        -v/--verbose flag)
