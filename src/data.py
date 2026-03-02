import yfinance as yf
import pandas as pd

def download_prices(tickers: list[str], start: str = "2015-01-01") -> pd.DataFrame:
    df = yf.download(
        tickers,
        start=start,
        auto_adjust=True,
        group_by="ticker",
        progress=False,
        threads=True,
    )

    # Normalize output: matrix of Close prices with columns = tickers
    if isinstance(df.columns, pd.MultiIndex):
        closes = df.xs("Close", axis=1, level=1)
    else:
        closes = df[["Close"]].rename(columns={"Close": tickers[0]})

    closes = closes.dropna(how="all")
    return closes