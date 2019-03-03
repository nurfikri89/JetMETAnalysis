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

import copy
import re

JETVARS = cms.PSet(P4Vars,
  HFHEF     = Var("HFHadronEnergyFraction()", float, doc = "energy fraction in forward hadronic calorimeter", precision = 10),
  HFEMEF    = Var("HFEMEnergyFraction()",     float, doc = "energy fraction in forward EM calorimeter",       precision = 10),
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

    self.algoKey     = 'algo'
    self.sizeKey     = 'size'
    self.recoKey     = 'reco'
    self.puMethodKey = 'puMethod'
    self.jetRegex = re.compile(
      r'(?P<{algo}>({algoList}))(?P<{size}>[0-9]+)(?P<{reco}>(pf|calo))(?P<{puMethod}>(chs|puppi|sk|cs|))'.format(
        algo     = self.algoKey,
        algoList = '|'.join(supportedJetAlgos.keys()),
        size     = self.sizeKey,
        reco     = self.recoKey,
        puMethod = self.puMethodKey,
      )
    )

    self.pfLabel = "packedPFCandidates"
    self.pvLabel = "offlineSlimmedPrimaryVertices"
    self.svLabel = "slimmedSecondaryVertices"
    self.muLabel = "slimmedMuons"
    self.elLabel = "slimmedElectrons"
    self.gpLabel = "prunedGenParticles"

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
        minPt              = 5.,
        inputCollection    = "",
        bTagDiscriminators = None,
        JETCorrLevels      = None,
        postfix            = "",
      ):

    print(
      "prepNanoAOD::JetAdder::addCollection: adding collection: {}{}".format(
        jet,
        " ({})".format(postfix) if postfix else "",
      )
    )
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
    tagName = "{}{}".format(jetUpper, postfix)

    jetMatch = self.jetRegex.match(jetLower)
    if not jetMatch:
      raise RuntimeError('Invalid jet collection: %s' % jet)
    jetAlgo     = jetMatch.group(self.algoKey)
    jetSize     = jetMatch.group(self.sizeKey)
    jetReco     = jetMatch.group(self.recoKey)
    jetPUMethod = jetMatch.group(self.puMethodKey)

    jetSizeNr = float(jetSize) / 10.

    doCalo = jetReco == "calo"
    skipUserData = doCalo or (jetPUMethod == "puppi" and inputCollection == "")

    if inputCollection == "slimmedJets":
      assert(jetLower == "ak4pfchs")
    elif inputCollection == "slimmedJetsAK8":
      assert(jetLower == "ak8pfpuppi")
    elif inputCollection == "slimmedJetsPuppi":
      assert(jetLower == "ak4pfpuppi")
    elif inputCollection == "slimmedCaloJets":
      assert(jetLower == "ak4calo")
    
    jetCorrPayload = "{}{}{}".format(jetAlgo.upper(), jetSize, "Calo" if doCalo else jetReco.upper())
    if jetPUMethod == "puppi":
      jetCorrPayload += "Puppi"
    else:
      jetCorrPayload += jetPUMethod.lower()

    if not inputCollection or doCalo:
      # set up PF candidates
      pfCand = "{}{}".format(self.pfLabel, jetPUMethod)
      if pfCand not in self.prerequisites:
        if jetPUMethod == "":
          pass
        elif jetPUMethod == "chs":
          setattr(proc, pfCand,
            cms.EDFilter("CandPtrSelector",
              src = cms.InputTag(self.pfLabel),
              cut = cms.string("fromPV"),
            )
          )
          self.prerequisites.append(pfCand)
        elif jetPUMethod == "puppi":
          setattr(proc, pfCand,
            puppi.clone(
              candName   = cms.InputTag(self.pfLabel),
              vertexName = cms.InputTag(self.pvLabel),
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
            jetAlgorithm = cms.string(supportedJetAlgos[jetAlgo]),
            rParam       = cms.double(jetSizeNr),
          )
        )
        self.prerequisites.append(genPartNoNu)

      # create the recojet collection
      if not doCalo:
        jetCollection = '{}Collection'.format(tagName)
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
            jetAlgorithm  = cms.string(supportedJetAlgos[jetAlgo]),
            rParam        = cms.double(jetSizeNr),
          )
        )
        currentTasks.append(jetCollection)
      else:
        jetCollection = inputCollection

      # PATify
      jetCorrections = (
        "{}{}{}{}".format(
          jetAlgo.upper(),
          jetSize,
          "Calo" if doCalo else jetReco.upper(),
          "Puppi" if jetPUMethod == "puppi" else jetPUMethod.lower()
        ),
        JETCorrLevels,
        "None",
      )
      addJetCollection(
        proc,
        labelName          = tagName,
        jetSource          = cms.InputTag(jetCollection),
        algo               = jetAlgo,
        rParam             = jetSizeNr,
        pvSource           = cms.InputTag(self.pvLabel),
        pfCandidates       = cms.InputTag(self.pfLabel),
        svSource           = cms.InputTag(self.svLabel),
        muSource           = cms.InputTag(self.muLabel),
        elSource           = cms.InputTag(self.elLabel),
        btagDiscriminators = bTagDiscriminators if not doCalo else [ "None" ],
        jetCorrections     = jetCorrections,
        genJetCollection   = cms.InputTag(genPartNoNu),
        genParticles       = cms.InputTag(self.gpLabel),
      )
      setattr(getattr(proc, "patJets{}".format(tagName)),           "getJetMCFlavour", cms.bool(not doCalo))
      setattr(getattr(proc, "patJetCorrFactors{}".format(tagName)), "payload",         cms.string(jetCorrPayload))
      selJet = "selectedPatJets{}".format(tagName)
    else:
      if inputCollection in [ "slimmedJets", "slimmedJetsPuppi", "slimmedCaloJets" ]:
        genPartNoNu = "slimmedGenJets"
      elif inputCollection in [ "slimmedJetsAK8" ]:
        genPartNoNu = "slimmedGenJetsAK8"
      else:
        raise RuntimeError("Internal error")
      selJet = inputCollection

    if not skipUserData:
      jercVar = "jercVars{}".format(tagName)
      if jercVar in self.main:
        raise ValueError("Step '%s' already implemented" % jercVar)
      setattr(proc, jercVar, proc.jercVars.clone(srcJet = cms.InputTag(selJet)))
      currentTasks.append(jercVar)

      looseJetId = "looseJetId{}".format(tagName)
      if looseJetId in self.main:
        raise ValueError("Step '%s' already implemented" % looseJetId)
      setattr(proc, looseJetId, proc.looseJetId.clone(src = cms.InputTag(selJet)))

      tightJetId = "tightJetId{}".format(tagName)
      if tightJetId in self.main:
        raise ValueError("Step '%s' already implemented" % tightJetId)
      setattr(proc, tightJetId, proc.tightJetId.clone(src = cms.InputTag(selJet)))
      currentTasks.append(tightJetId)

      tightJetIdLepVeto = "tightJetIdLepVeto{}".format(tagName)
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
        payload         = cms.string(jetCorrPayload),
        rho             = "fixedGridRhoFastjetAll{}".format("Calo" if doCalo else ""),
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

    table = "{}Table".format(tagName)
    if table in self.main:
      raise ValueError("Step '%s' already implemented" % table)
    setattr(proc, table, cms.EDProducer("SimpleCandidateFlatTableProducer",
        src       = cms.InputTag(updatedJets),
        cut       = cms.string(""),
        name      = cms.string(name),
        doc       = cms.string(doc),
        singleton = cms.bool(False),
        extension = cms.bool(False),
        variables = JETVARS.clone() if not skipUserData else cms.PSet(
          P4Vars,
          area = jetTable.variables.area,
          rawFactor = jetTable.variables.rawFactor,
        ),
      )
    )
    currentTasks.append(table)
    
    genTable = "{}GenTable".format(tagName)
    if genTable in self.main:
      raise ValueError("Step '%s' already implemented" % genTable)
    setattr(proc, genTable, cms.EDProducer("SimpleCandidateFlatTableProducer",
        src       = cms.InputTag(genPartNoNu),
        cut       = cms.string(""),
        name      = cms.string('Gen{}'.format(name)),
        doc       = cms.string('{} (generator level)'.format(doc)),
        singleton = cms.bool(False),
        extension = cms.bool(False),
        variables = cms.PSet(P4Vars),
      )
    )
    currentTasks.append(genTable)

    if not skipUserData:
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

  ######################################################################################################################

  ja = JetAdder()

  # standard jets
  ja.addCollection(process, jet = "ak4pf",      name = "JetPF",       doc = "AK4PF jets",      minPt = 10.)
  ja.addCollection(process, jet = "ak4pfpuppi", name = "AK4JetPUPPI", doc = "AK4PFPUPPI jets", postfix = "Rebuild")
  ja.addCollection(process, jet = "ak4pfpuppi", name = "JetPUPPI",    doc = "AK4PFPUPPI jets", inputCollection = "slimmedJetsPuppi") # pT > 20
  ja.addCollection(process, jet = "ak4calo",    name = "CaloJet",     doc = "AK4Calo jets",    inputCollection = "slimmedCaloJets") # pT > 20
  ja.addCollection(process, jet = "ak8pf",      name = "FatJetPF",    doc = "AK8PF jets")
  ja.addCollection(process, jet = "ak8pfchs",   name = "FatJetCHS",   doc = "AK8PFCHS jets")

  # non-standard jets
  ja.addCollection(process, jet = "ak1pf"   ,   name = "AK1PFJet",    doc = "AK1PF jets")
  ja.addCollection(process, jet = "ak1pfchs",   name = "AK1Jet",      doc = "AK1PFCHS jets")
  ja.addCollection(process, jet = "ak2pf"   ,   name = "AK2PFJet",    doc = "AK2PF jets")
  ja.addCollection(process, jet = "ak2pfchs",   name = "AK2Jet",      doc = "AK2PFCHS jets")
  ja.addCollection(process, jet = "ak5pf",      name = "AK5PFJet",    doc = "AK5PF jets")
  ja.addCollection(process, jet = "ak5pfchs",   name = "AK5Jet",      doc = "AK5PFCHS jets")
  ja.addCollection(process, jet = "ak6pf"   ,   name = "AK6PFJet",    doc = "AK6PF jets")
  ja.addCollection(process, jet = "ak6pfchs",   name = "AK6Jet",      doc = "AK6PFCHS jets")
  ja.addCollection(process, jet = "ak7pf"   ,   name = "AK7PFJet",    doc = "AK7PF jets")
  ja.addCollection(process, jet = "ak7pfchs",   name = "AK7Jet",      doc = "AK7PFCHS jets")
  ja.addCollection(process, jet = "ak9pf"   ,   name = "AK9PFJet",    doc = "AK9PF jets")
  ja.addCollection(process, jet = "ak9pfchs",   name = "AK9Jet",      doc = "AK9PFCHS jets")
  ja.addCollection(process, jet = "ak10pf"   ,  name = "AK10PFJet",   doc = "AK10PF jets")
  ja.addCollection(process, jet = "ak10pfchs",  name = "AK10Jet",     doc = "AK10PFCHS jets")

  # need to use empty list of JEC levels, otherwise would get this error:
  # cannot find key 1 in the JEC payload, this usually means you have to change the global tag
  ja.addCollection(process, jet = "kt4pf",      name = "Kt4Jet",      doc = "KT4PF jets",      JETCorrLevels = [])
  ja.addCollection(process, jet = "kt6pf",      name = "Kt6Jet",      doc = "KT6PF jets",      JETCorrLevels = [])

  # ca would be possible if its corrections were available in JetCorrectionsRecord/GT
  # in principle, could use some other jet corrections since the jet collection is non-standard anyways

  process.nanoSequenceMC += ja.getSequence(process)

