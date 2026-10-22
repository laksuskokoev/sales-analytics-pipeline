import sys
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.pipeline import build


def test_pipeline_metrics():
    d=build()
    row=d['summary'].iloc[0]
    assert row.completed_orders <= row.all_orders
    assert row.net_sales > 0
    assert 0 < row.product_contribution < row.net_sales
    assert int(d['channels'].orders.sum()) == int(row.all_orders)
    assert int(d['statuses'].orders.sum()) == int(row.all_orders)
    assert abs(d['categories'].net_sales.sum()-row.net_sales) < .01


def test_daily_totals():
    d=build()
    assert abs(d['daily'].net_sales.sum()-d['summary'].iloc[0].net_sales)<.01
    assert len(d['daily'])==90


def test_output_files():
    build()
    for file in ('summary.csv','daily.csv','categories.csv','channels.csv','statuses.csv'):
        assert (ROOT/'reports'/file).exists()
    for file in ('daily_sales.png','category_contribution.png'):
        assert (ROOT/'figures'/file).exists()
