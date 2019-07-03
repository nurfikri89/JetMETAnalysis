#ifndef JetMETAnalysis_JetUtilities_EventInfo_h
#define JetMETAnalysis_JetUtilities_EventInfo_h

/** \class EventInfo
 *
 * Dataformat class for accessing event-level quantities.
 *
 * \authors Christian Veelken, Tallinn;
 *          Karl Ehataht, Tallinn
 *
 */

#include <Rtypes.h> // Float_t, UInt_t, ULong64_t

#include <iostream> // std::ostream

class EventInfo
{
public:
  EventInfo() = default;
  EventInfo(UInt_t run,
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
            Float_t gpudensity);

  ~EventInfo() {}

  UInt_t run() const;
  UInt_t lumi() const;
  ULong64_t event() const;

  Int_t numPU() const;
  Float_t numPU_true() const;
  Int_t numVertices() const;
  Float_t vertexZ() const;
  Float_t rho() const;

  Float_t weight() const;
  Float_t pThat() const;

  Float_t pudensity() const;
  Float_t gpudensity() const;

  friend class EventInfoReader;

private:
  UInt_t    run_;         ///< run number
  UInt_t    lumi_;        ///< luminosity
  ULong64_t event_;       ///< event number
  Int_t     numPU_;       ///< actual number of pileup interactions
  Float_t   numPU_true_;  ///< true number of pileup interactions (mean of Poisson distribution)
  Int_t     numVertices_; ///< number of reconstructed proton-proton collision vertices (including pileup)
  Float_t   vertexZ_;     ///< position, along beam direction, of hard-scatter vertex
  Float_t   rho_;         ///< average energy density in the event (reconstructed by FastJet algorithm)
  Float_t   weight_;      ///< MC generator weight
  Float_t   pThat_;       ///< MC generator pT scale  
  Float_t   pudensity_;   ///< PU vertices / mm
  Float_t   gpudensity_;  ///< Generator-level PU vertices / mm
};

std::ostream &
operator<<(std::ostream & os,
           const EventInfo & info);

#endif // JetMETAnalysis_JetUtilities_EventInfo_h
