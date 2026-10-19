create or replace view marts.mart_unit_economics as
with customers as (
    select
        r.customer_unique_id,
        r.monetary,
        r.segment,
        cc.channel,
        date_trunc('month', fo.first_order_date)::date as cohort_month
    from marts.rfm r
    join staging.customer_channel cc
      on r.customer_unique_id = cc.customer_unique_id
    join (
        select c.customer_unique_id, min(f.order_date) as first_order_date
        from marts.fact_orders f
        join staging.customers c on f.customer_id = c.customer_id
        where f.order_status = 'delivered'
        group by c.customer_unique_id
    ) fo on r.customer_unique_id = fo.customer_unique_id
),
agg as (
    select
        channel,
        cohort_month,
        count(*)              as new_customers,
        sum(monetary)         as cohort_revenue,
        avg(monetary)         as avg_ltv
    from customers
    group by channel, cohort_month
)
select
    ms.month,
    ms.channel,
    ms.spend,
    coalesce(agg.new_customers, 0)                                    as new_customers,
    agg.cohort_revenue,
    round(ms.spend / nullif(agg.new_customers, 0), 2)                 as cac,
    round(agg.avg_ltv, 2)                                             as avg_ltv,
    round(agg.avg_ltv / nullif(ms.spend / nullif(agg.new_customers, 0), 0), 2) as ltv_cac_ratio,
    round((agg.cohort_revenue - ms.spend) / nullif(ms.spend, 0) * 100, 1) as romi_pct
from staging.marketing_spend ms
left join agg on ms.month = agg.cohort_month and ms.channel = agg.channel
order by ms.month, ms.channel;