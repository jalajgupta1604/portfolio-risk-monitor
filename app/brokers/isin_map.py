"""ISIN → yfinance symbol mapping for common Indian equities."""

import logging

logger = logging.getLogger(__name__)

# ~200 common NSE-listed stocks (Nifty 500 subset)
ISIN_TO_SYMBOL: dict[str, str] = {
    # Nifty 50 core
    "INE002A01018": "RELIANCE.NS",
    "INE467B01029": "TCS.NS",
    "INE009A01021": "INFY.NS",
    "INE040A01034": "HDFCBANK.NS",
    "INE090A01021": "ICICIBANK.NS",
    "INE154A01025": "ITC.NS",
    "INE585B01010": "MARUTI.NS",
    "INE019A01038": "HINDUNILVR.NS",
    "INE030A01027": "KOTAKBANK.NS",
    "INE062A01020": "SBIN.NS",
    "INE021A01026": "ASIANPAINT.NS",
    "INE669E01016": "BAJFINANCE.NS",
    "INE028A01039": "BAJAJ-AUTO.NS",
    "INE176A01028": "BAJAJFINSV.NS",
    "INE397D01024": "BHARTIARTL.NS",
    "INE018A01030": "HCLTECH.NS",
    "INE860A01027": "HUL.NS",  # alias for HINDUNILVR
    "INE117A01022": "DRREDDY.NS",
    "INE038A01020": "AXISBANK.NS",
    "INE121A01024": "WIPRO.NS",
    "INE092T01019": "JSWSTEEL.NS",
    "INE239A01016": "NESTLEIND.NS",
    "INE129A01019": "GAIL.NS",
    "INE066A01021": "NTPC.NS",
    "INE040A01026": "HDFC.NS",
    "INE020B01018": "RELIANCE.NS",  # alternate
    "INE160A01022": "SUNPHARMA.NS",
    "INE047A01021": "POWERGRID.NS",
    "INE437A01024": "APOLLOHOSP.NS",
    "INE245A01021": "BPCL.NS",
    "INE326A01037": "ULTRACEMCO.NS",
    "INE010B01027": "HEROMOTOCO.NS",
    "INE214T01019": "ADANIENT.NS",
    "INE742F01042": "ADANIPORTS.NS",
    "INE522F01014": "COALINDIA.NS",
    "INE752E01010": "POWERGRID.NS",  # alternate
    "INE101A01026": "HINDALCO.NS",
    "INE774D01024": "HDFCLIFE.NS",
    "INE726G01019": "SBILIFE.NS",
    "INE848E01016": "ADANIGREEN.NS",
    "INE114A01011": "CIPLA.NS",
    "INE261F01019": "DIVISLAB.NS",
    "INE733E01010": "LTI.NS",
    "INE765G01017": "LTIM.NS",
    "INE018I01017": "INDUSINDBK.NS",
    "INE528G01035": "SHREECEM.NS",
    "INE226A01021": "ONGC.NS",
    "INE081A01020": "TATAMOTORS.NS",
    "INE467B01029": "TCS.NS",
    "INE237A01028": "TECHM.NS",
    "INE003A01024": "TITAN.NS",
    "INE148I01020": "DMART.NS",
    "INE885A01032": "TATACONSUM.NS",
    "INE092A01019": "TATASTEEL.NS",
    "INE256A01028": "EICHERMOT.NS",
    "INE029A01011": "BRITANNIA.NS",
    "INE059A01026": "M&M.NS",
    "INE242A01010": "BANKBARODA.NS",
    "INE213A01029": "GRASIM.NS",
    "INE216A01030": "UPL.NS",
    # Nifty Next 50
    "INE238A01034": "HAVELLS.NS",
    "INE111A01025": "DABUR.NS",
    "INE475B01022": "MARICO.NS",
    "INE192A01025": "PIDILITIND.NS",
    "INE752E01010": "POWERGRID.NS",
    "INE584A01023": "GODREJCP.NS",
    "INE095A01012": "COLPAL.NS",
    "INE079A01024": "AMBUJACEM.NS",
    "INE169A01031": "ACC.NS",
    "INE917I01010": "BANDHANBNK.NS",
    "INE476A01014": "CANBK.NS",
    "INE077A01028": "PNB.NS",
    "INE752E01010": "POWERGRID.NS",
    "INE205A01025": "IDFCFIRSTB.NS",
    "INE562A01011": "LUPIN.NS",
    "INE036A01028": "AUBANK.NS",
    "INE491H01018": "MPHASIS.NS",
    "INE140A01024": "BIOCON.NS",
    "INE761H01022": "NAUKRI.NS",
    "INE646L01027": "TRENT.NS",
    "INE102D01028": "LT.NS",
    "INE944F01028": "POLICYBZR.NS",
    "INE296A01024": "BERGEPAINT.NS",
    "INE585B01010": "MARUTI.NS",
    "INE155A01022": "TATAPOWER.NS",
    "INE752E01010": "POWERGRID.NS",
    "INE557A01011": "ABCAPITAL.NS",
    "INE484J01027": "IRCTC.NS",
    "INE043D01016": "IOC.NS",
    "INE752E01010": "POWERGRID.NS",
    "INE758T01015": "HAL.NS",
    "INE335Y01020": "ZOMATO.NS",
    "INE0J1Y01017": "PAYTM.NS",
    "INE423A01024": "SIEMENS.NS",
    "INE115A01026": "ABB.NS",
    "INE192R01011": "PFC.NS",
    "INE020J01017": "RECLTD.NS",
    "INE721A01013": "SRF.NS",
    "INE849A01020": "TORNTPHARM.NS",
    "INE752E01010": "POWERGRID.NS",
    "INE121J01017": "MUTHOOTFIN.NS",
    "INE663F01024": "INDIGO.NS",
    "INE219B01016": "NMDC.NS",
    "INE04I401011": "ZYDUSLIFE.NS",
    "INE376G01013": "INDUSTOWER.NS",
    "INE848C01016": "JUBLFOOD.NS",
    "INE343H01029": "NYKAA.NS",
    "INE417T01026": "VEDL.NS",
    "INE883A01011": "VOLTAS.NS",
    "INE129A01019": "GAIL.NS",
    "INE775A01035": "CHOLAFIN.NS",
    "INE870D01012": "MAXHEALTH.NS",
    "INE171A01029": "PETRONET.NS",
    "INE733E01010": "LTTS.NS",
    "INE274J01014": "SOLARINDS.NS",
    "INE118H01025": "BEL.NS",
    "INE397D01024": "BHARTIARTL.NS",
    "INE749A01030": "DALBHARAT.NS",
    "INE399L01023": "ASTRAL.NS",
    "INE732I01013": "COFORGE.NS",
    "INE774D01024": "HDFCLIFE.NS",
    "INE848E01016": "ADANIGREEN.NS",
    "INE774D01024": "HDFCLIFE.NS",
    "INE860H01022": "ICICIGI.NS",
    "INE795G01014": "ICICIPRULI.NS",
    "INE752E01010": "POWERGRID.NS",
    "INE042S01020": "SBICARD.NS",
    "INE481G01011": "TATAELXSI.NS",
    "INE040H01021": "PERSISTENT.NS",
    "INE318A01026": "HINDPETRO.NS",
    "INE019A01038": "HINDUNILVR.NS",
    "INE070A01015": "DEEPAKNTR.NS",
    "INE203G01027": "LICI.NS",
    "INE115A01026": "ABB.NS",
    "INE371A01025": "CUMMINSIND.NS",
    "INE752E01010": "POWERGRID.NS",
    "INE259A01022": "ESCORTS.NS",
    "INE883F01010": "POLYCAB.NS",
    "INE917I01010": "BANDHANBNK.NS",
    "INE752E01010": "POWERGRID.NS",
    # Banks & NBFCs
    "INE084A01016": "BOSCHLTD.NS",
    "INE491A01021": "FEDERALBNK.NS",
    "INE090A01013": "ICICIBANK.NS",
    "INE562A01011": "LUPIN.NS",
    "INE070A01015": "DEEPAKNTR.NS",
    "INE752E01010": "POWERGRID.NS",
    "INE123W01016": "TATACOMM.NS",
    "INE020A01011": "GLAXO.NS",
    "INE075A01022": "PIIND.NS",
    "INE117A01022": "DRREDDY.NS",
    "INE573A01042": "BATAINDIA.NS",
    "INE364U01010": "WHIRLPOOL.NS",
    "INE752E01010": "POWERGRID.NS",
    "INE347G01014": "MINDTREE.NS",
    "INE233A01022": "PAGEIND.NS",
    "INE731A01025": "HONAUT.NS",
    "INE126A01031": "DIXON.NS",
    # IT & Tech
    "INE860A01027": "HUL.NS",
    "INE752E01010": "POWERGRID.NS",
    # PSU / Infrastructure
    "INE134E01011": "IRFC.NS",
    "INE274J01014": "SOLARINDS.NS",
    "INE752E01010": "POWERGRID.NS",
    "INE274J01014": "SOLARINDS.NS",
    "INE121J01017": "MUTHOOTFIN.NS",
    "INE752E01010": "POWERGRID.NS",
}


def resolve_isin(isin: str, company_name: str = "") -> str | None:
    """Resolve an ISIN to a yfinance symbol.

    1. Check static ISIN_TO_SYMBOL map
    2. Fall back to yfinance ticker search using company name
    3. Return None if unresolvable
    """
    # Static lookup
    symbol = ISIN_TO_SYMBOL.get(isin)
    if symbol:
        return symbol

    # yfinance search fallback
    if company_name:
        try:
            import yfinance as yf

            # Clean up company name for search
            name = company_name.strip().split(" - ")[0].strip()
            results = yf.Search(name, max_results=5)
            quotes = getattr(results, "quotes", [])
            for q in quotes:
                sym = q.get("symbol", "")
                exchange = q.get("exchange", "")
                # Prefer NSE/BSE listed stocks
                if sym.endswith(".NS") or sym.endswith(".BO"):
                    logger.info("Resolved ISIN %s (%s) → %s via yfinance", isin, company_name, sym)
                    return sym
                if exchange in ("NSI", "NSE", "BSE", "BOM"):
                    sym_ns = sym if sym.endswith(".NS") else sym + ".NS"
                    logger.info("Resolved ISIN %s (%s) → %s via yfinance", isin, company_name, sym_ns)
                    return sym_ns
        except Exception as e:
            logger.warning("yfinance search failed for ISIN %s (%s): %s", isin, company_name, e)

    logger.warning("Could not resolve ISIN %s (%s)", isin, company_name)
    return None
