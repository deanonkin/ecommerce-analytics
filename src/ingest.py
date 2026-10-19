"""
Загрузка сырых CSV Olist в Supabase (схема staging).
Запуск: python src/ingest.py
"""
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# 1. Читаем пароли из .env
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# 2. Собираем строку подключения
connection_url = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(connection_url)

# 3. Список файлов: имя CSV -> имя таблицы в staging
FILES = {
    "olist_orders_dataset.csv": "orders",
    "olist_order_items_dataset.csv": "order_items",
    "olist_customers_dataset.csv": "customers",
    "olist_products_dataset.csv": "products",
    "olist_sellers_dataset.csv": "sellers",
    "olist_order_payments_dataset.csv": "payments",
    "olist_order_reviews_dataset.csv": "reviews",
    "product_category_name_translation.csv": "category_translation",
}

RAW_DIR = Path("data/raw")

# 4. Загружаем каждый файл
for csv_name, table_name in FILES.items():
    path = RAW_DIR / csv_name
    if not path.exists():
        print(f"⚠️  Пропуск: {path} не найден")
        continue

    print(f"→ Читаю {csv_name} ...")
    df = pd.read_csv(path)

    print(f"   Строк: {len(df)}, колонок: {len(df.columns)}")
    print(f"   Гружу в staging.{table_name} ...")

    df.to_sql(
        name=table_name,
        con=engine,
        schema="staging",
        if_exists="replace",   # на первом запуске создаст, при повторе — перезапишет
        index=False,
        chunksize=5000,
        method="multi",
    )

    print(f"   ✅ Готово\n")

print("Все файлы загружены.")