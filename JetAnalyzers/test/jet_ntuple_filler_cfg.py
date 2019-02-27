import FWCore.ParameterSet.Config as cms
import os

JET_CHOICES = [ 'ak4pf', 'ak4pfchs', 'ak4pfpuppi', 'ak8pf', 'ak8pfchs', 'ak8pfpuppi' ]
ENV_NAME = 'JET_NTUPLE_FILLER'

jetChoice = ''
if ENV_NAME in os.environ:
    jetChoice = os.environ['JET_NTUPLE_FILLER']
    if jetChoice not in JET_CHOICES:
        raise RuntimeError('Invalid value for %s: %s' % (ENV_NAME, jetChoice))
else:
    raise RuntimeError('Environment variable %s not set' % ENV_NAME)

if jetChoice == 'ak4pf':
    recJets = 'JetPF'
elif jetChoice == 'ak4pfchs':
    recJets = 'Jet'
elif jetChoice == 'ak4pfpuppi':
    recJets = 'JetPUPPI'
elif jetChoice == 'ak8pf':
    recJets = 'FatJetPF'
elif jetChoice == 'ak8pfchs':
    recJets = 'FatJetCHS'
elif jetChoice == 'ak8pfpuppi':
    recJets = 'FatJet'
else:
    raise RuntimeError('Unsupported jet collection: %s' % jetChoice)

if jetChoice.startswith('ak4'):
    genJets = 'GenJet'
elif jetChoice.startswith('ak8'):
    genJets = 'GenJetAK8'
else:
    raise RuntimeError('Unsupported jet collection: %s' % jetChoice)

process = cms.PSet()

process.fwliteInput = cms.PSet(
    fileNames = cms.vstring(),
    maxEvents = cms.int32(-1),
    outputEvery = cms.uint32(1)
)

process.fwliteOutput = cms.PSet(
    fileName=cms.string('jet_ntuple_filler_%s.root' % jetChoice)
)

process.jet_ntuple_filler = cms.PSet(
    inputTreeName = cms.string('Events'),

    src_recJets = cms.string(recJets),
    src_genJets = cms.string(genJets),
    src_numPU = cms.string('Pileup_nPU'),
    src_numPU_true = cms.string('Pileup_nTrueInt'),
    src_numVertices = cms.string('PV_npvsGood'),
    src_vertexZ = cms.string('PV_z'),
    src_rho = cms.string('fixedGridRhoFastjetAll'),
    src_weight = cms.string('Generator_weight'),
    src_pThat = cms.string('Generator_binvar'),
    src_pudensity = cms.string('Pileup_pudensity'),
    src_gpudensity = cms.string('Pileup_gpudensity'),
    
    dR_match = cms.double(0.25),

    # Flag to apply jet energy corrections (after correcting back the jet energies stored on nanoAOD to their "raw" values).
    # The following settings are supported for this flag:
    #  - 'l1'     (L1Fastjet)
    #  - 'l2l3'   (L2Relative+L3Absolute)
    #  - 'l1l2l3' (L1Fastjet+L2Relative+L3Absolute)
    #  - ''       (no jet energy corrections applied)
    jetCorrectionLevels = cms.string(''),
    jecFilePath = cms.string('JetMETAnalysis/JetAnalyzers/data/JEC_Fall17_17Nov2017_V8_MC/'),
    jecFileName_l1 = cms.string('Fall17_17Nov2017_V8_MC_L1FastJet_AK4PFchs.txt'),
    jecFileName_l2 = cms.string('Fall17_17Nov2017_V8_MC_L2Relative_AK4PFchs.txt'),
    jecFileName_l3 = cms.string('Fall17_17Nov2017_V8_MC_L3Absolute_AK4PFchs.txt'),
    
    outputTreeName = cms.string('%s/t' % jetChoice),
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
    # The default value is 1+4+64=69.
    # Options marked with an asterisk are not supported yet.
    outputTree_flags = cms.uint32(85),

    # Flag to enable (True) or disable (False) debug output
    isDEBUG = cms.bool(False)
)

process.fwliteInput.fileNames = cms.vstring(
  "file:JME-RunIIFall17NanoAOD.root"
)
#process.fwliteInput.outputEvery = cms.uint32(1)
#process.fwliteInput.maxEvents = cms.int32(100)
#process.jet_ntuple_filler.isDEBUG = cms.bool(True)
