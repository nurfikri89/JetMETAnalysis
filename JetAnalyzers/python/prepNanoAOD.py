import FWCore.ParameterSet.Config as cms

from PhysicsTools.NanoAOD.common_cff import Var, P4Vars

from RecoJets.JetProducers.PFJetParameters_cfi import PFJetParameters
from RecoJets.JetProducers.GenJetParameters_cfi import GenJetParameters
from RecoJets.JetProducers.AnomalousCellParameters_cfi import AnomalousCellParameters

from Configuration.Eras.Modifier_run2_miniAOD_80XLegacy_cff import run2_miniAOD_80XLegacy
from Configuration.Eras.Modifier_run2_nanoAOD_94X2016_cff import run2_nanoAOD_94X2016

from PhysicsTools.PatAlgos.tools.jetTools import addJetCollection
from PhysicsTools.PatAlgos.producersLayer1.jetUpdater_cfi import updatedPatJets
from PhysicsTools.PatAlgos.recoLayer0.jetCorrFactors_cfi import patJetCorrFactors

#TODO: review pT thresholds
#TODO: consider CALO, JPT jets
#TODO: handle PUPPI method in JetAdder

PRECISION = 10
JETVARS = cms.PSet(P4Vars,
  area      = Var("jetArea()",                                        float, doc = "jet catchment area, for JECs",                                         precision = PRECISION),
  chHEF     = Var("chargedHadronEnergyFraction()",                    float, doc = "charged Hadron Energy Fraction",                                       precision = PRECISION),
  neHEF     = Var("neutralHadronEnergyFraction()",                    float, doc = "neutral Hadron Energy Fraction",                                       precision = PRECISION),
  chEmEF    = Var("chargedEmEnergyFraction()",                        float, doc = "charged Electromagnetic Energy Fraction",                              precision = PRECISION),
  neEmEF    = Var("neutralEmEnergyFraction()",                        float, doc = "neutral Electromagnetic Energy Fraction",                              precision = PRECISION),
  muEF      = Var("muonEnergyFraction()",                             float, doc = "muon Energy Fraction",                                                 precision = PRECISION),
  HFHEF     = Var("HFHadronEnergyFraction()",                         float, doc = "energy fraction in forward hadronic calorimeter",                      precision = PRECISION),
  HFEMEF    = Var("HFEMEnergyFraction()",                             float, doc = "energy fraction in forward EM calorimeter",                            precision = PRECISION),
  rawFactor = Var("1.-jecFactor('Uncorrected')",                      float, doc = "1 - Factor to get back to raw pT",                                     precision = PRECISION),
  jetId     = Var("userInt('tightId')*2+4*userInt('tightIdLepVeto')", int,   doc = "Jet ID flags bit1 is loose, bit2 is tight, bit3 is tightLepVeto",      precision = PRECISION),
  jercCHPUF = Var("userFloat('jercCHPUF')",                           float, doc = "Pileup Charged Hadron Energy Fraction with the JERC group definition", precision = PRECISION),
  jercCHF   = Var("userFloat('jercCHF')",                             float, doc = "Charged Hadron Energy Fraction with the JERC group definition",        precision = PRECISION),
)

for modifier in run2_miniAOD_80XLegacy, run2_nanoAOD_94X2016:
  modifier.toModify(JETVARS,
    jetId = Var("userInt('tightId')*2+userInt('looseId')", int, doc = "Jet ID flags bit1 is loose, bit2 is tight", precision = PRECISION)
  )

import copy
import re

class JetAdder(object):
  def __init__(self):
    self.prerequisites = []
    self.main = []
    
    self.bTagDiscriminators = [
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
    self.JETCorrLevels = [ "L1FastJet", "L2Relative", "L3Absolute" ]

    self.algoMap = {
      "ak" : "AntiKt",
      "ca" : "CambridgeAachen",
    }
    self.algoKey     = 'algo'
    self.sizeKey     = 'size'
    self.puMethodKey = 'puMethod'
    self.jetRegex = re.compile(r'(?P<{algo}>({algoList}))(?P<{size}>[0-9]+)pf(?P<{puMethod}>(chs|puppi|sk|cs|))'.format(
      algo     = self.algoKey,
      algoList = '|'.join(self.algoMap.keys()),
      size     = self.sizeKey,
      puMethod = self.puMethodKey,
    ))

  def getSequence(self, proc):
    resultSequence = cms.Sequence()
    tasks = self.prerequisites + self.main
    for idx, task in enumerate(tasks):
      resultSequence.insert(idx, getattr(proc, task))
    return resultSequence
  
  def addCollection(self,
        proc,
        jet,
        name,
        doc,
        minPt = 5.,
        inputCollection = "",
        bTagDiscriminators = None,
        JETCorrLevels = None,
        pfLabel = "packedPFCandidates",
        pvLabel = "offlineSlimmedPrimaryVertices",
        svLabel = "slimmedSecondaryVertices",
        muLabel = "slimmedMuons",
        elLabel = "slimmedElectrons",
        gpLabel = "prunedGenParticles",
      ):

    print("prepNanoAOD::JetAdder::addCollection: adding collection: {}".format(jet))

    if not bTagDiscriminators:
      bTagDiscriminators = self.bTagDiscriminators
    if not JETCorrLevels:
      JETCorrLevels = self.JETCorrLevels

    # decide which jet collection we're dealing with
    jetLower = jet.lower()
    jetUpper = jet.upper()
    jetMatch = self.jetRegex.match(jetLower)
    if not jetMatch:
      raise RuntimeError('Invalid jet collection: %s' % jet)
    jetAlgo     = jetMatch.group(self.algoKey)
    jetSize     = jetMatch.group(self.sizeKey)
    jetPUMethod = jetMatch.group(self.puMethodKey)

    jet_size_nr = float(jetSize) / 10.

    currentTasks = []

    if not inputCollection:
      # set up PF candidates
      pfCand = "{}{}".format(pfLabel, jetPUMethod)
      if pfCand not in self.prerequisites:
        if jetPUMethod == "":
          pass
        elif jetPUMethod == "chs":
          setattr(proc, pfCand,
            cms.EDFilter("CandPtrSelector",
              src = cms.InputTag(pfLabel),
              cut = cms.string("fromPV"),
            )
          )
          self.prerequisites.append(pfCand)
        else:
          raise RuntimeError("Currently unsupported PU method: '%s'" % jetPUMethod)

      # set up gen particles
      genPartNoNu = "{}{}{}".format(jetAlgo.upper(), jetSize, 'GenJetsNoNu')
      if genPartNoNu not in self.prerequisites:
        packedGenPartNoNu = "packedGenParticlesForJetsNoNu"
        if packedGenPartNoNu not in self.prerequisites:
          setattr(proc, packedGenPartNoNu, cms.EDFilter("CandPtrSelector",
              src = cms.InputTag("packedGenParticles"),
              cut = cms.string("abs(pdgId) != 12 && abs(pdgId) != 14 && abs(pdgId) != 16"),
            )
          )
          self.prerequisites.append(packedGenPartNoNu)
        setattr(proc, genPartNoNu,
          cms.EDProducer("FastjetJetProducer",
            GenJetParameters.clone(
              src = packedGenPartNoNu,
            ),
            AnomalousCellParameters,
            jetAlgorithm = cms.string(self.algoMap[jetAlgo]),
            rParam       = cms.double(jet_size_nr),
          )
        )
        self.prerequisites.append(genPartNoNu)

      # create the recojet collection
      jetCollection = '{}Collection'.format(jetUpper)
      if jetCollection in self.main:
        raise ValueError("Step '%s' already implemented" % jetCollection)
      setattr(proc, jetCollection,
        cms.EDProducer("FastjetJetProducer",
          PFJetParameters.clone(
            src           = cms.InputTag(pfCand),
            doAreaFastjet = True,
            jetPtMin      = cms.double(minPt),
          ),
          AnomalousCellParameters,
          jetAlgorithm  = cms.string(self.algoMap[jetAlgo]),
          rParam        = cms.double(jet_size_nr),
        )
      )
      currentTasks.append(jetCollection)

      # PATify
      jetCorrections = ("{}{}PF{}".format(jetAlgo.upper(), jetSize, jetPUMethod.lower()), JETCorrLevels, "None")
      addJetCollection(
        proc,
        labelName          = jetUpper,
        jetSource          = cms.InputTag(jetCollection),
        algo               = jetAlgo,
        rParam             = jet_size_nr,
        pvSource           = cms.InputTag(pvLabel),
        pfCandidates       = cms.InputTag(pfLabel),
        svSource           = cms.InputTag(svLabel),
        muSource           = cms.InputTag(muLabel),
        elSource           = cms.InputTag(elLabel),
        btagDiscriminators = bTagDiscriminators,
        jetCorrections     = jetCorrections,
        genJetCollection   = cms.InputTag(genPartNoNu),
        genParticles       = cms.InputTag(gpLabel),
      )
      selJet = "selectedPatJets{}".format(jetUpper)
    else:
      selJet = "slimmedJetsPuppi"

    jercVar = "jercVars{}".format(jetUpper)
    if jercVar in self.main:
      raise ValueError("Step '%s' already implemented" % jercVar)
    setattr(proc, jercVar, proc.jercVars.clone(srcJet = cms.InputTag(selJet)))
    currentTasks.append(jercVar)

    looseJetId = "looseJetId{}".format(jetUpper)
    if looseJetId in self.main:
      raise ValueError("Step '%s' already implemented" % looseJetId)
    setattr(proc, looseJetId, proc.looseJetId.clone(src = cms.InputTag(selJet)))

    tightJetId = "tightJetId{}".format(jetUpper)
    if tightJetId in self.main:
      raise ValueError("Step '%s' already implemented" % tightJetId)
    setattr(proc, tightJetId, proc.tightJetId.clone(src = cms.InputTag(selJet)))
    currentTasks.append(tightJetId)

    tightJetIdLepVeto = "tightJetIdLepVeto{}".format(jetUpper)
    if tightJetIdLepVeto in self.main:
      raise ValueError("Step '%s' already implemented" % tightJetIdLepVeto)
    setattr(proc, tightJetIdLepVeto, proc.tightJetIdLepVeto.clone(src = cms.InputTag(selJet)))
    currentTasks.append(tightJetIdLepVeto)

    selectedPatJetsWithUserData = "{}WithUserData".format(selJet)
    if selectedPatJetsWithUserData in self.main:
      raise ValueError("Step '%s' already implemented" % selectedPatJetsWithUserData)
    setattr(proc, selectedPatJetsWithUserData,
      cms.EDProducer("PATJetUserDataEmbedder",
        src = cms.InputTag(selJet),
        userFloats = cms.PSet(
          jercCHPUF = cms.InputTag("{}:chargedHadronPUEnergyFraction".format(jercVar)),
          jercCHF   = cms.InputTag("{}:chargedHadronCHSEnergyFraction".format(jercVar)),
        ),
        userInts = cms.PSet(
          tightId        = cms.InputTag(tightJetId),
          tightIdLepVeto = cms.InputTag(tightJetIdLepVeto),
        ),
      )
    )
    for modifier in run2_miniAOD_80XLegacy, run2_nanoAOD_94X2016:
      selectedPatJetsWithUserDataObj = getattr(proc, selectedPatJetsWithUserData)
      modifier.toModify(selectedPatJetsWithUserDataObj.userInts,
        looseId        = cms.InputTag(looseJetId),
        tightIdLepVeto = None,
      )
    currentTasks.append(selectedPatJetsWithUserData)

    jetCorrFactors = "jetCorrFactors{}".format(jetUpper)
    if jetCorrFactors in self.main:
      raise ValueError("Step '%s' already implemented" % jetCorrFactors)
    setattr(proc, jetCorrFactors, patJetCorrFactors.clone(
        src             = selectedPatJetsWithUserData,
        levels          = cms.vstring(JETCorrLevels),
        primaryVertices = cms.InputTag(pvLabel),
      )
    )
    currentTasks.append(jetCorrFactors)

    updatedJets = "updatedJets{}".format(jetUpper)
    if updatedJets in self.main:
      raise ValueError("Step '%s' already implemented" % updatedJets)
    setattr(proc, updatedJets, updatedPatJets.clone(
        addBTagInfo          = False,
        jetSource            = selectedPatJetsWithUserData,
        jetCorrFactorsSource = cms.VInputTag(cms.InputTag(jetCorrFactors)),
      )
    )
    currentTasks.append(updatedJets)

    table = "{}Table".format(jetUpper)
    if table in self.main:
      raise ValueError("Step '%s' already implemented" % table)
    setattr(proc, table, cms.EDProducer("SimpleCandidateFlatTableProducer",
        src       = cms.InputTag(updatedJets),
        cut       = cms.string(""),
        name      = cms.string(name),
        doc       = cms.string(doc),
        singleton = cms.bool(False),
        extension = cms.bool(False),
        variables = JETVARS.clone(),
      )
    )
    currentTasks.append(table)

    altTasks = copy.deepcopy(currentTasks)
    for idx, task in enumerate(altTasks):
      if task == tightJetIdLepVeto:
        altTasks[idx] = looseJetId
    for modifier in run2_miniAOD_80XLegacy, run2_nanoAOD_94X2016:
      modifier.toReplaceWith(currentTasks, altTasks)

    self.main.extend(currentTasks)

def prepNanoAOD(process):

  # additional variables to AK4PFCHS
  process.jetTable.variables.HFHEF  = JETVARS.HFHEF
  process.jetTable.variables.HFEMEF = JETVARS.HFEMEF

  # additional variables to AK8PFPUPPI
  process.fatJetTable.variables.chHEF  = JETVARS.chHEF
  process.fatJetTable.variables.neHEF  = JETVARS.neHEF
  process.fatJetTable.variables.chEmEF = JETVARS.chEmEF
  process.fatJetTable.variables.neEmEF = JETVARS.neEmEF
  process.fatJetTable.variables.muEF   = JETVARS.muEF
  process.fatJetTable.variables.HFHEF  = JETVARS.HFHEF
  process.fatJetTable.variables.HFEMEF = JETVARS.HFEMEF

  process.jercVarsFatJet = process.jercVars.clone(
    srcJet = cms.InputTag("selectedUpdatedPatJetsAK8WithDeepInfo"),
    maxDR = cms.double(0.8),
  )
  process.slimmedJetsAK8WithUserData.userFloats.jercCHPUF = cms.InputTag(
    "%s:chargedHadronPUEnergyFraction"  % process.jercVarsFatJet.label()
  )
  process.slimmedJetsAK8WithUserData.userFloats.jercCHF = cms.InputTag(
    "%s:chargedHadronCHSEnergyFraction" % process.jercVarsFatJet.label()
  )
  process.fatJetTable.variables.jercCHPUF = JETVARS.jercCHPUF
  process.fatJetTable.variables.jercCHF   = JETVARS.jercCHF
  process.jetSequence.insert(0, process.jercVarsFatJet)

  # use the same cuts for AK4PFCHS and AK8PFPUPPI as in MINIAOD
  process.finalJets.cut             = cms.string("") # 15 -> 10
  process.finalJetsAK8.cut          = cms.string("") # 170 -> 170
  process.genJetTable.cut           = cms.string("") # 10 -> 8
  process.genJetFlavourTable.cut    = cms.string("") # 10 -> 8
  process.genJetAK8Table.cut        = cms.string("") # 100 -> 80
  process.genJetAK8FlavourTable.cut = cms.string("") # 100 -> 80

  ja = JetAdder()
  ja.addCollection(process, jet = "ak4pfpuppi", name = "JetPUPPI",  doc = "AK4PFPUPPI jets", inputCollection = "slimmedJetsPuppi")
  ja.addCollection(process, jet = "ak4pf",      name = "JetPF",     doc = "AK4PF jets",      minPt = 10.)
  ja.addCollection(process, jet = "ak8pfchs",   name = "FatJetCHS", doc = "AK8PFCHS jets",   minPt = 50.)
  ja.addCollection(process, jet = "ak8pf",      name = "FatJetPF",  doc = "AK8PF jets",      minPt = 20.)
  process.nanoSequenceMC += ja.getSequence(process)
