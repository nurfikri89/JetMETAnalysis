#ifndef JetMETAnalysis_JetUtilities_RecoJetReader_h
#define JetMETAnalysis_JetUtilities_RecoJetReader_h

/** \class RecoJetReader
 *
 * Read collection of jets from nanoAOD Ntuple.
 *
 * \authors Christian Veelken, Tallinn;
 *          Karl Ehataht, Tallinn
 *
 */

#include "JetMETAnalysis/JetUtilities/interface/ReaderBase.h" // ReaderBase
#include "JetMETAnalysis/JetUtilities/interface/RecoJet.h" // RecoJet

#include <map> // std::map<,>

// forward declarations
class TTree;

class RecoJetReader
  : public ReaderBase
{
 public:
  RecoJetReader(const std::string & branchName_obj);
  ~RecoJetReader();

  /**
   * @brief Call tree->SetBranchAddress for all RecoJet branches
   */
  void
  setBranchAddresses(TTree * tree) override;

  /**
   * @brief Read branches from tree and use information to fill collection of RecoJet objects
   * @return Collection of RecoJet objects
   */
  std::vector<RecoJet>
  read() const;

protected:
 /**
   * @brief Initialize names of branches to be read from tree
   */
  void
  setBranchNames();

  const unsigned int max_nJets_;
  std::string branchName_num_;
  std::string branchName_obj_;

  std::string branchName_pt_;
  std::string branchName_eta_;
  std::string branchName_phi_;
  std::string branchName_mass_;
  std::string branchName_area_;
  std::string branchName_rawFactor_;
  std::string branchName_chHEF_;
  std::string branchName_neHEF_;
  std::string branchName_chEmEF_;
  std::string branchName_neEmEF_;
  std::string branchName_muEF_;
  std::string branchName_hfEF_;
  std::string branchName_hfmEF_;
  std::string branchName_jetId_;

  UInt_t nJets_;
  Float_t * jet_pt_;
  Float_t * jet_eta_;
  Float_t * jet_phi_;
  Float_t * jet_mass_;
  Float_t * jet_area_;
  Float_t * jet_rawFactor_;
  Float_t * jet_chHEF_;
  Float_t * jet_neHEF_;
  Float_t * jet_chEmEF_;
  Float_t * jet_neEmEF_;
  Float_t * jet_muEF_;
  Float_t * jet_hfEF_;
  Float_t * jet_hfmEF_;
  Int_t * jet_jetId_;

  // CV: make sure that only one RecoJetReader instance exists for a given branchName,
  //     as ROOT cannot handle multiple TTree::SetBranchAddress calls for the same branch.
  static std::map<std::string, int> numInstances_;
  static std::map<std::string, RecoJetReader *> instances_;
};

#endif // JetMETAnalysis_JetAnalyzers_RecoJetReader_h
