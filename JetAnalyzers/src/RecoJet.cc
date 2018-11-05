#include "JetMETAnalysis/JetAnalyzers/interface/RecoJet.h"

#include "JetMETAnalysis/JetAnalyzers/interface/GenJet.h" // GenJet

RecoJet::RecoJet(const Jet & jet,
		 Float_t area,
		 Float_t rawFactor,
		 Float_t chHEF,
		 Float_t neHEF,
		 Float_t chEmEF,
		 Float_t neEmEF,
		 Int_t jetId)
  : Jet(jet)
  , area_(area)
  , rawFactor_(rawFactor)
  , chHEF_(chHEF)
  , neHEF_(neHEF)
  , chEmEF_(chEmEF)
  , neEmEF_(neEmEF)
  , jetId_(jetId)
{}

RecoJet::~RecoJet()
{}

void
RecoJet::set_genJet(const GenJet * genJet)
{
  genJet_.reset(genJet);
}

Float_t 
RecoJet::area() const
{
  return area_;
}

Float_t 
RecoJet::rawFactor() const
{
  return rawFactor_;
}
  
Float_t 
RecoJet::chHEF() const
{
  return chHEF_;
}

Float_t 
RecoJet::neHEF() const
{
  return neHEF_;
}

Float_t 
RecoJet::chEmEF() const
{
  return chEmEF_;
}

Float_t 
RecoJet::neEmEF() const
{
  return neEmEF_;
}

Int_t 
RecoJet::jetId() const
{
  return jetId_;
}

const GenJet *
RecoJet::genJet() const
{
  return genJet_.get();
}

std::ostream &
operator<<(std::ostream & stream,
           const RecoJet & jet)
{ 
  stream << static_cast<const Jet &>(jet)             << ","
            "area = " << jet.area()                   << ","
            "rawFactor = " << jet.rawFactor()         << ","
            "chHEF = " << jet.chHEF()                 << ","
            "neHEF = " << jet.neHEF()                 << ","
            "chEmEF = " << jet.chEmEF()               << ","
            "neEmEF = " << jet.neEmEF()               << ","   
            "jetId = " << jet.jetId()                 << "\n";
  stream << "gen. matching:\n";
  stream << " jet = " << jet.genJet();
  if(jet.genJet())
  {
    stream << ": " << *(jet.genJet());
  } 
  stream << '\n';
  return stream;
}
