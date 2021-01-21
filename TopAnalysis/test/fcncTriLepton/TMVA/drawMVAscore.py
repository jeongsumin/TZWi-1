import sys, os
from ROOT import *

#channels = ["TTZct", "TTZut", "STZct", "STZut"]
channels = ["TTZct", "STZct"]
molist = ["ElElEl", "MuElEl", "ElMuMu", "MuMuMu"]
#mclist = ["DYJets", "SingleTop", "SingleTopV", "ZZ", "WZ", "WW", "TTH", "TTV", "TTJets"]
mclist = ["DYJets", "others", "SingleTopV", "ZZ", "WZ", "TTV", "TTJets"]
#colorlist = ["kOrange+1", "kMagenta+1", "kMagenta+2", "kCyan-1", "kAzure+6", "kBlue-6", "kRed+3", "kRed+4", "kRed"]
colorlist = ["kOrange+1", "kYellow-6", "kMagenta+2", "kCyan-1", "kAzure+6", "kRed+4", "kRed"]
bkg_dirname = "bugfix_bkg1_half"

rootDir = '%s/src/TZWi/TopAnalysis/test/fcncTriLepton/' % os.environ["CMSSW_BASE"]
for ch in channels:
    if not os.path.exists( os.path.join(rootDir, 'TMVA', 'shape', bkg_dirname, 'plots_'+ ch) ):
        os.makedirs(os.path.join(rootDir, 'TMVA', 'shape', bkg_dirname, 'plots_'+ ch))

def createCanvasPads():
    c = TCanvas("c", "canvas", 800, 800)
    pad1 = TPad("pad1", "pad1", 0, 0.3, 1, 1.0)
    #pad1.SetBottomMargin(0.1)
    pad1.SetBottomMargin(0.05)
    pad1.SetGridx()
    pad1.Draw()

    c.cd()
    pad2 = TPad("pad2", "pad2", 0, 0, 1, 0.3)
    pad2.SetTopMargin(0)
    pad2.SetBottomMargin(0.35)
    pad2.SetGridx()
    pad2.SetGridy()
    pad2.SetTickx(1)
    pad2.Draw()

    return c, pad1, pad2

def createRatio(hdata, hbkg):
    hratio = hdata.Clone("hratio")
    hratio.SetLineColor(kBlack)
    hratio.SetMaximum(1.5)
    hratio.SetMinimum(0.5)
    hratio.Sumw2()
    hratio.SetStats(0)
    hratio.Divide(hbkg)
    hratio.SetMarkerStyle(21)
    
    return hratio

def drawplot(hdata, hbkg, hsig, hratio, legend, mode, ch):
#def drawplot (hdata, hbkg, hsig, mode):

    c, pad1, pad2 = createCanvasPads()

    pad1.cd()
    #hdata.SetTitle("%s_MVAscore"%mode)
    if mode == "all":
        hdata.SetTitle("%s_%s_MVAscore;;Events" % (ch, mode))
    else:
        hdata.SetTitle("%s_MVAscore;;Events"%mode)
    #hdata.GetXaxis().SetTitleSize(0)
    #hdata.GetXaxis().SetTitleOffset(0)
    hdata.GetXaxis().SetLabelOffset(999)
    hdata.GetXaxis().SetLabelSize(0)
    hdata.GetYaxis().SetTitleOffset(1)
    hdata.GetYaxis().SetLabelSize(0.04)
    hdata.SetMarkerStyle(8)
    hdata.SetMarkerSize(1)
    hdata.SetLineColor(kBlack)
    hdata.SetStats(0)
    hdata.Draw("ep")
    hbkg.Draw("hist, same") # THStack
    hdata.Draw("ep, same")
    if ch == "TTZct" or ch == "STZct":
        hsig.SetLineColor(eval("kBlue"))
    elif ch == "TTZut" or ch == "STZut":
        hsig.SetLineColor(eval("kGreen"))
    hsig.SetLineWidth(2)
    hsig.SetStats(0)
    hsig.Scale(10) ## Signal MC scaling
    hsig.Draw("same, hist")
    leg.SetNColumns(3)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.Draw()

    c.cd()

    pad2.cd()
    hratio.Draw("ep")
    hratio.SetTitle(";score;Data/MC")
    hratio.GetYaxis().SetNdivisions(505)
    #hratio.GetYaxis().SetTitleSize(20)
    hratio.GetYaxis().SetTitleSize(0.08)
    hratio.GetYaxis().SetTitleFont(40)
    hratio.GetYaxis().SetTitleOffset(0.4)
    hratio.GetYaxis().SetLabelFont(43)
    hratio.GetYaxis().SetLabelSize(22)

    #hratio.GetXaxis().SetTitleSize(20)
    hratio.GetXaxis().SetTitleSize(0.08)
    hratio.GetXaxis().SetTitleFont(40)
    #hratio.GetXaxis().SetTitleOffset(4.)
    hratio.GetXaxis().SetTitleOffset(1)
    hratio.GetXaxis().SetLabelFont(43)
    #hratio.GetXaxis().SetLabelSize(20)
    hratio.GetXaxis().SetLabelSize(22)

    c.SaveAs(os.path.join(rootDir, 'TMVA', 'shape', bkg_dirname, 'plots_'+ ch, "MVAdist_%s_%s.png"%(mode,ch)))
    c.SaveAs(os.path.join(rootDir, 'TMVA', 'shape', bkg_dirname, 'plots_'+ ch, "MVAdist_%s_%s.pdf"%(mode,ch)))

for ch in channels:
    f = TFile.Open("shape/%s/add_shape_%s.root"%(bkg_dirname, ch))
    hdata_all = TH1F("hdata_all", "hdata_all", 10, -1.0, 1.0)
    hsig_all = TH1F("hsig_all", "hsig_all", 10, -1.0, 1.0)
    #hmc_all = THStack("hmc_all", "")
    hmc_all = []
    hmc_all_stack = THStack("hmc_all_stack", "")
    for mc in mclist:
        mc_allmo = TH1F("allmo_%s"%mc, "allmo_%s"%mc, 10, -1.0, 1.0)
        hmc_all.append(mc_allmo)
    hmc_all0 = TH1F("hmc_all", "hmc_all", 10, -1.0, 1.0)
    leg_all = TLegend(0.22, 0.70, 0.90, 0.85)
    for i, mode in enumerate(molist):
        hs = THStack("hs", "")
        hs0 = TH1F("hs0","hs0", 10, -1.0, 1.0)
        #leg = TLegend(0.50, 0.72, 0.90, 0.85)
        leg = TLegend(0.22, 0.70, 0.90, 0.85)
        for j, mc in enumerate(mclist):
            htemp = f.Get("%s_%s"%(mode, mc))
            hs0.Add(htemp)
            hmc_all0.Add(htemp)
            htemp.SetLineColor(kBlack)
            htemp.SetFillColor(eval(colorlist[j]))
            hs.Add(htemp)
            #hmc_all.Add(htemp)
            for mchist_allmo in hmc_all:
                if (htemp.GetName()).split('_')[1] == (mchist_allmo.GetName()).split('_')[1]:
                #mc in mchist_allmo.GetName()
                    mchist_allmo.Add(htemp)
            leg.AddEntry(htemp, mc, "F")
            leg_all.AddEntry(htemp, mc, "F")
        hdata = f.Get("%s_data_obs"%mode)
        hsig = f.Get("%s_%s"%(mode,ch))
        hdata_all.Add(hdata)
        hsig_all.Add(hsig)
        leg.AddEntry(hsig, "%sX10"%ch, "l")
        leg.AddEntry(hdata, "Data", "lp")
        hratio = createRatio(hdata, hs0) # hsig for test
        hs0.Delete()
        gROOT.SetBatch(kTRUE)
        drawplot(hdata, hs, hsig, hratio, leg, mode, ch)
    for j, mchist_allmo in enumerate(hmc_all):
        mchist_allmo.SetLineColor(kBlack)
        mchist_allmo.SetFillColor(eval(colorlist[j]))
        hmc_all_stack.Add(mchist_allmo)
    leg_all.AddEntry(hsig_all, "%sX10"%ch, "l")
    leg_all.AddEntry(hdata_all, "Data", "lp")
    hratio_all = createRatio(hdata_all, hmc_all0)
    hmc_all0.Delete()
    drawplot(hdata_all, hmc_all_stack, hsig_all, hratio_all, leg_all, "all", ch)
    f.Close()
