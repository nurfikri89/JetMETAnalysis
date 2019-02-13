import FWCore.ParameterSet.Config as cms
from PhysicsTools.NanoAOD.common_cff import Var

def prepNanoAOD(process):

  process.jetTable.variables.HFHEF  = Var("HFHadronEnergyFraction()", float, doc = "energy fraction in forward hadronic calorimeter", precision = 6)
  process.jetTable.variables.HFEMEF = Var("HFEMEnergyFraction()",     float, doc = "energy fraction in forward EM calorimeter",       precision = 6)

  process.fatJetTable.variables.chHEF  = Var("chargedHadronEnergyFraction()", float, doc = "charged Hadron Energy Fraction",                  precision = 6)
  process.fatJetTable.variables.neHEF  = Var("neutralHadronEnergyFraction()", float, doc = "neutral Hadron Energy Fraction",                  precision = 6)
  process.fatJetTable.variables.chEmEF = Var("chargedEmEnergyFraction()",     float, doc = "charged Electromagnetic Energy Fraction",         precision = 6)
  process.fatJetTable.variables.neEmEF = Var("neutralEmEnergyFraction()",     float, doc = "neutral Electromagnetic Energy Fraction",         precision = 6)
  process.fatJetTable.variables.muEF   = Var("muonEnergyFraction()",          float, doc = "muon Energy Fraction",                            precision = 6)
  process.fatJetTable.variables.HFHEF  = Var("HFHadronEnergyFraction()",      float, doc = "energy fraction in forward hadronic calorimeter", precision = 6)
  process.fatJetTable.variables.HFEMEF = Var("HFEMEnergyFraction()",          float, doc = "energy fraction in forward EM calorimeter",       precision = 6)

  process.finalJets.cut             = cms.string("") # 15 -> 10
  process.finalJetsAK8.cut          = cms.string("") # 170 -> 170
  process.genJetTable.cut           = cms.string("") # 10 -> 8
  process.genJetFlavourTable.cut    = cms.string("") # 10 -> 8
  process.genJetAK8Table.cut        = cms.string("") # 100 -> 80
  process.genJetAK8FlavourTable.cut = cms.string("") # 100 -> 80
