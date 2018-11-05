#ifndef JetMETAnalysis_JetAnalyzers_GenJet_h
#define JetMETAnalysis_JetAnalyzers_GenJet_h

/** \class GenJet
 *
 * Dataformat class for accessing information on generator-level jets.
 *
 * \authors Christian Veelken, Tallinn;
 *          Karl Ehataht, Tallinn
 *
 */

#include "JetMETAnalysis/JetAnalyzers/interface/Jet.h" // Jet

class GenJet
  : public Jet
{
public:
  GenJet() = default;
  GenJet(const Jet & jet,
	 Int_t partonFlavour,
	 UInt_t hadronFlavour);

  ~GenJet() {}

  /**
   * @brief Funtions to access data-members
   * @return Values of data-members
   */
  Int_t partonFlavour() const;
  UInt_t hadronFlavour() const;

  friend class GenJetReader;

protected:
  Int_t partonFlavour_;  ///< flavour from parton matching
  UInt_t hadronFlavour_; ///< flavour from hadron ghost clustering
};

std::ostream &
operator<<(std::ostream & stream,
           const GenJet & jet);

#endif // JetMETAnalysis_JetAnalyzers_GenJet_h
