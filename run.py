import matplotlib.pyplot as plt
from pathlib import Path

from src.universe import get_ftse100_tickers
from src.data import download_prices
from src.backtest import backtest_topN_momentum
from src.metrics import (
    sharpe, max_drawdown, beta,
    drawdown_series, rolling_sharpe,
    cagr, annual_vol
)

BASE = Path(__file__).resolve().parent
IMG = BASE / "images"
OUT = BASE / "outputs"
IMG.mkdir(exist_ok=True)
OUT.mkdir(exist_ok=True)

def savefig(name: str):
    plt.tight_layout()
    plt.savefig(IMG / name, dpi=220, bbox_inches="tight")
    plt.close()

def main():
    tickers = get_ftse100_tickers()
    print(f"Universe size: {len(tickers)}")

    prices = download_prices(tickers, start="2015-01-01")
    print(f"Price matrix shape: {prices.shape}")

    # IMPORTANT: this returns 3 values now
    equity, strat_ret, turnover = backtest_topN_momentum(
        prices, top_n=10, cost_bps_per_turnover=10
    )

    # Benchmark
    bench_prices = download_prices(["ISF.L"], start="2015-01-01")
    bench = bench_prices["ISF.L"].resample("ME").last()
    bench_equity = (bench.pct_change().fillna(0) + 1).cumprod()
    bench_equity = bench_equity.reindex(equity.index).dropna()
    bench_ret = bench_equity.pct_change().dropna()

    # 1) Equity curve
    plt.figure()
    equity.plot(label="Top10 Momentum")
    bench_equity.plot(label="Benchmark (ISF.L)")
    plt.title("Equity Curves")
    plt.xlabel("Date")
    plt.ylabel("Growth of £1")
    plt.legend()
    savefig("equity_curves.png")

    # 2) Drawdown
    dd = drawdown_series(equity)
    plt.figure()
    dd.plot()
    plt.title("Drawdown (Strategy)")
    plt.xlabel("Date")
    plt.ylabel("Drawdown")
    savefig("drawdown.png")

    # 3) Rolling Sharpe
    rs = rolling_sharpe(strat_ret.dropna(), window=36, rf_annual=0.02)
    plt.figure()
    rs.plot()
    plt.axhline(0)
    plt.title("Rolling Sharpe (36-month)")
    plt.xlabel("Date")
    plt.ylabel("Sharpe")
    savefig("rolling_sharpe_36m.png")

    # 4) Turnover
    plt.figure()
    turnover.plot()
    plt.title("Monthly Turnover")
    plt.xlabel("Date")
    plt.ylabel("Turnover")
    savefig("turnover.png")

    # Metrics
    aligned = strat_ret.to_frame("strat").join(
        bench_ret.to_frame("bench"), how="inner"
    ).dropna()

    summary = {
        "StartDate": str(equity.index.min().date()),
        "EndDate": str(equity.index.max().date()),
        "CAGR": cagr(equity),
        "AnnualVol": annual_vol(strat_ret.dropna()),
        "Sharpe": sharpe(strat_ret.dropna()),
        "MaxDrawdown": max_drawdown(equity),
        "Beta_vs_ISF": beta(aligned["strat"], aligned["bench"]),
        "AvgMonthlyTurnover": float(turnover.dropna().mean()),
    }

    (OUT / "performance_summary.txt").write_text(
        "\n".join([f"{k}: {v}" for k, v in summary.items()])
    )

    print("✅ Saved charts to:", IMG)
    print("✅ Updated summary to:", OUT / "performance_summary.txt")

if __name__ == "__main__":
    main()