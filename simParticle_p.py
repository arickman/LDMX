#plot of simParticle momentum
from __future__ import division

import numpy as np
import ROOT as r
import argparse
import copy
import os
import math
import matplotlib
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

momentum = []
for entry in xrange(0, tree.GetEntries()):
    tree.GetEntry(entry)
    pSum = 0
    for sParticle in sParticles :
        pSum += np.linalg.norm(sParticle.getMomentum())
    momentum = np.append(momentum, pSum) #should be an array of all 4's

#Generate the plot

#ROOT
hist = TH1D('momHist', 'Momentum', 20, -150, 150)
fill_hist(hist, momentum, None) #takes in weights as the 3rd arg
c1 = TCanvas("c1")
hist.SetTitle( "Momentum")
hist.Draw()
hist.Write()
c1.Update()
#c1.Print("simParticle_p.pdf")

#Python
# plt.hist(momentum)
# plt.title("3-Momentum Magnitude")
# plt.xlabel("Value")
# plt.ylabel("Frequency")
# plt.show()




