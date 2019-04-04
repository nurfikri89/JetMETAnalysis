from CRABClient.UserUtilities import config, getUsernameFromSiteDB

import re
import os

def get_env_var(env_var, fail_if_not_exists = True):
  if env_var not in os.environ:
    if fail_if_not_exists:
      raise ValueError("$%s not defined" % env_var)
    else:
      return ''
  return os.environ[env_var]

home_site       = 'T2_EE_Estonia'
input_cfg       = get_env_var('INPUT_CFG')
job_version     = get_env_var('JOB_VERSION')
dataset_name    = get_env_var('DATASET')
dataset_pattern = get_env_var('DATASET_PATTERN')

dataset_match   = re.match(dataset_pattern, dataset_name)
if not dataset_match:
  raise ValueError("Dataset '%s' did not match to pattern '%s'" % (dataset_name, dataset_pattern))

id_ = '%s_%s__%s' % (job_version, dataset_match.group(1), dataset_match.group(2))
requestName      = id_
outputDatasetTag = id_

max_outputDatasetTag_len = 160 - len(getUsernameFromSiteDB())
if len(outputDatasetTag) > max_outputDatasetTag_len:
  outputDatasetTag = outputDatasetTag[:max_outputDatasetTag_len]

if len(requestName) > 100:
  requestName_new = requestName[:90] + requestName[-10:]
  print("Changing old request name '{rqname_old}' -> '{rqname_new}'".format(
    rqname_old = requestName,
    rqname_new = requestName_new,
  ))
  requestName = requestName_new

config = config()

config.General.requestName     = requestName
config.General.workArea        = os.path.join(os.path.expanduser('~'), 'crab_projects')
config.General.transferOutputs = True
config.General.transferLogs    = True

config.JobType.pluginName = 'Analysis'
config.JobType.psetName   = input_cfg

config.Site.storageSite = home_site

config.Data.inputDataset     = dataset_name
config.Data.inputDBS         = 'global'
config.Data.splitting        = 'EventAwareLumiBased'
config.Data.unitsPerJob      = 50000
config.Data.outLFNDirBase    = '/store/user/%s/%s' % (getUsernameFromSiteDB(), job_version)
config.Data.publication      = False
config.Data.outputDatasetTag = outputDatasetTag

config.Data.allowNonValidInputDataset = True
