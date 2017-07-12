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

def created_within_target(particle) :
    if abs(particle.getVertex()[2]) < 0.550 : return True 
    return False

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
eCounter = 0
gCounter = 0
posCounter = 0
counter = 0
eVec = []
posVec = []
gammaVec = []
for entry in xrange(0, tree.GetEntries()):
    tree.GetEntry(entry)
    for sParticle in sParticles :
        vPos = np.append(vPos, sParticle.getVertex()[2])
        #if -100 < sParticle.getVertex()[2] < 50:
        if created_within_target(sParticle) :
            counter += 1
            if sParticle.getPdgID() == 11: 
                eCounter += 1
                eVec = np.append(eVec, sParticle.getEnergy())
            if sParticle.getPdgID() == 22: 
                gCounter += 1
                gammaVec = np.append(gammaVec, sParticle.getEnergy())
            if sParticle.getPdgID() == -11: 
                posCounter += 1
                posVec = np.append(posVec, sParticle.getEnergy())
    	#print("Particle Type: " + str(sParticle.getPdgID()))
    	#print("Vertex Position: " + str(sParticle.getVertex()[2]))
print("Electron Count: " + str(eCounter))
print("Gamma Count: " + str(gCounter))
print("Positron Count: " + str(posCounter))
print("Total Particles: " + str(counter))
#Generate the plot

#Python
plt.hist(vPos)
plt.title("Vertex Position")
plt.xlabel("Value")
plt.ylabel("Frequency")
plt.show()
plt.savefig('simParticle_vPos.pdf')

#ROOT
r.gStyle->SetOptStat(0)
c1 = TCanvas("c1")
c1.SetLogy()
r.gStyle->SetOptStat(0)
myLegend = TLegend(1,10,0.48,0.9)
hist = TH1D('Electron Energy', 'Electron Energy', 100, 0, 5000)
fill_hist(hist, eVec)
hist.SetTitle( "Energy of particles produced at Target")
hist.SetLineColor(1)
myLegend.AddEntry(hist, "Electron", "L")
hist.Draw()

hist2 = TH1D('Positron Energy', 'Positron Energy', 20, 0, 5000)
fill_hist(hist2, posVec)
hist2.SetLineColor(2)
myLegend.AddEntry(hist2, "Positron", "L")
hist2.Draw("same")

hist3 = TH1D('Gamma Energy', 'Gamma Energy', 20, 0, 5000)
fill_hist(hist3, gammaVec)
hist3.SetLineColor(3)
myLegend.AddEntry(hist3, "Gamma", "L")
hist3.Draw("same")
myLegend.Draw()
c1.SaveAs("energiesAtTarget.pdf")



