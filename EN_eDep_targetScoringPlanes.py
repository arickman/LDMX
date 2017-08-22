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

hits = r.TClonesArray('ldmx::SimTrackerHit')
tree.SetBranchAddress("TargetScoringPlaneHits_sim", r.AddressOf(hits))

eDepVec = []
eDepSummed = []
for entry in xrange(0, tree.GetEntries()):
    tree.GetEntry(entry)
    eDepSum = 0
    for hit in hits : 
        eDepVec.append(hit.getEdep())
        eDepSum += hit.getEdep()
    eDepSummed.append(eDepSum)


#ROOT
c1 = TCanvas("c1")
r.gStyle.SetOptStat(0)
#c1.SetLogy()
hist = TH1D('eDep', 'eDep', 25, 0, 2.5)
fill_hist(hist, eDepVec)
hist.SetTitle( "Energy Deposition in Target Scoring Planes")
#change style
hist.SetFillColor(r.kGreen - 3)
#hist.SetFillStyle(3025)
hist.Draw()
c1.SaveAs("EN_eDep_targetScoringPlanes.pdf")

c1.Clear()
hist2 = TH1D('summedEdep', 'summedEdep', 200, 0, 10)
fill_hist(hist2, eDepSummed)
hist2.SetTitle( "Summed Hit Energy Deposited in Target Scoring Planes")
#change style
hist2.SetFillColor(9)
#hist2.SetFillStyle(3025)
hist2.Draw()
c1.SaveAs("eDepSummedTargetScoringPlanes.pdf")












