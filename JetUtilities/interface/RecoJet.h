#ifndef JetMETAnalysis_JetUtilities_RecoJet_h
#define JetMETAnalysis_JetUtilities_RecoJet_h

/** \class RecoJet
 *
 * Dataformat class for accessing information on reconstructed jets.
 *
 * \authors Christian Veelken, Tallinn;
 *          Karl Ehataht, Tallinn
 *
 */

#include "JetMETAnalysis/JetUtilities/interface/Jet.h" // Jet

// forward declarations
class GenJet;

class RecoJet
  : public Jet
{
 public:
  RecoJet() = default;
  RecoJet(const Jet & jet,
          Float_t area,
          Float_t rawFactor,
          Float_t chHEF,
          Float_t neHEF,
          Float_t chEmEF,
          Float_t neEmEF,
          Float_t muEF,
          Int_t jetId);

  ~RecoJet() {}

  /**
   * @brief Set links to generator-level jets (matched by dR)
   */
  void set_genJet(const GenJet * genJet);

  /**
   * @brief Funtions to access data-members
   * @return Values of data-members
   */
  Float_t area() const;
  Float_t rawFactor() const;
  Float_t chHEF() const;
  Float_t neHEF() const;
  Float_t chEmEF() const;
  Float_t neEmEF() const;
  Float_t muEF() const;
  Int_t jetId() const;

  const GenJet * genJet() const;

  friend class RecoJetReader;

 protected:
  Float_t area_;      ///< jet catchment area, for JECs
  Float_t rawFactor_; ///< 1 - Factor to get back to raw pT
  Float_t chHEF_;     ///< charged Hadron Energy Fraction
  Float_t neHEF_;     ///< neutral Hadron Energy Fraction
  Float_t chEmEF_;    ///< charged Electromagnetic Energy Fraction
  Float_t neEmEF_;    ///< neutral Electromagnetic Energy Fraction
  Float_t muEF_;      ///< muon Energy Fraction
  Int_t jetId_;       ///< jet ID, as explained in https://twiki.cern.ch/twiki/bin/view/CMS/JetID13TeVRun2017

  const GenJet* genJet_; ///< matching to generator-level jet  
};

std::ostream &
operator<<(std::ostream & stream,
           const RecoJet & jet);

#endif // JetMETAnalysis_JetUtilities_RecoJet_h

