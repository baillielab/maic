#!/opt/local/bin/python
# -*- coding: UTF-8 -*-

import string, math, copy, random, itertools, timeit, scipy.stats, os, sys
from statsmodels.sandbox.stats.multicomp import multipletests
from bisect import bisect_left
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
#------------------------------------
'''
META ANALYSIS BY INFORMATION CONTENT (MAIC) FUNCTIONS
Notes on terminology:
A "dataset" is either an input list, or a sublist generated from an input list by the list splitting procedure.
The term "weight" is used throughout to refer to the weighting given to a dataset.
The term "score" is used to refer to the score given to a given entity (e.g. a gene) in a list.
'''
#------------------------------------
# CROSS functions
#------------------------------------

def refineweightings(thisdict, scores, thisgene="null"):
	'''create a new dict of dataset weightings for a given set of scores'''
	out = {}
	for sublist in thisdict:
		try:
			if thisgene!="null":
				scorelist = [float(sum(scores[gene].values())) for gene in thisdict[sublist] if gene!=thisgene]	   
			else:
				scorelist = [float(sum(scores[gene].values())) for gene in thisdict[sublist]]
		except:
			print "error in refineweightings:", sublist, gene
		if len(scorelist)>0: score = float(sum(scorelist))/len(scorelist) #average
		else: score = 0.0
		#-----------
		#score = math.sqrt(score)  #control score to prevent exponential rise
		rp=2
		score = math.pow(score,1.0/rp)
		#-----------
		out[sublist] = max(score,0) # set minimum score=0
	return out

def makescorecounter(useweightings, usedatasets, usecategories, exclude_current_gene=False, randomlabel="RAND", firstrun=False):
	''' create a new set of entity scores (genescores) for a given set of dataset weightings '''
	allgenes = list(set(itertools.chain(*usedatasets.values()))) #remake sc dict
	categorycounter={}
	u = {}
	if exclude_current_gene and not firstrun:
		oldscores=copy.copy(makescorecounter(useweightings, usedatasets, useweightings, True))
	for d in usedatasets:
		u[d]={}
		for g in usedatasets[d]: #make dict of all genes in usedatasets[dataset]. Marginally faster.
			u[d][g]=1
	for gene in allgenes: 
		try: categorycounter[gene]
		except: categorycounter[gene]={}
		for d in u:
			try: 
				u[d][gene]
			except:
				continue
			if exclude_current_gene and not firstrun:
				useweightings = refineweightings(usedatasets, oldscores, gene) #recalculate
			newscore = useweightings[d]
			if usecategories[d] != randomlabel:
				try:
					categorycounter[gene][usecategories[d]]
				except:
					categorycounter[gene][usecategories[d]] = []
				categorycounter[gene][usecategories[d]].append(newscore)
	sc = {g:{c:max(categorycounter[g][c]) for c in categorycounter[g]} for g in categorycounter}
	return sc

def checkdelta(old,new, stability):
	''' quantify the overall change between two crossvalidation iterations '''
	deltalist = [float(abs(old[x]-new[x]))/old[x]>stability for x in new.keys()] #proportion change
	return sum(deltalist)>0 #True if any list is changing more than "stability"

def crossvalidate(dsw, ds, these_categories, s, max_i):
	''' iterate through the crossvalidation method until a stable set of weightings is reached '''
	changing = True
	i = 0
	while changing:
		old_dw=dsw
		#CROSSVALIDATE
		scorecounter = makescorecounter(dsw, ds, these_categories)
		dsw = refineweightings(ds, scorecounter)
		changing = checkdelta(old_dw, dsw, s)
		i+=1
		if i>max_i:
			print "failed to reach stability"
			break
	return dsw

#--------------------------------------------------
# output/storage functions
#--------------------------------------------------

def storedata(ws, es, storeweightings, currentscores, ds):
	''' add the current weightes and scores to existing containers, for use in outputs that describe the maic process'''
	allgenes = list(set(itertools.chain(*ds.values())))
	for gene in allgenes:
		try:es[gene].append(sum(currentscores[gene].values()))
		except:es[gene].append(0)
	for d in storeweightings:
		try: ws[d].append(storeweightings[d])
		except: ws[d]=[storeweightings[d]]
	return ws, es

#--------------------------------------------------
# calibration/numerical transform functions
#--------------------------------------------------
def fix_output(inputval, outtype='rawscore', meanrand='null', sdrand='null', baselinevalue='null', f=2, d=0):
	''' apply a numerical transform to scale the final output scores '''
	# z-score independent values first
	if outtype == 'rawscore':
		return inputval
	if outtype == 'baseline':
		return max(inputval-baselinevalue,0)
	if outtype == 'powerraw':
		return math.pow(inputval,f)
	if outtype == 'lnraw':
		return math.log(inputval)+f
	# z-score dependent values
	if sdrand>0:
		z = (inputval-meanrand)/sdrand #how many SDs above meanrand is this score?
		zb = (baselinevalue-meanrand)/sdrand # expected to be a negative z score
	else:
		print "error: sdrand=0", sdrand
		sys.exit()
	if outtype == "zscore":
		z = max(-d,z)+d
		return max(z,0)
	if outtype == "baselinez":
		d = -zb # recalibrate displacement to make baselinevalue = 0
		z = max(-d,z)+d
		return max(z,0)
	if outtype == "rootz":
		z = max(-d,z)+d
		z = math.pow(z,1.0/f)
		return max(z,0)
	else:
		print "***uncaught option in fix_output:", outtype
		return inputval


def sum_output(thistype, f, d, ds, dsw, oo, thesecats):
	''' add up the output scores in a dictionary that can then be sorted with the best scores at the top '''
	sr={}
	big_sr={} # hold all hits, not just the best ones
	outputcounter={}
	for dataset in ds:
		dw = dsw[dataset]
		for gene in ds[dataset]:
			dw = dw - (0.0000001 * ds[dataset].index(gene))
			try: outputcounter[gene]
			except: outputcounter[gene]={}
			try: sr[gene]
			except: 
				sr[gene]={}
				big_sr[gene]={}
			if thesecats[dataset] in outputcounter[gene]:
				# then this gene already has a score in this category
				if dw > outputcounter[gene][thesecats[dataset]]:
					# then this new score is higher than the existing one in this category
					outputcounter[gene][thesecats[dataset]] = dw 
					sr[gene][thesecats[dataset]] = "%s:%s"%(dataset, dw)
				else:
					pass
			else:
				outputcounter[gene][thesecats[dataset]] = dw
				sr[gene][thesecats[dataset]] = "%s:%s"%(dataset, dw)
			big_sr[gene][dataset] = "%s:%s"%(dataset, dw)
	sorts={}
	bd={}
	for key in outputcounter:
		bd[key]=[]
		for cat in oo:
			if cat in outputcounter[key]:
				entry = outputcounter[key][cat]
			else:
				entry = 0
			bd[key].append(entry)
		sorts[key]=sum(bd[key])
	return sorts, sr, bd, big_sr

#------------------------------------
# data splits functions
#------------------------------------
def getoptimiselist(start,end, thisone, thesedatasets, thesescores):
	'''
	return the current genescores FROM ALL OTHER LISTS for a defined section of a given list
	ie Quantify the external support for each gene in this list
	'''
	w={}
	for g in thesescores:
		w[g]={}
		for d in thesescores[g]:
			s = string.split(d,"||")[0]
			if s!=thisone:
				w[g][d]=thesescores[g][d]
	o=[] 
	for i in range(start+1,end+1):
		o.append(math.sqrt(float(sum([sum(w[x].values()) for x in thesedatasets[thisone][start:i]]))/(i-start)))
	return o, w

def getsplits(thisone, thesedatasets, thesescores, c, doplotsplits=False, splitsdir='null'):
	'''
	Detect the rank positions in this ranked dataset at which it should be split
	'''
	workingsplitlen = 1 #can't be less than 1
	newsplits=[0]
	operational_wsl=[workingsplitlen]
	yvals=[]
	ch=0 # x will be the chop index
	startoptimising, wsc = getoptimiselist(ch, len(thesedatasets[thisone]) ,thisone, thesedatasets, thesescores) #best score for the remaining list
	opstore=startoptimising
	chopval = 100000
	chopvals=[]
	redo=False
	while ch < (len(thesedatasets[thisone])-workingsplitlen):
		if redo:
			optimising, wsc = getoptimiselist(ch, len(thesedatasets[thisone]) ,thisone, thesedatasets, thesescores) #best score for the remaining list
		else:
			optimising = startoptimising[ch:]
		chopvals.append(min([max(optimising)*c,chopval]))
		# ensure gradient is down
		chopval = min(chopvals)
		for m in range(len(optimising)-1,0-1,-1): #read backwards through optimising score list
			if optimising[m] > chopval:
				break
		if m==0: #then we made it all the way to the beginning without finding a split. Game over.
			ch=len(thesedatasets[thisone])
		else: # there is a new split found. Chop the list at that point.
			ch = m+1 #add one to each split list. 
		if ch < newsplits[-1]+workingsplitlen: # then this value is not a splitlen away from the last split
			ch = newsplits[-1]+workingsplitlen
		#update workingsplitlen
		thissplitlen = ch - newsplits[-1]
		workingsplitlen = max(workingsplitlen, thissplitlen)
		operational_wsl.append(workingsplitlen)
		#check if this is going to make a short final list.
		if ch > len(thesedatasets[thisone])-workingsplitlen: # then the last list will be smaller. This is not allowed.
			ch = len(thesedatasets[thisone]) # no need to update workingsplitlen as this is by definition the last one.
		#OK - employ this chosen chop.
		yvals += optimising[:(ch-newsplits[-1])]
		newsplits.append(ch)
	#one last time
	if newsplits[-1] < len(thesedatasets[thisone]):
		newsplits.append(len(thesedatasets[thisone])) #to avoid missing last entry
	#-------------
	if doplotsplits:
		#fill in the rest
		optimising,wsc = getoptimiselist(newsplits[-2], len(thesedatasets[thisone]) ,thisone, thesedatasets, thesescores)
		if len(yvals) < len(thesedatasets[thisone]):
			yvals += optimising[ch-len(thesedatasets[thisone]):] # fill in yvals to the end
		externalscores = [sum(wsc[x].values()) for x in thesedatasets[thisone]]
		savesplits(yvals, externalscores, opstore, newsplits, thisone, c, chopvals, splitsdir)
	#-------------
	return newsplits


def savesplits(yvals, externalscores, opstore, newsplits, thisone, c, chopvals, splitsdir):
	'''Save ranked list information content decay graph data'''
	json_data = {
		'yvals': yvals,
		'externalscores': externalscores,
		'opstore': opstore,
		'newsplits': newsplits,
		'thisone': thisone,
		'c': c,
		'chopvals': chopvals,
		'splitsdir': splitsdir,
	}
	with open(os.path.join(splitsdir, '{}.json'.format(thisone)), 'w') as fp:
		json.dump(json_data, fp)

#--------------------------------------------------
# generic functions
#--------------------------------------------------
def fix_permissions(this_path):
	os.system("/bin/chmod 755 %s"%(this_path))
	
def check_dir(this_dir):
	if not os.path.isdir(this_dir):
		os.mkdir(this_dir)
	fix_permissions(this_dir)

def unique_in_order(thislist):
	newlist=[]
	alreadydict={}
	for entry in thislist:
		try:
			alreadydict[entry]
			continue
		except:
			newlist.append(entry)
			alreadydict[entry]=1
	return newlist

def quartiles(thislist):
	if len(thislist)<1:
		return "empty_thislist"
	outputs={}
	outputs[0] = min(thislist)
	outputs[1] = max(thislist)
	for i in [0.25,0.5,0.75]:
		index=int(i * float(len(thislist))) # the index in complete thislist
		if index<0:
			outputs[i] = "<%s"%thislist[0]
			continue
		try:
			thislist.sort()
			outputs[i] = thislist[index]
		except:
			outputs[i] = "centile_error"
	return [outputs[x] for x in [0,0.25,0.5,0.75,1]]

def msd(x):
	n, mean, std = len(x), 0, 0
	for a in x:
		mean = mean + a
	mean = mean / float(n)
	for a in x:
		std = std + (a - mean)**2
	std = math.sqrt(std / float(n-1))
	return mean, std

def empiricalp(thisvalue, sortedempiricalcollection):
	if len(sortedempiricalcollection) == 0:
		return 1
	return 1-float(bisect_left(sortedempiricalcollection,thisvalue))/len(sortedempiricalcollection)  #  already accounts for duplicate values. 

#--------------------------------------------------
#--------------------------------------------------
