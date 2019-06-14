#!/opt/local/bin/python
# -*- coding: UTF-8 -*-
#--------------
version = 0.1
#--------------
import argparse, sys, json
#--------------
from maic_functions import *
# DATA SOURCES
defaultdatasource = "../inputdata/test"

#--------------------------------
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--filename',	default=defaultdatasource, help='filename')
parser.add_argument('-z', '--z',	action="store_true",	default=False,	help='use a z-score from permuted lists')
parser.add_argument('-b', '--baseline',	action="store_true",	default=False,	help='calculate a baseline from random data')
parser.add_argument('-c', '--chop_threshold',	type=float,	default=0.8,	help='0<chop_threshold<1')
parser.add_argument('-m', '--max_input_len',	type=int,	default=2000,	help='maximum list length to include')
parser.add_argument('-n', '--numperms',	type=int,	default=100,	help='number of permutations (to generate z score)')
parser.add_argument('-e', '--exclude_current_gene',	action="store_true",	default=False,	help='default=False. Less biased but much much slower. Does not significantly affect results. ')
args = parser.parse_args()
module = sys.modules[__name__]
for name,value in vars(args).iteritems():
	print name, value
	setattr(module, name, value)
#-----------------------------
# KEY SETTINGS
#-----------------------------
# MAIC settings
eliminatecategories = False #DEFAULT==NO. Stops category-level analyses
randomsourcelen = 20000 # the size of the pool from which these lists are sampled. Human = 20000.
# MAIC PARAMATERS WITH ARBITRARY SETTINGS TO PREVENT INFINITE LOOPS.
stability = 0.01 #iterate until average proportion change each iteration is less than this.
max_iterations = 100 # maximum. iterations of whole MAIC. STABILITY REACHED AFTER 4
maxrotations = 100 # maximum. stop looking for stable cuts after this many iterations
num_rand_datasets_for_baseline = 10
#--------------
# List splitting settings
fix_ranked = True # use list splitting
#--------------
# Numerical transform settings
if z:
	includerandom = True #recalculate random
	transform_type = "zscore" # "zscore" "pvalue" "rawscore" "rootz" "baseline" "baselinez"
	displacement = 1
	if baseline:
		transform_type = " " # "zscore" "pvalue" "rawscore" "rootz" "baseline" "baselinez"
else:
	includerandom = False #recalculate random
	transform_type = "rawscore" # "zscore" "pvalue" "rawscore" "rootz" "baseline" "baselinez"
	displacement = 0
	if baseline:
		transform_type = "baseline" # "zscore" "pvalue" "rawscore" "rootz" "baseline" "baselinez"

usestored = True # enable use of stored sd and mean if one exists from an identical pattern of inputs
ignoreversion = False # ignore version number (of script) in stored mean and sd file
assume_msd = False
if includerandom:
	assume_msd = False
assumedmean, assumedsd = (1.26673655625, 0.102058420202)
#--------------
# output and visualisation settings
verbose = True
makematrix = True
plotsoff = False  # save time for validation runs
#--------------
# labels and fileanmes
randomlabel = "RAND" # text string used to identify random lists that are added to input set and then removed at end.
settingsfilename = "settings.txt"
resultsdir = '../results'
stage_store_dirname = "stage_store"
split_data_dirname = "split_data"
supdir = "../sup-files"
perm_set_scores_file = os.path.join(supdir, 'permstore.txt')
perm_elementscores_file = os.path.join(supdir, 'permstore_elements.txt')
#-##################################################################
def dump_now(thislabel):
	'''Save ranked list information content decay graph data'''
	json_data = {
		"datasetweightings":datasetweightings,
		"datasets":datasets,
		"categories":categories,
		"structure":structure,
		"originaldatasets":originaldatasets,
		"output_category_order":output_category_order,
		"scorecounter":scorecounter,
		"outputlabel":outputlabel,
		"outputdir":outputdir,
	}
	check_dir(stage_store_dir)
	dump_filename = os.path.join(stage_store_dir, thislabel)
	with open(dump_filename, 'w') as fp:
		json.dump(json_data, fp)

#-##################################################################
#~ make an informative label for the outputs
filelabel = filename.replace(".txt","")
filelabel = os.path.split(filename)[-1]
outputlabel = "%s_v%s_%s"%(filelabel, version, chop_threshold)
if includerandom:
	outputlabel += '_nPerms%s'%numperms
if exclude_current_gene:
	outputlabel += '_ExcludeCurrent'
if eliminatecategories:
	outputlabel += '_nocat'
if baseline:
	outputlabel += '_baseline%s'%(num_rand_datasets_for_baseline)
#-##########################
#~ check the necessary directories exist. If not, create them.
check_dir(resultsdir)
outputdir = os.path.join(resultsdir, outputlabel)
check_dir(outputdir)
stage_store_dir = os.path.join(outputdir, stage_store_dirname)
if not(plotsoff):
	split_data_dir = os.path.join(outputdir, split_data_dirname)
	check_dir(split_data_dir)
#--------------------
#~ STORE ALL SETTINGS IN THE OUTPUT DIRECTORY
o=open(os.path.join(outputdir,settingsfilename), "w")
o.write("version\t%s\n"%(version))
o.write("filename\t%s\n"%(filename))
o.write("chop_threshold\t%s\n"%(chop_threshold))
o.write("max_input_len\t%s\n"%(max_input_len))
o.write("max_iterations\t%s\n"%(max_iterations))
o.write("maxrotations\t%s\n"%(maxrotations))
o.write("exclude_current_gene\t%s\n"%(exclude_current_gene))
o.write("includerandom\t%s\n"%(includerandom))
o.write("numperms\t%s\n"%(numperms))
o.write("transform_type\t%s\n"%(transform_type))
o.write("randomsourcelen\t%s\n"%(randomsourcelen))
o.write("assume_msd\t%s\n"%(assume_msd))
o.write("assumedmean\t%s\n"%(assumedmean))
o.write("assumedsd\t%s\n"%(assumedsd))
o.write("verbose\t%s\n"%(verbose))
o.write("fix_ranked\t%s\n"%(fix_ranked))
o.write("eliminatecategories\t%s\n"%(eliminatecategories))
o.write("num_rand_datasets_for_baseline\t%s\n"%(num_rand_datasets_for_baseline))
o.close()
#--------------------
if randomsourcelen < 18000:
	print "##### NB randomsourcelen %s is lower than expected ########"%randomsourcelen
#-##########################
# -- static objects --
categories={}
datasetorder=[] #list of datasets in the order in which they appear in the input file
structure={}
output_category_order=[]
# -- working objects --
datasets={}
datasetweightings={}
# -- storage objects --
weightingstore={}
evolutionstore={}
baselinevalue = 0
#-##########################
#~ read data file, identifying a name, category and structure for each input list
f=open(filename)
lines=f.readlines()
f.close()
transient_category_order=[]
if len(lines)==1:
	lines=string.split(lines[0],"\r") # to fix encoding error
for line in lines:
	if line[:5]=="-----":
		break
	line=string.split(string.strip(line),"\t")
	line=[string.strip(x) for x in line]
	if len(line)<4:
		print line, "too short"
		continue
	cat = line[0]
	name = line[1]
	genelist = [x for x in line[4:] if x != ""]
	if max_input_len != "none" and line[2]=="RANKED": # no sense in chopping unranked lists
		genelist=genelist[:max_input_len]
	datasetorder.append(name)
	datasets[name]=[]
	datasetweightings[name]=1
	for gene in genelist:
		if gene not in datasets[name]:
			datasets[name].append(gene) #preserve order, remove duplicates
	structure[name]=line[2]
	if eliminatecategories:
		categories[name]=name # use dataset name as category in order to eliminate the effect of categories altogether.
	else:
		categories[name]=cat
	transient_category_order.append(categories[name])
output_category_order = unique_in_order(transient_category_order)
print "CATEGORIES IN USE:", ", ".join(output_category_order)

#~ work out pattern to describe key characteristics of this input set, so that we can search for stored permuted results. The only purpose of permutations is the generate two numbers: mean and SD. These are stored for each input pattern in a "permstore" file.
catlens = {x:[] for x in categories.values()}
for name in datasets:
	rankstatus="u"
	if structure[name]=="RANKED":
		rankstatus="r"
	catlens[categories[name]].append("%s%s"%(len(datasets[name]), rankstatus))
catkeys = [".".join([c for c in sorted(catlens[thiscat])]) for thiscat in catlens]
patternkey = "|".join(sorted(catkeys))
patternkey += "[c=%s;v=%s]"%(chop_threshold, version) #describes the input list pattern that determines perms

#~ search permstore file for an existing mean and SD for this input pattern.
if usestored and transform_type == 'zscore' or transform_type == 'baselinez':
	f=open(perm_set_scores_file)
	lines = [string.split(string.strip(line),"\t") for line in f.readlines()]
	f.close()
	for line in lines:
		if ignoreversion:
			thiskey = string.split(line[0],";")[0]
			searchkey = string.split(patternkey,";")[0]
		else:
			thiskey = line[0]
			searchkey = patternkey
		if thiskey == searchkey:
			permsfound = int(line[3])
			if permsfound >= numperms:
				assumedmean = float(line[1])
				assumedsd = float(line[2])
				includerandom = False
				if ignoreversion:
					print "WARNING: IGNORING VERSION NUMBER IN STORED MEAN/SD SELECTION"
				print "******OLD PATTERN FOUND*******"
				print "Permutations will not be recalculated. Using mean:", assumedmean, "and sd:", assumedsd, "from", permsfound,"previous permutations"
				break #choose the first one we come to

#------------------------------------------------------------------------------------
originaldatasets=copy.copy(datasets)
referencedatasets=copy.copy(datasets)
#------------------------------------------------------------------------------------

#~ run n(=numperms) permutations of this input pattern to get a new mean and SD
#------------------------------------------------------
#START PERMUTATIONS
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
if includerandom:
	#obtain genenames
	permutedscores=[]
	permutedgenescores=[]
	permobjects={}
	for n in range(numperms):
		print "%s of %s permutations for %s %s key= %s"%(n, numperms, filename ,chop_threshold, patternkey)
		randomdatasets={}
		randsetweightings={}
		randcats={}
		randstruct={}
		permutedgenes=[]
		thisnum=0
		for d in datasets:
			name = "~~random~~%s"%thisnum
			thisnum+=1
			genelist = [int(random.random()*randomsourcelen)  for x in range(len(datasets[d]))] #len(d) random choices from randomsetlen
			permutedgenes+=genelist
			randomdatasets[name]=genelist
			randsetweightings[name]=1
			randcats[name]=categories[d] # the actual category of the input list
			randstruct[name] = structure[d] # the actual structure (ie. RANDOM/NOT) of the input list
		permutedgenes=list(set(permutedgenes))

		#CROSSVALIDATE
		randsetweightings = crossvalidate(randsetweightings, randomdatasets, randcats, stability, max_iterations)
		randcounter = makescorecounter(randsetweightings, randomdatasets, randcats, exclude_current_gene=exclude_current_gene)

		if fix_ranked:
			#loop through all ranked datasets, cutting them at different lenghts to find the strongest possible list
			randranked = [x for x in randomdatasets if randstruct[x] == "RANKED"]
			randcounter = makescorecounter(randsetweightings, randomdatasets, randcats, exclude_current_gene=exclude_current_gene)

			splitdict={}
			for rd in randranked:
				#get all splits in one go first
				splits = getsplits(rd, randomdatasets, randcounter, chop_threshold)
				if len(splits)>2:
					splitdict[rd]=splits
			#then apply them
			for sd in splitdict:
				thesesplits = splitdict[sd]
				for s in range(len(thesesplits)-1):
					new = "%s||%s"%(sd, s)
					randomdatasets[new] = randomdatasets[sd][thesesplits[s]:thesesplits[s+1]]
					randsetweightings[new] = randsetweightings[sd]
					randcats[new] = randcats[sd]
					randstruct[new] = randstruct[sd]
				del randomdatasets[sd]

		#CROSSVALIDATE
		randsetweightings = crossvalidate(randsetweightings, randomdatasets, randcats, stability, max_iterations)
		randcounter = makescorecounter(randsetweightings, randomdatasets, randcats, exclude_current_gene=exclude_current_gene)
		permutedgenescores+=[sum(randcounter[x].values()) for x in randcounter]
		permutedscores+=randsetweightings.values()
		permobjects[n]=[copy.copy(randomdatasets), copy.copy(randsetweightings), copy.copy(list(set(randcats.values()))), copy.copy(randcats)]
	#---------
	# STORE DATASET SCORES
	print "random SET score distribution:", quartiles(permutedscores)
	o=open(os.path.join(outputdir, "randomsetscores.txt"),"w")
	for score in permutedscores:
		o.write("%s\t"%score)
	o.close()
	meanrand, sdrand = msd(permutedscores)
	print "(%s, %s)"%(meanrand, sdrand)
	#store for later
	o=open(perm_set_scores_file, 'a')
	o.write("%s\t%s\t%s\t%s\n"%(patternkey,meanrand,sdrand,numperms))
	o.close()
	#---------
	# STORE ELEMENT SCORES
	# now go through all permutations and pick up the z-scores or whatever output has been chosen
	permstore_elementscores = []
	for i in permobjects:
		permsortingscores, permsourceweightingstorerecord, permbreakdown, permbigsourcerecord = sum_output(transform_type, f=2, d=displacement, ds=permobjects[i][0], dsw=permobjects[i][1], oo=permobjects[i][2], thesecats=permobjects[i][3])
		permstore_elementscores += permsortingscores.values()
	permstore_elementscores = sorted(permstore_elementscores)
	print "random ELEMENT score distribution:", quartiles(permstore_elementscores)
	if False:
		o=open(os.path.join(outputdir, "randomelementscores.txt"),"w")
		for score in permstore_elementscores:
			o.write("%s\t"%score)
		o.close()
	meangene, sdgene = msd(permstore_elementscores)
	print "(%s, %s)"%(meangene, sdgene)
	#store for later
	o=open(perm_elementscores_file, 'a')
	o.write("%s\t%s\t%s\t%s\n"%(patternkey, meangene, sdgene, numperms))
	o.close()
elif assumedsd:
	meanrand, sdrand = (assumedmean, assumedsd)
else:
	transform_type = "rawscore" #as there is no mean or sd to use!
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#END PERMUTATIONS
#------------------------------------------------------

#------------------------------------
#~ dump the initial overlap-only state for use in visualisations.
datasetweightings  = {d:1 for d in datasets}
scorecounter = makescorecounter(datasetweightings, datasets, categories, exclude_current_gene=exclude_current_gene)
if makematrix:
	dump_now("matrix_start")

#~ Now run crossvalidation with real data (step by step process described here repeats the permutation section, needlessly...)
#~ [1] add random lists to input set. These will be used to quantify the "zero information" baseline in this context. Different for every input set.
#------------------------------------
# QUANTIFY BASELINE
#------------------------------------
if baseline:
	#~ create a background dataset from the real gene names included in the input file, plus random integers to make it up to length
	allgenenames = list(set(itertools.chain(*originaldatasets.values())))
	paddinglen = randomsourcelen - len(allgenenames)
	background = allgenenames + [int(random.random()*paddinglen) for x in range(paddinglen)]
	#------------------------------------
	#~ put random datasets into all the necessary input variables. It turns out that there are 6
	for i in range(num_rand_datasets_for_baseline):
		dsname = '{}{}'.format(randomlabel, i)
		datasets[dsname] = random.sample(background, max_input_len)
		categories[dsname] = randomlabel
		structure[dsname] = "UNRANKED"
		datasetorder.append(dsname)
		datasetweightings[dsname] = 1
	output_category_order.append(randomlabel)
	#------------------------------------
	#~ take an immutable copy of the full list of lists at this stage. This will be used as a reference once the list splitting process begins, because part of that process involves creating new sublists and adding them to the input dataset
	referencedatasets=copy.copy(datasets) # to protect against modification during list splitting

#------------------------------------
#~ [2] run first iteration as a simple count of overlaps
scorecounter = makescorecounter(datasetweightings, datasets, categories, exclude_current_gene=exclude_current_gene)
datasetweightings = refineweightings(datasets, scorecounter)

#------------------------------------
#make storage dicts
for dataset in datasetweightings:
	weightingstore[dataset]=[datasetweightings[dataset]]
for dataset in datasets:
	for gene in datasets[dataset]:
		evolutionstore[gene]=[]

#~ [3] run a complete crossvalidation, iterating to stability, on the input sets without splitting ranked lists.
datasetweightings = crossvalidate(datasetweightings, datasets, categories, stability, max_iterations)
scorecounter = makescorecounter(datasetweightings, datasets, categories, exclude_current_gene=exclude_current_gene)
weightingstore, evolutionstore = storedata(weightingstore, evolutionstore, datasetweightings, scorecounter, datasets)

#~ [4] using the results of this initial crossvalidation, read through each ranked list assessing the total information content from position 0 to position n, where n is in range(0,len(list)), an information content is the crossvalidation score obtained if the list were truncated at each position (list=list[:n])
#~ (this splitting section should be an independent object. The crossvalidation method itself already is.)
#------------------------------------

#------------------------------------
if makematrix:
	dump_now("matrix_rand_start")
#------------------------------------

rankeddatasets = [x for x in datasets if structure[x] == "RANKED"]
if fix_ranked and len(rankeddatasets)>0:

	scorecounter = makescorecounter(datasetweightings, datasets, categories, exclude_current_gene=exclude_current_gene)
	splitdict={}
	rolling=True
	splittingiterations=0
	while splittingiterations < maxrotations and rolling:
		print "splittingiterations", splittingiterations
		datasets = copy.copy(referencedatasets) # REVERT SCORES TO OLD DATASETS
		datasetweightings = refineweightings(datasets, scorecounter)
		#loop through all ORIGINAL datasets, cutting them at different lengths to find the strongest possible list
		#~ first read right through all lists and decide on all the points at which it should be cut (i.e. where crossvalidation score has fallen to maximum*chop_threshold; 80% of max)
		for rd in rankeddatasets:
			splits = getsplits(rd,datasets,scorecounter, chop_threshold, doplotsplits=True, splitsdir=split_data_dir)
			if len(splits)>2:
				try:
					splitdict[rd]
				except:
					splitdict[rd] = []
				splitdict[rd].append(splits)
		#~ then apply these splits to each original input list by creating 2 or more new lists, labelled as the original input list, with an integer indicating the rank of this new split list, e.g. Karlas_et_al||0, Karlas_et_al||1 , Karlas_et_al||2
		for sd in splitdict:
			thesesplits = splitdict[sd][-1]
			dsl=[]
			for s in range(len(thesesplits)-1):
				new = "%s||%s"%(sd, s)
				datasets[new] = datasets[sd][thesesplits[s]:thesesplits[s+1]]
				#-----------
				if verbose and False:
					print "new list created (", new, ") from position", thesesplits[s], "to", thesesplits[s+1], ":", datasets[new]
					dsl.append(len(datasets[new]))
					print len(datasets[sd]), dsl
				#-----------
				datasetweightings[new] = datasetweightings[sd] #this makes the graph jump but actual value doesn't matter
				categories[new] = categories[sd]
				structure[new] = structure[sd]
			del datasets[sd]

		#~ the repeat a full crossvalidation to stability using these new lists
		#CROSSVALIDATE
		datasetweightings = crossvalidate(datasetweightings, datasets, categories, stability, max_iterations)
		scorecounter = makescorecounter(datasetweightings, datasets, categories, exclude_current_gene=exclude_current_gene)
		weightingstore, evolutionstore = storedata(weightingstore, evolutionstore, datasetweightings, scorecounter, datasets)

		splittingiterations+=1
		if splittingiterations>1:
			rolling=False
			for r in splitdict:
				if len(splitdict[r])>1:
					#IS THE LENGTH OF THIS LIST EQUAL TO THE LENGTH OF THE SAME LIST IN THE PREVIOUS ITERATION?
					if splitdict[r][-2] != splitdict[r][-1]:
						rolling=True #another iteration is required to reach stability
					else:
						rolling=False
		#~ then continue to repeat this list splitting loop until the split positions in all lists stop changing with each loop.



#~ [5] calculate the "zero information" baseline from the random lists
#------------------------------------
if baseline and num_rand_datasets_for_baseline>0:
	# get baseline value
	r = [datasetweightings[x] for x in datasetweightings if categories[x]==randomlabel]
	baselinevalue = msd(r)[0]
	print "baselinevalue", baselinevalue

#------------------------------------
if makematrix:
	dump_now("matrix_end")
#------------------------------------


if baseline and num_rand_datasets_for_baseline>0:
	#~ remove the random lists
	for i in range(num_rand_datasets_for_baseline):
		dsname = '{}{}'.format(randomlabel, i)
		del datasets[dsname]
		del categories[dsname]
		del structure[dsname]
		datasetorder.remove(dsname)
		del datasetweightings[dsname]
	output_category_order.remove(randomlabel)

#------------------------------------
if makematrix:
	dump_now("matrix_rand_end")
#------------------------------------

#~ [6] numerically transform the output scores
raw_weightings = copy.copy(datasetweightings)
datasetweightings = {}
for ds in raw_weightings:
	datasetweightings[ds] = fix_output(raw_weightings[ds], transform_type, meanrand=meanrand, sdrand=sdrand, baselinevalue=baselinevalue)
	print "{} raw: {} fixed:{}".format(ds, raw_weightings[ds], datasetweightings[ds])
scorecounter = makescorecounter(datasetweightings, datasets, categories, exclude_current_gene=exclude_current_gene)
sortingscores, sourcerecord, breakdown, bigsourcerecord = sum_output(transform_type, f=2, d=displacement, ds=datasets, dsw=datasetweightings, oo=output_category_order, thesecats=categories)

#------------------------------------
if makematrix:
	dump_now("matrix_fixed")
#------------------------------------



#--------------------------------------------------
#--------------------------------------------------
#~ WRITE OUTPUT FILES
#--------------------------------------------------
#--------------------------------------------------
o=open(os.path.join(outputdir, "values_used.txt"),"w")
o.write("baselinevalue\t{}\n".format(baselinevalue))
o.write("meanrand\t{}\n".format(meanrand))
o.write("sdrand\t{}\n".format(sdrand))
o.close()
#--------------------------------------------------
o=open(os.path.join(outputdir, "FINAL_GENESCORES.txt"),"w")
o.write("gene\t")
for cat in output_category_order:
	o.write("%s\t"%cat)
o.write("tot\tsources\tfullsources\n")
i=0
for key, value in sorted(sortingscores.iteritems(), key=lambda (k,v): (v,k), reverse=True):
	o.write("%s\t"%(key))
	for e in breakdown[key]:
		o.write("%s\t"%(e))
	o.write("%s\t"%(sortingscores[key]))
	slist=sourcerecord[key].values()
	o.write("%s\t"%(",".join(slist)))
	bigslist=bigsourcerecord[key].values()
	o.write("%s\n"%(",".join(bigslist)))
	i+=1
o.close()
#--------------------------------------------------
o=open(os.path.join(outputdir, "DATASET_SCORES.txt"),"w")
o.write("dataset\tweightingstore\n")
o.write("RAWSCORES\n")
for c in output_category_order:
	for d in sorted([x for x in datasets if categories[x]==c]):
		o.write("%s\t"%d)
		for entry in weightingstore[d]:
			o.write("%s\t"%(entry))
		o.write("\n")
o.write("\n{}\n".format(transform_type))
for c in output_category_order:
	for d in sorted([x for x in datasets if categories[x]==c]):
		o.write("%s\t"%d)
		for entry in weightingstore[d]:
			o.write("%s\t"%(fix_output(entry, transform_type, meanrand=meanrand, sdrand=sdrand, baselinevalue=baselinevalue)))
		o.write("\n")
	o.write("\n")
o.close()
#--------------------------------------------------
o=open(os.path.join(outputdir, "GENE_EVOLUTION.txt"),"w")
for key, value in sorted(sortingscores.iteritems(), key=lambda (k,v): (v,k)):
	o.write("%s\t"%key)
	for entry in evolutionstore[key]:
		try:
			float(entry)
			entry =  fix_output(entry, transform_type, meanrand=meanrand, sdrand=sdrand, baselinevalue=baselinevalue)
		except:
			pass
		o.write("%s\t"%entry)
	o.write("\n")
o.close()
#--------------------------------------------------
lencounter=0
toplimit=1000 # count the scores in the top x genes from this list.
dsdic={}
for d in originaldatasets:
	dsdic[d] = [sortingscores[x] for x in originaldatasets[d][:toplimit]]
dsdicsort = {d:float(sum(dsdic[d]))/len(dsdic[d]) for d in dsdic.keys() if len(dsdic[d])>0}
o=open(os.path.join(outputdir, "comparedatasets.txt"),"w")
for d, value in sorted(dsdicsort.iteritems(), key=lambda (k,v): (v,k), reverse=True):
	o.write("%s\t%s\t%s\n"%(d, value, '\t'.join( [str(x) for x in dsdic[d]] )))
o.close()




















