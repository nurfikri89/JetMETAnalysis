import FWCore.ParameterSet.Config as cms

from PhysicsTools.NanoAOD.common_cff import Var, P4Vars
from PhysicsTools.NanoAOD.jets_cff import jetTable

from RecoJets.JetProducers.PFJetParameters_cfi import PFJetParameters
from RecoJets.JetProducers.GenJetParameters_cfi import GenJetParameters
from RecoJets.JetProducers.AnomalousCellParameters_cfi import AnomalousCellParameters

from Configuration.Eras.Modifier_run2_miniAOD_80XLegacy_cff import run2_miniAOD_80XLegacy
from Configuration.Eras.Modifier_run2_nanoAOD_94X2016_cff import run2_nanoAOD_94X2016

from PhysicsTools.PatAlgos.tools.jetTools import addJetCollection, supportedJetAlgos
from PhysicsTools.PatAlgos.producersLayer1.jetUpdater_cfi import updatedPatJets
from PhysicsTools.PatAlgos.recoLayer0.jetCorrFactors_cfi import patJetCorrFactors

from CommonTools.PileupAlgos.Puppi_cff import puppi
from CommonTools.PileupAlgos.softKiller_cfi import softKiller

import copy
import re

# the following collections have only 4-momentum, scale factor and jet area stored:
# ak4calo, ak4pfpuppi (no input collection), ak8pfpuppi (no input collection), ak4pfsk
config = [
  # standard jets
  { "jet" : "ak4pf",      "enabled" : True,  "name" : "JetPF",           "doc" : "AK4PF jets"     , "minPt" : 10. },
  { "jet" : "ak4pfpuppi", "enabled" : True,  "name" : "JetPUPPI",        "doc" : "AK4PFPUPPI jets", "inputCollection" : "slimmedJetsPuppi" }, # pT > 20
  { "jet" : "ak4calo",    "enabled" : False, "name" : "CaloJet",         "doc" : "AK4Calo jets"   , "inputCollection" : "slimmedCaloJets" }, # pT > 20
  { "jet" : "ak8pf",      "enabled" : True,  "name" : "FatJetPF",        "doc" : "AK8PF jets"     },
  { "jet" : "ak8pfchs",   "enabled" : True,  "name" : "FatJetCHS",       "doc" : "AK8PFCHS jets"  },
  # standard jets, reconstruction algorithm rerun on packedPFCandidates (in which charged particles must have pT > 3 GeV)
  { "jet" : "ak4pfchs",   "enabled" : False, "name" : "JetRebuilt",      "doc" : "AK4PFCHS jets" },
  { "jet" : "ak4pfpuppi", "enabled" : False, "name" : "JetPUPPIRebuilt", "doc" : "AK4PFPUPPI jets" },
  { "jet" : "ak8pfpuppi", "enabled" : False, "name" : "FatJetRebuilt",   "doc" : "AK8PFPUPPI jets" },
  # non-standard jets
  { "jet" : "ak1pf",      "enabled" : False, "name" : "AK1PFJet",        "doc" : "AK1PF jets" },
  { "jet" : "ak1pfchs",   "enabled" : False, "name" : "AK1Jet",          "doc" : "AK1PFCHS jets" },
  { "jet" : "ak2pf",      "enabled" : False, "name" : "AK2PFJet",        "doc" : "AK2PF jets" },
  { "jet" : "ak2pfchs",   "enabled" : False, "name" : "AK2Jet",          "doc" : "AK2PFCHS jets" },
  { "jet" : "ak5pf",      "enabled" : False, "name" : "AK5PFJet",        "doc" : "AK5PF jets" },
  { "jet" : "ak5pfchs",   "enabled" : False, "name" : "AK5Jet",          "doc" : "AK5PFCHS jets" },
  { "jet" : "ak6pf",      "enabled" : False, "name" : "AK6PFJet",        "doc" : "AK6PF jets" },
  { "jet" : "ak6pfchs",   "enabled" : False, "name" : "AK6Jet",          "doc" : "AK6PFCHS jets" },
  { "jet" : "ak7pf",      "enabled" : False, "name" : "AK7PFJet",        "doc" : "AK7PF jets" },
  { "jet" : "ak7pfchs",   "enabled" : False, "name" : "AK7Jet",          "doc" : "AK7PFCHS jets" },
  { "jet" : "ak9pf",      "enabled" : False, "name" : "AK9PFJet",        "doc" : "AK9PF jets" },
  { "jet" : "ak9pfchs",   "enabled" : False, "name" : "AK9Jet",          "doc" : "AK9PFCHS jets" },
  { "jet" : "ak10pf",     "enabled" : False, "name" : "AK10PFJet",       "doc" : "AK10PF jets" },
  { "jet" : "ak10pfchs",  "enabled" : False, "name" : "AK10Jet",         "doc" : "AK10PFCHS jets" },
  # need to use empty list of JEC levels, otherwise would get this error:
  # cannot find key X in the JEC payload, this usually means you have to change the global tag
  { "jet" : "kt4pf",      "enabled" : False, "name" : "Kt4Jet",          "doc" : "KT4PF jets",      "JETCorrLevels" : [] },
  { "jet" : "kt6pf",      "enabled" : False, "name" : "Kt6Jet",          "doc" : "KT6PF jets",      "JETCorrLevels" : [] },
  # more non-standard jets
  { "jet" : "ak4pfsk",    "enabled" : False, "name" : "AK4PFSKJet",      "doc" : "AK4PFSK jets" },
  { "jet" : "ak4pfcs",    "enabled" : False, "name" : "AK4PFCSJet",      "doc" : "AK4PFCS jets", "minPt" : 100. },
  # ca would be possible if its corrections were available in GT (JetCorrectionsRecord)
  # in principle, we could use some other jet corrections since the ca jet collection is non-standard anyways
]
config = list(filter(lambda k: k['enabled'], config))

# not meant to be used by JetAdder, rather by prodNanoAOD.sh, jet_ntuple_filler_cfg.py and run_workflow.sh
# config_ext = copy.deepcopy(config)
config_ext = []
config_ext.extend([
  { "jet" : "ak4pfchs",   "enabled" : True,  "name" : "Jet",       "genName" : "GenJet",    "inputCollection" : "slimmedJets" },
  { "jet" : "ak8pfpuppi", "enabled" : True,  "name" : "FatJet",    "genName" : "GenJetAK8", "inputCollection" : "slimmedJetsAK8" },
  { "jet" : "ak4pf",      "enabled" : True,  "name" : "JetPF",     "genName" : "GenJet",    "inputCollection" : "slimmedJets" },
  { "jet" : "ak4pfpuppi", "enabled" : True,  "name" : "JetPUPPI",  "genName" : "GenJet",    "inputCollection" : "slimmedJets" },
  { "jet" : "ak8pfchs",   "enabled" : True,  "name" : "FatJetCHS", "genName" : "GenJetAK8", "inputCollection" : "slimmedJetsAK8" },
])

binning = {
  "ak4pf"      : { "binseta" : [ -2, -1, 0, 1, 2 ], "binspt" : [ 20, 30, 50, 70, 100, 150, 200,      300, 400, 500, 600, 800, 1000 ] },
  "ak4pfchs"   : { "binseta" : [ -2, -1, 0, 1, 2 ], "binspt" : [ 20, 30, 50, 70, 100, 150, 200,      300, 400, 500, 600, 800, 1000 ] },
  "ak4pfpuppi" : { "binseta" : [ -2, -1, 0, 1, 2 ], "binspt" : [ 20, 30, 50, 70, 100, 150, 200,      300, 400, 500, 600, 800, 1000 ] },
  "ak8pf"      : { "binseta" : [ -2, -1, 0, 1, 2 ], "binspt" : [                           200, 250, 300, 400, 500, 600, 800, 1000 ] },
  "ak8pfchs"   : { "binseta" : [ -2, -1, 0, 1, 2 ], "binspt" : [                           200, 250, 300, 400, 500, 600, 800, 1000 ] },
  "ak8pfpuppi" : { "binseta" : [ -2, -1, 0, 1, 2 ], "binspt" : [                           200, 250, 300, 400, 500, 600, 800, 1000 ] },
}

def getGenJetName(name):
  return 'Gen{}'.format(name)

class JetInfo(object):
  def __init__(self, jet, inputCollection):
    self.jet = jet
    self.inputCollection = inputCollection
  
    algoKey     = 'algo'
    sizeKey     = 'size'
    recoKey     = 'reco'
    puMethodKey = 'puMethod'
    jetRegex = re.compile(
      r'(?P<{algo}>({algoList}))(?P<{size}>[0-9]+)(?P<{reco}>(pf|calo))(?P<{puMethod}>(chs|puppi|sk|cs|))'.format(
        algo     = algoKey,
        algoList = '|'.join(supportedJetAlgos.keys()),
        size     = sizeKey,
        reco     = recoKey,
        puMethod = puMethodKey,
      )
    )

    jetMatch = jetRegex.match(jet.lower())
    if not jetMatch:
      raise RuntimeError('Invalid jet collection: %s' % jet)
    self.jetAlgo     = jetMatch.group(algoKey)
    self.jetSize     = jetMatch.group(sizeKey)
    self.jetReco     = jetMatch.group(recoKey)
    self.jetPUMethod = jetMatch.group(puMethodKey)

    self.jetSizeNr = float(self.jetSize) / 10.

    self.doCalo = self.jetReco == "calo"
    self.doCS   = self.jetPUMethod == "cs"
    self.skipUserData = self.doCalo or (self.jetPUMethod in [ "puppi", "sk" ] and inputCollection == "")
    
    self.jetCorrPayload = "{}{}{}".format(
      self.jetAlgo.upper(), self.jetSize, "Calo" if self.doCalo else self.jetReco.upper()
    )
    if self.jetPUMethod == "puppi":
      self.jetCorrPayload += "Puppi"
    elif self.jetPUMethod in [ "cs", "sk" ]:
      self.jetCorrPayload += "chs"
    else:
      self.jetCorrPayload += self.jetPUMethod.lower()

JETVARS = cms.PSet(P4Vars,
  HFHEF     = Var("HFHadronEnergyFraction()", float, doc = "energy fraction in forward hadronic calorimeter", precision = 6),
  HFEMEF    = Var("HFEMEnergyFraction()",     float, doc = "energy fraction in forward EM calorimeter",       precision = 6),
  area      = jetTable.variables.area,
  chHEF     = jetTable.variables.chHEF,
  neHEF     = jetTable.variables.neHEF,
  chEmEF    = jetTable.variables.chEmEF,
  neEmEF    = jetTable.variables.neEmEF,
  muEF      = jetTable.variables.muEF,
  rawFactor = jetTable.variables.rawFactor,
  jetId     = jetTable.variables.jetId,
  jercCHPUF = jetTable.variables.jercCHPUF,
  jercCHF   = jetTable.variables.jercCHF,
)

for modifier in run2_miniAOD_80XLegacy, run2_nanoAOD_94X2016:
  modifier.toModify(JETVARS,
    jetId = Var("userInt('tightId')*2+userInt('looseId')", int, doc = "Jet ID flags bit1 is loose, bit2 is tight")
  )

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

    self.pfLabel = "packedPFCandidates"
    self.pvLabel = "offlineSlimmedPrimaryVertices"
    self.svLabel = "slimmedSecondaryVertices"
    self.muLabel = "slimmedMuons"
    self.elLabel = "slimmedElectrons"
    self.gpLabel = "prunedGenParticles"
  
  #
  # NOTE:FIKRIEDIT:This only works for 10_4_X
  # Commenting this at the moment  
  #
  # def getSequence(self, proc):
  #   resultSequence = cms.Sequence()
  #   tasks = self.prerequisites + self.main
  #   for idx, task in enumerate(tasks):
  #     resultSequence.insert(idx, getattr(proc, task))
  #   return resultSequence

  #
  # NOTE:FIKRIEDIT:This works for 10_2_15
  # Slightly modified version from above
  #
  def getSequence(self, proc):

    tasks = self.prerequisites + self.main
    for idx, task in enumerate(tasks):
      print idx, " | ", task
      if idx == 0:
        resultSequence = cms.Sequence(getattr(proc, task))
      else:
        resultSequence.insert(idx, getattr(proc, task))
    return resultSequence
  
  def addCollection(self,
        proc,
        jet,
        name,
        doc,
        genName            = "",
        minPt              = 5.,
        inputCollection    = "",
        bTagDiscriminators = None,
        JETCorrLevels      = None,
      ):

    print("prepNanoAOD::JetAdder::addCollection: adding collection: {}".format(jet))
    # print("prepNanoAOD::JetAdder::addCollection: name:{}|doc:{}|genName:{}|".format(jet,doc, genName))
    currentTasks = []

    if name in [ "Jet", "FatJet" ]:
      raise RuntimeError("Name already taken: %s" % name)

    if inputCollection and inputCollection not in [
        "slimmedJets", "slimmedJetsAK8", "slimmedJetsPuppi", "slimmedCaloJets",
      ]:
      raise RuntimeError("Invalid input collection: %s" % inputCollection)

    if bTagDiscriminators is None:
      bTagDiscriminators = self.bTagDiscriminators

    if JETCorrLevels is None:
      JETCorrLevels = self.JETCorrLevels

    # decide which jet collection we're dealing with
    jetLower = jet.lower()
    jetUpper = jet.upper()
    tagName = jetUpper
    jetInfo = JetInfo(jet, inputCollection)
    

    #
    # doGenJets? 
    # - Skip AK4GenJets and AK8GenJets.
    # They're already available in the default NanoAOD
    #
    doProduceGenJets = True
    if jetInfo.jetSize  == "4" and jetInfo.jetAlgo == "ak":
      doProduceGenJets = False
    elif jetInfo.jetSize  == "8" and jetInfo.jetAlgo == "ak":
      doProduceGenJets = False

    if inputCollection == "slimmedJets":
      assert(jetLower == "ak4pfchs")
    elif inputCollection == "slimmedJetsAK8":
      assert(jetLower == "ak8pfpuppi")
    elif inputCollection == "slimmedJetsPuppi":
      assert(jetLower == "ak4pfpuppi")
    elif inputCollection == "slimmedCaloJets":
      assert(jetLower == "ak4calo")

    if not inputCollection or jetInfo.doCalo:
      #
      # set up PF candidates
      #
      pfCand = self.pfLabel
      if jetInfo.jetPUMethod not in [ "", "cs" ]:
        pfCand += jetInfo.jetPUMethod
      if pfCand not in self.prerequisites:
        if jetInfo.jetPUMethod in [ "", "cs" ]:
          pass
        elif jetInfo.jetPUMethod == "chs":
          setattr(proc, pfCand,
            cms.EDFilter("CandPtrSelector",
              src = cms.InputTag(self.pfLabel),
              cut = cms.string("fromPV"),
            )
          )
          self.prerequisites.append(pfCand)
        elif jetInfo.jetPUMethod == "puppi":
          setattr(proc, pfCand,
            puppi.clone(
              candName   = cms.InputTag(self.pfLabel),
              vertexName = cms.InputTag(self.pvLabel),
            )
          )
          self.prerequisites.append(pfCand)
        elif jetInfo.jetPUMethod == "sk":
          setattr(proc, pfCand,
            softKiller.clone(
              PFCandidates = cms.InputTag(self.pfLabel),
              rParam       = cms.double(jetInfo.jetSizeNr),
            )
          )
          self.prerequisites.append(pfCand)
        else:
          raise RuntimeError("Currently unsupported PU method: '%s'" % jetInfo.jetPUMethod)
        # print("prepNanoAOD::JetAdder::addCollection: PUMethod prerequisites append: {}".format(pfCand))
      #
      # set up gen particles
      #
      genJetsCollection = "{}{}{}".format(jetInfo.jetAlgo.upper(), jetInfo.jetSize, 'GenJetsNoNu')
      if doProduceGenJets:
        if genJetsCollection not in self.prerequisites:
          packedGenPartNoNu = "packedGenParticlesForJetsNoNu"
          if packedGenPartNoNu not in self.prerequisites:
            setattr(proc, packedGenPartNoNu, cms.EDFilter("CandPtrSelector",
                src = cms.InputTag("packedGenParticles"),
                cut = cms.string("abs(pdgId) != 12 && abs(pdgId) != 14 && abs(pdgId) != 16"),
              )
            )
            self.prerequisites.append(packedGenPartNoNu)
            # print("prepNanoAOD::JetAdder::addCollection: GenParticles prerequisites append: {}".format(packedGenPartNoNu))
          #
          # Create the GenJet collection
          #
          setattr(proc, genJetsCollection,
            cms.EDProducer("FastjetJetProducer",
              GenJetParameters.clone(
                src          = packedGenPartNoNu,
                doAreaFastjet = cms.bool(True),
              ),
              AnomalousCellParameters,
              jetAlgorithm = cms.string(supportedJetAlgos[jetInfo.jetAlgo]),
              rParam       = cms.double(jetInfo.jetSizeNr),
            )
          )
          self.prerequisites.append(genJetsCollection)
          # print("prepNanoAOD::JetAdder::addCollection: GenJets prerequisites append: {}".format(genJetsCollection))
      #
      # create the recojet collection
      #
      if not jetInfo.doCalo:
        jetCollection = '{}Collection'.format(tagName)
        if jetCollection in self.main:
          raise ValueError("Step '%s' already implemented" % jetCollection)
        setattr(proc, jetCollection,
          cms.EDProducer("FastjetJetProducer",
            PFJetParameters.clone(
              src           = cms.InputTag(pfCand),
              doAreaFastjet = cms.bool(True),
              jetPtMin      = cms.double(minPt),
            ),
            AnomalousCellParameters,
            jetAlgorithm              = cms.string(supportedJetAlgos[jetInfo.jetAlgo]),
            rParam                    = cms.double(jetInfo.jetSizeNr),
            useConstituentSubtraction = cms.bool(jetInfo.doCS),
            csRParam                  = cms.double(0.4 if jetInfo.doCS else -1.),
            csRho_EtaMax              = PFJetParameters.Rho_EtaMax if jetInfo.doCS else cms.double(-1.),
            useExplicitGhosts         = cms.bool(jetInfo.doCS or jetInfo.jetPUMethod == "sk"),
          )
        )
        currentTasks.append(jetCollection)
      else:
        jetCollection = inputCollection

      # PATify
      if jetInfo.jetPUMethod == "puppi":
        jetCorrLabel = "Puppi"
      elif jetInfo.jetPUMethod in [ "cs", "sk" ]:
        jetCorrLabel = "chs"
      else:
        jetCorrLabel = jetInfo.jetPUMethod
      
      jetCorrections = (
        "{}{}{}{}".format(
          jetInfo.jetAlgo.upper(),
          jetInfo.jetSize,
          "Calo" if jetInfo.doCalo else jetInfo.jetReco.upper(),
          jetCorrLabel
        ),
        JETCorrLevels,
        "None",
      )
      
      #
      # Use the default AK4 and AK8 GenJets in MiniAOD for
      # any AK4 and AK8 reco jets 
      #
      if jetInfo.jetSize  == "4" and jetInfo.jetAlgo == "ak":
        genJetsCollection = "slimmedGenJets"
      elif jetInfo.jetSize  == "8" and jetInfo.jetAlgo == "ak":
        genJetsCollection = "slimmedGenJetsAK8"
      
      addJetCollection(
        proc,
        labelName          = tagName,
        jetSource          = cms.InputTag(jetCollection),
        algo               = jetInfo.jetAlgo,
        rParam             = jetInfo.jetSizeNr,
        pvSource           = cms.InputTag(self.pvLabel),
        pfCandidates       = cms.InputTag(self.pfLabel),
        svSource           = cms.InputTag(self.svLabel),
        muSource           = cms.InputTag(self.muLabel),
        elSource           = cms.InputTag(self.elLabel),
        btagDiscriminators = bTagDiscriminators if not jetInfo.doCalo else [ "None" ],
        jetCorrections     = jetCorrections,
        genJetCollection   = cms.InputTag(genJetsCollection),
        genParticles       = cms.InputTag(self.gpLabel),
      )
      
      getJetMCFlavour = not jetInfo.doCalo and jetInfo.jetPUMethod != "cs"
      
      setattr(getattr(proc, "patJets{}".format(tagName)),           "getJetMCFlavour", cms.bool(getJetMCFlavour))
      setattr(getattr(proc, "patJetCorrFactors{}".format(tagName)), "payload",         cms.string(jetInfo.jetCorrPayload))
      selJet = "selectedPatJets{}".format(tagName)
    
    else:
      if inputCollection in [ "slimmedJets", "slimmedJetsPuppi", "slimmedCaloJets" ]:
        genJetsCollection = "slimmedGenJets"
      elif inputCollection in [ "slimmedJetsAK8" ]:
        genJetsCollection = "slimmedGenJetsAK8"
      else:
        raise RuntimeError("Internal error")
      
      selJet = inputCollection

    if not jetInfo.skipUserData:
      #
      #
      #
      jercVar = "jercVars{}".format(tagName)
      if jercVar in self.main:
        raise ValueError("Step '%s' already implemented" % jercVar)
      setattr(proc, jercVar, proc.jercVars.clone(srcJet = cms.InputTag(selJet)))
      currentTasks.append(jercVar)
      #
      #
      #
      looseJetId = "looseJetId{}".format(tagName)
      if looseJetId in self.main:
        raise ValueError("Step '%s' already implemented" % looseJetId)
      setattr(proc, looseJetId, proc.looseJetId.clone(src = cms.InputTag(selJet)))
      #
      #
      #
      tightJetId = "tightJetId{}".format(tagName)
      if tightJetId in self.main:
        raise ValueError("Step '%s' already implemented" % tightJetId)
      setattr(proc, tightJetId, proc.tightJetId.clone(src = cms.InputTag(selJet)))
      currentTasks.append(tightJetId)
      #
      #
      #
      tightJetIdLepVeto = "tightJetIdLepVeto{}".format(tagName)
      if tightJetIdLepVeto in self.main:
        raise ValueError("Step '%s' already implemented" % tightJetIdLepVeto)
      setattr(proc, tightJetIdLepVeto, proc.tightJetIdLepVeto.clone(src = cms.InputTag(selJet)))
      currentTasks.append(tightJetIdLepVeto)
      #
      #
      #
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
    else:
      selectedPatJetsWithUserData = "selectedPatJets{}".format(tagName)

    # Not sure why we can't re-use patJetCorrFactors* created by addJetCollection() (even cloning doesn't work)
    # Let's just create our own
    jetCorrFactors = "jetCorrFactors{}".format(tagName)
    if jetCorrFactors in self.main:
      raise ValueError("Step '%s' already implemented" % jetCorrFactors)
    setattr(proc, jetCorrFactors, patJetCorrFactors.clone(
        src             = selectedPatJetsWithUserData,
        levels          = cms.vstring(JETCorrLevels),
        primaryVertices = cms.InputTag(self.pvLabel),
        payload         = cms.string(jetInfo.jetCorrPayload),
        rho             = "fixedGridRhoFastjetAll{}".format("Calo" if jetInfo.doCalo else ""),
      )
    )
    currentTasks.append(jetCorrFactors)

    updatedJets = "updatedJets{}".format(tagName)
    if updatedJets in self.main:
      raise ValueError("Step '%s' already implemented" % updatedJets)
    setattr(proc, updatedJets, updatedPatJets.clone(
        addBTagInfo          = False,
        jetSource            = selectedPatJetsWithUserData,
        jetCorrFactorsSource = cms.VInputTag(cms.InputTag(jetCorrFactors)),
      )
    )
    currentTasks.append(updatedJets)
    
    ############################
    # Tables
    ############################
    #
    # RecoJet Collection
    #
    table = "{}Table".format(tagName)
    if table in self.main:
      raise ValueError("Step '%s' already implemented" % table)
    
    if jetInfo.skipUserData:
      if jetInfo.doCalo:
        tableContents = cms.PSet(
          P4Vars,
          area      = jetTable.variables.area,
          rawFactor = jetTable.variables.rawFactor,
          emf       = Var("emEnergyFraction()", float, doc = "electromagnetic energy fraction", precision = 10),
        )
      else:
        tableContents = cms.PSet(
          P4Vars,
          area      = jetTable.variables.area,
          rawFactor = jetTable.variables.rawFactor,
        )
    else:
      # NOTE:FIKRIEDIT:
      #
      #
      tableContents = JETVARS.clone()
      #
      # 
      # Take variables list from original 
      # https://github.com/cms-sw/cmssw/blob/CMSSW_10_2_X/PhysicsTools/NanoAOD/python/jets_cff.py#L200
      #
      # tableContents = jetTable.variables.clone()
    
    setattr(proc, table, cms.EDProducer("SimpleCandidateFlatTableProducer",
        src       = cms.InputTag(updatedJets),
        cut       = cms.string(""),
        name      = cms.string(name),
        doc       = cms.string(doc),
        singleton = cms.bool(False),
        extension = cms.bool(False),
        variables = tableContents,
      )
    )
    currentTasks.append(table)

    #
    # 
    # 
    if doProduceGenJets:
      #
      # GenJet Collection
      #
      genJetName = genName if genName else getGenJetName(name)
      genTable = "{}GenTable".format(tagName)
      if genTable in self.main:
        raise ValueError("Step '%s' already implemented" % genTable)

      setattr(proc, genTable, cms.EDProducer("SimpleCandidateFlatTableProducer",
          src       = cms.InputTag(genJetsCollection),
          cut       = cms.string(""),
          name      = cms.string(genJetName),
          doc       = cms.string('{} (generator level)'.format(doc)),
          singleton = cms.bool(False),
          extension = cms.bool(False),
          variables = cms.PSet(P4Vars,
          area      = jetTable.variables.area,
          ),
        )
      )    
      currentTasks.append(genTable)
      #
      # GenJet Flavour Labelling
      #
      genFlavour = "{}GenFlavour".format(tagName)
      if genFlavour in self.main:
        raise ValueError("Step '%s' already implemented" % genFlavour)
      setattr(proc, genFlavour, cms.EDProducer("JetFlavourClustering",
          jets                     = cms.InputTag(genJetsCollection),
          bHadrons                 = cms.InputTag("patJetPartons", "bHadrons"),
          cHadrons                 = cms.InputTag("patJetPartons", "cHadrons"),
          partons                  = cms.InputTag("patJetPartons", "physicsPartons"),
          leptons                  = cms.InputTag("patJetPartons", "leptons"),
          jetAlgorithm             = cms.string(supportedJetAlgos[jetInfo.jetAlgo]),
          rParam                   = cms.double(jetInfo.jetSizeNr),
          ghostRescaling           = cms.double(1e-18),
          hadronFlavourHasPriority = cms.bool(False),
        )
      )
      currentTasks.append(genFlavour)
      #
      # GenJet Flavour Table
      #
      genFlavourTable = "{}GenFlavourTable".format(tagName)
      if genFlavourTable in self.main:
        raise ValueError("Step '%s' already implemented" % genFlavourTable)
      setattr(proc, genFlavourTable, cms.EDProducer("GenJetFlavourTableProducer",
          name            = cms.string(genJetName),
          src             = cms.InputTag(genJetsCollection),
          cut             = cms.string(""),
          deltaR          = cms.double(0.1),
          jetFlavourInfos = cms.InputTag(genFlavour),
        )
      )
      currentTasks.append(genFlavourTable)

    if not jetInfo.skipUserData:
      altTasks = copy.deepcopy(currentTasks)
      for idx, task in enumerate(altTasks):
        if task == tightJetIdLepVeto:
          altTasks[idx] = looseJetId
      for modifier in run2_miniAOD_80XLegacy, run2_nanoAOD_94X2016:
        modifier.toReplaceWith(currentTasks, altTasks)

    self.main.extend(currentTasks)

def prepNanoAOD(process):
  #
  # additional variables to AK4PFCHS
  #
  process.jetTable.variables.HFHEF  = JETVARS.HFHEF
  process.jetTable.variables.HFEMEF = JETVARS.HFEMEF
  #
  # additional variables to AK4GenJets
  #
  process.genJetTable.variables.area = JETVARS.area
  #
  # additional variables to AK8GenJets
  #
  process.genJetAK8Table.variables.area = JETVARS.area
  #
  # additional variables to AK8PFPUPPI
  #
  # These variables are not stored for ak8pfchs (slimmedJetsAK8)
  # in MiniAOD if their pt < 170 GeV.
  #
  process.fatJetTable.variables.chHEF  = Var("?isPFJet()?chargedHadronEnergyFraction():-1", float, doc="charged Hadron Energy Fraction", precision= 6)
  process.fatJetTable.variables.neHEF  = Var("?isPFJet()?neutralHadronEnergyFraction():-1", float, doc="neutral Hadron Energy Fraction", precision= 6)
  process.fatJetTable.variables.chEmEF = Var("?isPFJet()?chargedEmEnergyFraction():-1",     float, doc="charged Electromagnetic Energy Fraction", precision= 6)
  process.fatJetTable.variables.neEmEF = Var("?isPFJet()?neutralEmEnergyFraction():-1",     float, doc="neutral Electromagnetic Energy Fraction", precision= 6)
  process.fatJetTable.variables.muEF   = Var("?isPFJet()?muonEnergyFraction():-1",          float, doc="muon Energy Fraction", precision= 6)
  process.fatJetTable.variables.HFHEF  = Var("?isPFJet()?HFHadronEnergyFraction():-1",      float, doc="energy fraction in forward hadronic calorimeter", precision = 6)
  process.fatJetTable.variables.HFEMEF = Var("?isPFJet()?HFEMEnergyFraction():-1",          float, doc="energy fraction in forward EM calorimeter",       precision = 6)

  #
  # NOTE: FIKRI EDIT:This does NOT work with 10_2_15
  #
  # process.jercVarsFatJet = process.jercVars.clone(
  #   srcJet = cms.InputTag("selectedUpdatedPatJetsAK8WithDeepInfo"),
  #   maxDR = cms.double(0.8),
  # )
  # process.slimmedJetsAK8WithUserData.userFloats.jercCHPUF = cms.InputTag(
  #   "%s:chargedHadronPUEnergyFraction"  % process.jercVarsFatJet.label()
  # )
  # process.slimmedJetsAK8WithUserData.userFloats.jercCHF = cms.InputTag(
  #   "%s:chargedHadronCHSEnergyFraction" % process.jercVarsFatJet.label()
  # )
  #
  # This does work with 10_2_15
  #
  process.jercVarsFatJet = process.jercVars.clone(
    srcJet = cms.InputTag("updatedJetsAK8"),
    maxDR = cms.double(0.8),
  )
  process.jetSequence.insert(process.jetSequence.index(process.updatedJetsAK8WithUserData), process.jercVarsFatJet)
  
  process.updatedJetsAK8WithUserData.userFloats.jercCHPUF = cms.InputTag(
    "%s:chargedHadronPUEnergyFraction"  % process.jercVarsFatJet.label()
  )
  process.updatedJetsAK8WithUserData.userFloats.jercCHF = cms.InputTag(
    "%s:chargedHadronCHSEnergyFraction" % process.jercVarsFatJet.label()
  )
  process.fatJetTable.variables.jercCHPUF = JETVARS.jercCHPUF
  process.fatJetTable.variables.jercCHF   = JETVARS.jercCHF

  # # use the same cuts for AK4PFCHS and AK8PFPUPPI as in MINIAOD
  process.finalJets.cut             = cms.string("") # 15 -> 10
  process.finalJetsAK8.cut          = cms.string("") # 170 -> 170
  process.genJetTable.cut           = cms.string("") # 10 -> 8
  process.genJetFlavourTable.cut    = cms.string("") # 10 -> 8
  process.genJetAK8Table.cut        = cms.string("") # 100 -> 80
  process.genJetAK8FlavourTable.cut = cms.string("") # 100 -> 80

  ######################################################################################################################

  ja = JetAdder()

  for jetConfig in config:
    cfg = { k : v for k, v in jetConfig.items() if k != "enabled" }
    ja.addCollection(process, **cfg)


  process.nanoSequenceMC += ja.getSequence(process)

  # print process.nanoSequenceMC.dumpPython()
  # print process.jetSequence.dumpPython()
  # print process.jetSequence.index(process.updatedJetsAK8WithUserData)