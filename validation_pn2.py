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
        kin = particle.getEnergy()
        delt = 0.5
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

hits = r.TClonesArray('ldmx::EcalHit')
tree.SetBranchAddress("ecalDigis_recon", r.AddressOf(hits))

eDepSummed = []
eDepReadout = []
for entry in xrange(0, tree.GetEntries()):
    tree.GetEntry(entry)
    eDepSum = 0
    for hit in hits : 
        #print("Energy dep from this hit is: " + str(simHit.getEdep()))
        eDepReadout.append(hit.getEnergy())
        eDepSum += simHit.getEnergy()
    eDepSummed.append(eDepSum)

#Histograms

#ROOT
c1 = TCanvas("c1")
c1.SetLogy()
hist = TH1D('readoutEdep', 'readoutEdep', 50, 0, 200)
fill_hist(hist, eDepReadout)
hist.SetTitle( "Readout Hit Energy Deposited in ECal")
#change style
#hist.SetFillColor(8)
#hist.SetFillStyle(3025)
hist.Draw()
c1.SaveAs("eDepReadoutEcal.pdf")

hist2 = TH1D('summedEdep', 'summedEdep', 50, 0, 500)
fill_hist(hist2, eDepSummed)
hist2.SetTitle( "Summed Hit Energy Deposited in ECal")
#change style
#hist2.SetFillColor(9)
#hist2.SetFillStyle(3025)
hist2.Draw()
c1.SaveAs("eDepSummedEcal.pdf")
