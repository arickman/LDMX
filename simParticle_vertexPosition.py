#plot of simParticle vertex position
from __future__ import division

import numpy as np
import ROOT as r
import argparse
import copy
import os
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from ROOT import TFile,TTree,AddressOf,gROOT
from ROOT import TCanvas
from ROOT import TH1D
from ROOT import TLegend
from root_numpy import fill_hist

from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import LogNorm

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

vPos = []
for entry in xrange(0, tree.GetEntries()):
    tree.GetEntry(entry)
    for sParticle in sParticles :
    	vPos = np.append(vPos, sParticle.getVertex()[2])
    	if abs(sParticle.getVertex()[2]) < 100:
    		print("Particle Type: " + str(sParticle.getPdgID()))
    		print("Vertex Position: " + str(sParticle.getVertex()[2]))

#Generate the plot

#Python
plt.hist(vPos)
plt.title("Vertex Position")
plt.xlabel("Value")
plt.ylabel("Frequency")
plt.show()
plt.savefig('simParticle_vPos.pdf')







