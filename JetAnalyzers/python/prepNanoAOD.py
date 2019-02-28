import FWCore.ParameterSet.Config as cms

from PhysicsTools.NanoAOD.common_cff import Var, P4Vars
from RecoJets.JetProducers.ak8PFJets_cfi import ak8PFJetsCHS, ak8PFJets
from RecoJets.JetProducers.ak4PFJets_cfi import ak4PFJets, ak4PFJetsPuppi
from RecoJets.JetProducers.ak4GenJets_cfi import ak4GenJets
from RecoJets.JetProducers.ak8GenJets_cfi import ak8GenJets
from Configuration.Eras.Modifier_run2_miniAOD_80XLegacy_cff import run2_miniAOD_80XLegacy
from Configuration.Eras.Modifier_run2_nanoAOD_94X2016_cff import run2_nanoAOD_94X2016
from PhysicsTools.PatAlgos.tools.jetTools import addJetCollection
from PhysicsTools.PatAlgos.producersLayer1.jetUpdater_cfi import updatedPatJets
from PhysicsTools.PatAlgos.recoLayer0.jetCorrFactors_cfi import patJetCorrFactors

def prepNanoAOD(process):
  #TODO: review pT thresholds

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

  process.jercVarsFatJet = process.jercVars.clone(srcJet = cms.InputTag("selectedUpdatedPatJetsAK8WithDeepInfo"), maxDR = cms.double(0.8))
  process.slimmedJetsAK8WithUserData.userFloats.jercCHPUF = cms.InputTag("jercVarsFatJet:chargedHadronPUEnergyFraction")
  process.slimmedJetsAK8WithUserData.userFloats.jercCHF   = cms.InputTag("jercVarsFatJet:chargedHadronCHSEnergyFraction")
  process.fatJetTable.variables.jercCHPUF = Var("userFloat('jercCHPUF')", float, doc = "Pileup Charged Hadron Energy Fraction with the JERC group definition", precision = 10)
  process.fatJetTable.variables.jercCHF   = Var("userFloat('jercCHF')",   float, doc = "Charged Hadron Energy Fraction with the JERC group definition",        precision = 10)
  process.jetSequence.insert(0, process.jercVarsFatJet)

  # use the same cuts for AK4PFCHS and AK8PFPUPPI as in MINIAOD
  process.finalJets.cut             = cms.string("") # 15 -> 10
  process.finalJetsAK8.cut          = cms.string("") # 170 -> 170
  process.genJetTable.cut           = cms.string("") # 10 -> 8
  process.genJetFlavourTable.cut    = cms.string("") # 10 -> 8
  process.genJetAK8Table.cut        = cms.string("") # 100 -> 80
  process.genJetAK8FlavourTable.cut = cms.string("") # 100 -> 80

  # define labels
  pfLabel = "packedPFCandidates"
  pvLabel = "offlineSlimmedPrimaryVertices"
  svLabel = "slimmedSecondaryVertices"
  muLabel = "slimmedMuons"
  elLabel = "slimmedElectrons"
  gpLabel = "prunedGenParticles"
  
  bTagDiscriminators = [
    'pfTrackCountingHighEffBJetTags',
    'pfTrackCountingHighPurBJetTags',
    'pfJetProbabilityBJetTags',
    'pfJetBProbabilityBJetTags',
    'pfSimpleSecondaryVertexHighEffBJetTags',
    'pfSimpleSecondaryVertexHighPurBJetTags',
    'pfCombinedSecondaryVertexV2BJetTags',
    'pfCombinedInclusiveSecondaryVertexV2BJetTags',
    'pfCombinedMVAV2BJetTags',
    'pfDeepCSVJetTags:probb',
    'pfDeepCSVJetTags:probbb',
    'pfBoostedDoubleSecondaryVertexAK8BJetTags',
  ]

  # prepare CHS
  process.chs = cms.EDFilter("CandPtrSelector",
     src = cms.InputTag(pfLabel),
     cut = cms.string("fromPV"),
  )
  process.packedGenParticlesForJetsNoNu = cms.EDFilter("CandPtrSelector",
    src = cms.InputTag("packedGenParticles"),
    cut = cms.string("abs(pdgId) != 12 && abs(pdgId) != 14 && abs(pdgId) != 16"),
  )
  process.ak4GenJetsNoNu = ak4GenJets.clone(
    src = cms.InputTag(process.packedGenParticlesForJetsNoNu.label()),
  )
  process.ak8GenJetsNoNu = ak8GenJets.clone(
    src = cms.InputTag(process.packedGenParticlesForJetsNoNu.label()),
  )
  lxCorrections = [ "L1FastJet", "L2Relative", "L3Absolute" ]
  lxCorrectionsExt = lxCorrections + [ "L2L3Residual" ]

  process.prerequisites = cms.Sequence(
    process.chs + process.packedGenParticlesForJetsNoNu + process.ak4GenJetsNoNu + process.ak8GenJetsNoNu
  )

  # prepare jet variables
  jetVars = cms.PSet(P4Vars,
    area      = Var("jetArea()",                                        float, doc = "jet catchment area, for JECs",                                         precision = 10),
    chHEF     = Var("chargedHadronEnergyFraction()",                    float, doc = "charged Hadron Energy Fraction",                                       precision = 10),
    neHEF     = Var("neutralHadronEnergyFraction()",                    float, doc = "neutral Hadron Energy Fraction",                                       precision = 10),
    chEmEF    = Var("chargedEmEnergyFraction()",                        float, doc = "charged Electromagnetic Energy Fraction",                              precision = 10),
    neEmEF    = Var("neutralEmEnergyFraction()",                        float, doc = "neutral Electromagnetic Energy Fraction",                              precision = 10),
    muEF      = Var("muonEnergyFraction()",                             float, doc = "muon Energy Fraction",                                                 precision = 10),
    HFHEF     = Var("HFHadronEnergyFraction()",                         float, doc = "energy fraction in forward hadronic calorimeter",                      precision = 10),
    HFEMEF    = Var("HFEMEnergyFraction()",                             float, doc = "energy fraction in forward EM calorimeter",                            precision = 10),
    rawFactor = Var("1.-jecFactor('Uncorrected')",                      float, doc = "1 - Factor to get back to raw pT",                                     precision = 10),
    jetId     = Var("userInt('tightId')*2+4*userInt('tightIdLepVeto')", int,   doc = "Jet ID flags bit1 is loose, bit2 is tight, bit3 is tightLepVeto",      precision = 10),
    jercCHPUF = Var("userFloat('jercCHPUF')",                           float, doc = "Pileup Charged Hadron Energy Fraction with the JERC group definition", precision = 10),
    jercCHF   = Var("userFloat('jercCHF')",                             float, doc = "Charged Hadron Energy Fraction with the JERC group definition",        precision = 10),
  )
  for modifier in run2_miniAOD_80XLegacy, run2_nanoAOD_94X2016:
    modifier.toModify(jetVars,
      jetId = Var("userInt('tightId')*2+userInt('looseId')", int, doc = "Jet ID flags bit1 is loose, bit2 is tight", precision = 10)
    )

  # introduce AK8PFCHS collection
  process.ak8PFJetsCHS = ak8PFJetsCHS.clone(
    src           = cms.InputTag(process.chs.label()),
    doAreaFastjet = True,
    jetPtMin      = cms.double(50.0),
  )
  # PATify
  ak8PFJetsCHS_label = "AK8PFJetsCHS"
  addJetCollection(
    process,
    labelName          = ak8PFJetsCHS_label,
    jetSource          = cms.InputTag(process.ak8PFJetsCHS.label()),
    algo               = "ak",
    rParam             = 0.8, #NB! expects the raw float type
    pvSource           = cms.InputTag(pvLabel),
    pfCandidates       = cms.InputTag(pfLabel),
    svSource           = cms.InputTag(svLabel),
    muSource           = cms.InputTag(muLabel),
    elSource           = cms.InputTag(elLabel),
    btagDiscriminators = bTagDiscriminators,
    jetCorrections     = ("AK8PFchs", lxCorrections, "None"),
    genJetCollection   = cms.InputTag(process.ak8GenJetsNoNu.label()),
    genParticles       = cms.InputTag(gpLabel),
  )
  sel_ak8PFJetsCHS_label = "selectedPatJets%s" % ak8PFJetsCHS_label
  process.jercVarsAK8PFJetsCHS = process.jercVars.clone(srcJet = cms.InputTag(sel_ak8PFJetsCHS_label))
  process.looseJetIdAK8PFJetsCHS = process.looseJetId.clone(src = cms.InputTag(sel_ak8PFJetsCHS_label))
  process.tightJetIdAK8PFJetsCHS = process.tightJetId.clone(src = cms.InputTag(sel_ak8PFJetsCHS_label))
  process.tightJetIdLepVetoAK8PFJetsCHS = process.tightJetIdLepVeto.clone(src = cms.InputTag(sel_ak8PFJetsCHS_label))
  process.selectedPatJetsAK8PFJetsCHSWithUserData = cms.EDProducer("PATJetUserDataEmbedder",
     src = cms.InputTag(sel_ak8PFJetsCHS_label),
     userFloats = cms.PSet(
       jercCHPUF = cms.InputTag("%s:chargedHadronPUEnergyFraction"  % process.jercVarsAK8PFJetsCHS.label()),
       jercCHF   = cms.InputTag("%s:chargedHadronCHSEnergyFraction" % process.jercVarsAK8PFJetsCHS.label())
     ),
     userInts = cms.PSet(
       tightId        = cms.InputTag(process.tightJetIdAK8PFJetsCHS.label()),
       tightIdLepVeto = cms.InputTag(process.tightJetIdLepVetoAK8PFJetsCHS.label()),
     ),
  )
  for modifier in run2_miniAOD_80XLegacy, run2_nanoAOD_94X2016:
    modifier.toModify(process.selectedPatJetsAK8PFJetsCHSWithUserData.userInts,
      looseId = cms.InputTag(process.looseJetIdAK8PFJetsCHS.label()),
      tightIdLepVeto = None,
    )
  process.jetCorrFactorsAK8PFJetsCHS = patJetCorrFactors.clone(
    src             = process.selectedPatJetsAK8PFJetsCHSWithUserData.label(),
    levels          = cms.vstring(lxCorrectionsExt),
    primaryVertices = cms.InputTag(pvLabel),
  )
  process.updatedAK8PFJetsCHS = updatedPatJets.clone(
    addBTagInfo          = False,
    jetSource            = process.selectedPatJetsAK8PFJetsCHSWithUserData.label(),
    jetCorrFactorsSource = cms.VInputTag(cms.InputTag(process.jetCorrFactorsAK8PFJetsCHS.label())),
  )
  process.ak8PFJetsCHSTable = cms.EDProducer("SimpleCandidateFlatTableProducer",
    src       = cms.InputTag(process.updatedAK8PFJetsCHS.label()),
    cut       = cms.string(""),
    name      = cms.string("FatJetCHS"),
    doc       = cms.string("AK8PFCHS jets"),
    singleton = cms.bool(False),
    extension = cms.bool(False),
    variables = jetVars.clone(),
  )
  process.ak8PFJetsCHS_sequence = cms.Sequence(
    process.ak8PFJetsCHS + process.jercVarsAK8PFJetsCHS + process.tightJetIdAK8PFJetsCHS + \
    process.tightJetIdLepVetoAK8PFJetsCHS + process.selectedPatJetsAK8PFJetsCHSWithUserData + \
    process.jetCorrFactorsAK8PFJetsCHS + process.updatedAK8PFJetsCHS + process.ak8PFJetsCHSTable
  )

  # introduce AK8PF collection
  process.ak8PFJets = ak8PFJets.clone(
    src           = cms.InputTag(pfLabel),
    doAreaFastjet = True,
    jetPtMin      = cms.double(20.0),
  )
  # PATify
  ak8PFJets_label = "AK8PFJets"
  addJetCollection(
    process,
    labelName          = ak8PFJets_label,
    jetSource          = cms.InputTag(process.ak8PFJets.label()),
    algo               = "ak",
    rParam             = 0.8, #NB! expects the raw float type
    pvSource           = cms.InputTag(pvLabel),
    pfCandidates       = cms.InputTag(pfLabel),
    svSource           = cms.InputTag(svLabel),
    muSource           = cms.InputTag(muLabel),
    elSource           = cms.InputTag(elLabel),
    btagDiscriminators = bTagDiscriminators,
    jetCorrections     = ("AK8PF", lxCorrections, "None"),
    genJetCollection   = cms.InputTag(process.ak8GenJetsNoNu.label()),
    genParticles       = cms.InputTag(gpLabel),
  )
  sel_ak8PFJets_label = "selectedPatJets%s" % ak8PFJets_label
  process.jercVarsAK8PFJets = process.jercVars.clone(srcJet = cms.InputTag(sel_ak8PFJets_label))
  process.looseJetIdAK8PFJets = process.looseJetId.clone(src = cms.InputTag(sel_ak8PFJets_label))
  process.tightJetIdAK8PFJets = process.tightJetId.clone(src = cms.InputTag(sel_ak8PFJets_label))
  process.tightJetIdLepVetoAK8PFJets = process.tightJetIdLepVeto.clone(src = cms.InputTag(sel_ak8PFJets_label))
  process.selectedPatJetsAK8PFJetsWithUserData = cms.EDProducer("PATJetUserDataEmbedder",
     src = cms.InputTag(sel_ak8PFJets_label),
     userFloats = cms.PSet(
       jercCHPUF = cms.InputTag("%s:chargedHadronPUEnergyFraction"  % process.jercVarsAK8PFJets.label()),
       jercCHF   = cms.InputTag("%s:chargedHadronCHSEnergyFraction" % process.jercVarsAK8PFJets.label())
     ),
     userInts = cms.PSet(
       tightId        = cms.InputTag(process.tightJetIdAK8PFJets.label()),
       tightIdLepVeto = cms.InputTag(process.tightJetIdLepVetoAK8PFJets.label()),
     ),
  )
  for modifier in run2_miniAOD_80XLegacy, run2_nanoAOD_94X2016:
    modifier.toModify(process.selectedPatJetsAK8PFJetsWithUserData.userInts,
      looseId = cms.InputTag(process.looseJetIdAK8PFJets.label()),
      tightIdLepVeto = None,
    )
  process.jetCorrFactorsAK8PFJets = patJetCorrFactors.clone(
    src             = process.selectedPatJetsAK8PFJetsWithUserData.label(),
    levels          = cms.vstring(lxCorrectionsExt),
    primaryVertices = cms.InputTag(pvLabel),
  )
  process.updatedAK8PFJets = updatedPatJets.clone(
    addBTagInfo          = False,
    jetSource            = process.selectedPatJetsAK8PFJetsWithUserData.label(),
    jetCorrFactorsSource = cms.VInputTag(cms.InputTag(process.jetCorrFactorsAK8PFJets.label())),
  )
  process.ak8PFJetsTable = cms.EDProducer("SimpleCandidateFlatTableProducer",
    src       = cms.InputTag(process.updatedAK8PFJets.label()),
    cut       = cms.string(""),
    name      = cms.string("FatJetPF"),
    doc       = cms.string("AK8PF jets"),
    singleton = cms.bool(False),
    extension = cms.bool(False),
    variables = jetVars.clone(),
  )
  process.ak8PFJets_sequence = cms.Sequence(
    process.ak8PFJets + process.jercVarsAK8PFJets + process.tightJetIdAK8PFJets + process.tightJetIdLepVetoAK8PFJets + \
    process.selectedPatJetsAK8PFJetsWithUserData + process.jetCorrFactorsAK8PFJets + process.updatedAK8PFJets + \
    process.ak8PFJetsTable
  )

  # introduce AK4PF collection
  process.ak4PFJets = ak4PFJets.clone(
    src           = cms.InputTag(pfLabel),
    doAreaFastjet = True,
    jetPtMin      = cms.double(10.0),
  )
  # PATify
  ak4PFJets_label = "AK4PFJets"
  addJetCollection(
    process,
    labelName          = ak4PFJets_label,
    jetSource          = cms.InputTag(process.ak4PFJets.label()),
    algo               = "ak",
    rParam             = 0.4, #NB! expects the raw float type
    pvSource           = cms.InputTag(pvLabel),
    pfCandidates       = cms.InputTag(pfLabel),
    svSource           = cms.InputTag(svLabel),
    muSource           = cms.InputTag(muLabel),
    elSource           = cms.InputTag(elLabel),
    btagDiscriminators = bTagDiscriminators,
    jetCorrections     = ("AK4PF", lxCorrections, "None"),
    genJetCollection   = cms.InputTag(process.ak4GenJetsNoNu.label()),
    genParticles       = cms.InputTag(gpLabel),
  )
  sel_ak4PFJets_label = "selectedPatJets%s" % ak4PFJets_label
  process.jercVarsAK4PFJets = process.jercVars.clone(srcJet = cms.InputTag(sel_ak4PFJets_label))
  process.looseJetIdAK4PFJets = process.looseJetId.clone(src = cms.InputTag(sel_ak4PFJets_label))
  process.tightJetIdAK4PFJets = process.tightJetId.clone(src = cms.InputTag(sel_ak4PFJets_label))
  process.tightJetIdLepVetoAK4PFJets = process.tightJetIdLepVeto.clone(src = cms.InputTag(sel_ak4PFJets_label))
  process.selectedPatJetsAK4PFJetsWithUserData = cms.EDProducer("PATJetUserDataEmbedder",
     src = cms.InputTag(sel_ak4PFJets_label),
     userFloats = cms.PSet(
       jercCHPUF = cms.InputTag("%s:chargedHadronPUEnergyFraction"  % process.jercVarsAK4PFJets.label()),
       jercCHF   = cms.InputTag("%s:chargedHadronCHSEnergyFraction" % process.jercVarsAK4PFJets.label())
     ),
     userInts = cms.PSet(
       tightId        = cms.InputTag(process.tightJetIdAK4PFJets.label()),
       tightIdLepVeto = cms.InputTag(process.tightJetIdLepVetoAK4PFJets.label()),
     ),
  )
  for modifier in run2_miniAOD_80XLegacy, run2_nanoAOD_94X2016:
    modifier.toModify(process.selectedPatJetsAK4PFJetsWithUserData.userInts,
      looseId = cms.InputTag(process.looseJetIdAK4PFJets.label()),
      tightIdLepVeto = None,
    )
  process.jetCorrFactorsAK4PFJets = patJetCorrFactors.clone(
    src             = process.selectedPatJetsAK4PFJetsWithUserData.label(),
    levels          = cms.vstring(lxCorrectionsExt),
    primaryVertices = cms.InputTag(pvLabel),
  )
  process.updatedAK4PFJets = updatedPatJets.clone(
    addBTagInfo          = False,
    jetSource            = process.selectedPatJetsAK4PFJetsWithUserData.label(),
    jetCorrFactorsSource = cms.VInputTag(cms.InputTag(process.jetCorrFactorsAK4PFJets.label())),
  )
  process.ak4PFJetsTable = cms.EDProducer("SimpleCandidateFlatTableProducer",
    src       = cms.InputTag(process.updatedAK4PFJets.label()),
    cut       = cms.string(""),
    name      = cms.string("JetPF"),
    doc       = cms.string("AK4PF jets"),
    singleton = cms.bool(False),
    extension = cms.bool(False),
    variables = jetVars.clone(),
  )
  process.ak4PFJets_sequence = cms.Sequence(
    process.ak4PFJets + process.jercVarsAK4PFJets + process.tightJetIdAK4PFJets + process.tightJetIdLepVetoAK4PFJets + \
    process.selectedPatJetsAK4PFJetsWithUserData + process.jetCorrFactorsAK4PFJets + process.updatedAK4PFJets + \
    process.ak4PFJetsTable
  )

  # introduce AK4PFPUPPI collection
  slimmedJetsPuppi_str = "slimmedJetsPuppi"
  process.jercVarsAK4PFJetsPuppi = process.jercVars.clone(srcJet = cms.InputTag(slimmedJetsPuppi_str))
  process.looseJetIdAK4PFJetsPuppi = process.looseJetId.clone(src = cms.InputTag(slimmedJetsPuppi_str))
  process.tightJetIdAK4PFJetsPuppi = process.tightJetId.clone(src = cms.InputTag(slimmedJetsPuppi_str))
  process.tightJetIdLepVetoAK4PFJetsPuppi = process.tightJetIdLepVeto.clone(src = cms.InputTag(slimmedJetsPuppi_str))
  process.slimmedJetsPuppiWithUserData = cms.EDProducer("PATJetUserDataEmbedder",
     src = cms.InputTag(slimmedJetsPuppi_str),
     userFloats = cms.PSet(
       jercCHPUF = cms.InputTag("%s:chargedHadronPUEnergyFraction"  % process.jercVarsAK4PFJetsPuppi.label()),
       jercCHF   = cms.InputTag("%s:chargedHadronCHSEnergyFraction" % process.jercVarsAK4PFJetsPuppi.label())
     ),
     userInts = cms.PSet(
       tightId        = cms.InputTag(process.tightJetIdAK4PFJetsPuppi.label()),
       tightIdLepVeto = cms.InputTag(process.tightJetIdLepVetoAK4PFJetsPuppi.label()),
     ),
  )
  for modifier in run2_miniAOD_80XLegacy, run2_nanoAOD_94X2016:
    modifier.toModify(process.slimmedJetsPuppiWithUserData.userInts,
      looseId = cms.InputTag(process.looseJetIdAK4PFJetsPuppi.label()),
      tightIdLepVeto = None,
    )
  process.ak4PFJetsPuppiTable = cms.EDProducer("SimpleCandidateFlatTableProducer",
    src       = cms.InputTag(process.slimmedJetsPuppiWithUserData.label()), # pT > 20 GeV
    cut       = cms.string(""),
    name      = cms.string("JetPUPPI"),
    doc       = cms.string("AK4PFPUPPI jets"),
    singleton = cms.bool(False),
    extension = cms.bool(False),
    variables = jetVars.clone(),
  )
  process.ak4PFJetsPuppi_sequence = cms.Sequence(
    process.jercVarsAK4PFJetsPuppi + process.tightJetIdAK4PFJetsPuppi + process.tightJetIdLepVetoAK4PFJetsPuppi + \
    process.slimmedJetsPuppiWithUserData + process.ak4PFJetsPuppiTable
  )

  _jetSequence_80X_ak8PFJetsCHS = process.ak8PFJetsCHS_sequence.copy()
  _jetSequence_80X_ak8PFJetsCHS.replace(process.tightJetIdLepVetoAK8PFJetsCHS, process.looseJetIdAK8PFJetsCHS)
  run2_miniAOD_80XLegacy.toReplaceWith(process.ak8PFJetsCHS_sequence, _jetSequence_80X_ak8PFJetsCHS)

  _jetSequence_80X_ak8PFJets = process.ak8PFJets_sequence.copy()
  _jetSequence_80X_ak8PFJets.replace(process.tightJetIdLepVetoAK8PFJets, process.looseJetIdAK8PFJets)
  run2_miniAOD_80XLegacy.toReplaceWith(process.ak8PFJets_sequence, _jetSequence_80X_ak8PFJets)

  _jetSequence_80X_ak4PFJets = process.ak4PFJets_sequence.copy()
  _jetSequence_80X_ak4PFJets.replace(process.tightJetIdLepVetoAK4PFJets, process.looseJetIdAK4PFJets)
  run2_miniAOD_80XLegacy.toReplaceWith(process.ak4PFJets_sequence, _jetSequence_80X_ak4PFJets)

  _jetSequence_80X_ak4PFJetsPuppi = process.ak4PFJetsPuppi_sequence.copy()
  _jetSequence_80X_ak4PFJetsPuppi.replace(process.tightJetIdLepVetoAK4PFJetsPuppi, process.looseJetIdAK4PFJetsPuppi)
  run2_miniAOD_80XLegacy.toReplaceWith(process.ak4PFJetsPuppi_sequence, _jetSequence_80X_ak4PFJetsPuppi)

  _jetSequence_94X2016_ak8PFJetsCHS = process.ak8PFJetsCHS_sequence.copy()
  _jetSequence_94X2016_ak8PFJetsCHS.replace(process.tightJetIdLepVetoAK8PFJetsCHS, process.looseJetIdAK8PFJetsCHS)
  run2_nanoAOD_94X2016.toReplaceWith(process.ak8PFJetsCHS_sequence, _jetSequence_94X2016_ak8PFJetsCHS)

  _jetSequence_94X2016_ak8PFJets = process.ak8PFJets_sequence.copy()
  _jetSequence_94X2016_ak8PFJets.replace(process.tightJetIdLepVetoAK8PFJets, process.looseJetIdAK8PFJets)
  run2_nanoAOD_94X2016.toReplaceWith(process.ak8PFJets_sequence, _jetSequence_94X2016_ak8PFJets)

  _jetSequence_94X2016_ak4PFJets = process.ak4PFJets_sequence.copy()
  _jetSequence_94X2016_ak4PFJets.replace(process.tightJetIdLepVetoAK4PFJets, process.looseJetIdAK4PFJets)
  run2_nanoAOD_94X2016.toReplaceWith(process.ak4PFJets_sequence, _jetSequence_94X2016_ak4PFJets)

  _jetSequence_94X2016_ak4PFJetsPuppi = process.ak4PFJetsPuppi_sequence.copy()
  _jetSequence_94X2016_ak4PFJetsPuppi.replace(process.tightJetIdLepVetoAK4PFJetsPuppi, process.looseJetIdAK4PFJetsPuppi)
  run2_nanoAOD_94X2016.toReplaceWith(process.ak4PFJetsPuppi_sequence, _jetSequence_94X2016_ak4PFJetsPuppi)

  process.nanoSequenceMC += process.prerequisites + process.ak8PFJetsCHS_sequence + process.ak8PFJets_sequence + \
                            process.ak4PFJets_sequence + process.ak4PFJetsPuppi_sequence
