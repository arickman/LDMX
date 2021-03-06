#!/usr/bin/env python
from __future__ import division

import numpy as np
import argparse
import subprocess
import copy
import os
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import LogNorm

command = ['bash', '-c', 'source /nfs/slac/g/ldmx/users/arickman/LDMX/setup.sh && env']
proc = subprocess.Popen(command, stdout=subprocess.PIPE)

for line in proc.stdout:
    (key, _, value) = line.partition('=')
    os.environ[key] = value.strip()

proc.communicate()

os.system("source /nfs/slac/g/ldmx/users/arickman/LDMX/setup.sh")

import ROOT as r

from ROOT import TFile,TTree,AddressOf,gROOT
from ROOT import TCanvas
from ROOT import TH1D
from ROOT import TH2D
from ROOT import TLegend
from ROOT import TColor
from root_numpy import fill_hist

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

filename = args.rfile_path
nameToSave = filename[:-5] + '_result.root'
# if "_" in filename:
#     b1,b2,b3,b4,b5,b6,b7,nameToSave = filename.split("_")
# else: nameToSave = "error"

if not args.rfile_path:
    parser.error('A ROOT file needs to be specified')

ldmx_lib_path = '%s/lib/libEvent.so' % os.environ['LDMX_SW_DIR']
r.gSystem.Load(ldmx_lib_path)

rfile = r.TFile(args.rfile_path)
tree = rfile.Get("LDMX_Events")

sParticles = r.TClonesArray('ldmx::SimParticle')
tree.SetBranchAddress("SimParticles_sim", r.AddressOf(sParticles))

protonVec = []
pionVec = []
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
    pionMom = 0
    protonMom = 0
    protonTheta = 0
    pionTheta = 0
    for dCount in xrange(0, incidentElectron.getDaughterCount()):
        daughter = incidentElectron.getDaughter(dCount)
        if is_pion(daughter) : 
            pionMult += 1
            if pionMult == 1 : 
                pionMom = np.linalg.norm(daughter.getMomentum())
                pionTheta = find_theta(daughter)
        elif daughter.getPdgID() == 2212 : 
            protonMult += 1
            if protonMult == 1:
                protonMom = np.linalg.norm(daughter.getMomentum())
                protonTheta = find_theta(daughter)
    
    #populate the energy vs theta vectors if we are dealing with the desired single particle final state
    if pionMult == 1 :
        pionVec.append([pionTheta, pionMom])
    if protonMult == 1: 
        protonVec.append([protonTheta, protonMom])

#convert to np arrays
pionArray = np.array(pionVec)
protonArray = np.array(protonVec)

#Histograms

#ROOT
print 'Saving to: %s' % nameToSave                                                                    
rfile = TFile(nameToSave, "RECREATE")
#Scatter plot of theta vs T(pion) for single pion final state
c1 = TCanvas("c1")
r.gStyle.SetOptStat(0)
hist = TH2D('Theta Vs Momentum', 'Theta vs Mom', 36, 0, 180, 50, 0, 5000)
fill_hist(hist, pionArray)
hist.SetTitle("Theta vs Momentum(pion) for Single pion Final State")
#hist.Draw("COLZ")
#c1.SaveAs("/nfs/slac/g/ldmx/production/arickman/4pt0_gev_e_target_en_v3_magnet/ENangleMomPion_" + nameToSave)
hist.Write()

#Scatter plot of theta vs T(proton) for single proton final state
c1.Clear()
hist2 = TH2D('Theta Vs Momentum', 'Theta Vs Momentum', 36, 0, 180, 50, 0, 5000)
fill_hist(hist2, protonArray)
hist2.SetTitle("Theta vs Momentum(proton) for Single proton Final State")
#hist2.Draw("COLZ")
#c1.SaveAs("/nfs/slac/g/ldmx/production/arickman/4pt0_gev_e_target_en_v3_magnet/ENangleMomProton_" + nameToSave)
hist2.Write()
rfile.Close()










