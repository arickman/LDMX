
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

def find_theta(particle) :
    beamLineVec = [0, 0, particle.getMomentum()[2]]
    if np.inner(particle.getMomentum(), beamLineVec) < 0 : print ("NEGATIVE")
    return 57.295779513 * np.arccos((np.inner(particle.getMomentum(), beamLineVec))/(particle.getMomentum()[2] * np.linalg.norm(daughter.getMomentum())))
    #daughter.getMomentum()[2]/(np.linalg.norm(daughter.getMomentum()))

def wExpression(particle):
    if (particle):
        mom = np.linalg.norm(particle.getMomentum())
        print("Momentum is: " + str(mom))
        kin = particle.getEnergy()
        print("kinetic energy is: " + str(kin))
        delt = 0.5
        print("W is equal to: " + str((mom + kin)/(2*math.sqrt(1 + math.pow(delt, 2)))) - delt*np.cos(find_theta(particle)))
        return ((mom + kin)/(2*math.sqrt(1 + math.pow(delt, 2)))) - delt*np.cos(find_theta(particle))

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
wVec = []
hardestHadronMomVec = []
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
    if (PNGamma) :
        print("The angle is: " + str(find_theta(PNGamma)))
        if find_theta(PNGamma) > 100 : 
            wVec.append(wExpression(PNGamma))
        PNGammaEnergy = np.append(PNGammaEnergy, PNGamma.getEnergy())
        multiplicity = np.append(multiplicity, PNGamma.getDaughterCount())

        #Now we have the PNGamma, let's loop through its daughters and find the hardest hadron
        #ASSUMPTION: Hard is defined as having the greatest pz
        hardestHadronMom = 0
        for dCount in xrange(0, PNGamma.getDaughterCount()):
            daughter = PNGamma.getDaughter(dCount)
            if not_hadron(daughter): continue
            #Now we are dealing with a hadron
            if daughter.getMomentum()[2] >  hardestHadronMom : 
                    hardestHadronMom = daughter.getMomentum()[2] 
        #Append the arrays to plot now
        hardestHadronMomVec = np.append(hardestHadronMomVec, hardestHadronMom)
    

#Histograms

#ROOT
c1 = TCanvas("c1")
c1.SetLogy()
hist = TH1D('PNgammaEHist', 'PNGammaE', 20, 0, 5000)
fill_hist(hist, PNGammaEnergy)
hist.SetTitle( "PN Gamma Energy")
#change style
hist.SetFillColor(8)
hist.SetFillStyle(3025)
hist.Draw()
c1.SaveAs("validation_PNGammaEnergy.pdf")

#Multiplicity plot
c1.Clear()
hist2 = TH1D('Mult', 'Multiplicity', 130, 0, 130)
fill_hist(hist2, multiplicity)
hist2.SetTitle("PN Multiplicity")
#hist2.SetFillColor(9)
#hist2.SetFillStyle(3025)
hist2.Draw()
c1.SaveAs("validation_multiplicity.pdf")

#w plot
c1.Clear()
hist3 = TH1D('w', 'w', 500, 0, 5000)
fill_hist(hist3, wVec)
hist3.SetTitle("W")
#hist3.SetFillColor(10)
#ist3.SetFillStyle(3025)
hist3.Draw()
c1.SaveAs("validation_W.pdf")

#ROOT-hardest hardron momentum
c1.Clear()
c1.SetLogy()
hist4 = TH1D('hhp', 'hhp', 20, 0, 5000)
fill_hist(hist4, hardestHadronMomVec)
hist4.SetTitle( "Hardest Hadron Momentum")
#change style
hist4.SetFillColor(13)
hist4.SetFillStyle(3025)
hist4.Draw()
c1.SaveAs("HardestHadronMomLogy.pdf")





