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
from ROOT import TH2D
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

protonProton = []
protonGamma = []
pionPion = []
pionGamma = []
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
    pionE = 0
    protonE = 0
    protonTheta = 0
    pionTheta = 0
    for dCount in xrange(0, PNGamma.getDaughterCount()):
        daughter = PNGamma.getDaughter(dCount)
        print("theta: " + str(find_theta(daughter)))
        if is_pion(daughter) : 
            pionMult += 1
            if pionMult == 1 : 
                pionE = daughter.getEnergy()
                pionTheta = find_theta(daughter)
        elif daughter.getPdgID() == 2212 : 
            protonMult += 1
            if protonMult == 1:
                protonE = daughter.getEnergy()
                protonTheta = find_theta(daughter)
    
    #populate the energy vs theta vectors if we are dealing with the desired single particle final state
    gammaE = PNGamma.getEnergy()
    if pionMult == 1 :
        pionPion.append([pionTheta, pionE])
        pionGamma.append([pionTheta, gammaE])
    if protonMult == 1: 
        protonProton.append([protonTheta, protonE])
        protonGamma.append([protonTheta, gammaE])


#convert to np arrays
pionPion = np.array(pionPion)
protonGamma = np.array(protonGamma)
protonProton = np.array(protonProton)
pionGamma = np.array(pionGamma)


#Histograms

#ROOT
#Scatter plot of theta vs T(pion) for single pion final state
c1 = TCanvas("c1")
r.gStyle.SetOptStat(0)
hist5 = TH2D('Theta Vs T', 'Theta vs T', 36, 0, 180, 100, 0, 10000)
fill_hist(hist5, pionPion)
hist5.SetTitle("Theta vs T(pion) for Single pion Final State")
hist5.Draw("COLZ")
c1.SaveAs("angleEnergyPion.pdf")

#Scatter plot of theta vs T(proton) for single proton final state
c1.Clear()
hist6 = TH2D('Theta Vs T', 'Theta vs T', 36, 0, 180, 100, 0, 10000)
fill_hist(hist6, protonProton)
hist6.SetTitle("Theta vs T(proton) for Single proton Final State")
hist6.Draw("COLZ")
c1.SaveAs("angleEnergyProton.pdf")

#Scatter plot of theta vs T(PNGamma) for single pion final state
c1.Clear()
hist7 = TH2D('Theta Vs T', 'Theta vs T', 36, 0, 180, 100, 0, 10000)
fill_hist(hist7, pionGamma)
hist7.SetTitle("Theta vs T(PNGamma) for Single pion Final State")
hist7.Draw("COLZ")
c1.SaveAs("angleEnergyGammaPion.pdf")

#Scatter plot of theta vs T(PNGamma) for single proton final state
c1.Clear()
hist8 = THD('Theta Vs T', 'Theta vs T', 36, 0, 180, 100, 0, 10000)
fill_hist(hist8, protonGamma)
hist8.SetTitle("Theta vs T(PNGamma) for Single proton Final State")
hist8.Draw("COLZ")
c1.SaveAs("angleEnergyGammaProton.pdf")










