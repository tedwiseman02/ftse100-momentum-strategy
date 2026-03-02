import pandas as pd

def momentum_12_1(prices: pd.DataFrame) -> pd.DataFrame:
    monthly = prices.resample("ME").last()
    mom = monthly.shift(1) / monthly.shift(12) - 1
    return mom.dropna(how="all")

def backtest_topN_momentum(
    prices: pd.DataFrame,
    top_n: int = 10,
    cost_bps_per_turnover: float = 10.0,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    Returns:
      equity: monthly equity curve
      monthly_returns: strategy monthly returns (net of costs)
      turnover: monthly turnover (0..1 approx)
    """
    monthly_prices = prices.resample("ME").last()
    mom = momentum_12_1(prices)

    dates = mom.index.intersection(monthly_prices.index)
    mom = mom.loc[dates]
    monthly_prices = monthly_prices.loc[dates]

    equity = pd.Series(index=dates, dtype=float)
    monthly_ret = pd.Series(index=dates, dtype=float)
    turnover_s = pd.Series(index=dates, dtype=float)

    prev_weights = None
    equity.iloc[0] = 1.0
    monthly_ret.iloc[0] = 0.0
    turnover_s.iloc[0] = 0.0

    for i in range(1, len(dates)):
        dt_prev = dates[i - 1]
        dt = dates[i]

        scores = mom.loc[dt_prev].dropna()
        picks = scores.sort_values(ascending=False).head(top_n).index.tolist()

        weights = pd.Series(0.0, index=monthly_prices.columns)
        if len(picks) > 0:
            weights.loc[picks] = 1.0 / len(picks)

        r = (monthly_prices.loc[dt] / monthly_prices.loc[dt_prev] - 1.0).fillna(0.0)
        gross = float((weights * r).sum())

        if prev_weights is None:
            turnover = float(weights.abs().sum())  # entering
        else:
            turnover = float((weights - prev_weights).abs().sum() / 2.0)

        cost = (cost_bps_per_turnover / 10000.0) * turnover
        net = gross - cost

        monthly_ret.iloc[i] = net
        turnover_s.iloc[i] = turnover
        equity.iloc[i] = equity.iloc[i - 1] * (1.0 + net)

        prev_weights = weights

    equity.name = f"Top{top_n}_Momentum_Equity"
    monthly_ret.name = "StrategyMonthlyReturn"
    turnover_s.name = "Turnover"
    return equity, monthly_ret, turnover_s