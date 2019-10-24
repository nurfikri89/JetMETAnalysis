#!/bin/bash

#
# Specify input file(s)
#
INDIR="/afs/cern.ch/user/n/nbinnorj/work/public/CustomNanoAOD-JME/"
INFILES=${INDIR}"tree.root"
#
# Specify output file
#
OUTDIR="./"
OUTFILE=${OUTDIR}"JRA.root"
#
# Config file
#
CFGFILE=${CMSSW_BASE}"/src/JetMETAnalysis/JetAnalyzers/test/jet_ntuple_filler_cfg_v1.py"

echo "INFILES : "${INFILES}
echo "OUTFILE : "${OUTFILE}
echo "CFGFILE : "${CFGFILE}

export JEC_VER=Autumn18_V8_MC

JETS=(
"ak4pfchs"
"ak4pf"
"ak4pfpuppi"
"ak8pfpuppi"
"ak8pf"
"ak8pfchs"
)

for JET in "${JETS[@]}"; do
  export JETNAME="${JET}"
  echo "Running Ntuple filler for $JETNAME jets at `date`";

  jet_ntuple_filler \
  inputFiles=${INFILES} \
  outputFile=${OUTFILE} \
  tag=${JETNAME} \
  cfg=${CFGFILE} 
  #\
  # 2>&1 | tee ./filler_${JETNAME}.log;
  echo "Finished at `date`"
  echo ""
  echo ""
  echo "" 
  echo""
done