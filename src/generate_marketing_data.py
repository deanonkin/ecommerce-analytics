"""
Генерация синтетических маркетинговых данных для unit economics.
Запуск: python src/generate_marketing_data.py
"""
import os
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# фиксируем seed — чтобы результат был воспроизводимым
np.random.seed(42)

# ============================================================
# 1. Каналы привлечения для каждого клиента
# ============================================================
customers = pd.read_sql("select customer_unique_id from marts.rfm", engine)

channels = ["organic_search", "paid_search", "social", "direct", "email", "referral"]
weights  = [0.30,             0.20,          0.15,     0.15,     0.10,    0.10]

customers["channel"] = np.random.choice(channels, size=len(customers), p=weights)

# ============================================================
# 2. Новые клиенты по каналам и месяцам
# ============================================================
first_orders = pd.read_sql("""
    select c.customer_unique_id, min(f.order_date) as first_order_date
    from marts.fact_orders f
    join staging.customers c on f.customer_id = c.customer_id
    where f.order_status = 'delivered'
    group by c.customer_unique_id
""", engine)

first_orders["cohort_month"] = (
    pd.to_datetime(first_orders["first_order_date"])
      .dt.to_period("M")
      .dt.to_timestamp()
)

new_cust = (
    first_orders
    .merge(customers, on="customer_unique_id")
    .groupby(["cohort_month", "channel"])
    .size()
    .reset_index(name="new_customers")
)

# ============================================================
# 3. Расход = new_customers × target_CAC × шум
# ============================================================
target_cac = {
    "organic_search": 15,
    "paid_search":    50,
    "social":         40,
    "direct":         10,
    "email":          20,
    "referral":       25,
}

new_cust["target_cac"] = new_cust["channel"].map(target_cac)
new_cust["noise"]      = np.random.uniform(0.8, 1.2, size=len(new_cust))
new_cust["spend"]      = (new_cust["new_customers"] * new_cust["target_cac"] * new_cust["noise"]).round(2)

marketing_spend = (
    new_cust[["cohort_month", "channel", "spend"]]
    .rename(columns={"cohort_month": "month"})
)

# ============================================================
# 4. Записываем в staging
# ============================================================
with engine.begin() as conn:
    customers[["customer_unique_id", "channel"]].to_sql(
        "customer_channel", conn, schema="staging", index=False, if_exists="replace"
    )
    marketing_spend.to_sql(
        "marketing_spend", conn, schema="staging", index=False, if_exists="replace"
    )

print(f"customer_channel: {len(customers)} строк")
print(f"marketing_spend:  {len(marketing_spend)} строк")
print(marketing_spend.head())