import numpy as np
import pandas as pd

def max_drawdown(equity_curve: pd.Series) -> float:
    peak = equity_curve.cummax()
    dd = equity_curve / peak - 1.0
    return float(dd.min())

def sharpe(returns: pd.Series, rf_annual: float = 0.02) -> float:
    rf_daily = rf_annual / 252
    excess = returns - rf_daily
    return float(np.sqrt(252) * excess.mean() / excess.std()) if excess.std() != 0 else np.nan

def beta(strategy_ret: pd.Series, bench_ret: pd.Series) -> float:
    aligned = pd.concat([strategy_ret, bench_ret], axis=1).dropna()
    x = aligned.iloc[:, 1].values
    y = aligned.iloc[:, 0].values
    if x.var() == 0:
        return np.nan
    return float(np.cov(y, x)[0, 1] / x.var())