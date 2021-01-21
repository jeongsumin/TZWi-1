#!/usr/bin/env python
# @(#)root/tmva $Id$
# ------------------------------------------------------------------------------ #
# Project      : TMVA - a Root-integrated toolkit for multivariate data analysis #
# Package      : TMVA                                                            #
# Python script: TMVAClassification.py                                           #
#                                                                                #
# This python script provides examples for the training and testing of all the   #
# TMVA classifiers through PyROOT.                                               #
#                                                                                #
# The Application works similarly, please see:                                   #
#    TMVA/macros/TMVAClassificationApplication.C                                 #
# For regression, see:                                                           #
#    TMVA/macros/TMVARegression.C                                                #
#    TMVA/macros/TMVARegressionpplication.C                                      #
# and translate to python as done here.                                          #
#                                                                                #
# As input data is used a toy-MC sample consisting of four Gaussian-distributed  #
# and linearly correlated input variables.                                       #
#                                                                                #
# The methods to be used can be switched on and off via the prompt command, for  #
# example:                                                                       #
#                                                                                #
#    python TMVAClassification.py --methods Fisher,Likelihood                    #
#                                                                                #
# The output file "TMVA.root" can be analysed with the use of dedicated          #
# macros (simply say: root -l <../macros/macro.C>), which can be conveniently    #
# invoked through a GUI that will appear at the end of the run of this macro.    #
#                                                                                #
# for help type "python TMVAClassification.py --help"                            #
# ------------------------------------------------------------------------------ #

# --------------------------------------------
# Standard python import
import sys    # exit
import time   # time accounting
import getopt # command line parser

# --------------------------------------------
import os
import yaml
from glob import glob

#options
print("Usage: python TMVAClassification.py mode -options")
print("Usage: python TMVAClassification.py --channel TTZct --mode ElElEl --method BDT,BDTG --outputfile fcnc_3El_TTZct_4bkg_BDT_G")
print("Usage: python TMVAClassification.py -C TTZct,TTZut -M ElElEl,MuElEl -m BDT,BDTG -o fcnc_3El_1Mu2El_TTsig_4bkg_BDT_G")
print("Usage: python TMVAClassification.py -C STZct,STZut -m BDT,BDTG -o fcnc_allCH_STsig_4bkg_BDT_G")
print("The weight directory name will be same to output name (result_+outputname)")

# Default settings for command line arguments
DEFAULT_OUTFNAME = "TMVA.root"
DEFAULT_INFNAME  = "tmva_class_example.root"
DEFAULT_TREESIG  = "TreeS"
DEFAULT_TREEBKG  = "TreeB"
#DEFAULT_METHODS = "BDT,BDTG,BDT850,BDT200,BDT100,BDT50,BDTG_ST,BDTG225,BDTGt1,BDTG_TT,BDTGt2"
DEFAULT_METHODS = "BDTG,BDTG_ST,BDTG225,BDTGt1,BDTG_TT,BDTGt2"
#DEFAULT_METHODS = "BDTG_TT"
DEFAULT_WEIGHTDIR = "dataset"
DEFAULT_MODE = ["ElElEl", "MuElEl", "MuMuMu", "ElMuMu"]
DEFAULT_CUT = ""
DEFAULT_CHANNEL = ["TTZct", "TTZut", "STZct", "STZut"]

# Print usage help
def usage():
    print " "
    print "Usage: python %s [options]" % sys.argv[0]
    print "  -m | --methods    : gives methods to be run (default: all methods)"
    print "  -i | --inputfile  : name of input ROOT file (default: '%s')" % DEFAULT_INFNAME
    print "  -o | --outputfile : name of output ROOT file containing results (default: '%s')" % DEFAULT_OUTFNAME
    print "  -t | --inputtrees : input ROOT Trees for signal and background (default: '%s %s')" \
          % (DEFAULT_TREESIG, DEFAULT_TREEBKG)
    print "  -M | --mode       : select mode [ElElEl, MuElEl, MuMuMu, ElMuMu] (default: all mode; '%s')" % DEFAULT_MODE
    print "  -C | --channel    : select signal MC (TTZct, TTZut, STZct, STZut) (default: all signal MC; '%s')" % DEFAULT_CHANNEL
    print "  -v | --verbose"
    print "  -? | --usage      : print this help message"
    print "  -h | --help       : print this help message"
    print " "

# Main routine
def main():

    try:
        # retrive command line options
        shortopts  = "m:i:t:o:M:C:vh?"
        longopts   = ["methods=", "inputfile=", "inputtrees=", "outputfile=", "mode=", "channel=", "verbose", "help", "usage"]
        opts, args = getopt.getopt( sys.argv[1:], shortopts, longopts )

    except getopt.GetoptError:
        # print help information and exit:
        print "ERROR: unknown options in argument %s" % sys.argv[1:]
        usage()
        sys.exit(1)

    #infname     = DEFAULT_INFNAME
    treeNameSig = DEFAULT_TREESIG
    treeNameBkg = DEFAULT_TREEBKG
    outfname    = DEFAULT_OUTFNAME
    methods     = DEFAULT_METHODS
    verbose     = False
    weightdir   = DEFAULT_WEIGHTDIR
    mode        = DEFAULT_MODE
    cut         = DEFAULT_CUT
    channel     = DEFAULT_CHANNEL

    for o, a in opts:
        if o in ("-?", "-h", "--help", "--usage"):
            usage()
            sys.exit(0)
        elif o in ("-m", "--methods"):
            methods = a
        elif o in ("-i", "--inputfile"):
            infname = a
        elif o in ("-o", "--outputfile"):
            outfname = a
            weightdir = 'result_' + a
        elif o in ("-t", "--inputtrees"):
            a.strip()
            trees = a.rsplit( ' ' )
            trees.sort()
            trees.reverse()
            if len(trees)-trees.count('') != 2:
                print "ERROR: need to give two trees (each one for signal and background)"
                print trees
                sys.exit(1)
            treeNameSig = trees[0]
            treeNameBkg = trees[1]
        elif o in ("-v", "--verbose"):
            verbose = True
        elif o in ("-M", "--mode"):
            mode = a.replace(' ',',').split(',')
        elif o in ("-C", "--channel"):
            channel = a.replace(' ',',').split(',')

    # Print methods
    print channel
    mlist = methods.replace(' ',',').split(',')
    print "=== TMVAClassification: use method(s)..."
    for m in mlist:
        if m.strip() != '':
            print "=== - <%s>" % m.strip()

    # Import ROOT classes
    #from ROOT import gSystem, gROOT, gApplication, TFile, TTree, TCut
    from ROOT import *
    
    # check ROOT version, give alarm if 5.18 
    if gROOT.GetVersionCode() >= 332288 and gROOT.GetVersionCode() < 332544:
        print "*** You are running ROOT version 5.18, which has problems in PyROOT such that TMVA"
        print "*** does not run properly (function calls with enums in the argument are ignored)."
        print "*** Solution: either use CINT or a C++ compiled version (see TMVA/macros or TMVA/examples),"
        print "*** or use another ROOT version (e.g., ROOT 5.19)."
        sys.exit(1)
    
    # Import TMVA classes from ROOT
    #from ROOT import TMVA
    TMVA.Tools.Instance()

    # Output file
    if not os.path.exists( 'output' ):
      os.makedirs('output')
    outdir = 'output/'
    outputFile = TFile( outdir+outfname+".root", 'RECREATE' )
    
    # Create instance of TMVA factory (see TMVA/macros/TMVAClassification.C for more factory options)
    # All TMVA output can be suppressed by removing the "!" (not) in 
    # front of the "Silent" argument in the option string
    factory = TMVA.Factory( "TMVAClassification", outputFile, 
                            "!V:!Silent:Color:DrawProgressBar:Transformations=I;D;P;G,D:AnalysisType=Classification" )
                            #"!V:!Silent:Color:DrawProgressBar:Transformations=I:AnalysisType=Classification" )

    # Set verbosity
    factory.SetVerbose( verbose )

    # If you wish to modify default settings 
    # (please check "src/Config.h" to see all available global options)
    #    gConfig().GetVariablePlotting()).fTimesRMS = 8.0
    #    gConfig().GetIONames()).fWeightFileDir = "myWeightDirectory"

    dataloader = TMVA.DataLoader( "dataset" )
    TMVA.gConfig().GetIONames().fWeightFileDir = weightdir

    # Define the input variables that shall be used for the classifier training
    # note that you may also use variable expressions, such as: "3*var1/var2*abs(var3)"
    # [all types of expressions that can also be parsed by TTree::Draw( "expression" )]

    #varListF = [
    #  "MVAinput_WLZL1_dPhi", "MVAinput_WLZL1_dR", "MVAinput_WLZL2_dPhi", "MVAinput_WLZL2_dR", "MVAinput_ZL1ZL2_dPhi", "MVAinput_ZL1ZL2_dR",
    #  "MVAinput_J1_DeepJetB", "MVAinput_J1_pt", "MVAinput_ZL1J1_dPhi", "MVAinput_ZL1J1_dR", "MVAinput_ZL2J1_dPhi", "MVAinput_ZL2J1_dR", "MVAinput_WLJ1_dPhi", "MVAinput_WLJ1_dR",
    #  "MVAinput_bJ_DeepJetB", "MVAinput_qJ_DeepJetB", "MVAinput_bJ_pt", "MVAinput_qJ_pt", "MVAinput_bJqJ_dPhi", "MVAinput_bJqJ_dR", 
    #  "MVAinput_WLbJ_dPhi", "MVAinput_WLbJ_dR", "MVAinput_WLqJ_dPhi", "MVAinput_WLqJ_dR", "MVAinput_ZL1bJ_dPhi", "MVAinput_ZL1bJ_dR", "MVAinput_ZL1qJ_dPhi", "MVAinput_ZL1qJ_dR",
    #  "MVAinput_ZL2bJ_dPhi", "MVAinput_ZL2bJ_dR", "MVAinput_ZL2qJ_dPhi", "MVAinput_ZL2qJ_dR",
    #  "Z_mass", "W_MT", 
    #]
    if "TTZct" in channel or "TTZut" in channel:
        dataloader.AddVariable( "Z_mass","Z mass","", 'F' )#31
        # add more variables for test
        #dataloader.AddVariable("TriLepton_mass", "total invariant mass of the leptons", "", 'F')#44,New
        #dataloader.AddVariable("TriLepton_WleptonZdPhi", "dPhi of Z/WL", "", 'F')#46,New
        #dataloader.AddVariable("TriLepton_WleptonZdR", "dR of Z/WL", "", 'F')#47,New
        #dataloader.AddVariable("nBjet", "number of b jets", "", 'F')#61,New

        dataloader.AddVariable( "W_MT", "Transeverse mass of W", "", "F" )#62
        # add more variables for test
        #dataloader.AddVariable("KinTopWb_eta", "pseudo rapidity of the SM top", "", 'F')#65,New

        dataloader.AddVariable( "KinTopWb_mass", "SM Top mass", "", "F" )#67
        dataloader.AddVariable( "KinTopZq_mass", "FCNC Top mass", "", "F" )#71

        dataloader.AddVariable( "MVAinput_bJ_DeepJetB", "DeepJetBtagger of SM bjet", "", "F" )
        dataloader.AddVariable( "MVAinput_qJ_DeepJetB", "DeepJetBtagger of FCNC jet", "", "F" )
        dataloader.AddVariable( "MVAinput_bJ_pt", "Transverse momentum of SM bjet", "", "F" )
        dataloader.AddVariable( "MVAinput_bJqJ_dR", "dR of SM bjet and FCNC jet","", "F" )
        dataloader.AddVariable( "MVAinput_WLbJ_dPhi", "dPhi of WL/SM bjet", "", "F" )#94
        # add more variables for test
        #dataloader.AddVariable("MVAinput_WLbJ_dR", "dR of WL/SM bjet", "", 'F')#95,New

        dataloader.AddVariable( "MVAinput_WLqJ_dR", "dR of lepton from W and FCNC jet", "", "F" )
        dataloader.AddVariable( "MVAinput_ZL1bJ_dR", "dR of ZL1/SM bjet", "", "F" )
        dataloader.AddVariable( "MVAinput_ZL1qJ_dR", "dR of ZL1/FCNC jet", "", "F" )
        # add more variables for test

    elif "STZct" in channel or "STZut" in channel:
        dataloader.AddVariable( "Z_mass","Z mass","", 'F' )
        dataloader.AddVariable( "TriLepton_WleptonZdPhi", "dPhi of Z/WL", "", "F" )
        dataloader.AddVariable( "TriLepton_WleptonZdR", "dR of Z/WL", "", "F" )
        dataloader.AddVariable( "W_MT", "Transeverse mass of W", "", "F" )
        dataloader.AddVariable( "KinTopWb_pt", "Transverse momentum of SM top", "", "F" )
        dataloader.AddVariable( "KinTopWb_phi", "phi of SM top", "", "F" )

        dataloader.AddVariable( "MVAinput_WLZL1_dPhi", "dPhi of lepton from W and lepton from Z", "", "F" )
        dataloader.AddVariable( "MVAinput_WLZL1_dR", "dR of lepton from W and lepton from Z", "", "F" )
        dataloader.AddVariable( "MVAinput_bJ_DeepJetB", "DeepJetBtagger of SM bjet", "", "F" )
        dataloader.AddVariable( "MVAinput_WLbJ_dPhi", "dPhi of WL/SM bjet", "", "F" )
        dataloader.AddVariable( "MVAinput_WLbJ_dR", "dR of WL/SM bjet", "", "F" )
        dataloader.AddVariable( "MVAinput_ZL1bJ_dR", "dR of lepton from Z/SM bjet", "", "F" )

    # You can add so-called "Spectator variables", which are not used in the MVA training, 
    # but will appear in the final "TestTree" produced by TMVA. This TestTree will contain the 
    # input variables, the response values of all trained MVAs, and the spectator variables
    #factory.AddSpectator( "spec1:=var1*2",  "Spectator 1", "units", 'F' )
    #factory.AddSpectator( "spec2:=var1*3",  "Spectator 2", "units", 'F' )

    # Set individual event weights (the variables must exist in the original TTree)
    #    for signal    : factory.SetSignalWeightExpression    ("weight1*weight2");
    #    for background: factory.SetBackgroundWeightExpression("weight1*weight2");
    #dataloader.SetWeightExpression("xsecNorm")

    dataloader.AddSpectator( "LeadingLepton_pt" )
    dataloader.AddSpectator( "Z_charge" )
    dataloader.AddSpectator( "nGoodLepton" )
    dataloader.AddSpectator( "GoodLeptonCode" )
    dataloader.AddSpectator( "MVAinput_Status" )

    # Read input data
    rootDir = '%s/src/TZWi/TopAnalysis/test/fcncTriLepton/' % os.environ["CMSSW_BASE"]
    kisti_store = '/xrootd/store/user/heewon/'
    #ntupleDir = 'ntuple_2016'
    ntupleDir = 'ntuple_2016_tightLepVetoJet'
    dName = rootDir + ntupleDir

    procInfo = yaml.load(open(rootDir+"config/grouping.yaml").read())["processes"]
    crosssection = yaml.load(open(rootDir+"config/crosssection.yaml").read())["crosssection"]
    entries = yaml.load(open(rootDir+"config/crosssection.yaml").read())["Entries"]
    datasetInfo = {}
    #for f in glob(rootDir+"config/dataset/MC*16*.yaml"):
    #  for datasetGroup, dataset in yaml.load(open(f).read())['dataset'].iteritems():
    #    datasetInfo[datasetGroup] = dataset.keys()
    for f in glob(rootDir+"config/datasets/MC*16*.yaml"):
      if 'dataset' not in datasetInfo: datasetInfo["dataset"] = {}
      datasetInfo["dataset"].update(yaml.load(open(f).read())["dataset"])

    modes = mode

    fLists_sig = []
    fLists_bkg = []
    #Input list names are comes from 'title' at grouping.yaml
    #all signal title = ["STZct", "STZut", "TTZct", "TTZut"]
    #all background title = ["DYJets", "SingleTop", "ttJets", "ZZ", "WZ", "WW", "SingleTopV", "ttV", "ttH"]
    #High fraction bkgs in the Top pair Signal Region: ["DYJets", "ttJets", "ZZ", "WZ"]
    inputSigList = channel
    if DEFAULT_CHANNEL == channel:
      print("There are no particular signal region. No cut and all signals will be contained")
    # WZ, DY, ZZ -> Treatment in WZCR estimation, ttjet -> Treatment in TTCR estimation
    #high fraction in the Single Top Signal Region & all channel: WZ > DYjet > ZZ > ttjets > SingleTopV(tZq) > ttV > others
    #inputBkgList = ["DYJets", "ttJets", "ZZ", "WZ"] 
    #high fraction in the Top pair Signal Region & all channel: WZ > DYjet > ttV > ZZ > SingleTopV(tZq) > ttjets > others
    #inputBkgList = ["WZ", "DYJets", "ttV", "ZZ"]

    # Backgrounds for training in TTZct (Since June 24th)
    #inputBkgList = ["WZ", "ZZ"]
    # All backgrounds
    #inputBkgList = ["ttJets", "DYJets", "SingleTop", "SingleTopV", "WW", "WZ", "ZZ", "ttV", "ttH"]
    # Bug : Some of the SingleTop sample; "ST_tW_top & antitop _5f_inclusiveDecays TuneCUETP8 M1(M2T4)" has no LHEScaleWeight
    # So just now, exception SingleTop for training
    #inputBkgList = ["ttJets", "DYJets", "SingleTopV", "WZ", "ZZ", "ttV", "ttH"]
    inputBkgList = ["SingleTopV", "WZ", "ZZ", "ttV"]

    for mo in modes:
      for proc in procInfo:
        if "Data" in procInfo[proc]['title']: continue
        for datasetGroup in procInfo[proc]['datasets']:
          #print(datasetGroup)
          #print(datasetInfo['dataset'][datasetGroup].keys())
          for datasetName in datasetInfo['dataset'][datasetGroup].keys():
            for inputSig in inputSigList:
              if ("FCNC" in datasetGroup) and (inputSig in procInfo[proc]['title']):
                fLists_sig.append(glob(dName+"/*/%s/%s" % (mo, datasetName[1:].replace('/','.'))))
            for inputBkg in inputBkgList:
              if ("FCNC" not in datasetGroup) and (inputBkg in procInfo[proc]['title']):
                fLists_bkg.append(glob(dName+"/*/%s/%s" % (mo, datasetName[1:].replace('/','.'))))
    print(fLists_sig)

    # Because of xsecNorm bug
    # LHEScaleWeight[4] : norminal
    # 1. weight before apply TriggerSF & seperate el/mu SF
    #dataloader.SetSignalWeightExpression("LHEScaleWeight[4]*genWeight/abs(genWeight)*puWeight*BtagWeight*LeptonSF*xsecNorm")
    #dataloader.SetBackgroundWeightExpression("LHEScaleWeight[4]*genWeight/abs(genWeight)*puWeight*BtagWeight*LeptonSF")
    #dataloader.SetBackgroundWeightExpression("LHEScaleWeight[4]*genWeight/abs(genWeight)")
    # 2. weight after apply TriggerSF & seperate el/mu SF
    dataloader.SetSignalWeightExpression("LHEScaleWeight[4]*genWeight/abs(genWeight)*puWeight*BtagWeight*Trigger_SF*Electron_SF*MuonID_SF*MuonISO_SF")
    dataloader.SetBackgroundWeightExpression("LHEScaleWeight[4]*genWeight/abs(genWeight)*puWeight*BtagWeight*Trigger_SF*Electron_SF*MuonID_SF*MuonISO_SF")

    trees = []
    for fsig in fLists_sig:
      #print(fsig[0])
      signalWeight = 1.0
      file_list = os.listdir(fsig[0])
      for file_l in file_list:
        #print(file_l)
        f = TFile.Open(fsig[0]+"/"+file_l)
        t_sig = f.Get("Events")
        if (t_sig.GetEntries() == 0): continue
        dataloader.AddSignalTree( t_sig, signalWeight )
        trees.append([f, t_sig])

    for fbkg in fLists_bkg:
      print(fbkg[0])
      backgroundWeight = 1.0
      #for xsec in crosssection:
      #    for num in entries:
      #        if num == "TT":
      #            name = "MC2016." + num + ".powheg"
      #        else:
      #            name = "MC2016." + num
      #        for dataset_key in datasetInfo["dataset"][name].keys():
      #            if dataset_key[1:] == (fbkg[0].split('/')[-1]).replace('.','/') and num == xsec:
      #                backgroundWeight = (crosssection[xsec]/entries[num])*35900
      #print backgroundWeight
      file_list = os.listdir(fbkg[0])
      for file_l in file_list:
        f = TFile.Open(fbkg[0]+"/"+file_l)
        t_bkg = f.Get("Events")
        if (t_bkg.GetEntries() == 0): continue
        dataloader.AddBackgroundTree( t_bkg, backgroundWeight )
        trees.append([f, t_bkg])

    # Apply additional cuts on the signal and background sample.

    print channel
    # TTSR
    if "TTZct" in channel or "TTZut" in channel:
      mycutSig = TCut( "HLT == 1 && TMath::Abs(Z_mass-91.2) < 7.5 && nGoodJet >= 2 && nGoodJet <= 3 && nBjet >= 1 && TMath::Abs(GoodLeptonCode) == 111 && nGoodLepton == 3 && LeadingLepton_pt > 25 && Z_charge == 0 && W_MT <= 300" )
      mycutBkg = TCut( "HLT == 1 && TMath::Abs(Z_mass-91.2) < 7.5 && nGoodJet >= 2 && nGoodJet <= 3 && nBjet >= 1 && TMath::Abs(GoodLeptonCode) == 111 && nGoodLepton == 3 && LeadingLepton_pt >25 && Z_charge == 0 && W_MT <= 300" )
    # STSR
    elif "STZct" in channel or "STZut" in channel:
      mycutSig = TCut( "HLT == 1 && TMath::Abs(Z_mass-91.2) < 7.5 && nGoodJet == 1 && nBjet == 1 && TMath::Abs(GoodLeptonCode) == 111 && nGoodLepton == 3 && LeadingLepton_pt > 25 && Z_charge == 0 && W_MT <= 300" )
      mycutBkg = TCut( "HLT == 1 && TMath::Abs(Z_mass-91.2) < 7.5 && nGoodJet == 1 && nBjet == 1 && TMath::Abs(GoodLeptonCode) == 111 && nGoodLepton == 3 && LeadingLepton_pt > 25 && Z_charge == 0 && W_MT <= 300" )
    elif DEFAULT_CHANNEL == channel:
      mycutSig = TCut( cut )
      mycutBkg = TCut( cut )

    # Here, the relevant variables are copied over in new, slim trees that are
    # used for TMVA training and testing
    # "SplitMode=Random" means that the input events are randomly shuffled before
    # splitting them into training and test samples

    #by mode
    # 1. LooseJet
    # Train:Test = 7:3
    # 1) (number of entries of each mode)*0.7
    '''
    sig_num_TTZct = ['11194', '15014', '28438', '19983']
    sig_num_TTZut = ['10382', '13913', '26353', '18392']
    sig_num_STZct = ['7456', '10296', '17715', '12443']
    sig_num_STZut= ['5789', '7905', '13828', '9750']
    bkg_num_TT = ['17973', '10651', '21398', '33436'] # bkg = WZ, ZZ
    bkg_num_ST = ['27525', '12827', '25801', '53956'] # bkg = WZ, ZZ
    bkg_num_others = ['43284', '58631', '110085', '77351']
    # 2) total number of entries
    tot_sig_num_TTZct = 106614
    tot_sig_num_TTZut = 98627
    tot_sig_num_STZct = 68442
    tot_sig_num_STZut = 53246
    tot_bkg_num_TT = 119224 # bkg = WZ, ZZ
    tot_bkg_num_ST = 171585 # bkg = WZ, ZZ
    '''
    # 2. TightLepVetoJet
    # 1) Total number of entries in each mode [3El, 1Mu2El, 3Mu, 1El2Mu]
    sig_num_TTZct = [16001, 21442, 40610, 28537]
    sig_num_TTZut = [14844, 19864, 37640, 26271]
    sig_num_STZct = [10701, 14781, 25430, 17857]
    sig_num_STZut = [8315, 11360, 19847, 13997]
    #bkg_num_all_TT = [23010, 14425, 28981, 42693] # bkg = WZ, ZZ
    #bkg_num_all_ST = [36756, 18286, 36816, 72068] # bkg = WZ, ZZ
    bkg_num_all_TT = [60656, 65502, 123537, 109315] # bkg = stV, wz, zz, ttV
    bkg_num_all_ST = [49749, 35983, 71524, 95771] # bkg = stV, wz, zz, ttV
    #bkg_num_all_TT = [60818, 65733, 124005, 109660] # bkg = all
    #bkg_num_all_ST = [49797, 36048, 71652, 95880] # bkg = all
    #bkg_num_all_TT = [60797, 65720, 123963, 109622] # bkg = all - (ST, ww, dyjets)
    #bkg_num_all_ST = [49770, 36018, 71615, 95839] # bkg = all - (ST, ww, dyjets)
    # 2) 0.5 * (number of entries) but little bit difference [+10~15 in train]
    #sig_num_TTZct = [8010, 10730, 20315, 14280]
    #sig_num_TTZut = [7435, 9945, 18830, 13145]
    #sig_num_STZct = [5360, 7400, 12730, 8940]
    #sig_num_STZut= [4170, 5690, 9935, 7010]
    #bkg_num_TT = [11515, 7225, 14500, 21360] # bkg = WZ, ZZ
    #bkg_num_ST = [18390, 9155, 18420, 36045] # bkg = WZ, ZZ
    #bkg_num_others = ['43284', '58631', '110085', '77351']
    #bkg_num_all_TT = [30420, 32880, 62015, 54840]
    #bkg_num_all_ST = [24910, 18035, 35840, 47950]
    #bkg_num_all_TT = [30340, 32760, 61780, 54670] # bkg = stV, wz, zz, ttV
    #bkg_num_all_ST = [24885, 18000, 35772, 47895] # bkg = stV, wz, zz, ttV
    # +30~
    #sig_num_TTZct = [8030, 10750, 20335, 14300]
    #sig_num_TTZut = [7455, 9965, 18850, 13165]
    #sig_num_STZct = [5380, 7420, 12750, 8960]
    #sig_num_STZut= [4190, 5710, 9955, 7030]
    #bkg_num_all_TT = [30360, 32780, 61800, 54690] # bkg = stV, wz, zz, ttV
    #bkg_num_all_ST = [24905, 18020, 35790, 47915]
    # +50~
    #sig_num_TTZct = [8050, 10770, 20355, 14320]
    #sig_num_TTZut = [7475, 9985, 18870, 13185]
    #sig_num_STZct = [5400, 7440, 12770, 8980]
    #sig_num_STZut= [4210, 5730, 9975, 7050]
    #bkg_num_all_TT = [30380, 32800, 61820, 54710] # bkg = stV, wz, zz, ttV
    #bkg_num_all_ST = [24925, 18040, 35810, 47935]
    #bkg_num_all_TT = [30426, 32890, 61995, 54830] # bkg = stV, wz, zz, ttV, ttH
    #bkg_num_all_ST = [24915, 18032, 35812, 47933]
    #sig_num_TTZct = [8050, 10770, 20355, 14320]
    #sig_num_TTZut = [7475, 9985, 18870, 13185]
    #sig_num_STZct = [5400, 7440, 12770, 8980]
    #sig_num_STZut= [4210, 5730, 9975, 7050]
    #bkg_num_all_TT = [30380, 32800, 61820, 54710] # bkg = stV, wz, zz, ttV
    #bkg_num_all_ST = [24925, 18040, 35810, 47935]
    # total number of entries
    #tot_sig_num_TTZct = 106590
    #tot_sig_num_TTZut = 98619
    #tot_sig_num_STZct = 68769
    #tot_sig_num_STZut = 53519
    #tot_bkg_num_TT = 109109 # bkg = WZ, ZZ
    #tot_bkg_num_ST = 163926 # bkg = WZ, ZZ
    #bkg_sim number, not all entries in each mode
    tot_sig_num_TTZct = sig_num_TTZct[0]+sig_num_TTZct[1]+sig_num_TTZct[2]+sig_num_TTZct[3]
    tot_sig_num_TTZut = sig_num_TTZut[0]+sig_num_TTZut[1]+sig_num_TTZut[2]+sig_num_TTZut[3]
    tot_sig_num_STZct = sig_num_STZct[0]+sig_num_STZct[1]+sig_num_STZct[2]+sig_num_STZct[3]
    tot_sig_num_STZut = sig_num_STZut[0]+sig_num_STZut[1]+sig_num_STZut[2]+sig_num_STZut[3]
    tot_bkg_num_TT = bkg_num_all_TT[0]+bkg_num_all_TT[1]+bkg_num_all_TT[2]+bkg_num_all_TT[3]
    tot_bkg_num_ST = bkg_num_all_ST[0]+bkg_num_all_ST[1]+bkg_num_all_ST[2]+bkg_num_all_ST[3]

    mode_num = -1 # Using @ all mode (For test BDT option)
    if len(modes) == 1:
        for mo in modes:
            if mo == "ElElEl": mode_num = 0
            elif mo == "MuElEl": mode_num = 1
            elif mo == "MuMuMu": mode_num = 2
            elif mo == "ElMuMu": mode_num = 3

    if len(inputSigList) == 1:
        if "TTZct" in channel:
            # For test all mode (3E,1M2E,3M,1E2M) & bkg: WZ & ZZ 
            #if mode_num < 0 and len(inputBkgList) == 2:
            if mode_num < 0 and len(inputBkgList) == 4:
                options = "nTrain_Signal="+str(tot_sig_num_TTZct*0.5)+":nTrain_Background="+str(tot_bkg_num_TT*0.5)+":nTest_Signal=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V"
                #options = "nTrain_Signal="+str(tot_sig_num_TTZct*0.7)+":nTrain_Background="+str(tot_bkg_num_TT*0.7)+":nTest_Signal=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V"
                #options = "nTest_Signal=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V"
            # For training (bkg: WZ & ZZ)
            #elif mode_num >= 0 and len(inputBkgList) == 2:
                #options = "nTrain_Signal="+str(sig_num_TTZct[mode_num])+":nTrain_Background="+str(bkg_num_TT[mode_num])+":nTest_Signal=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V"
                #options = "nTest_Signal=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V"
            # All backgrounds
            elif mode_num >= 0 and len(inputBkgList) == 4:
                options = "nTrain_Signal="+str(sig_num_TTZct[mode_num]*0.5)+":nTrain_Background="+str(bkg_num_all_TT[mode_num]*0.5)+":nTest_Signal=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V"
                #options = "nTrain_Signal="+str(sig_num_TTZct[mode_num]*0.7)+":nTrain_Background="+str(bkg_num_all_TT[mode_num]*0.7)+":nTest_Signal=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V"
            else:
                options = "nTest_Signal=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V"

        elif "TTZut" in channel:
            # For test all mode (3E,1M2E,3M,1E2M) & bkg: WZ & ZZ
            #if mode_num < 0 and len(inputBkgList) == 2:
            if mode_num < 0 and len(inputBkgList) == 4:
                options = "nTrain_Signal="+str(tot_sig_num_TTZut*0.5)+":nTrain_Background="+str(tot_bkg_num_TT*0.5)+":nTest_Signal=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V"
                #options = "nTrain_Signal="+str(tot_sig_num_TTZut*0.7)+":nTrain_Background="+str(tot_bkg_num_TT*0.7)+":nTest_Signal=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V"
                #options = "nTest_Signal=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V"
            # For training (bkg: WZ & ZZ)
            #elif mode_num >= 0 and len(inputBkgList) == 2:
            #    options = "nTrain_Signal="+str(sig_num_TTZut[mode_num])+":nTrain_Background="+str(bkg_num_TT[mode_num])+":nTest_Signal=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V"
                #options = "nTest_Signal=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V"
            # All backgrounds
            elif mode_num >= 0 and len(inputBkgList) == 4:
                options = "nTrain_Signal="+str(sig_num_TTZut[mode_num]*0.5)+":nTrain_Background="+str(bkg_num_all_TT[mode_num]*0.5)+":nTest_Signal=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V"
                #options = "nTrain_Signal="+str(sig_num_TTZut[mode_num]*0.7)+":nTrain_Background="+str(bkg_num_all_TT[mode_num]*0.7)+":nTest_Signal=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V"
            else:
                options = "nTest_Signal=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V"
        elif "STZct" in channel:
            #if mode_num < 0 and len(inputBkgList) == 2:
            if mode_num < 0 and len(inputBkgList) == 4:
                options = "nTrain_Signal="+str(tot_sig_num_STZct*0.5)+":nTrain_Background="+str(tot_bkg_num_ST*0.5)+":nTest_Signal=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V"
                #options = "nTrain_Signal="+str(tot_sig_num_STZct*0.7)+":nTrain_Background="+str(tot_bkg_num_ST*0.7)+":nTest_Signal=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V"
                #options = "nTest_Signal=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V"
            #elif mode_num >= 0 and len(inputBkgList) == 2:
            #    options = "nTrain_Signal="+str(sig_num_STZct[mode_num])+":nTrain_Background="+str(bkg_num_ST[mode_num])+":nTest_Signal=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V"
                #options = "nTest_Signal=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V"
            # All backgrounds
            elif mode_num >= 0 and len(inputBkgList) == 4:
                options = "nTrain_Signal="+str(sig_num_STZct[mode_num]*0.5)+":nTrain_Background="+str(bkg_num_all_ST[mode_num]*0.5)+":nTest_Signal=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V"
                #options = "nTrain_Signal="+str(sig_num_STZct[mode_num]*0.7)+":nTrain_Background="+str(bkg_num_all_ST[mode_num]*0.7)+":nTest_Signal=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V"
            else:
                options = "nTest_Signal=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V"
        elif "STZut" in channel:
            #if mode_num < 0 and len(inputBkgList) == 2:
            if mode_num < 0 and len(inputBkgList) == 4:
                options = "nTrain_Signal="+str(tot_sig_num_STZut*0.5)+":nTrain_Background="+str(tot_bkg_num_ST*0.5)+":nTest_Signal=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V"
                #options = "nTrain_Signal="+str(tot_sig_num_STZut*0.7)+":nTrain_Background="+str(tot_bkg_num_ST*0.7)+":nTest_Signal=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V"
                #options = "nTest_Signal=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V"
            #elif mode_num >= 0 and len(inputBkgList) == 2:
            #    options = "nTrain_Signal="+str(sig_num_STZut[mode_num])+":nTrain_Background="+str(bkg_num_ST[mode_num])+":nTest_Signal=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V"
                #options = "nTest_Signal=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V"
            # All backgrounds
            elif mode_num >= 0 and len(inputBkgList) == 4:
                options = "nTrain_Signal="+str(sig_num_STZut[mode_num]*0.5)+":nTrain_Background="+str(bkg_num_all_ST[mode_num]*0.5)+":nTest_Signal=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V"
                #options = "nTrain_Signal="+str(sig_num_STZut[mode_num]*0.7)+":nTrain_Background="+str(bkg_num_all_ST[mode_num]*0.7)+":nTest_Signal=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V"
            else:
                options = "nTest_Signal=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V"
        else:
            options = "nTest_Signal=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V"

    dataloader.PrepareTrainingAndTestTree( mycutSig, mycutBkg, options )

    # --------------------------------------------------------------------------------------------------

    # ---- Book MVA methods
    #
    # please lookup the various method configuration options in the corresponding cxx files, eg:
    # src/MethoCuts.cxx, etc, or here: http://tmva.sourceforge.net/optionRef.html
    # it is possible to preset ranges in the option string in which the cut optimisation should be done:
    # "...:CutRangeMin[2]=-1:CutRangeMax[2]=1"...", where [2] is the third input variable

    # Cut optimisation

    # Boosted Decision Trees
    # BDTG Default: NTrees=400:MinNodeSize=2.5%:BoostType=Grad:Shrinkage=0.10:UseBaggedBoost:BaggedSampleFraction=0.5:nCuts=20:MaxDepth=2
    # SeparationType default = GiniIndex
    if "BDTG" in mlist:
        #factory.BookMethod( dataloader, TMVA.Types.kBDT, "BDTG", "!H:!V:NTrees=400:MinNodeSize=5%:BoostType=Grad:Shrinkage=0.30:UseBaggedBoost:BaggedSampleFraction=0.5:SeparationType=GiniIndex:nCuts=20:MaxDepth=3:NegWeightTreatment=Pray")
        factory.BookMethod( dataloader, TMVA.Types.kBDT, "BDTG", "!H:!V:NTrees=200:MinNodeSize=5%:BoostType=Grad:Shrinkage=0.50:SeparationType=GiniIndex:nCuts=15:MaxDepth=3:NegWeightTreatment=Pray")
        #factory.BookMethod( dataloader, TMVA.Types.kBDT, "BDTG", "!H:!V:NTrees=200:MinNodeSize=5%:BoostType=Grad:Shrinkage=0.50:SeparationType=GiniIndex:UseBaggedBoost:BaggedSampleFraction=0.8:nCuts=20:MaxDepth=5:NegWeightTreatment=Pray" )
        #name: optChange
        #factory.BookMethod( dataloader, TMVA.Types.kBDT, "BDTG", "!H:!V:NTrees=400:MinNodeSize=2.5%:BoostType=Grad:Shrinkage=0.10:UseBaggedBoost:BaggedSampleFraction=0.5:nCuts=20:MaxDepth=2:NegWeightTreatment=Pray" )
        #name: IgnNegWeight
        #factory.BookMethod( dataloader, TMVA.Types.kBDT, "BDTG", "!H:!V:NTrees=400:MinNodeSize=2.5%:BoostType=Grad:Shrinkage=0.10:UseBaggedBoost:BaggedSampleFraction=0.5:nCuts=20:MaxDepth=2:NegWeightTreatment=IgnoreNegWeightsInTraining" )
    if "BDTG225" in mlist:
        factory.BookMethod( dataloader, TMVA.Types.kBDT, "BDTG225", "!H:!V:NTrees=225:MinNodeSize=5%:BoostType=Grad:Shrinkage=0.30:UseBaggedBoost:BaggedSampleFraction=0.5:SeparationType=GiniIndex:nCuts=20:MaxDepth=3:NegWeightTreatment=Pray")
    if "BDTGt1" in mlist:
        factory.BookMethod( dataloader, TMVA.Types.kBDT, "BDTGt1", "!H:!V:NTrees=400:MinNodeSize=5%:BoostType=Grad:Shrinkage=0.50:SeparationType=GiniIndex:nCuts=20:MaxDepth=5:NegWeightTreatment=Pray")
    if "BDTG_ST" in mlist:
        factory.BookMethod( dataloader, TMVA.Types.kBDT, "BDTG_ST", "!H:!V:NTrees=200:MinNodeSize=5%:BoostType=Grad:Shrinkage=0.50:SeparationType=GiniIndex:nCuts=15:MaxDepth=3:NegWeightTreatment=Pray")
    #if "BDTG_ST" in mlist: # add bagged boost
    #    factory.BookMethod( dataloader, TMVA.Types.kBDT, "BDTG_ST", "!H:!V:NTrees=200:MinNodeSize=5%:BoostType=Grad:Shrinkage=0.50:SeparationType=GiniIndex:nCuts=15:MaxDepth=3:NegWeightTreatment=Pray:UseBaggedBoost:BaggedSampleFraction=0.8")
    if "BDTG_TT" in mlist:
        factory.BookMethod( dataloader, TMVA.Types.kBDT, "BDTG_TT", "!H:!V:NTrees=200:MinNodeSize=5%:BoostType=Grad:Shrinkage=0.50:SeparationType=GiniIndex:nCuts=20:MaxDepth=5:NegWeightTreatment=Pray")
    #if "BDTG_TT" in mlist: #add bagged boost
    #    factory.BookMethod( dataloader, TMVA.Types.kBDT, "BDTG_TT", "!H:!V:NTrees=200:MinNodeSize=5%:BoostType=Grad:Shrinkage=0.50:SeparationType=GiniIndex:nCuts=20:MaxDepth=5:NegWeightTreatment=Pray:UseBaggedBoost:BaggedSampleFraction=0.8")
    if "BDTGt2" in mlist:
        factory.BookMethod( dataloader, TMVA.Types.kBDT, "BDTGt2", "!H:!V:NTrees=400:MinNodeSize=5%:BoostType=Grad:Shrinkage=0.20:SeparationType=GiniIndex:UseBaggedBoost:BaggedSampleFraction=0.8:nCuts=15:MaxDepth=3:NegWeightTreatment=Pray")

    # BDT Defalut: MinNodeSize=2.5%:MaxDepth=3:BoostType=AdaBoost:AdaBoostBeta=0.5:SeparationType=GiniIndex:nCuts=20
    if "BDT" in mlist:
        factory.BookMethod( dataloader, TMVA.Types.kBDT, "BDT", "!H:!V:NTrees=400:MinNodeSize=5%:MaxDepth=3:BoostType=AdaBoost:AdaBoostBeta=0.5:SeparationType=GiniIndex:nCuts=20:NegWeightTreatment=Pray" )

    if "BDT200" in mlist:
        factory.BookMethod( dataloader, TMVA.Types.kBDT, "BDT200", "!H:!V:NTrees=200:MinNodeSize=5%:MaxDepth=3:BoostType=AdaBoost:AdaBoostBeta=0.5:SeparationType=GiniIndex:nCuts=20:NegWeightTreatment=Pray" )

    if "BDT100" in mlist:
        factory.BookMethod( dataloader, TMVA.Types.kBDT, "BDT100", "!H:!V:NTrees=100:MinNodeSize=5%:MaxDepth=3:BoostType=AdaBoost:AdaBoostBeta=0.5:SeparationType=GiniIndex:nCuts=20:NegWeightTreatment=Pray" )

    if "BDT850" in mlist:
        factory.BookMethod( dataloader, TMVA.Types.kBDT, "BDT850", "!H:!V:NTrees=850:MinNodeSize=5%:MaxDepth=3:BoostType=AdaBoost:AdaBoostBeta=0.5:SeparationType=GiniIndex:nCuts=20:NegWeightTreatment=Pray" )

    if "BDT50" in mlist:
        factory.BookMethod( dataloader, TMVA.Types.kBDT, "BDT50", "!H:!V:NTrees=50:MinNodeSize=5%:MaxDepth=3:BoostType=AdaBoost:AdaBoostBeta=0.5:SeparationType=GiniIndex:nCuts=20:NegWeightTreatment=Pray" )



   # Multi-architecture DNN implementation.
    if ("DNN_CPU" or "DNN_GPU") in mlist:
      # General layout.
      layout = "Layout=TANH|128,TANH|128,TANH|128,LINEAR"
      dnnOptions = ["!H:V:ErrorStrategy=CROSSENTROPY:VarTransform=N:WeightInitialization=XAVIERUNIFORM"]
      dnnOptions.append(layout)

      trainSteps = [
          ["LearningRate=1e-1","WeightDecay=1e-4","Momentum=0.9"],
          ["LearningRate=1e-2","WeightDecay=1e-4","Momentum=0.9"],
          ["LearningRate=1e-3","WeightDecay=1e-4","Momentum=0.0"],
      ]
      dropConfig = ["DropConfig=0.0+0.5+0.5+0.5", "DropConfig=0.0+0.0+0.0+0.0", "DropConfig=0.0+0.0+0.0+0.0"]
      trainStretagy0 = ["Repetitions=1","ConvergenceSteps=20","Regularization=L2","BatchSize=256","TestRepetitions=10","Multithreading=True"]
      dnnOptions.append("TrainingStrategy=%s" % ("|".join([",".join(trainStretagy0+steps+dropConfig) for steps in trainSteps])))

      # Cuda implementation.
      if "DNN_GPU" in mlist:
         dnnOptions.append("Architecture=GPU")
         factory.BookMethod(dataloader, TMVA.Types.kDNN, "DNN_GPU", ":".join(dnnOptions))

      # Multi-core CPU implementation.
      if "DNN_CPU" in mlist:
         dnnOptions.append("Architecture=CPU")
         factory.BookMethod(dataloader, TMVA.Types.kDNN, "DNN_CPU", ":".join(dnnOptions))



    # --------------------------------------------------------------------------------------------------
            
    # ---- Now you can tell the factory to train, test, and evaluate the MVAs. 

    # Train MVAs
    factory.TrainAllMethods()
    
    # Test MVAs
    factory.TestAllMethods()
    
    # Evaluate MVAs
    factory.EvaluateAllMethods()
    
    # Save the output.
    outputFile.Close()
    
    print "=== wrote root file %s\n" % outfname
    print "=== TMVAClassification is done!\n"
    
    # open the GUI for the result macros    
    #TMVA.TMVAGui(outfname+".root")
    
    # keep the ROOT thread running
    #gApplication.Run() 

# ----------------------------------------------------------

if __name__ == "__main__":
    main()
