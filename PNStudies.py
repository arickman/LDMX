
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
from ROOT import TColor
from root_numpy import fill_hist

from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import LogNorm

def created_within_target(particle) :
    if abs(particle.getVertex()[2]) < 0.550 : return True 
    return False

def is_incident(particle) :
    return (particle.getPdgID() == 11) & (particle.getParentCount() == 0)

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

PNGammaEnergy = []
multiplicity = []
for entry in xrange(0, tree.GetEntries()):
    tree.GetEntry(entry)
    #find the incident electron
    incidentElectron = None
    for sParticle in sParticles :
        if sParticle.getPdgID() != 11: continue
        if is_incident(sParticle) :
            incidentElectron = sParticle
            break

    #from the incident e, find the PNGamma that interacted with a nucleus in the target
#Don't fully understand how this proves that this gamma underwent a PN reaction????
    PNGamma = None
    for daughterCount in xrange(0, incidentElectron.getDaughterCount()):
        daughter = incidentElectron.getDaughter(daughterCount)
        if daughter.getDaughterCount() == 0 : continue #continue skips the rest of the commands in this iteration of the loop
        if (daughter.getPdgID() == 22 and created_within_target(daughter) and created_within_target(daughter.getDaughter(0))):
            PNGamma = daughter
            break
    PNGammaEnergy = np.append(PNGammaEnergy, PNGamma.getEnergy())
    multiplicity = np.append(multiplicity, PNGamma.getDaughterCount())

#Histogram of PN gamma energy

#ROOT
c1 = TCanvas("c1")
hist = TH1D('PNgammaEHist', 'PNGammaE', 20, 0, 5000)
fill_hist(hist, PNGammaEnergy)
hist.SetTitle( "PN Gamma Energy")
#change style
hist.SetFillColor(8)
hist.SetFillStyle(3025)
hist.Draw()
c1.SaveAs("PNGammaEnergyTest.pdf")

#Multiplicity plot
c1.Clear()
hist2 = TH1D('Mult', 'Multiplicity', 1, 0, 500)
fill_hist(hist2, multiplicity)
hist2.SetTitle("PN Multiplicity")
hist2.SetFillColor(9)
hist2.SetFillStyle(3025)
hist2.Draw()
c1.SaveAs("multiplicity.pdf")






