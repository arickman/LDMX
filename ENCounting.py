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

pionMultVec = []
protonMultVec = []
neutronMultVec = []
hardChargedMultVec = []
zeroCharged = 0
oneCharged = 0
twoCharged = 0
threeCharged = 0
fourPlusCharged = 0
zeroPion = 0
onePion = 0
twoPion = 0
threePion = 0
fourPlusPion = 0
for entry in xrange(0, tree.GetEntries()):
    tree.GetEntry(entry)
    #find the incident electron
    incidentElectron = None
    for sParticle in sParticles :
        if sParticle.getPdgID() != 11: continue
        if is_incident(sParticle) :
            incidentElectron = sParticle
            break
    

    #loop through daughters of Incident electron, which will be the products of the EN reaction.
    pionMult = 0
    protonMult = 0
    neutronMult = 0
    hardChargedMult = 0
    hardPionMult = 0
    for dCount in xrange(0, incidentElectron.getDaughterCount()):
        daughter = incidentElectron.getDaughter(dCount)
        if daughter.getCharge() != 0 and np.linalg.norm(daughter.getMomentum()) > 50 : hardChargedMult += 1
        if is_pion(daughter) and daughter.getCharge() != 0 and np.linalg.norm(daughter.getMomentum()) > 50 : hardPionMult += 1
        if is_pion(daughter) : pionMult += 1
        if daughter.getPdgID() == 2112 : neutronMult += 1
        if daughter.getPdgID() == 2212 : protonMult += 1
            

    #Add to the charged particle counters:
    if hardChargedMult == 0 : zeroCharged += 1
    if hardChargedMult == 1 : oneCharged += 1
    if hardChargedMult == 2 : twoCharged += 1
    if hardChargedMult == 3 : threeCharged += 1
    if hardChargedMult > 3 :  fourPlusCharged += 1
    if hardPionMult == 0 : zeroPion += 1
    if hardPionMult == 1 : onePion += 1
    if hardPionMult == 2 : twoPion += 1
    if hardPionMult == 3 : threePion += 1
    if hardPionMult > 3 :  fourPlusPion += 1
    

    #Append the arrays to plot 
    pionMultVec = np.append(pionMultVec, pionMult)
    protonMultVec = np.append(protonMultVec, protonMult) 
    neutronMultVec = np.append(neutronMultVec, neutronMult)
    hardChargedMultVec = np.append(hardChargedMultVec, hardChargedMult)



#Printout the counters of each fraction
print("The fraction of events with 0 hard charged particles: " + str(zeroCharged/tree.GetEntries()))
print("The fraction of events with 1 hard charged particle: " + str(oneCharged/tree.GetEntries()))
print("The fraction of events with 2 hard charged particles: " + str(twoCharged/tree.GetEntries()))
print("The fraction of events with 3 hard charged particles: " + str(threeCharged/tree.GetEntries()))
print("The fraction of events with 4+ hard charged particles: " + str(fourPlusCharged/tree.GetEntries()))
print("The fraction of events with 0 hard pions: " + str(zeroPion/tree.GetEntries()))
print("The fraction of events with 1 hard pion: " + str(onePion/tree.GetEntries()))
print("The fraction of events with 2 hard pions: " + str(twoPion/tree.GetEntries()))
print("The fraction of events with 3 hard pions: " + str(threePion/tree.GetEntries()))
print("The fraction of events with 4+ hard pions: " + str(fourPlusPion/tree.GetEntries()))


#ROOT
c1 = TCanvas("c1")
r.gStyle.SetOptStat(0)
#c1.SetLogy()
hist = TH1D('pi-mult', 'pi-mult', 30, 0, 30)
fill_hist(hist, pionMultVec)
hist.SetTitle( "Pion Multiplicity")
#change style
hist.SetFillColor(r.kGreen - 3)
#hist.SetFillStyle(3025)
hist.Draw()
c1.SaveAs("ENpionMult.pdf")

c1.Clear()
#c1.SetLogy()
hist2 = TH1D('proton-mult', 'proton-mult', 30, 0, 30)
fill_hist(hist2, protonMultVec)
hist2.SetTitle("Proton Multiplicity")
hist2.SetFillColor(r.kBlack)
#hist2.SetFillStyle(3025)
hist2.Draw()
c1.SaveAs("ENprotonMult.pdf")

c1.Clear()
#c1.SetLogy()
hist3 = TH1D('neutron-mult', 'neutron-mult', 50, 0, 100)
fill_hist(hist3, neutronMultVec)
hist3.SetTitle("Neutron Multiplicity")
hist3.SetFillColor(r.kRed)
#hist2.SetFillStyle(3025)
hist3.Draw()
c1.SaveAs("ENneutronMult.pdf")

c1.Clear()
#c1.SetLogy()
hist4 = TH1D('hard, charged particle-mult', 'hard, charged particle-mult', 50, 0, 100)
fill_hist(hist4, hardChargedMultVec)
hist4.SetTitle("Hard, Charged Particle Multiplicity")
hist4.SetFillColor(r.kBlue)
#hist2.SetFillStyle(3025)
hist4.Draw()
c1.SaveAs("ENchargedMult.pdf")











