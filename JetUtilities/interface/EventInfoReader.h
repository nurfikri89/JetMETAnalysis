#ifndef JetMETAnalysis_JetUtilities_EventInfoReader_h
#define JetMETAnalysis_JetUtilities_EventInfoReader_h

#include "JetMETAnalysis/JetUtilities/interface/ReaderBase.h" // ReaderBase
#include "JetMETAnalysis/JetUtilities/interface/EventInfo.h" // EventInfo

// forward declarations
class TTree;

class EventInfoReader
  : public ReaderBase
{
public:
  EventInfoReader(const std::string& branchName_numPU,
                  const std::string& branchName_numPU_true,
                  const std::string& branchName_numVertices,
                  const std::string& branchName_vertexZ,
                  const std::string& branchName_rho,
                  const std::string& branchName_weight,
                  const std::string& branchName_pThat,
                  const std::string& branchName_pudensity,
                  const std::string& branchName_gpudensity);

  ~EventInfoReader() {}

  void
  setBranchAddresses(TTree * tree) override;

  EventInfo
  read() const;

protected:
  std::string branchName_run_;
  std::string branchName_lumi_;
  std::string branchName_event_;
  std::string branchName_numPU_;
  std::string branchName_numPU_true_;
  std::string branchName_numVertices_;
  std::string branchName_vertexZ_;
  std::string branchName_rho_;
  std::string branchName_weight_;
  std::string branchName_pThat_;
  std::string branchName_pudensity_;
  std::string branchName_gpudensity_;

  EventInfo evtInfo_;
};

#endif // JetMETAnalysis_JetUtilities_EventInfoReader_h
