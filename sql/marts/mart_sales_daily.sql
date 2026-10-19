create or replace view marts.mart_sales_daily as
select
    order_date,
    count(distinct order_id)         as orders,
    count(distinct customer_id)      as customers,
    sum(items_total)                 as revenue,
    sum(freight_total)               as freight,
    round(avg(items_total)::numeric, 2) as aov,
    round(avg(review_score)::numeric, 2) as avg_review
from marts.fact_orders
where order_status = 'delivered'
group by order_date
order by order_date;