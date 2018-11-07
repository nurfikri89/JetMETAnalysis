import FWCore.ParameterSet.Config as cms
import os

process = cms.PSet()

process.fwliteInput = cms.PSet(
    fileNames = cms.vstring(),
    maxEvents = cms.int32(-1),
    outputEvery = cms.uint32(100000)
)

process.fwliteOutput = cms.PSet(
    fileName = cms.string('')
)

process.jet_ntuple_filler = cms.PSet(
    inputTreeName = cms.string('Events'),

    src_recJets = cms.string('Jet'),
    src_genJets = cms.string('GenJet'),
    src_numPU = cms.string('nPU'),
    src_numPU_true = cms.string('nTrueInt'),
    src_numVertices = cms.string('PV_npvs'),
    src_vertexZ = cms.string('PV_z'),
    src_rho = cms.string('fixedGridRhoFastjetAll'),
    src_weight = cms.string('weight'),
    src_pThat = cms.string('binvar'),
    
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
    
    outputTreeName = cms.string('t'),
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
    outputTree_flags = cms.uint32(69),

    # Flag to enable (True) or disable (False) debug output
    isDEBUG = cms.bool(True)
)
