import sys, os
from ROOT import *

#channels = ["TTZct", "TTZut", "STZct", "STZut"]
channels = ["TTZct", "STZct"]
molist = ["ElElEl", "MuElEl", "ElMuMu", "MuMuMu"]
mclist = ["DYJets", "SingleTop", "SingleTopV", "ZZ", "WZ", "WW", "TTH", "TTV", "TTJets"]
colorlist = ["kOrange+1", "kMagenta+1", "kMagenta+2", "kCyan-1", "kAzure+6", "kBlue-6", "kRed+3", "kRed+4", "kRed"]
syslist = ["jer", "jes", "PU", "ElSF", "MuID", "MuISO", "MuR", "MuF", "BtagJES", "BtagLF", "BtagHF", "BtagHFStats1", "BtagHFStats2", "BtagLFStats1", "BtagLFStats2", "BtagCQErr1", "BtagCQErr2"]
bkg_dirname = "bugfix_bkg1_half"

rootDir = '%s/src/TZWi/TopAnalysis/test/fcncTriLepton/' % os.environ["CMSSW_BASE"]
for ch in channels:
    if not os.path.exists( os.path.join(rootDir, 'TMVA', 'shape', bkg_dirname, 'plots_'+ ch) ):
        os.makedirs(os.path.join(rootDir, 'TMVA', 'shape', bkg_dirname, 'plots_'+ ch))
#if not os.path.exists( os.path.join(rootDir, 'TMVA', 'shape', 'plots_TTZut') ):
#    os.makedirs(os.path.join(rootDir, 'TMVA', 'shape', 'plots_TTZut'))

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
    #pad2.SetBottomMargin(0.2)
    pad2.SetBottomMargin(0.35)
    pad2.SetGridx()
    pad2.SetGridy()
    pad2.Draw()

    return c, pad1, pad2

def createRatio(hcent, hsys, color):
    hratio = hcent.Clone("hratio")
    hratio.SetLineColor(eval(color))
    hratio.SetMaximum(1.5)
    hratio.SetMinimum(0.5)
    hratio.Sumw2()
    hratio.SetStats(0)
    hratio.Divide(hsys)
    hratio.SetMarkerStyle(21)
    hratio.SetMarkerColor(eval(color))
    
    return hratio

def drawplot(hcent, hup, hdown, hratioup, hratiodown, legend, mode, channel, syst, flag):
#def drawplot (hdata, hbkg, hsig, channel):

    c, pad1, pad2 = createCanvasPads()

    pad1.cd()
    hdown.SetTitle("%s_MVAscore;;Events"%syst)
    hdown.SetLineColor(kRed)
    hdown.SetStats(0)
    hdown.GetXaxis().SetLabelOffset(999)
    hdown.GetXaxis().SetLabelSize(0)
    hdown.GetYaxis().SetTitleOffset(1)
    hdown.GetYaxis().SetLabelSize(0.04)
    hdown.Draw("hist")
    hup.SetLineColor(kBlue)
    hup.Draw("same, hist")
    hcent.SetLineColor(kBlack)
    hcent.Draw("same, hist")
    leg.SetNColumns(3)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.Draw()

    c.cd()

    pad2.cd()
    hratioup.Draw("ep")
    hratioup.SetTitle(";score;central/syst")
    #hratioup.GetYaxis().SetTitle("central/syst")
    hratioup.GetYaxis().SetNdivisions(505)
    #hratioup.GetYaxis().SetTitleSize(20)
    hratioup.GetYaxis().SetTitleSize(0.08)
    hratioup.GetYaxis().SetTitleFont(40)
    hratioup.GetYaxis().SetTitleOffset(1.55)
    hratioup.GetYaxis().SetLabelFont(43)
    hratioup.GetYaxis().SetLabelSize(22)

    #hratioup.GetXaxis().SetTitleSize(20)
    hratioup.GetXaxis().SetTitleSize(0.08)
    hratioup.GetXaxis().SetTitleFont(40)
    #hratioup.GetXaxis().SetTitleOffset(4.)
    hratioup.GetXaxis().SetTitleOffset(1)
    hratioup.GetXaxis().SetLabelFont(43)
    #hratioup.GetXaxis().SetLabelSize(15)
    hratioup.GetXaxis().SetLabelSize(22)

    hratiodown.Draw("ep, same")

    #c.SaveAs(os.path.join(rootDir, 'TMVA', 'shape', 'plots_'+ channel, "MVAdist_%s_%s.png"%(syst,flag)))
    c.SaveAs(os.path.join(rootDir, 'TMVA', 'shape', bkg_dirname, 'plots_'+ channel, "MVAdist_%s_%s.pdf"%(syst,flag)))
    c.Delete()


for ch in channels:
    f = TFile.Open("shape/%s/shape_%s.root"%(bkg_dirname, ch))
    hscent = TH1F("hscent","hscent", 10, -1.0, 1.0)
    hscentsig = TH1F("hscentsig","hscentsig", 10, -1.0, 1.0)
    for i, mode in enumerate(molist):
        htcentsig = f.Get("%s_%s"%(mode, ch))
        hscentsig.Add(htcentsig)
        for j, mc in enumerate(mclist):
            htcent = f.Get("%s_%s"%(mode, mc))
            hscent.Add(htcent)
    for syst in syslist:
        #leg = TLegend(0.60, 0.72, 0.80, 0.85)
        leg = TLegend(0.55, 0.72, 0.80, 0.88)
        hsup = TH1F("hsup","hsup", 10, -1.0, 1.0)
        hsdown = TH1F("hsdown","hsdown", 10, -1.0, 1.0)
        hsupsig = TH1F("hsupsig","hsupsig", 10, -1.0, 1.0)
        hsdownsig = TH1F("hsdownsig","hsdownsig", 10, -1.0, 1.0)
        for mo1 in molist:
            htupsig = f.Get("%s_%s_%sUp"%(mo1, ch, syst))
            htdownsig = f.Get("%s_%s_%sDown"%(mo1, ch, syst))
            hsupsig.Add(htupsig)
            hsdownsig.Add(htdownsig)
            for mc1 in mclist:
                htup = f.Get("%s_%s_%sUp"%(mo1, mc1, syst))
                htdown = f.Get("%s_%s_%sDown"%(mo1, mc1, syst))
                hsup.Add(htup)
                hsdown.Add(htdown)

        leg.AddEntry(hscent, "central", "l")
        leg.AddEntry(hsup, "Up", "l")
        leg.AddEntry(hsdown, "Down", "l")
        hratioup = createRatio(hscent, hsup, "kRed") # hsig for test
        hratiodown = createRatio(hscent, hsdown, "kBlue") # hsig for test
        gROOT.SetBatch(kTRUE)
        drawplot(hscent, hsup, hsdown, hratioup, hratiodown, leg, mode, ch, syst, "background")
        hratioup.Delete()
        hratiodown.Delete()
        hratioupsig = createRatio(hscentsig, hsupsig, "kRed") # hsig for test
        hratiodownsig = createRatio(hscentsig, hsdownsig, "kBlue") # hsig for test
        drawplot(hscentsig, hsupsig, hsdownsig, hratioupsig, hratiodownsig, leg, mode, ch, syst, "signal")
        hratioupsig.Delete()
        hratiodownsig.Delete()
        leg.Delete()
        hsup.Delete()
        hsdown.Delete()
        hsupsig.Delete()
        hsdownsig.Delete()
    hscentsig.Delete()
    hscent.Delete()
    f.Close()
