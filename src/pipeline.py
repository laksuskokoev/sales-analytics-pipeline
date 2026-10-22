"""Load CSV -> SQLite -> SQL aggregation -> CSV reports & plots."""
from pathlib import Path
import sqlite3
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA, REPORTS, FIGURES, SQL = [ROOT / p for p in ('data','reports','figures','sql')]


def build():
    products = pd.read_csv(DATA / 'products_synthetic.csv')
    orders = pd.read_csv(DATA / 'orders_synthetic.csv')
    assert orders.order_id.is_unique, 'Order IDs must be unique'
    assert orders.product_id.isin(products.product_id).all(), 'Unknown product ID'
    assert (orders.quantity > 0).all(), 'Nonpositive quantity'
    assert (products.unit_price >= products.unit_cost).all(), 'Unexpected cost > price'
    assert orders.status.isin(['completed','cancelled','returned']).all()
    REPORTS.mkdir(exist_ok=True)
    FIGURES.mkdir(exist_ok=True)
    # File-backed database is reproducible; replace tables on each run.
    db = ROOT / 'sales.sqlite'
    with sqlite3.connect(db) as con:
        orders.to_sql('orders', con, if_exists='replace', index=False)
        products.to_sql('products', con, if_exists='replace', index=False)
        summary = pd.read_sql_query((SQL/'metrics.sql').read_text(encoding='utf-8'), con)
        daily = pd.read_sql_query('''SELECT order_date,
          ROUND(SUM(CASE WHEN status='completed' THEN quantity*unit_price ELSE 0 END),2) net_sales,
          SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) completed_orders
          FROM orders JOIN products USING(product_id) GROUP BY order_date ORDER BY order_date''', con)
        categories = pd.read_sql_query('''SELECT category,
          ROUND(SUM(CASE WHEN status='completed' THEN quantity*unit_price ELSE 0 END),2) net_sales,
          ROUND(SUM(CASE WHEN status='completed' THEN quantity*(unit_price-unit_cost) ELSE 0 END),2) product_contribution
          FROM orders JOIN products USING(product_id) GROUP BY category ORDER BY net_sales DESC''', con)
        channels = pd.read_sql_query('''SELECT channel, COUNT(*) orders,
          SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) completed_orders,
          ROUND(100.0*SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END)/COUNT(*),2) completion_rate_pct,
          ROUND(SUM(CASE WHEN status='completed' THEN quantity*unit_price ELSE 0 END),2) net_sales
          FROM orders JOIN products USING(product_id) GROUP BY channel ORDER BY net_sales DESC''', con)
        statuses = pd.read_sql_query('SELECT status, COUNT(*) orders FROM orders GROUP BY status', con)
    for name, df in [('summary',summary),('daily',daily),('categories',categories),('channels',channels),('statuses',statuses)]:
        df.to_csv(REPORTS/f'{name}.csv', index=False)
    fig,ax=plt.subplots(figsize=(10,4))
    ax.plot(pd.to_datetime(daily.order_date), daily.net_sales)
    ax.set(title='Daily net sales (synthetic data)', ylabel='RUB', xlabel='Date')
    fig.autofmt_xdate();fig.tight_layout();fig.savefig(FIGURES/'daily_sales.png',dpi=145);plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,4))
    ax.bar(categories.category, categories.product_contribution)
    ax.set(title='Product contribution by category',ylabel='RUB (excludes fixed costs)')
    fig.tight_layout();fig.savefig(FIGURES/'category_contribution.png',dpi=145);plt.close(fig)
    print('Success: reports and figures generated.')
    print(summary.to_string(index=False))
    return {'summary':summary,'daily':daily,'categories':categories,'channels':channels,'statuses':statuses}

if __name__ == '__main__':
    build()
