#!/bin/bash

echo -e "binseta = -2 -1 0 1 2\nbinspt = 20 30 50 70 100 150 200     300 400 500 600 800 1000" > cfg_ak4pfchs.txt
echo -e "binseta = -2 -1 0 1 2\nbinspt =                     200 250 300 400 500 600 800 1000" > cfg_ak8pfpuppi.txt

JECPATH=$CMSSW_BASE/src/JetMETAnalysis/JetAnalyzers/data/JEC_Fall17_17Nov2017_V8_MC

jet_apply_jec_x -input JRA.root               -era Fall17_17Nov2017_V8_MC -levels 1 -output JRA_L1.root               -jecpath $JECPATH -L1FastJet true -algs ak4pfchs ak8pfpuppi
jet_apply_jec_x -input jet_ntuple_filler.root -era Fall17_17Nov2017_V8_MC -levels 1 -output jet_ntuple_filler_L1.root -jecpath $JECPATH -L1FastJet true -algs ak4pfchs ak8pfpuppi

jet_response_analyzer_x cfg_ak4pfchs.txt   -input JRA_L1.root               -output JRA_response_ak4pfchs.root                 -algs ak4pfchsl1   -drmax 0.25
jet_response_analyzer_x cfg_ak8pfpuppi.txt -input JRA_L1.root               -output JRA_response_ak8pfpuppi.root               -algs ak8pfpuppil1 -drmax 0.25
jet_response_analyzer_x cfg_ak4pfchs.txt   -input jet_ntuple_filler_L1.root -output jet_ntuple_filler_response_ak4pfchs.root   -algs ak4pfchsl1   -drmax 0.25
jet_response_analyzer_x cfg_ak8pfpuppi.txt -input jet_ntuple_filler_L1.root -output jet_ntuple_filler_response_ak8pfpuppi.root -algs ak8pfpuppil1 -drmax 0.25

hadd -f JRA_response.root               JRA_response_ak4pfchs.root               JRA_response_ak8pfpuppi.root
hadd -f jet_ntuple_filler_response.root jet_ntuple_filler_response_ak4pfchs.root jet_ntuple_filler_response_ak8pfpuppi.root

jet_l2_correction_x -era JRA               -input JRA_response.root               -output JRA_l2.root               -batch true -algs ak4pfchsl1 ak8pfpuppil1 -l2l3 true
jet_l2_correction_x -era jet_ntuple_filler -input jet_ntuple_filler_response.root -output jet_ntuple_filler_l2.root -batch true -algs ak4pfchsl1 ak8pfpuppil1 -l2l3 true

mv JRA_L2Relative_AK4PFchsl1.txt                 JRA_L2Relative_AK4PFchs.txt
mv JRA_L2Relative_AK8PFPuppil1.txt               JRA_L2Relative_AK8PFPuppi.txt
mv jet_ntuple_filler_L2Relative_AK4PFchsl1.txt   jet_ntuple_filler_L2Relative_AK4PFchs.txt
mv jet_ntuple_filler_L2Relative_AK8PFPuppil1.txt jet_ntuple_filler_L2Relative_AK8PFPuppi.txt

jet_apply_jec_x -input JRA.root               -era JRA               -levels 2 -output JRA_jec_reapply.root               -jecpath $PWD -L1FastJet true -algs ak4pfchs ak8pfpuppi
jet_apply_jec_x -input jet_ntuple_filler.root -era jet_ntuple_filler -levels 2 -output jet_ntuple_filler_jec_reapply.root -jecpath $PWD -L1FastJet true -algs ak4pfchs ak8pfpuppi
