import FWCore.ParameterSet.Config as cms
import os
import ast

from JetMETAnalysis.JetAnalyzers.prepNanoAOD import getGenPartName, JetInfo

ENV_NAME = 'JET_NTUPLE_FILLER'
JEC_VER = 'Fall17_17Nov2017_V8_MC'

jetChoice = None
if ENV_NAME in os.environ:
    jetChoice = ast.literal_eval(os.environ['JET_NTUPLE_FILLER'])
else:
    raise RuntimeError('Environment variable %s not set' % ENV_NAME)

getFromJetChoice = lambda key: jetChoice[key] if key in jetChoice else ''

recJets = jetChoice['name']
genJets = getFromJetChoice('genName')
if not genJets:
  genJets = getGenPartName(recJets)
jetInfo = JetInfo(jetChoice['jet'], getFromJetChoice('inputCollection'))
jetName = jetChoice['jet']

outputTree_flags = 1 + 4 + 16
if 'pf' in jetChoice['jet']:
    outputTree_flags += 64
    if jetInfo.skipUserData:
        jetType = 2
    else:
        jetType = 0
elif 'calo' in jetChoice['jet']:
    outputTree_flags += 32
    jetType = 1
else:
    raise RuntimeError("Invalid jet collection: %s" % jetChoice['jet'])

process = cms.PSet()

process.fwliteInput = cms.PSet(
    fileNames = cms.vstring(),
    maxEvents = cms.int32(-1),
    outputEvery = cms.uint32(1)
)

process.fwliteOutput = cms.PSet(
    fileName = cms.string('jet_ntuple_filler_{}.root'.format(jetName))
)

process.jet_ntuple_filler = cms.PSet(
    inputTreeName = cms.string('Events'),

    src_recJets     = cms.string(recJets),
    src_genJets     = cms.string(genJets),
    src_numPU       = cms.string('Pileup_nPU'),
    src_numPU_true  = cms.string('Pileup_nTrueInt'),
    src_numVertices = cms.string('PV_npvsGood'),
    src_vertexZ     = cms.string('PV_z'),
    src_rho         = cms.string('fixedGridRhoFastjetAll'),
    src_weight      = cms.string('Generator_weight'),
    src_pThat       = cms.string('Generator_binvar'),
    src_pudensity   = cms.string('Pileup_pudensity'),
    src_gpudensity  = cms.string('Pileup_gpudensity'),
    
    dR_match = cms.double(0.25),

    # Flag to apply jet energy corrections (after correcting back the jet energies stored on nanoAOD to their "raw" values).
    # The following settings are supported for this flag:
    #  - 'l1'     (L1Fastjet)
    #  - 'l2l3'   (L2Relative+L3Absolute)
    #  - 'l1l2l3' (L1Fastjet+L2Relative+L3Absolute)
    #  - ''       (no jet energy corrections applied -- the default)
    jetCorrectionLevels = cms.string(''),
    jecFilePath = cms.string('JetMETAnalysis/JetAnalyzers/data/JEC_{}/'.format(JEC_VER)),
    jecFileName_l1 = cms.string('{}_L1FastJet_{}.txt'.format(JEC_VER, jetInfo.jetCorrPayload)),
    jecFileName_l2 = cms.string('{}_L2Relative_{}.txt'.format(JEC_VER, jetInfo.jetCorrPayload)),
    jecFileName_l3 = cms.string('{}_L3Absolute_{}.txt'.format(JEC_VER, jetInfo.jetCorrPayload)),
    
    outputTreeName = cms.string('{}/t'.format(jetName)),
    # Configuration of output TTree. The value is bit coded. 
    # The bits have the following meaning:
    # - 0  (  1) to be enabled always
    # - 1  (  2) enable if calibrating HLT jets
    # - 2  (  4) enable generator-level jet flavor matching
    # - 3* (  8) "do balancing"
    # - 4* ( 16) "do composition"
    # - 5  ( 32) enable if calibrating Calo jets
    # - 6  ( 64) enable if calibrating PF jets ("regular" PF, PFchs, or PUPPI)
    # - 7* (128) "save candidates"
    # Options marked with an asterisk are not supported yet.
    outputTree_flags = cms.uint32(outputTree_flags),

    # Jet type:
    # - 0                  -- PF jet
    # - 1                  -- Calo jet
    # - (any other number) -- jets with only 4-momentum, JEC raw factor and area
    # (The flag esentially determines what information is available about the jet collection.)
    jetType = cms.uint32(jetType),

    # Flag to enable (True) or disable (False) debug output
    isDEBUG = cms.bool(False)
)

process.fwliteInput.fileNames = cms.vstring(
  "file:JME-RunIIFall17NanoAOD.root"
)
