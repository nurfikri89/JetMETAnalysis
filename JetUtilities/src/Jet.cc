#include "JetMETAnalysis/JetUtilities/interface/Jet.h" // Jet

#include <cmath> // std::fabs()

Jet::Jet(Double_t pt,
         Double_t eta,
         Double_t phi,
         Double_t mass,
         Double_t area)
  : pt_(pt)
  , eta_(eta)
  , phi_(phi)
  , mass_(mass)
  , area_(area)
  , absEta_(std::fabs(eta_))
  , p4_{pt_, eta_, phi_, mass_}
{}

Float_t
Jet::pt() const
{
  return pt_;
}

Float_t
Jet::eta() const
{
  return eta_;
}

Float_t
Jet::phi() const
{
  return phi_;
}

Float_t
Jet::mass() const
{
  return mass_;
}

Float_t
Jet::area() const
{
  return area_;
}

Float_t
Jet::absEta() const
{
  return absEta_;
}

const Jet::LorentzVector &
Jet::p4() const
{
  return p4_;
}

std::ostream &
operator<<(std::ostream & stream,
           const Jet & jet)
{
  stream << " pT = "   << jet.pt()          << ","
            " eta = "  << jet.eta()         << ","
            " phi = "  << jet.phi()         << ","
            " mass = " << jet.mass()        << ","
            " area = " << jet.area()        << ","
            " E = "    << jet.p4().energy() << ","
            " |p| = "  << jet.p4().P();
  return stream;
}
