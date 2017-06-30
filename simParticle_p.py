#plot of simParticle momentum
from __future__ import division

import ROOT as r
import argparse
import copy
import os
import math
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import LogNorm
from numpy import linalg as la
from scipy.stats import norm

parser = argparse.ArgumentParser(description='')
parser.add_argument('-i', action='store', dest='rfile_path', 
                    help='ROOT file to processed.')
args = parser.parse_args()

if not args.rfile_path:
    parser.error('A ROOT file needs to be specified')

ldmx_lib_path = '%s/lib/libEvent.so' % os.environ['LDMX_SW_DIR']
r.gSystem.Load(ldmx_lib_path)

rfile = r.TFile(args.rfile_path)
tree = rfile.Get("LDMX_Events")

sParticles = r.TClonesArray('ldmx::SimParticle')
tree.SetBranchAddress("SimParticles_sim", r.AddressOf(sParticles))

momentum = []
for entry in xrange(0, tree.GetEntries()):
    tree.GetEntry(entry)
    pSum = 0
    for sParticle in sParticles :
        pSum += np.linalg.norm(sParticle.getMomentum())
    momentum = np.append(momentum, pSum) #should be an array of all 4's

#Generate the plot
plt.hist(momentum)
plt.title("3-Momentum Magnitude")
plt.xlabel("Value")
plt.ylabel("Frequency")
plt.show()