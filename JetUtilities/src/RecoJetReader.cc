#include "JetMETAnalysis/JetUtilities/interface/RecoJetReader.h" // RecoJetReader

#include "FWCore/Utilities/interface/Exception.h" // cms::Exception

#include "JetMETAnalysis/JetUtilities/interface/BranchAddressInitializer.h" // BranchAddressInitializer

#include <TTree.h> // TTree
#include <TString.h> // Form()

std::map<std::string, int> RecoJetReader::numInstances_;
std::map<std::string, RecoJetReader *> RecoJetReader::instances_;

RecoJetReader::RecoJetReader(const std::string & branchName_obj,
                             bool run_ak4pfchs)
  : max_nJets_(256)
  , branchName_num_(Form("n%s", branchName_obj.data()))
  , branchName_obj_(branchName_obj)
  , run_ak4pfchs_(run_ak4pfchs)
  , jet_pt_(nullptr)
  , jet_eta_(nullptr)
  , jet_phi_(nullptr)
  , jet_mass_(nullptr)
  , jet_area_(nullptr)
  , jet_rawFactor_(nullptr)
  , jet_chHEF_(nullptr)
  , jet_neHEF_(nullptr)
  , jet_chEmEF_(nullptr)
  , jet_neEmEF_(nullptr)
  , jet_muEF_(nullptr)
  , jet_jetId_(nullptr)
{
  setBranchNames();
}

RecoJetReader::~RecoJetReader()
{
  --numInstances_[branchName_obj_];
  assert(numInstances_[branchName_obj_] >= 0);
  if(numInstances_[branchName_obj_] == 0)
  {
    RecoJetReader * const gInstance = instances_[branchName_obj_];
    assert(gInstance);
    delete[] gInstance->jet_pt_;
    delete[] gInstance->jet_eta_;
    delete[] gInstance->jet_phi_;
    delete[] gInstance->jet_mass_;
    delete[] gInstance->jet_area_;
    delete[] gInstance->jet_rawFactor_;
    delete[] gInstance->jet_chHEF_;
    delete[] gInstance->jet_neHEF_;
    delete[] gInstance->jet_chEmEF_;
    delete[] gInstance->jet_neEmEF_;
    delete[] gInstance->jet_muEF_;
    delete[] gInstance->jet_jetId_;
    instances_[branchName_obj_] = nullptr;
  }
}

void
RecoJetReader::setBranchNames()
{
  if(numInstances_[branchName_obj_] == 0)
  {
    branchName_pt_ = Form("%s_%s", branchName_obj_.data(), "pt");
    branchName_eta_ = Form("%s_%s", branchName_obj_.data(), "eta");
    branchName_phi_ = Form("%s_%s", branchName_obj_.data(), "phi");
    branchName_mass_ = Form("%s_%s", branchName_obj_.data(), "mass");
    branchName_area_ = Form("%s_%s", branchName_obj_.data(), "area");
    branchName_rawFactor_ = Form("%s_%s", branchName_obj_.data(), "rawFactor");
    branchName_chHEF_ = Form("%s_%s", branchName_obj_.data(), "chHEF");
    branchName_neHEF_ = Form("%s_%s", branchName_obj_.data(), "neHEF");
    branchName_chEmEF_ = Form("%s_%s", branchName_obj_.data(), "chEmEF");
    branchName_neEmEF_ = Form("%s_%s", branchName_obj_.data(), "neEmEF");
    branchName_muEF_ = Form("%s_%s", branchName_obj_.data(), "muEF");
    branchName_jetId_ = Form("%s_%s", branchName_obj_.data(), "jetId");
    instances_[branchName_obj_] = this;
  }
  else
  {
    if(branchName_num_ != instances_[branchName_obj_]->branchName_num_)
    {
      throw cms::Exception("RecoJetReader::setBranchNames")
        << "Association between configuration parameters 'branchName_num' and 'branchName_obj' must be unique:"
        << " present association 'branchName_num' = " << branchName_num_ << " with 'branchName_obj' = " << branchName_obj_
        << " does not match previous association 'branchName_num' = " << instances_[branchName_obj_]->branchName_num_
        << " with 'branchName_obj' = " << instances_[branchName_obj_]->branchName_obj_ << " !!\n";
    }
  }
  ++numInstances_[branchName_obj_];
}

void
RecoJetReader::setBranchAddresses(TTree * tree)
{
  if(instances_[branchName_obj_] == this)
  {
    BranchAddressInitializer bai(tree, max_nJets_);
    bai.setBranchAddress(nJets_, branchName_num_);
    bai.setBranchAddress(jet_pt_, branchName_pt_);
    bai.setBranchAddress(jet_eta_, branchName_eta_);
    bai.setBranchAddress(jet_phi_, branchName_phi_);
    bai.setBranchAddress(jet_mass_, branchName_mass_);
    bai.setBranchAddress(jet_area_, branchName_area_);
    bai.setBranchAddress(jet_rawFactor_, branchName_rawFactor_);
    bai.setBranchAddress(jet_chHEF_, run_ak4pfchs_ ? branchName_chHEF_ : "");
    bai.setBranchAddress(jet_neHEF_, run_ak4pfchs_ ? branchName_neHEF_ : "");
    bai.setBranchAddress(jet_chEmEF_, run_ak4pfchs_ ? branchName_chEmEF_ : "");
    bai.setBranchAddress(jet_neEmEF_, run_ak4pfchs_ ? branchName_neEmEF_ : "");
    bai.setBranchAddress(jet_muEF_, run_ak4pfchs_ ? branchName_muEF_ : "");
    bai.setBranchAddress(jet_jetId_, branchName_jetId_);
  }
}

std::vector<RecoJet>
RecoJetReader::read() const
{
  const RecoJetReader * const gInstance = instances_[branchName_obj_];
  assert(gInstance);

  std::vector<RecoJet> jets;
  const UInt_t nJets = gInstance->nJets_;
  if(nJets > max_nJets_)
  {
    throw cms::Exception("RecoJetReader::read")
      << "Number of jets stored in Ntuple = " << nJets << ", "
         "exceeds max_nJets = " << max_nJets_ << " !!\n";
  }

  if(nJets > 0)
  {
    jets.reserve(nJets);
    for(UInt_t idxJet = 0; idxJet < nJets; ++idxJet)
    {
      jets.push_back({
        {
          gInstance->jet_pt_[idxJet],
          gInstance->jet_eta_[idxJet],
          gInstance->jet_phi_[idxJet],
          gInstance->jet_mass_[idxJet],
        },
        gInstance->jet_area_[idxJet],
        gInstance->jet_rawFactor_[idxJet],
        run_ak4pfchs_ ? gInstance->jet_chHEF_[idxJet] : 0.f,
        run_ak4pfchs_ ? gInstance->jet_neHEF_[idxJet] : 0.f,
        run_ak4pfchs_ ? gInstance->jet_chEmEF_[idxJet] : 0.f,
        run_ak4pfchs_ ? gInstance->jet_neEmEF_[idxJet] : 0.f,
        run_ak4pfchs_ ? gInstance->jet_muEF_[idxJet] : 0.f,
        gInstance->jet_jetId_[idxJet],
      });
    } // idxJet
  } // nJets > 0
  return jets;
}
