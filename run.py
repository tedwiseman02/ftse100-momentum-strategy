import matplotlib.pyplot as plt
from pathlib import Path

from src.universe import get_ftse100_tickers
from src.data import download_prices
from src.backtest import backtest_topN_momentum
from src.metrics import sharpe, max_drawdown, beta


BASE = Path(__file__).resolve().parent
IMG = BASE / "images"
OUT = BASE / "outputs"
IMG.mkdir(exist_ok=True)
OUT.mkdir(exist_ok=True)

def savefig(name: str):
    plt.tight_layout()
    plt.savefig(IMG / name, dpi=200, bbox_inches="tight")
    plt.close()

def main():
    tickers = get_ftse100_tickers()
    print(f"Universe size: {len(tickers)}")

    prices = download_prices(tickers, start="2015-01-01")
    print(f"Price matrix shape: {prices.shape}")

    equity = backtest_topN_momentum(prices, top_n=10, cost_bps_per_turnover=10)

    # Benchmark: iShares Core FTSE 100 UCITS ETF (London)
    bench_prices = download_prices(["ISF.L"], start="2015-01-01")
    bench = bench_prices["ISF.L"].resample("ME").last()
    bench_equity = (bench.pct_change().fillna(0) + 1).cumprod()

    plt.figure()
    equity.plot(label="Top10 Momentum")
    bench_equity.reindex(equity.index).plot(label="Benchmark (ISF.L)")
    plt.title("FTSE 100 Momentum Strategy vs Benchmark")
    plt.xlabel("Date")
    plt.ylabel("Growth of £1")
    plt.legend()
    savefig("equity_curves.png")

    strat_ret = equity.pct_change().dropna()
    bench_ret = bench_equity.reindex(equity.index).pct_change().dropna()

    summary = {
        "Sharpe": sharpe(strat_ret),
        "MaxDrawdown": max_drawdown(equity),
        "Beta": beta(strat_ret, bench_ret),
        "StartDate": str(equity.index.min().date()),
        "EndDate": str(equity.index.max().date()),
    }

    (OUT / "performance_summary.txt").write_text(
        "\n".join([f"{k}: {v}" for k, v in summary.items()])
    )

    print("✅ Saved chart to:", IMG / "equity_curves.png")
    print("✅ Saved metrics to:", OUT / "performance_summary.txt")

if __name__ == "__main__":
    main()