#ifndef JetMETAnalysis_JetUtilities_Jet_h
#define JetMETAnalysis_JetUtilities_Jet_h

/** \class Jet
 *
 * Dataformat base-class for accessing information on reconstructed and generator-level jets.
 *
 * \authors Christian Veelken, Tallinn;
 *          Karl Ehataht, Tallinn
 *
 */

#include <DataFormats/Math/interface/LorentzVector.h> // math::PtEtaPhiMLorentzVector

#include <Rtypes.h> // Float_t, Int_t, UInt_t

#include <iostream> // std::ostream

class Jet
{
public:
  typedef math::PtEtaPhiMLorentzVector LorentzVector;

  Jet() = default;
  Jet(Double_t pt,
      Double_t eta,
      Double_t phi,
      Double_t mass,
      Double_t area);

  virtual ~Jet() {}

  /**
   * @brief Funtions to access data-members
   * @return Values of data-members
   */
  Float_t pt() const;
  Float_t eta() const;
  Float_t phi() const;
  Float_t mass() const;
  Float_t area() const;
  Float_t absEta() const;
  const Jet::LorentzVector & p4() const;

protected:
  Float_t pt_;   ///< pT of the jet
  Float_t eta_;  ///< eta of the jet
  Float_t phi_;  ///< phi of the jet
  Float_t mass_; ///< mass of the jet
  Float_t area_; ///< area of the jet
  Float_t absEta_; ///< |eta| of the jet
  Jet::LorentzVector p4_; ///< 4-momentum constructed from the pT, eta, phi and mass
};

std::ostream &
operator<<(std::ostream & stream,
           const Jet & jet);

#endif // JetMETAnalysis_JetUtilities_Jet_h
