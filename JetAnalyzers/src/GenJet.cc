#include "JetMETAnalysis/JetAnalyzers/interface/GenJet.h" // GenJet

GenJet::GenJet(const Jet & jet,
	       Int_t partonFlavour,
	       UInt_t hadronFlavour)
  : Jet(jet)
  , partonFlavour_(partonFlavour)
  , hadronFlavour_(hadronFlavour)
{}

Int_t 
GenJet::partonFlavour() const
{
  return partonFlavour_;
}
 
UInt_t 
GenJet::hadronFlavour() const
{
  return hadronFlavour_;
}

std::ostream &
operator<<(std::ostream & stream,
           const GenJet & jet)
{ 
  stream << static_cast<const Jet &>(jet)             << ","
            "partonFlavour = " << jet.partonFlavour() << ","
            "hadronFlavour = " << jet.hadronFlavour();
  stream << '\n';
  return stream;
}
