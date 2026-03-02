import numpy as np
import pandas as pd

def max_drawdown(equity_curve: pd.Series) -> float:
    peak = equity_curve.cummax()
    dd = equity_curve / peak - 1.0
    return float(dd.min())

def drawdown_series(equity_curve: pd.Series) -> pd.Series:
    peak = equity_curve.cummax()
    dd = equity_curve / peak - 1.0
    dd.name = "Drawdown"
    return dd

def sharpe(returns: pd.Series, rf_annual: float = 0.02) -> float:
    rf_period = rf_annual / 12  # monthly RF because our returns are monthly
    excess = returns - rf_period
    if excess.std() == 0:
        return float("nan")
    return float(np.sqrt(12) * excess.mean() / excess.std())

def rolling_sharpe(returns: pd.Series, window: int = 36, rf_annual: float = 0.02) -> pd.Series:
    rf_period = rf_annual / 12
    excess = returns - rf_period
    rs = (np.sqrt(12) * excess.rolling(window).mean() / excess.rolling(window).std())
    rs.name = f"RollingSharpe_{window}m"
    return rs

def beta(strategy_ret: pd.Series, bench_ret: pd.Series) -> float:
    aligned = pd.concat([strategy_ret, bench_ret], axis=1).dropna()
    x = aligned.iloc[:, 1].values
    y = aligned.iloc[:, 0].values
    if x.var() == 0:
        return float("nan")
    return float(np.cov(y, x)[0, 1] / x.var())

def cagr(equity_curve: pd.Series, periods_per_year: int = 12) -> float:
    equity_curve = equity_curve.dropna()
    if len(equity_curve) < 2:
        return float("nan")
    years = (len(equity_curve) - 1) / periods_per_year
    if years <= 0:
        return float("nan")
    return float((equity_curve.iloc[-1] / equity_curve.iloc[0]) ** (1 / years) - 1)

def annual_vol(returns: pd.Series, periods_per_year: int = 12) -> float:
    return float(np.sqrt(periods_per_year) * returns.std())