
/** \executable jet_ntuple_filler
 *
 * Produce plain ROOT Ntuple in format expected by 'jet_response_analyzer_x',
 * using nanoAOD Ntuple as input.
 *
 * \authors Christian Veelken, Tallinn;
 *          Karl Ehataht, Tallinn
 *
 */

#include "FWCore/ParameterSet/interface/ParameterSet.h" // edm::ParameterSet
#include "FWCore/PythonParameterSet/interface/MakeParameterSets.h" // edm::readPSetsFrom()
#include "FWCore/Utilities/interface/Exception.h" // cms::Exception
#include "PhysicsTools/FWLite/interface/TFileService.h" // fwlite::TFileService
#include "DataFormats/FWLite/interface/InputSource.h" // fwlite::InputSource
#include "DataFormats/FWLite/interface/OutputFiles.h" // fwlite::OutputFiles
#include "CondFormats/JetMETObjects/interface/JetCorrectorParameters.h" // JetCorrectorParameters
#include "CondFormats/JetMETObjects/interface/FactorizedJetCorrector.h" // FactorizedJetCorrector
#include "FWCore/ParameterSet/interface/FileInPath.h" // edm::FileInPath
#include "DataFormats/Math/interface/deltaR.h" // deltaR
#include "DataFormats/Math/interface/deltaPhi.h" // deltaPhi

#include "JetMETAnalysis/JetAnalyzers/interface/RecoJet.h" // RecoJet
#include "JetMETAnalysis/JetAnalyzers/interface/RecoJetReader.h" // RecoJetReader
#include "JetMETAnalysis/JetAnalyzers/interface/GenJet.h" // GenJet
#include "JetMETAnalysis/JetAnalyzers/interface/GenJetReader.h" // GenJetReader
#include "JetMETAnalysis/JetAnalyzers/interface/JetCollectionGenMatcher.h" // JetCollectionGenMatcher
#include "JetMETAnalysis/JetAnalyzers/interface/EventInfo.h" // EventInfo
#include "JetMETAnalysis/JetAnalyzers/interface/EventInfoReader.h" // EventInfoReader
#include "JetMETAnalysis/JetAnalyzers/interface/TTreeWrapper.h" // TTreeWrapper
#include "JetMETAnalysis/JetUtilities/interface/JRAEvent.h" // JRAEvent

#include <TBenchmark.h> // TBenchmark

#include <string> // std::string
#include <vector> // std::vector<>
#include <iostream> // std::cout, std::endl
#include <cmath> // std::fabs

JetCorrectorParameters loadJetCorrPar(const std::string& jecFilePath, const std::string& jecFileName)
{
  std::string jecFileName_full = jecFilePath;
  if ( jecFileName_full.find_last_of('/') != (jecFileName_full.length() - 1) ) jecFileName_full.append("/");
  jecFileName_full.append(jecFileName);
  edm::FileInPath jecFileName_fip(jecFileName_full);
  JetCorrectorParameters jetCorrPar(jecFileName_fip.fullPath());
  return jetCorrPar;
}

int main(int argc, char* argv[])
{
//--- throw an exception in case ROOT encounters an error
  gErrorAbortLevel = kError;

//--- parse command-line arguments
  if ( argc < 2 ) {
    std::cout << "Usage: " << argv[0] << " [parameters.py]" << std::endl;
    return EXIT_FAILURE;
  }

  std::cout << "<jet_ntuple_filler>:" << std::endl;

//--- keep track of time it takes the macro to execute
  TBenchmark clock;
  clock.Start("jet_ntuple_filler");

//--- read python configuration parameters
  if ( !edm::readPSetsFrom(argv[1])->existsAs<edm::ParameterSet>("process") )
    throw cms::Exception("jet_ntuple_filler")
      << "No ParameterSet 'process' found in configuration file = " << argv[1] << " !!\n";

  edm::ParameterSet cfg = edm::readPSetsFrom(argv[1])->getParameter<edm::ParameterSet>("process");

  edm::ParameterSet cfg_jet_ntuple_filler = cfg.getParameter<edm::ParameterSet>("jet_ntuple_fille");

  std::string inputTreeName = cfg_jet_ntuple_filler.getParameter<std::string>("inputTreeName");

  std::string src_recJets = cfg_jet_ntuple_filler.getParameter<std::string>("src_recJets");
  std::string src_genJets = cfg_jet_ntuple_filler.getParameter<std::string>("src_genJets");
  std::string src_numPU = cfg_jet_ntuple_filler.getParameter<std::string>("src_numPU");
  std::string src_numPU_true = cfg_jet_ntuple_filler.getParameter<std::string>("src_numPU_true");
  std::string src_numVertices = cfg_jet_ntuple_filler.getParameter<std::string>("src_numVertices");
  std::string src_vertexZ = cfg_jet_ntuple_filler.getParameter<std::string>("src_vertexZ");
  std::string src_rho = cfg_jet_ntuple_filler.getParameter<std::string>("src_rho");
  std::string src_weight = cfg_jet_ntuple_filler.getParameter<std::string>("src_weight");
  std::string src_pThat = cfg_jet_ntuple_filler.getParameter<std::string>("src_pThat");
  
  double dR_match = cfg_jet_ntuple_filler.getParameter<double>("dR_match");

  std::string jetCorrectionLevels = cfg_jet_ntuple_filler.getParameter<std::string>("jetCorrectionLevels");
  std::string jecFilePath = cfg_jet_ntuple_filler.getParameter<std::string>("jecFilePath");
  std::string jecFileName_l1 = cfg_jet_ntuple_filler.getParameter<std::string>("jecFileName_l1");
  std::string jecFileName_l2 = cfg_jet_ntuple_filler.getParameter<std::string>("jecFileName_l2");
  std::string jecFileName_l3 = cfg_jet_ntuple_filler.getParameter<std::string>("jecFileName_l3");
  FactorizedJetCorrector* jetCorrector = nullptr;
  if ( jetCorrectionLevels != "" ) {
    std::vector<JetCorrectorParameters> jetCorrParams;
    if ( jetCorrectionLevels.find("l1") != std::string::npos ) {
      jetCorrParams.push_back(loadJetCorrPar(jecFilePath, jecFileName_l1));
    }
    if ( jetCorrectionLevels.find("l2") != std::string::npos ) {
      jetCorrParams.push_back(loadJetCorrPar(jecFilePath, jecFileName_l2));
    }
    if ( jetCorrectionLevels.find("l3") != std::string::npos ) {
      jetCorrParams.push_back(loadJetCorrPar(jecFilePath, jecFileName_l3));
    }
    if ( !(jetCorrParams.size() >= 1) ) 
      throw cms::Exception("jet_ntuple_filler")
	<< "Invalid Configuration parameter 'jetCorrectionLevels' = " << jetCorrectionLevels << " !!\n";
    jetCorrector = new FactorizedJetCorrector(jetCorrParams);
  }

  bool isDEBUG = cfg_jet_ntuple_filler.getParameter<bool>("isDEBUG");
  
  fwlite::InputSource inputFiles(cfg);
  int maxEvents = inputFiles.maxEvents();
  std::cout << " maxEvents = " << maxEvents << std::endl;
  unsigned reportEvery = inputFiles.reportAfter();

  fwlite::OutputFiles outputFile(cfg);
  fwlite::TFileService fs = fwlite::TFileService(outputFile.file().data());

  TTreeWrapper * inputTree = new TTreeWrapper(inputTreeName.data(), inputFiles.files(), maxEvents);

  std::cout << "Loaded " << inputTree -> getFileCount() << " file(s).\n";

  EventInfoReader* evtInfoReader = new EventInfoReader(
    src_numPU, src_numPU_true, src_numVertices, src_vertexZ, src_rho, 
    src_weight, src_pThat);
  inputTree->registerReader(evtInfoReader);

  RecoJetReader* recJetReader = new RecoJetReader(src_recJets);
  inputTree->registerReader(recJetReader);

  GenJetReader* genJetReader = new GenJetReader(src_genJets);
  inputTree->registerReader(genJetReader);

  JetCollectionGenMatcher jetGenMatcher;

  std::string outputTreeName = cfg_jet_ntuple_filler.getParameter<std::string>("outputTreeName");
  TTree* outputTree = fs.make<TTree>(outputTreeName.data(), outputTreeName.data());
  std::bitset<8> outputTree_flags = cfg_jet_ntuple_filler.getParameter<unsigned>("outputTree_flags");
  JRAEvent* outputTree_event = new JRAEvent(outputTree, outputTree_flags);

  int analyzedEntries = 0;
  int selectedEntries = 0;
  double selectedEntries_weighted = 0.;
  while ( inputTree->hasNextEvent() ) {

    EventInfo evtInfo = evtInfoReader->read();

    if ( inputTree->canReport(reportEvery) ) {
      std::cout << "processing Entry " << inputTree->getCurrentMaxEventIdx()
                << " or " << inputTree->getCurrentEventIdx() << " entry in #" << (inputTree->getProcessedFileCount() - 1)
                << " (run = " << evtInfo.run() << ", ls = " << evtInfo.lumi() << ", event = " << evtInfo.event() << ")"
                << " file (" << selectedEntries << " Entries selected)\n";
    }
    ++analyzedEntries;

    std::vector<RecoJet> recJets = recJetReader->read();
    std::vector<GenJet> genJets = genJetReader->read();
    jetGenMatcher.addGenJetMatch(recJets, genJets, dR_match);

    outputTree_event->clear();

    outputTree_event->npus->push_back(evtInfo.numPU());
    outputTree_event->tnpus->push_back(evtInfo.numPU_true());
    outputTree_event->bxns->push_back(0);
    outputTree_event->rho = evtInfo.rho();
    outputTree_event->pthat = evtInfo.pThat();
    outputTree_event->weight = evtInfo.weight();
    outputTree_event->refpvz = evtInfo.vertexZ();
    outputTree_event->npv = evtInfo.numVertices();
    outputTree_event->run = evtInfo.run();
    outputTree_event->lumi = evtInfo.lumi();
    outputTree_event->evt = evtInfo.event();
    outputTree_event->refdzvtx->push_back(0);

    int numRecJets_selected = 0;
    for ( std::vector<RecoJet>::const_iterator recJet = recJets.begin();
	  recJet != recJets.end(); ++recJet ) {
      const GenJet* genJet = recJet->genJet();
      if ( !genJet ) continue;
           
      double sf = 1. - recJet->rawFactor();
      Jet::LorentzVector recJetP4_raw(sf*recJet->pt(), recJet->eta(), recJet->phi(), sf*recJet->mass());
      assert(std::fabs(recJetP4_raw.eta() - recJet->eta()) < 1.e-2);
      assert(std::fabs(recJetP4_raw.phi() - recJet->phi()) < 1.e-2);

      double jec = 1.;
      if ( jetCorrector ) {
	jetCorrector->setJetEta(recJetP4_raw.eta());
	jetCorrector->setJetPt(recJetP4_raw.pt());
	jetCorrector->setJetA(recJet->area());
	jetCorrector->setRho(evtInfo.rho());
	jec = jetCorrector->getCorrection();
	if ( isDEBUG ) {
	  std::cout << "jet #" << numRecJets_selected << ":" 
		    << " calibrated pT = " << recJet->pt() << ", raw pT = " << recJetP4_raw.pt() << "," 
		    << " eta = " << recJet->eta() << ", phi = " << recJet->phi() << "," 
		    << " jec(" << jetCorrectionLevels << ") = " << jec << std::endl;
	}
      }

      outputTree_event->refrank->push_back(numRecJets_selected);
      outputTree_event->refpdgid->push_back(genJet->partonFlavour());
      outputTree_event->refpdgid_algorithmicDef->push_back(genJet->partonFlavour());
      outputTree_event->refpdgid_physicsDef->push_back(genJet->partonFlavour());
      outputTree_event->refe->push_back(genJet->p4().energy());
      outputTree_event->refpt->push_back(genJet->pt());
      outputTree_event->refeta->push_back(genJet->eta());
      outputTree_event->refphi->push_back(genJet->phi());
      outputTree_event->refy->push_back(genJet->p4().Rapidity());
      outputTree_event->refdphijt->push_back(deltaPhi(genJet->phi(), recJet->phi()));
      outputTree_event->refdrjt->push_back(deltaR(genJet->eta(), genJet->phi(), recJet->eta(), recJet->phi()));
      outputTree_event->refarea->push_back(0.); // not available in nanoAOD 
      outputTree_event->jte->push_back(recJetP4_raw.energy());
      outputTree_event->jtpt->push_back(recJetP4_raw.pt());
      outputTree_event->jteta->push_back(recJetP4_raw.eta());
      outputTree_event->jtphi->push_back(recJetP4_raw.phi());
      outputTree_event->jty->push_back(recJetP4_raw.Rapidity());
      outputTree_event->jtjec->push_back(jec);
      outputTree_event->jtarea->push_back(recJet->area());
      outputTree_event->jtemf->push_back(0.); // not available in nanoAOD 
      outputTree_event->jtchf->push_back(recJet->chHEF());
      outputTree_event->jtnhf->push_back(recJet->neHEF());
      outputTree_event->jtnef->push_back(recJet->neEmEF());
      outputTree_event->jtcef->push_back(recJet->chEmEF());
      outputTree_event->jtmuf->push_back(0.); // not available in nanoAOD 
      outputTree_event->jthfhf->push_back(0.); // not available in nanoAOD
      outputTree_event->jthfef->push_back(0.); // not available in nanoAOD
 
      ++numRecJets_selected;
    }

    outputTree_event->nref = numRecJets_selected;

    outputTree->Fill();
    
    ++selectedEntries;
    selectedEntries_weighted += evtInfo.weight();
  }

  std::cout << "max num. Entries = " << inputTree->getCumulativeMaxEventCount()
            << " (limited by " << maxEvents << ") processed in "
            << inputTree->getProcessedFileCount() << " file(s) (out of "
            << inputTree->getFileCount() << ")\n"
            << " analyzed = " << analyzedEntries << '\n'
            << " selected = " << selectedEntries << " (weighted = " << selectedEntries_weighted << ")\n\n"
            << "cut-flow table" << std::endl;
  
  delete recJetReader;
  delete genJetReader;

  delete jetCorrector;

  delete inputTree;

  clock.Show("jet_ntuple_filler");

  return EXIT_SUCCESS;
}
