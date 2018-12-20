#!/bin/bash

# Make sure that your VOMS proxy is open!

GT=94X_mc2017_realistic_v14
FILE=/store/mc/RunIIFall17DRPremix/QCD_Pt-15to7000_TuneCP5_Flat_13TeV_pythia8/AODSIM/94X_mc2017_realistic_v10-v1/50000/00304636-1BDB-E711-B6F3-FA163ECE02A9.root # 7k
AOD="root://cms-xrd-global.cern.ch//$FILE"
MINIAOD=JME-RunIIFall17MiniAOD.root
NANOAOD=JME-RunIIFall17NanoAOD.root
MINIAOD_CFG=JME-RunIIFall17MiniAOD_cfg.py
NANOAOD_CFG=JME-RunIIFall17NanoAOD_cfg.py
JET_NTUPLE_FILLER_FILE=jet_ntuple_filler.root

MAX_NOF_EVENTS=$(dasgoclient -query="file=$FILE | grep file.nevents")
NOF_EVENTS=$MAX_NOF_EVENTS

echo "Producing a MINIAODSIM from $NOF_EVENTS events (out of $MAX_NOF_EVENTS events) in file $FILE"

# source: https://cms-pdmv.cern.ch/mcm/chained_requests?dataset_name=QCD_Pt-15to7000_TuneCP5_Flat_13TeV_pythia8

# baseline taken from https://cms-pdmv.cern.ch/mcm/public/restapi/requests/get_setup/JME-RunIIFall17MiniAODv2-00001
cmsDriver.py step1 --fileout file:$MINIAOD --mc --eventcontent MINIAODSIM --runUnscheduled --datatier MINIAODSIM \
  --conditions $GT --step PAT --nThreads 4 --scenario pp --era Run2_2017,run2_miniAOD_94XFall17 \
  --python_filename $MINIAOD_CFG --no_exec --filein=$AOD -n $NOF_EVENTS

echo "Started at `date`"
cmsRun $MINIAOD_CFG &> miniaod.log
echo "Finished at `date`"

echo "Producing a NANOAODSIM file $NANOAOD from $MINIAOD"

# baseline taken from https://cms-pdmv.cern.ch/mcm/public/restapi/requests/get_setup/JME-RunIIFall17NanoAOD-00009
cmsDriver.py step1 --fileout file:$NANOAOD --mc --eventcontent NANOAODSIM --datatier NANOAODSIM --conditions $GT \
  --step NANO --nThreads 2 --era Run2_2017,run2_nanoAOD_94XMiniAODv2 --python_filename $NANOAOD_CFG \
  --no_exec --filein="file:$MINIAOD" -n $NOF_EVENTS

echo "Started at `date`"
cmsRun $NANOAOD_CFG &> nanoaod.log
echo "Finished at `date`"

echo "Running JRA at `date`"
cmsRun $CMSSW_BASE/src/JetMETAnalysis/JetAnalyzers/test/run_JRA_cfg.py &> jra.log
echo "Finished at `date`"

echo "Running Ntuple filler for AK4PFCHS jets at `date`"
export JET_NTUPLE_FILLER=1
jet_ntuple_filler $CMSSW_BASE/src/JetMETAnalysis/JetAnalyzers/test/jet_ntuple_filler_cfg.py &> filler_ak4.log
echo "Finished at `date`"

echo "Running Ntuple filler for AK8PUPPI at `date`"
export JET_NTUPLE_FILLER=0
jet_ntuple_filler $CMSSW_BASE/src/JetMETAnalysis/JetAnalyzers/test/jet_ntuple_filler_cfg.py &> filler_ak8.log
echo "Finished at `date`"

unset JET_NTUPLE_FILLER

echo "Hadding the results .."
hadd -f $JET_NTUPLE_FILLER_FILE jet_ntuple_filler_ak4.root jet_ntuple_filler_ak8.root &> hadd.log
echo "Finished hadding"
