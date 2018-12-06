#include "JetMETAnalysis/JetUtilities/interface/EventInfo.h"

EventInfo::EventInfo(UInt_t run,
                     UInt_t lumi,
                     ULong64_t event,
                     Int_t numPU,
                     Float_t numPU_true,
                     Int_t numVertices,
                     Float_t vertexZ,
                     Float_t rho,
                     Float_t weight,
                     Float_t pThat,
                     Float_t pudensity,
                     Float_t gpudensity)
  : run_(run)
  , lumi_(lumi)
  , event_(event)
  , numPU_(numPU)
  , numPU_true_(numPU_true)
  , numVertices_(numVertices)
  , vertexZ_(vertexZ)
  , rho_(rho)
  , weight_(weight)
  , pThat_(pThat)
  , pudensity_(pudensity)
  , gpudensity_(gpudensity)
{}

UInt_t 
EventInfo::run() const
{
  return run_;
}

UInt_t 
EventInfo::lumi() const
{
  return lumi_;
}
 
ULong64_t 
EventInfo::event() const
{
  return event_;
}

Int_t 
EventInfo::numPU() const
{
  return numPU_;
}

Float_t 
EventInfo::numPU_true() const
{
  return numPU_true_;
}

Int_t 
EventInfo::numVertices() const
{
  return numVertices_;
}

Float_t 
EventInfo::vertexZ() const
{
  return vertexZ_;
}

Float_t 
EventInfo::rho() const
{
  return rho_;
}

Float_t 
EventInfo::weight() const
{
  return weight_;
}

Float_t 
EventInfo::pThat() const
{
  return pThat_;
}

Float_t
EventInfo::pudensity() const
{
  return pudensity_;
}

Float_t
EventInfo::gpudensity() const
{
  return gpudensity_;
}

std::ostream &
operator<<(std::ostream & os,
           const EventInfo & info)
{
  os << "run = " << info.run() << ", ls = " << info.lumi() << ", event = " << info.event() << ":" << std::endl;
  os << " numPU: actual = " << info.numPU() << ", true = " << info.numPU_true() << std::endl;
  os << " rho = " << info.rho() << std::endl;
  os << " pudensity = " << info.pudensity() << ", gpudensity = " << info.gpudensity() << std::endl;
  os << "(weight = " << info.weight() << ", pThat = " << info.pThat() << ")" << std::endl;
  return os;
}
