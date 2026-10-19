create or replace view marts.fact_orders as
with items as (
    select
        order_id,
        count(*)              as item_count,
        sum(price)            as items_total,
        sum(freight_value)    as freight_total
    from staging.order_items
    group by order_id
),
payments as (
    select
        order_id,
        sum(payment_value)    as payment_total
    from staging.payments
    group by order_id
),
reviews as (
    select
        order_id,
        avg(review_score)     as review_score
    from staging.reviews
    group by order_id
)
select
    o.order_id,
    o.customer_id,
    o.order_status,
    o.order_purchase_timestamp::date       as order_date,
    o.order_purchase_timestamp,
    o.order_delivered_customer_date::date  as delivered_date,
    i.item_count,
    i.items_total,
    i.freight_total,
    p.payment_total,
    r.review_score
from staging.orders o
left join items    i on o.order_id = i.order_id
left join payments p on o.order_id = p.order_id
left join reviews  r on o.order_id = r.order_id;