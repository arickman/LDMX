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

def not_hadron(particle) : #ASSUMPTION: only non-hadrons produced are electrons, positrons and gammas
    if particle.getPdgID() == -11 or particle.getPdgID() == 11 or particle.getPdgID() == 22 :
        return True

def is_pion(particle) :
    if particle.getPdgID() == -211 or particle.getPdgID() == 111 or particle.getPdgID() == 211 :
        return True

def find_theta(particle) :
    beamLineVec = [0, 0, particle.getMomentum()[2]]
    if np.inner(particle.getMomentum(), beamLineVec) < 0 : print ("NEGATIVE")
    return 57.295779513 * np.arccos((np.inner(particle.getMomentum(), beamLineVec))/(particle.getMomentum()[2] * np.linalg.norm(daughter.getMomentum())))
    #daughter.getMomentum()[2]/(np.linalg.norm(daughter.getMomentum()))

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

pionMultVec = []
protonMultVec = []
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
    PNGamma = None
    for daughterCount in xrange(0, incidentElectron.getDaughterCount()):
        daughter = incidentElectron.getDaughter(daughterCount)
        if daughter.getDaughterCount() == 0 : continue #continue skips the rest of the commands in this iteration of the loop
        if (daughter.getPdgID() == 22 and created_within_target(daughter) and created_within_target(daughter.getDaughter(0))):
            PNGamma = daughter
            break

    #loop through daughters of PNGamma
    pionMult = 0
    protonMult = 0
    for dCount in xrange(0, PNGamma.getDaughterCount()):
        daughter = PNGamma.getDaughter(dCount)
        if is_pion(daughter) : pionMult += 1
        elif daughter.getPdgID() == 2212 : protonMult += 1
            
    #Append the arrays to plot 
    pionMultVec = np.append(pionMultVec, pionMult)
    protonMultVec = np.append(protonMultVec, protonMult)   


#Histograms

#ROOT
c1 = TCanvas("c1")
#c1.SetLogy()
hist = TH1D('pi-mult', 'pi-mult', 100, 0, 100)
fill_hist(hist, pionMultVec)
hist.SetTitle( "Pion Multiplicity")
#change style
#hist.SetFillStyle(3025)
hist.Draw()
c1.SaveAs("pionMult.pdf")

c1.Clear()
#c1.SetLogy()
hist2 = TH1D('proton-mult', 'proton-mult', 100, 0, 100)
fill_hist(hist2, protonMultVec)
hist2.SetTitle("Proton Multiplicity")
hist2.SetFillColor(r.kBlack)
#hist2.SetFillStyle(3025)
hist2.Draw()
c1.SaveAs("protonMult.pdf")

