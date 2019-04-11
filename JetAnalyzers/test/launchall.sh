#!/bin/bash

CFG_BASE=$CMSSW_BASE/src/JetMETAnalysis/JetAnalyzers/test
#CFG_MINIAOD=$CFG_BASE/cfg_mini.py
CFG_NANOAOD=$CFG_BASE/cfg_nano.py
#DATASET_MINIAOD=$CFG_BASE/datasets_aod.txt
DATASET_NANOAOD=$CFG_BASE/datasets_miniaod.txt
CRAB_CFG=$CFG_BASE/crab_cfg.py

export DATASET_PATTERN="^/(.*)/(.*)/[0-9A-Za-z]+$"

JOB_VERSION_SUFFIX="JME2019Apr05"
GT=102X_upgrade2018_realistic_v15
DRYRUN="" # use "--dryrun" while testing

## generate cfg file for producing MINIAODSIM files from AODSIM
#cmsDriver.py step1 --fileout file:JME-RunIIAutumn18MiniAOD.root --mc --eventcontent MINIAODSIM --runUnscheduled \
#  --datatier MINIAODSIM --conditions $GT --step PAT --nThreads 1 --geometry DB:Extended --era Run2_2018 \
#  --python_filename $CFG_MINIAOD --no_exec

# generate cfg file for producing NANOAODSIM files from MINIAODSIM
cmsDriver.py step1 --fileout tree.root --mc --eventcontent NANOAODSIM --datatier NANOAODSIM --conditions $GT \
  --step NANO --nThreads 1 --era Run2_2018,run2_nanoAOD_102Xv1 --python_filename $CFG_NANOAOD --no_exec \
  --customise_commands="from JetMETAnalysis.JetAnalyzers.prepNanoAOD import prepNanoAOD; prepNanoAOD(process)\n"

## submit MINIAODSIM jobs
#export INPUT_CFG=$CFG_MINIAOD
#export JOB_VERSION="Mini$JOB_VERSION_SUFFIX"
#export UNITS_PER_JOB=8000
#cat $DATASET_MINIAOD | while read LINE; do
#  export DATASET=$LINE
#
#  if [ -z "$DATASET" ]; then
#    continue; # it's an empty line, skip silently
#  fi
#  DATASET_SPLIT=$(echo "$DATASET" | tr '/' ' ')
#  DATASET_THIRD_PART=$(echo "$DATASET_SPLIT" | awk '{print $3}')
#  if [ "$DATASET_THIRD_PART" != "AODSIM" ]; then
#    echo "Not an AODSIM file: $DATASET";
#    exit 1;
#  fi
#
#  echo "Submitting MINIAODSIM production for: $DATASET";
#  crab submit $DRYRUN --config="$CRAB_CFG" --wait
#done

# submit NANOAODSIM jobs
export INPUT_CFG=$CFG_NANOAOD
export JOB_VERSION="Nano$JOB_VERSION_SUFFIX"
export UNITS_PER_JOB=20000
cat $DATASET_NANOAOD | while read LINE; do
  export DATASET=$LINE

  if [ -z "$DATASET" ]; then
    continue; # it's an empty line, skip silently
  fi
  DATASET_SPLIT=$(echo "$DATASET" | tr '/' ' ')
  DATASET_THIRD_PART=$(echo "$DATASET_SPLIT" | awk '{print $3}')
  if [ "$DATASET_THIRD_PART" != "MINIAODSIM" ]; then
    echo "Not an AODSIM file: $DATASET";
    exit 1;
  fi

  echo "Submitting NANOAODSIM production for: $DATASET";
  crab submit $DRYRUN --config="$CRAB_CFG" --wait
done
