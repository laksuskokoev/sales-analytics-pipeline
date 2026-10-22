-- Net sales and contribution exclude cancelled/returned orders.
-- Contribution is net sales minus product costs only, NOT net profit.
SELECT
    COUNT(*) AS all_orders,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed_orders,
    ROUND(SUM(CASE WHEN status = 'completed' THEN quantity * unit_price ELSE 0 END), 2) AS net_sales,
    ROUND(SUM(CASE WHEN status = 'completed' THEN quantity * (unit_price - unit_cost) ELSE 0 END), 2) AS product_contribution
FROM orders JOIN products USING (product_id);
