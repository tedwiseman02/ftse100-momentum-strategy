import pandas as pd

def momentum_12_1(prices: pd.DataFrame) -> pd.DataFrame:
    # Monthly (month-end) prices
    monthly = prices.resample("ME").last()
    # 12-1 momentum: 12-month return skipping the most recent month
    mom = monthly.shift(1) / monthly.shift(12) - 1
    return mom.dropna(how="all")

def backtest_topN_momentum(
    prices: pd.DataFrame,
    top_n: int = 10,
    cost_bps_per_turnover: float = 10.0,
) -> pd.Series:
    monthly_prices = prices.resample("ME").last()
    mom = momentum_12_1(prices)

    # Align dates
    dates = mom.index.intersection(monthly_prices.index)
    mom = mom.loc[dates]
    monthly_prices = monthly_prices.loc[dates]

    portfolio = pd.Series(index=dates, dtype=float)
    prev_weights = None

    for i in range(1, len(dates)):
        dt_prev = dates[i - 1]
        dt = dates[i]

        scores = mom.loc[dt_prev].dropna()
        picks = scores.sort_values(ascending=False).head(top_n).index.tolist()

        if len(picks) == 0:
            portfolio.iloc[i] = 1.0
            continue

        weights = pd.Series(0.0, index=monthly_prices.columns)
        weights.loc[picks] = 1.0 / len(picks)

        # Monthly returns for each asset
        r = (monthly_prices.loc[dt] / monthly_prices.loc[dt_prev] - 1.0).fillna(0.0)
        gross = float((weights * r).sum())

        # Turnover for simple transaction cost estimate
        if prev_weights is None:
            turnover = float(weights.abs().sum())
        else:
            turnover = float((weights - prev_weights).abs().sum() / 2.0)

        cost = (cost_bps_per_turnover / 10000.0) * turnover
        net = gross - cost

        portfolio.iloc[i] = 1.0 + net
        prev_weights = weights

    equity = portfolio.fillna(1.0).cumprod()
    equity.name = f"Top{top_n}_Momentum_Equity"
    return equity