#!/usr/bin/env python

#NB! the file works only on Tallinn cluster

# arguments:
# - list of input files (one file per line)
# - output directory
# - directory where the scripts will be stored

# what the script does
# - loop over the list of input files
# - per one input file:
#   - generate one cfg file per jet collection
#   - create a shell script that
#     - runs jet_ntuple_filler for each jet collection
#     - hadds the results
#     - copies the results to the output directory
#   - create a script or makefile that submits said shell scripts to SLURM
# the script maintains one-to-one correspondence b/w input and output files (for now)

from JetMETAnalysis.JetAnalyzers.prepNanoAOD import config_ext, getGenPartName, JetInfo

import argparse
import logging
import sys
import os
import jinja2
import getpass
import datetime
import stat
import re

CFG_TEMPLATE="""
import FWCore.ParameterSet.Config as cms

process = cms.PSet(
  fwliteInput = cms.PSet(
    fileNames = cms.vstring('{{ input_file }}'),
    maxEvents = cms.int32(-1),
    outputEvery = cms.uint32({{ outputEvery }}),
  ),
  fwliteOutput = cms.PSet(
    fileName = cms.string('{{ output_file }}'),
  ),
  jet_ntuple_filler = cms.PSet(
    inputTreeName = cms.string('Events'),
    src_recJets     = cms.string('{{ recJets }}'),
    src_genJets     = cms.string('{{ genJets }}'),
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
    jetCorrectionLevels = cms.string(''),
    jecFilePath = cms.string('JetMETAnalysis/JetAnalyzers/data/JEC_{}/'.format('{{ jec_ver }}')),
    jecFileName_l1 = cms.string('{}_L1FastJet_{}.txt'.format('{{ jec_ver }}', '{{ jetCorrPayload }}')),
    jecFileName_l2 = cms.string('{}_L2Relative_{}.txt'.format('{{ jec_ver }}', '{{ jetCorrPayload }}')),
    jecFileName_l3 = cms.string('{}_L3Absolute_{}.txt'.format('{{ jec_ver }}', '{{ jetCorrPayload }}')),
    outputTreeName = cms.string('{}/t'.format('{{ jetName }}')),
    outputTree_flags = cms.uint32({{ outputTree_flags }}),
    jetType = cms.uint32({{ jetType }}),
    isDEBUG = cms.bool({{ isDebug }}),
  )
)
"""

SHELL_TEMPLATE="""#!/bin/bash

unset JAVA_HOME

JOB_DIR="{{ job_dir }}/$SLURM_JOBID"
mkdir -p $JOB_DIR
cd $JOB_DIR

cleanup() {
    if [ ! -z "$1" ]; then
        echo "Deleting directory: rm -r $1"
        rm -r "$1";
    fi
}

{% for output_file in cfg_map %}

echo "Producing file {{ output_file }}"
jet_ntuple_filler {{ cfg_map[output_file]['cfg_file'] }} &> {{ cfg_map[output_file]['log_file'] }}
EXIT_CODE=$?

if [[ $EXIT_CODE -ne 0 ]]; then
    cleanup "$JOB_DIR";
    return $EXIT_CODE;
fi

if [ ! -f {{ output_file }} ]; then
  echo "Missing output file: {{ output_file }}";
  EXIT_CODE=1;
fi

if [[ $EXIT_CODE -ne 0 ]]; then
    cleanup "$JOB_DIR";
    return $EXIT_CODE;
fi
{% endfor %}

echo "Hadding the results into: {{ output_final }}"
hadd {{ output_final }} {{ cfg_map.keys()|join(' ') }}
EXIT_CODE=$?

if [[ $EXIT_CODE -ne 0 ]]; then
    cleanup "$JOB_DIR";
    return $EXIT_CODE;
fi

if [ ! -f {{ output_final }} ]; then
  echo "Missing output file: {{ output_final }}";
  EXIT_CODE=1;
fi

if [[ $EXIT_CODE -ne 0 ]]; then
    cleanup "$JOB_DIR";
    return $EXIT_CODE;
fi

echo "Copying {{ output_final }} to {{ output_remote }}"
{{ cp_cmd }} {{ output_final }} {{ output_remote }}

EXIT_CODE=$?

sleep 20 # sleep 20 seconds to make sure that the file is physically copied to the new location
cleanup "$JOB_DIR"

echo "Final exit code is: $EXIT_CODE"
exit $EXIT_CODE
"""

SUBMIT_TEMPLATE = """#!/bin/bash

{% for input_file in makefile_map %}
if [ ! -f {{ makefile_map[input_file]['output'] }} ]; then
  sbatch --partition=main --output={{ makefile_map[input_file]['log'] }} --mem=1800M {{ makefile_map[input_file]['script'] }}
fi
{% endfor %}
"""

MAKEFILE_TEMPLATE = """
.DEFAULT_GOAL := all
SHELL := /bin/bash

all: {% for input_file in makefile_map %}{{ makefile_map[input_file]['output'] }} {% endfor %}

clean:{% for input_file in makefile_map %}
\t{{ rm_cmd }} -f {{ makefile_map[input_file]['output'] }}{% endfor %}

sbatch:
\t{{ script_name }}

{% for input_file in makefile_map %}
{{ makefile_map[input_file]['output'] }}: sbatch
\t:

{% endfor %}
"""

class SmartFormatter(argparse.HelpFormatter):
  def _split_lines(self, text, width):
    if text.startswith('R|'):
      return text[2:].splitlines()
    return argparse.HelpFormatter._split_lines(self, text, width)

def add_chmodx(fn):
  st = os.stat(fn)
  os.chmod(fn, st.st_mode | stat.S_IEXEC)

def create_if_not_exists(dir_name):
  if not os.path.isdir(dir_name):
    try:
      os.makedirs(dir_name)
      logging.debug('Created directory: {}'.format(dir_name))
    except OSError as err:
      logging.error("Could not create directory {} because: {}".format(dir_name, err))
      sys.exit(1)

def getFromJetChoice(jetChoice, key):
  return jetChoice[key] if key in jetChoice else ''

def generate_cfg(input_file, scripts_dir, jec_ver):
  cfg_map = {}
  for jetChoice in config_ext:
    recJets = jetChoice['name']
    genJets = getFromJetChoice(jetChoice, 'genName')
    if not genJets:
      genJets = getGenPartName(recJets)

    jetInfo = JetInfo(jetChoice['jet'], getFromJetChoice(jetChoice, 'inputCollection'))
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

    input_file_basename = os.path.basename(input_file)
    input_file_filename, input_file_ext = os.path.splitext(input_file_basename)
    output_file = '{}_{}{}'.format(input_file_filename, jetName, input_file_ext)

    cfg_templated = jinja2.Template(CFG_TEMPLATE).render(
      input_file       = input_file,
      outputEvery      = 1000,
      output_file      = output_file,
      recJets          = recJets,
      genJets          = genJets,
      jec_ver          = jec_ver,
      jetCorrPayload   = jetInfo.jetCorrPayload,
      jetName          = jetName,
      outputTree_flags = outputTree_flags,
      jetType          = jetType,
      isDebug          = False,
    )
    cfg_base = input_file_filename.replace('tree', 'jnf')
    cfg_filename = '{}_{}_cfg.py'.format(cfg_base, jetName)
    cfg_name = os.path.join(scripts_dir, cfg_base, cfg_filename)
    cfg_dir = os.path.dirname(cfg_name)
    create_if_not_exists(cfg_dir)
    with open(cfg_name, 'w') as cfg_file:
      cfg_file.write(cfg_templated + '\n')
    logging.debug('Wrote: {}'.format(cfg_name))

    assert(output_file not in cfg_map)
    cfg_map[output_file] = cfg_name

  return cfg_map

def generate_script(cfg_map, input_file, output_dir, scripts_dir):
  cfg_remapped = {
    output_file : { 'cfg_file' : cfg_file, 'log_file' : cfg_file.replace('_cfg.py', '.log') }
    for output_file, cfg_file in cfg_map.items()
  }
  input_file_basename = os.path.basename(input_file)
  input_file_filename, input_file_ext = os.path.splitext(input_file_basename)
  output_file = os.path.join(output_dir, input_file_basename)
  if output_file.startswith('/hdfs'):
    output_file_sub = re.sub('^/hdfs', '', output_file)
    cp_cmd = 'hdfs dfs -copyFromLocal'
  else:
    output_file_sub = output_file
    cp_cmd = 'cp'

  shell_templated = jinja2.Template(SHELL_TEMPLATE).render(
    job_dir       = os.path.join('/scratch', getpass.getuser(), 'jme_{}'.format(datetime.date.today().isoformat())),
    cfg_map       = cfg_remapped,
    output_final  = input_file_basename,
    output_remote = output_file_sub,
    cp_cmd        = cp_cmd,
  )

  cfg_base = input_file_filename.replace('tree', 'jnf')
  shell_cfg_name = os.path.join(scripts_dir, cfg_base, 'batch_{}.sh'.format(input_file_filename))
  shell_cfg_dir = os.path.dirname(shell_cfg_name)
  create_if_not_exists(shell_cfg_dir)

  with open(shell_cfg_name, 'w') as shell_cfg:
    shell_cfg.write(shell_templated + '\n')
  logging.debug('Wrote: {}'.format(shell_cfg_name))

  add_chmodx(shell_cfg_name)

  return shell_cfg_name, output_file

def generate_makefile(makefile_map, scripts_dir):
  submit_templated = jinja2.Template(SUBMIT_TEMPLATE).render(makefile_map = makefile_map)
  submit_script_path = os.path.join(scripts_dir, 'submit.sh')
  with open(submit_script_path, 'w') as submit_script:
    submit_script.write(submit_templated + '\n')
  logging.debug('Wrote: {}'.format(submit_script_path))
  add_chmodx(submit_script_path)

  rm_cmd = 'hdfs dfs -rm' if all(map(lambda v: v['output'].startswith('/hdfs'), makefile_map.values())) else 'rm'

  makefile_templated = jinja2.Template(MAKEFILE_TEMPLATE).render(
    makefile_map = makefile_map,
    script_name  = submit_script_path,
    rm_cmd       = rm_cmd
  )
  makefile_path = os.path.join(scripts_dir, 'Makefile_jme')
  with open(makefile_path, 'w') as makefile:
    makefile.write(makefile_templated + '\n')
  logging.debug('Wrote {}'.format(makefile_path))
  return makefile_path

parser = argparse.ArgumentParser(formatter_class = lambda prog: SmartFormatter(prog, max_help_position = 40))
parser.add_argument(
  '-i', '--input', dest = 'input', metavar = 'file', required = True, type = str,
  help = 'R|File containing list of input files, one file per line',
)
parser.add_argument(
  '-o', '--output', dest = 'output', metavar = 'directory', required = True, type = str,
  help = 'R|Directory where the output files will be placed',
)
parser.add_argument(
  '-s', '--scripts', dest = 'scripts', metavar = 'directory', required = True, type = str,
  help = 'R|Directory where the config files and shell scripts are hosted',
)
parser.add_argument(
  '-j', '--jec', dest = 'jec', metavar = 'version', required = False, type = str, default = 'Autumn18_V8_MC',
  help = 'R|Version of reapplied JEC',
)
parser.add_argument(
  '-v', '--verbose', dest = 'verbose', action = 'store_true', default = False,
  help = 'R|Enable verbose printout',
)
args = parser.parse_args()

input_fn = args.input
output_dir = args.output
scripts_dir = args.scripts
jec = args.jec
verbose = args.verbose

logging.basicConfig(
  stream = sys.stdout,
  level  = logging.DEBUG if verbose else logging.INFO,
  format = '%(asctime)s - %(levelname)s: %(message)s'
)

if not os.path.isfile(input_fn):
  raise ValueError("No such file: %s" % input_fn)

create_if_not_exists(output_dir)
create_if_not_exists(scripts_dir)

input_files = []
with open(input_fn, 'r') as input_f:
  for line in input_f:
    line_stripped = line.rstrip('\n')
    if line_stripped:
      input_files.append(line_stripped)

logging.debug('Found {} input files; generating cfg files'.format(len(input_files)))
makefile_map = {}
for input_file in input_files:
  # keys = output files; values = cfg files
  cfg_map = generate_cfg(input_file, scripts_dir, jec)
  script_name, output_file = generate_script(cfg_map, input_file, output_dir, scripts_dir)
  assert(input_file not in makefile_map)
  makefile_map[input_file] = {
    'output' : output_file,
    'script' : script_name,
    'log'    : script_name.replace('.sh', '_wrapper.log'),
  }

makefile_path = generate_makefile(makefile_map, scripts_dir)
logging.info('Run: make -f {}'.format(makefile_path))
