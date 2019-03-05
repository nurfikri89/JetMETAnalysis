#!/bin/bash

ERA="Fall17_17Nov2017_V8_MC"
JECPATH=$CMSSW_BASE/src/JetMETAnalysis/JetAnalyzers/data/JEC_Fall17_17Nov2017_V8_MC

JETS=$(python -c "from JetMETAnalysis.JetAnalyzers.prepNanoAOD import config_ext as c; print('\n'.join(map(str, c)))")
JET_NAMES=$(python -c "from JetMETAnalysis.JetAnalyzers.prepNanoAOD import config_ext as c; print('\n'.join(map(lambda x: '%s%s' % (x['jet'], x['postfix'] if 'postfix' in x else ''), c)))")

for input_name in JRA jet_ntuple_filler; do

  input_file="${input_name}.root";
  jet_response_out="${input_name}_response.root"
  l1_output="${input_name}_L1.root"
  l1_algs=""
  l2l3_output="${input_name}_L2L3.root"
  final_output="${input_name}_final.root"

  echo "Running jet_apply_jec_x (L1) on ${input_name}"
  jet_apply_jec_x -input $input_file -era $ERA -levels 1 -output $l1_output -jecpath $JECPATH -L1FastJet true -algs $JET_NAMES &> out_apply_jec_l1_${input_name}.log
  echo "Exit code: $?"
  jet_responses=""

  for jet_name in ${JET_NAMES}; do
    jet_name_l1="${jet_name}l1"
    jet_response="${input_name}_response_${jet_name}.root"

    cfg_fn="cfg_${jet_name}.txt"
    rm -f $cfg_fn
    echo "Creating file ${cfg_fn} ..."
    for key in "binseta" "binspt"; do
      BINNING=$(python -c "from JetMETAnalysis.JetAnalyzers.prepNanoAOD import binning as b; print(' '.join(map(str, b['$jet_name']['$key'])))");
      echo "$key = $BINNING" >> ${cfg_fn};
    done

    echo "Running jet_response_analyzer_x on ${input_name} and ${jet_name}"
    jet_response_analyzer_x $cfg_fn -input ${l1_output} -output ${jet_response} -algs ${jet_name_l1} -drmax 0.25 &> out_jet_response_analyzer_${input_name}_${jet_name}.log
    echo "Exit code: $?"

    jet_responses="${jet_responses} ${jet_response}"
    l1_algs="${l1_algs} ${jet_name}l1"
  done

  echo "Running hadd on ${input_name}"
  hadd -f ${jet_response_out} ${jet_responses} &> out_hadd_${input_name}.log
  echo "Exit code: $?"

  echo "Running jet_l2_correction_x on ${input_name}"
  jet_l2_correction_x -era ${input_name} -input ${jet_response_out} -output ${l2l3_output} -batch true -algs ${l1_algs} -l2l3 true &> out_jet_l2_corrections_${input_name}.log
  echo "Exit code: $?"

  for f in ${input_name}_L2Relative_*l1.txt; do
    if [ -f $f ]; then
      mv $f $(echo "$f" | sed 's/l1.txt$/.txt/g')
    fi
  done

  echo "Running jet_apply_jec_x (L2L3) on ${input_name}"
  jet_apply_jec_x -input ${input_file} -era ${input_name} -levels 2 -output ${final_output} -jecpath $PWD -L1FastJet true -algs $JET_NAMES &> out_jet_apply_jec_l2l3_${input_name}.log
  echo "Exit code: $?"

done
