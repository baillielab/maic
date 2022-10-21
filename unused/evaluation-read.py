# coding=utf-8
import json
import numpy as np
import string, sys, os, subprocess
import argparse
import pandas as pd
import seaborn as sns
import matplotlib.pylab as plt
#-----------------------------
scriptpath = os.path.dirname(os.path.realpath(__file__))
#-----------------------------
parser = argparse.ArgumentParser()
parser.add_argument('-d', '--directory',\
                default="../evaluation_results/e170662",
                help='evaluation output directory')
args = parser.parse_args()
#-----------------------------
graphdir = '../'
exclusions = ["errors.txt"]
top = 10
#-----------------------------
r = list(string.ascii_uppercase)
r += ["{}{}".format(i,j) for i in r for j in r]
real_genes = r[:100]

def meanabsoluteerror(thislist):
    # find location of all real genes and append to index list
    index_list = []
    for i in real_genes:
        try:
            val = thislist.index(i)
        except:
            # break when i is not in list
            break 
        index_list.append(val)
    # find absolute error from each real gene from where they should be located
    z = 0
    index_list2 = []
    for i in index_list:
        i = abs(i - z)
        index_list2.append(i)
        z += 1
    return np.mean(index_list2)

def compensatedaverageoverlap(lista, listb=real_genes):
    compa=1
    compb=1
    if len(listb)>len(lista):
        compb = float(len(listb))/len(lista)
    if len(lista)>len(listb):
        compb = float(len(lista))/len(listb)
    similarities = [float(len(set(lista[:int(i*compa)])&set(listb[:int(i*compb)])))/i for i in range(1,min(len(lista),len(listb)))]
    return float(sum(similarities))/len(similarities)


def makeviolins(df, label):
    df = df.reindex_axis(df.abs().max().sort_values().index, axis='columns')
    sns.set(style="whitegrid")
    #----------------------------
    ax = sns.violinplot(data=df, cut=0)
    fig = ax.get_figure()
    fig.savefig('../graph_{}.png'.format(label))
    #-----------------------------
    wee = df[list(df)[:top]]
    ax = sns.violinplot(data=wee, cut=0)
    plt.xticks(rotation=90)
    plt.tight_layout()
    fig = ax.get_figure()
    fig.savefig('../graph_top{}_{}.png'.format(top, label))
    #-----------------------------
    print (wee.describe())
#-----------------------------
resultfiles = [x for x in os.listdir(args.directory) if x not in exclusions]
#-----------------------------
dfc = pd.DataFrame({})
dfm = pd.DataFrame({})

for res in resultfiles:
    caodic={}
    maedic={}
    with open(os.path.join(args.directory, res)) as f:
        data = json.load(f)
        resultdic = {}
        for thisresult in data:
            thisletter = thisresult['name']
            s = thisresult['adjusted_scores']
            for method in s.keys():
                try:
                    resultdic[method]
                except:
                    resultdic[method]={}
                resultdic[method][thisletter]=s[method]

    for method in resultdic:
        d = resultdic[method]
        outputlist = [k for k in sorted(d, key=d.get, reverse=True)]
        cao = compensatedaverageoverlap(outputlist)
        mae = meanabsoluteerror(outputlist)
        caodic[method]=cao
        maedic[method]=mae

    caonew = pd.DataFrame(caodic, index=[res])
    maenew = pd.DataFrame(maedic, index=[res])
    dfc = pd.concat([dfc, caonew], sort=True)
    dfm = pd.concat([dfm, caonew], sort=True)
#-----------------------------

makeviolins(dfc,"cao")
makeviolins(dfm,"mae")


