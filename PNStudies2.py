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

#ASSUMPTION: Hadrons only produced as daughters of a PN reaction
hardestHadronEVec = []
hardestHadronThetaVec = []
hardestPionEVec= []
hardestPionThetaVec = []
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
    
    #Now we have the PNGamma, let's loop through its daughters and find the hardest pion and hadron
    #ASSUMPTION: Hard is defined as having the greatest pz
    hardestPion = 0
    hardestHadron = 0
    hardestPionE = 0
    hardestHadronE = 0
    hardestPionTheta = 0
    hardestHadronTheta = 0
    for dCount in xrange(0, PNGamma.getDaughterCount()):
        daughter = PNGamma.getDaughter(dCount)
        if not_hadron(daughter): continue
        #Now we are dealing with a hadron, let's determine if it's a pion
        #Probably cleaner to find the hardestPion and Hadron and then get their energy and theta a single time at the end
        if is_pion(daughter) :
            if daughter.getEndPointMomentum()[2] >  hardestPion : 
                hardestPion = daughter.getEndPointMomentum()[2] 
                hardestPionE = daughter.getEnergy()
                hardestPionTheta = daughter.getEndPointMomentum()[2]/(np.linalg.norm(daughter.getEndPointMomentum()))
            if daughter.getEndPointMomentum()[2] >  hardestHadron : 
                hardestHadron = daughter.getEndPointMomentum()[2] 
                hardestHadronE = daughter.getEnergy()
                hardestHadronTheta = daughter.getEndPointMomentum()[2]/(np.linalg.norm(daughter.getEndPointMomentum()))
        #Other Hadron
        elif daughter.getEndPointMomentum()[2] >  hardestHadron : 
                hardestHadron = daughter.getEndPointMomentum()[2] 
                hardestHadronE = daughter.getEnergy()
                hardestHadronTheta = daughter.getEndPointMomentum()[2]/(np.linalg.norm(daughter.getEndPointMomentum()))

    #Append the arrays to plot now that we found the hh and hp
    hardestHadronEVec = np.append(hardestHadronEVec, hardestHadronE)
    hardestHadronThetaVec =np.append(hardestHadronThetaVec, np.arccos(hardestHadronTheta))
    hardestPionEVec = np.append(hardestPionEVec, hardestPionE)
    hardestPionThetaVec = np.append(hardestPionThetaVec, np.arccos(hardestPionTheta))

#Histograms

#ROOT
c1 = TCanvas("c1")
hist = TH1D('hhE', 'hhE', 20, 0, 5000)
fill_hist(hist, hardestHadronEVec)
hist.SetTitle( "Hardest Hadron Kinetic Energy")
#change style
hist.SetFillColor(13)
hist.SetFillStyle(3025)
hist.Draw()
c1.SaveAs("HardestHadronE.pdf")

c1.Clear()
hist2 = TH1D('hhT', 'hhT', 360, 0, 360)
fill_hist(hist2, hardestHadronThetaVec)
hist2.SetTitle("Hardest Hadron Theta")
hist2.SetFillColor(10)
hist2.SetFillStyle(3025)
hist2.Draw()
c1.SaveAs("HardestHadronTheta.pdf")

c1.Clear()
hist3 = TH1D('hpE', 'hhE', 20, 0, 5000)
fill_hist(hist3, hardestPionEVec)
hist3.SetTitle("Hardest Pion Kinetic Energy")
hist3.SetFillColor(11)
hist3.SetFillStyle(3025)
hist3.Draw()
c1.SaveAs("HardestPionE.pdf")

c1.Clear()
hist4 = TH1D('hpT', 'hpT', 360, 0, 360)
fill_hist(hist4, hardestPionThetaVec)
hist4.SetTitle("Hardest Pion Theta")
hist4.SetFillColor(12)
hist4.SetFillStyle(3025)
hist4.Draw()
c1.SaveAs("HardestPionTheta.pdf")

