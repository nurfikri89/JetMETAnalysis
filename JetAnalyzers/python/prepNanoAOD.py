import FWCore.ParameterSet.Config as cms

from PhysicsTools.NanoAOD.common_cff import Var, P4Vars
from RecoJets.JetProducers.ak8PFJets_cfi import ak8PFJetsCHS, ak8PFJets
from RecoJets.JetProducers.ak4PFJets_cfi import ak4PFJets, ak4PFJetsPuppi

def prepNanoAOD(process):
  #TODO: review pT thresholds
  #TODO: look into jet ID

  # additional variables to AK4PFCHS
  process.jetTable.variables.HFHEF  = Var("HFHadronEnergyFraction()", float, doc = "energy fraction in forward hadronic calorimeter", precision = 10)
  process.jetTable.variables.HFEMEF = Var("HFEMEnergyFraction()",     float, doc = "energy fraction in forward EM calorimeter",       precision = 10)

  # additional variables to AK8PFPUPPI
  process.fatJetTable.variables.chHEF  = Var("chargedHadronEnergyFraction()", float, doc = "charged Hadron Energy Fraction",                  precision = 10)
  process.fatJetTable.variables.neHEF  = Var("neutralHadronEnergyFraction()", float, doc = "neutral Hadron Energy Fraction",                  precision = 10)
  process.fatJetTable.variables.chEmEF = Var("chargedEmEnergyFraction()",     float, doc = "charged Electromagnetic Energy Fraction",         precision = 10)
  process.fatJetTable.variables.neEmEF = Var("neutralEmEnergyFraction()",     float, doc = "neutral Electromagnetic Energy Fraction",         precision = 10)
  process.fatJetTable.variables.muEF   = Var("muonEnergyFraction()",          float, doc = "muon Energy Fraction",                            precision = 10)
  process.fatJetTable.variables.HFHEF  = Var("HFHadronEnergyFraction()",      float, doc = "energy fraction in forward hadronic calorimeter", precision = 10)
  process.fatJetTable.variables.HFEMEF = Var("HFEMEnergyFraction()",          float, doc = "energy fraction in forward EM calorimeter",       precision = 10)

  # use the same cuts for AK4PFCHS and AK8PFPUPPI as in MINIAOD
  process.finalJets.cut             = cms.string("") # 15 -> 10
  process.finalJetsAK8.cut          = cms.string("") # 170 -> 170
  process.genJetTable.cut           = cms.string("") # 10 -> 8
  process.genJetFlavourTable.cut    = cms.string("") # 10 -> 8
  process.genJetAK8Table.cut        = cms.string("") # 100 -> 80
  process.genJetAK8FlavourTable.cut = cms.string("") # 100 -> 80

  # prepare CHS
  process.chs = cms.EDFilter("CandPtrSelector",
     src = cms.InputTag("packedPFCandidates"),
     cut = cms.string("fromPV"),
  )
  process.chs_sequence = cms.Sequence(process.chs)

  # prepare jet variables
  jetVars = cms.PSet(P4Vars,
    area      = Var("jetArea()",                     float, doc = "jet catchment area, for JECs",                    precision = 10),
    chHEF     = Var("chargedHadronEnergyFraction()", float, doc = "charged Hadron Energy Fraction",                  precision = 10),
    neHEF     = Var("neutralHadronEnergyFraction()", float, doc = "neutral Hadron Energy Fraction",                  precision = 10),
    chEmEF    = Var("chargedEmEnergyFraction()",     float, doc = "charged Electromagnetic Energy Fraction",         precision = 10),
    neEmEF    = Var("neutralEmEnergyFraction()",     float, doc = "neutral Electromagnetic Energy Fraction",         precision = 10),
    muEF      = Var("muonEnergyFraction()",          float, doc = "muon Energy Fraction",                            precision = 10),
    HFHEF     = Var("HFHadronEnergyFraction()",      float, doc = "energy fraction in forward hadronic calorimeter", precision = 10),
    HFEMEF    = Var("HFEMEnergyFraction()",          float, doc = "energy fraction in forward EM calorimeter",       precision = 10),
    rawFactor = Var("1.",                            float, doc = "default",                                                       ),
    jetId     = Var("1",                             int,   doc = "default",                                                       ),
  )

  # introduce AK8PFCHS collection
  process.ak8PFJetsCHS = ak8PFJetsCHS.clone(
    src           = cms.InputTag("chs"),
    doAreaFastjet = True,
    jetPtMin      = cms.double(20.0),
  )
  process.ak8PFJetsCHSTable = cms.EDProducer("SimpleCandidateFlatTableProducer",
    src       = cms.InputTag("ak8PFJetsCHS"),
    cut       = cms.string(""),
    name      = cms.string("FatJetCHS"),
    doc       = cms.string("AK8PFCHS jets"),
    singleton = cms.bool(False),
    extension = cms.bool(False),
    variables = jetVars.clone(),
  )
  process.ak8PFJetsCHS_sequence = cms.Sequence(process.ak8PFJetsCHS + process.ak8PFJetsCHSTable)

  # introduce AK8PF collection
  process.ak8PFJets = ak8PFJets.clone(
    src           = cms.InputTag("packedPFCandidates"),
    doAreaFastjet = True,
    jetPtMin      = cms.double(20.0),
  )
  process.ak8PFJetsTable = cms.EDProducer("SimpleCandidateFlatTableProducer",
    src       = cms.InputTag("ak8PFJets"),
    cut       = cms.string(""),
    name      = cms.string("FatJetPF"),
    doc       = cms.string("AK8PF jets"),
    singleton = cms.bool(False),
    extension = cms.bool(False),
    variables = jetVars.clone(),
  )
  process.ak8PFJets_sequence = cms.Sequence(process.ak8PFJets + process.ak8PFJetsTable)

  # introduce AK4PF collection
  process.ak4PFJets = ak4PFJets.clone(
    src           = cms.InputTag("packedPFCandidates"),
    doAreaFastjet = True,
    jetPtMin      = cms.double(10.0),
  )
  process.ak4PFJetsTable = cms.EDProducer("SimpleCandidateFlatTableProducer",
    src       = cms.InputTag("ak4PFJets"),
    cut       = cms.string(""),
    name      = cms.string("JetPF"),
    doc       = cms.string("AK4PF jets"),
    singleton = cms.bool(False),
    extension = cms.bool(False),
    variables = jetVars.clone(),
  )
  process.ak4PFJets_sequence = cms.Sequence(process.ak4PFJets + process.ak4PFJetsTable)

  # introduce AK4PFPUPPI collection
  jetVars_ak4PFJetsPuppi = jetVars.clone(
    rawFactor = Var("1.-jecFactor('Uncorrected')", float, doc = "1 - Factor to get back to raw pT", precision = 10),
  )
  process.ak4PFJetsPuppiTable = cms.EDProducer("SimpleCandidateFlatTableProducer",
    src       = cms.InputTag("slimmedJetsPuppi"), # pT > 20 GeV
    cut       = cms.string(""),
    name      = cms.string("JetPUPPI"),
    doc       = cms.string("AK4PFPUPPI jets"),
    singleton = cms.bool(False),
    extension = cms.bool(False),
    variables = jetVars_ak4PFJetsPuppi,
  )
  process.ak4PFJetsPuppi_sequence = cms.Sequence(process.ak4PFJetsPuppiTable)

  process.nanoSequenceMC += process.chs_sequence + process.ak8PFJetsCHS_sequence + process.ak8PFJets_sequence + \
                            process.ak4PFJets_sequence + process.ak4PFJetsPuppi_sequence
