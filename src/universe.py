def get_ftse100_tickers() -> list[str]:
    """
    Static FTSE 100 tickers (Yahoo Finance format).
    """

    tickers = [
        "AZN.L","HSBA.L","SHEL.L","BP.L","ULVR.L","GSK.L","RIO.L","DGE.L",
        "REL.L","BATS.L","NG.L","LSEG.L","BARC.L","PRU.L","LLOY.L","CRH.L",
        "VOD.L","TSCO.L","GLEN.L","BT-A.L","EXPN.L","FERG.L","IMB.L",
        "BA.L","SMIN.L","STAN.L","AAL.L","ABF.L","MNG.L","SBRY.L",
        "HLMA.L","KGF.L","SVT.L","UU.L","AUTO.L","SPX.L","RKT.L",
        "JD.L","RR.L","ITRK.L","WEIR.L","MRO.L","CNA.L","TW.L",
        "III.L","ENT.L","BEZ.L","HIK.L","PSN.L","PSON.L",
        "FLTR.L","SGE.L","CPG.L","SDR.L","WPP.L","ITV.L"
    ]

    return tickers