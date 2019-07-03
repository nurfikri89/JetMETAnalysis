#ifndef JetMETAnalysis_JetUtilities_ReaderBase_h
#define JetMETAnalysis_JetUtilities_ReaderBase_h

/** \class ReaderBase
 *
 * Purely virtual base class, which defines the interface for reading 
 * collections of reconstructed and generator-level jets from nanoAOD Ntuple.
 *
 * \authors Christian Veelken, Tallinn;
 *          Karl Ehataht, Tallinn
 *
 */

class TTree; // forward declaration

#include <string> // std::string

class ReaderBase
{
public:
  ReaderBase() = default;
  virtual ~ReaderBase() {}

  virtual void
  setBranchAddresses(TTree * tree) = 0;
};

#endif // JetMETAnalysis_JetUtilities_ReaderBase_h
