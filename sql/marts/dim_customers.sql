create or replace view marts.dim_customers as
with customer_orders as (
    select
        customer_id,
        min(order_date)                       as first_order_date,
        max(order_date)                       as last_order_date,
        count(distinct order_id)              as total_orders,
        sum(items_total)                      as total_revenue,
        avg(items_total)                      as avg_order_value
    from marts.fact_orders
    where order_status = 'delivered'
    group by customer_id
)
select
    c.customer_id,
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,
    co.first_order_date,
    co.last_order_date,
    coalesce(co.total_orders, 0)              as total_orders,
    coalesce(co.total_revenue, 0)             as total_revenue,
    co.avg_order_value,
    current_date - co.last_order_date         as days_since_last_order
from staging.customers c
left join customer_orders co on c.customer_id = co.customer_id;