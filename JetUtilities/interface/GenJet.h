#ifndef JetMETAnalysis_JetUtilities_GenJet_h
#define JetMETAnalysis_JetUtilities_GenJet_h

/** \class GenJet
 *
 * Dataformat class for accessing information on generator-level jets.
 *
 * \authors Christian Veelken, Tallinn;
 *          Karl Ehataht, Tallinn
 *
 */

#include "JetMETAnalysis/JetUtilities/interface/Jet.h" // Jet

class GenJet
  : public Jet
{
public:
  GenJet() = default;
  GenJet(const Jet & jet,
	 Int_t partonFlavour,
	 UChar_t hadronFlavour);

  ~GenJet() {}

  /**
   * @brief Funtions to access data-members
   * @return Values of data-members
   */
  Int_t partonFlavour() const;
  UChar_t hadronFlavour() const;

  friend class GenJetReader;

protected:
  Int_t partonFlavour_;  ///< flavour from parton matching
  UChar_t hadronFlavour_; ///< flavour from hadron ghost clustering
};

std::ostream &
operator<<(std::ostream & stream,
           const GenJet & jet);

#endif // JetMETAnalysis_JetUtilities_GenJet_h
