# Version 0.1

# Authors
JK Baillie

# Meta-analysis by information content (MAIC)
Data-driven aggregation of ranked and unranked lists


https://baillielab.net/maic

# Python 2.7

# basic usage

python maic.py -f <inputfilename>

# Input file format

Input is a series of lists of named entities, which may belong to categories.
Each line of the input file is a list of entities, separated by tab
The first four columns (tab-separated text strings) in each line specify features of the list in this line:
<category>  <list_label>  RANKED  <unused>  entity1 entity2 entity3 ...
<category>  <list_label>  RANKED  <unused>  entity1 entity2 entity3 ...
<category>  <list_label>  UNRANKED  <unused>  entity1 entity2 entity3 ...
<category>  <list_label>  UNRANKED  <unused>  entity1 entity2 entity3 ...

# Options

  -f FILENAME, --filename FILENAME
                        filename
  -z, --z               use a z-score from permuted lists
  -b, --baseline        calculate a baseline from random data
  -c CHOP_THRESHOLD, --chop_threshold CHOP_THRESHOLD
                        0<chop_threshold<1
  -m MAX_INPUT_LEN, --max_input_len MAX_INPUT_LEN
                        maximum list length to include
  -n NUMPERMS, --numperms NUMPERMS
                        number of permutations (to generate z score)
  -e, --exclude_current_gene
                        default=False. Less biased but much much slower. Does
                        not significantly affect results.

# Procedure summary
  #~ make an informative label for the outputs
  #~ check the necessary directories exist. If not, create them.
  #~ STORE ALL SETTINGS IN THE OUTPUT DIRECTORY
  #~ read data file, identifying a name, category and structure for each input list
  #~ work out pattern to describe key characteristics of this input set, so that we can search for stored permuted results. The only purpose of permutations is the generate two numbers: mean and SD. These are stored for each input pattern in a "permstore" file.
  #~ search permstore file for an existing mean and SD for this input pattern.
  #~ run n(=numrandom) permutations of this input pattern to get a new mean and SD
  #~ Now run crossvalidation with real data (step by step process described here repeats the permutation section, needlessly...)
#~ [1] add random lists to input set. These will be used to quantify the "zero information" baseline in this context. Different for every input set.
  #~ create a background dataset from the real gene names included in the input file, plus random integers to make it up to length
  #~ put random datasets into all the necessary input variables. It turns out that there are 6
  #~ take an immutable copy of the full list of lists at this stage. This will be used as a reference once the list splitting process begins, because part of that process involves creating new sublists and adding them to the input dataset
#~ [2] run first iteration as a simple count of overlaps
  #~ dump the initial overlap-only state for use in visualisations.
#~ [3] run a complete crossvalidation, iterating to stability, on the input sets without splitting ranked lists.
#~ [4] using the results of this initial crossvalidation, read through each ranked list assessing the total information content from position 0 to position n, where n is in range(0,len(list)), an information content is the crossvalidation score obtained if the list were truncated at each position (list=list[:n])
#~ (this splitting section should be an independent object. The crossvalidation method itself already is.)
  #~ first read right through all lists and decide on all the points at which it should be cut (i.e. where crossvalidation score has fallen to maximum*chop_threshold; 80% of max)
  #~ then apply these splits to each original input list by creating 2 or more new lists, labelled as the original input list, with an integer indicating the rank of this new split list, e.g. Karlas_et_al||0, Karlas_et_al||1 , Karlas_et_al||2
  #~ the repeat a full crossvalidation to stability using these new lists
  #~ then continue to repeat this list splitting loop until the split positions in all lists stop changing with each loop.
  #~ [5] calculate the "zero information" baseline from the random lists
  #~ remove the random lists
#~ [6] numerically transform the output scores
  #~ WRITE OUTPUT FILES
