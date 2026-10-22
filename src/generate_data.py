"""Reproducible synthetic e-commerce order and product data; no real customer data."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'

def generate(seed=2026, n=6000):
    rng = np.random.default_rng(seed)
    products = pd.DataFrame({
        'product_id': range(1, 13),
        'category': ['Electronics']*3+['Home']*3+['Beauty']*3+['Sports']*3,
        'unit_price': [8500, 12500, 2900, 1500, 3700, 6200, 700, 1900, 2400, 4100, 5500, 2200],
        'unit_cost': [6500, 9400, 1950, 800, 2300, 4000, 260, 780, 1100, 2450, 3400, 1050],
    })
    dates = pd.date_range('2026-01-01', '2026-03-31', freq='D')
    order_dates = rng.choice(dates, n, replace=True)
    ids = rng.choice(products.product_id.to_numpy(), n, replace=True)
    quantities = rng.choice([1,2,3], n, p=[.74,.21,.05])
    statuses = rng.choice(['completed','returned','cancelled'], n, p=[.86,.075,.065])
    channels = rng.choice(['organic','paid_search','social','referral'], n, p=[.38,.30,.20,.12])
    orders = pd.DataFrame({'order_id':range(1,n+1),'order_date': pd.to_datetime(order_dates).strftime('%Y-%m-%d'),
      'product_id': ids,'quantity':quantities,'channel':channels,'status': statuses})
    DATA.mkdir(exist_ok=True,parents=True)
    orders.to_csv(DATA/'orders_synthetic.csv', index=False)
    products.to_csv(DATA/'products_synthetic.csv', index=False)
    return orders, products

if __name__ == '__main__':
    orders,products = generate()
    print(f'Generated {len(orders)} orders and {len(products)} products')
