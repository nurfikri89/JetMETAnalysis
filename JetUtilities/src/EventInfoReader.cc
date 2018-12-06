#include "JetMETAnalysis/JetUtilities/interface/EventInfoReader.h"

#include "JetMETAnalysis/JetUtilities/interface/BranchAddressInitializer.h" // BranchAddressInitializer

#include <TTree.h> // TTree

EventInfoReader::EventInfoReader(const std::string& branchName_numPU,
                                 const std::string& branchName_numPU_true,
                                 const std::string& branchName_numVertices,
                                 const std::string& branchName_vertexZ,
                                 const std::string& branchName_rho,
                                 const std::string& branchName_weight,
                                 const std::string& branchName_pThat,
                                 const std::string& branchName_pudensity,
                                 const std::string& branchName_gpudensity)
  : branchName_run_("run")
  , branchName_lumi_("luminosityBlock")
  , branchName_event_("event")
  , branchName_numPU_(branchName_numPU)
  , branchName_numPU_true_(branchName_numPU_true)
  , branchName_numVertices_(branchName_numVertices)
  , branchName_vertexZ_(branchName_vertexZ)
  , branchName_rho_(branchName_rho)
  , branchName_weight_(branchName_weight)
  , branchName_pThat_(branchName_pThat)
  , branchName_pudensity_(branchName_pudensity)
  , branchName_gpudensity_(branchName_gpudensity)
{}

void
EventInfoReader::setBranchAddresses(TTree * tree)
{
  BranchAddressInitializer bai(tree);
  bai.setBranchAddress(evtInfo_.run_, branchName_run_);
  bai.setBranchAddress(evtInfo_.lumi_, branchName_lumi_);
  bai.setBranchAddress(evtInfo_.event_, branchName_event_);
  bai.setBranchAddress(evtInfo_.numPU_, branchName_numPU_);
  bai.setBranchAddress(evtInfo_.numPU_true_, branchName_numPU_true_);
  bai.setBranchAddress(evtInfo_.numVertices_, branchName_numVertices_);
  bai.setBranchAddress(evtInfo_.vertexZ_, branchName_vertexZ_);
  bai.setBranchAddress(evtInfo_.rho_, branchName_rho_);
  bai.setBranchAddress(evtInfo_.weight_, branchName_weight_);
  bai.setBranchAddress(evtInfo_.pThat_, branchName_pThat_);
  bai.setBranchAddress(evtInfo_.pudensity_, branchName_pudensity_);
  bai.setBranchAddress(evtInfo_.gpudensity_, branchName_gpudensity_);
}

EventInfo
EventInfoReader::read() const
{
  return evtInfo_;
}
