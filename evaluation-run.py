# coding=utf-8
import sys
import os
import json
import pandas as pd
import numpy as np
import subprocess

num_simultaneous = 2
testfiledir = "testsets"
#=====
# automatically detect version
version = subprocess.check_output("git log --pretty=format:'%h' -n 1", shell=True).decode('utf-8').strip()
results_dir = "../evaluation_results/{}".format(version)
errorfile = os.path.join(results_dir, "errors.txt")
#----------
def outname(m):
    return os.path.join(results_dir, m.replace('.txt','.json'))
#----------
if not os.path.exists(results_dir):
    os.makedirs(results_dir)
if not os.path.exists(errorfile):
    e=open(errorfile,'w')
    e.write('')
    e.close()
#----------
testfiles = [x for x in os.listdir(testfiledir) if x.endswith('.txt') and not x.startswith('.')]
#====
testfiles = testfiles[:2]
#====
for filename in testfiles:
    print (filename)
    procs = {}
    cmd = "nice python maic.py -q -f {}".format(os.path.join(testfiledir, filename)) 
    try:
        results = subprocess.check_output(cmd, shell=True)
        data = json.loads(results)
        with open(outname(filename), 'w') as o:
            json.dump(data,o)
    except:
        with open(errorfile, 'a') as e:
            e.write("{}\n".format(filename))













