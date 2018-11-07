#ifndef JetMETAnalysis_JetUtilities_JetCollectionGenMatcher_h
#define JetMETAnalysis_JetUtilities_JetCollectionGenMatcher_h

/** \class BranchAddressInitializer
 *
 * Auxiliary class to read from branches of nanoAOD Ntuple.
 *
 * \authors Christian Veelken, Tallinn;
 *          Karl Ehataht, Tallinn
 *
 */

#include <DataFormats/Math/interface/deltaR.h> // deltaR()

#include "JetMETAnalysis/JetUtilities/interface/RecoJet.h"
#include "JetMETAnalysis/JetUtilities/interface/GenJet.h"

class JetCollectionGenMatcher
{
public:
  JetCollectionGenMatcher() {}
  ~JetCollectionGenMatcher() {}

  /**
   * @brief Match reconstructed to generator-level jets by dR
   */
  void
  addGenJetMatch(const std::vector<RecoJet> & recJets,
                 const std::vector<GenJet> & genJets,
                 double dRmax,
                 double minPtRel = -1.) const
  {
    for(const RecoJet & recJet: recJets)
    {
      const GenJet * bestMatch = nullptr;
      double dR_bestMatch = 1.e+3;

      for(const GenJet & genJet: genJets)
      {
        const double dR = deltaR(
          recJet.eta(), recJet.phi(), genJet.eta(), genJet.phi()
        );
        const bool passesPtConstraint = (genJet.pt()/recJet.pt()) > minPtRel;
        if(dR < dRmax && dR < dR_bestMatch && passesPtConstraint)
        {
          bestMatch = const_cast<const GenJet *>(&genJet);
          dR_bestMatch = dR;
        }
      }

      if(bestMatch)
      {
        RecoJet * recJet_nonconst = const_cast<RecoJet *>(&recJet);
        recJet_nonconst->set_genJet(bestMatch);
      }
    }
  }
};

#endif // JetMETAnalysis_JetUtilities_JetCollectionGenMatcher_h
