# E-commerce Analytics — сквозной кейс аналитика

Сквозной аналитический проект на данных маркетплейса Olist (Бразилия, 2016–2018, ~96k доставленных заказов). От сырых CSV до интерактивного дашборда и бизнес-рекомендаций.

**Стек:** Supabase (PostgreSQL) · SQL · Python (pandas, scikit-learn, statsmodels) · Apache Superset
**Дашборд:** 

<p align="center">
  <img src="dashboards/screenshots/dashboard_overview.png" width="32%" alt="Overview" />
  <img src="dashboards/screenshots/dashboard_customers1.png" width="32%" alt="Customers_1" />
  <img src="dashboards/screenshots/dashboard_customers2.png" width="32%" alt="Customers_2" />
  <img src="dashboards/screenshots/dashboard_marketing.png" width="32%" alt="Marketing" />
</p>

---

## Что внутри

- **Данные:** Olist (заказы, клиенты, товары, платежи, отзывы). Маркетинговые расходы — синтетика (в Olist их нет, детали в `src/generate_marketing_data.py`).
- **Модель данных:** staging → marts (звёздная схема: `fact_orders`, `dim_customers`, `dim_products` + витрины).
- **Дашборд Superset:** 3 страницы — Overview (KPI, выручка по дням, категории), Customers (RFM, retention), Marketing (CAC, ROMI, LTV/CAC).
- **Python-анализ:** когорты, RFM-сегментация, юнит-экономика, линейная регрессия (прогноз), симуляция A/B-теста.

## Ключевые метрики

Revenue · AOV · Retention (M1–M12) · RFM · CAC · LTV · LTV/CAC · ROMI · MAPE · p-value

## Выводы

**Продажи.** Выручка ~13.5M BRL. Топ категорий: `health_beauty`, `watches_gifts`, `bed_bath_table`. Пик — ноябрь 2017 (Чёрная пятница).

**Клиенты.** 97% покупают **один раз** — особенность маркетплейса, не баг. Retention M1 = 3–5%, к M6 <1%. **Champions + Loyal (~7% клиентов) дают ~30% выручки** — закон Парето в действии.

<p align="center">
  <img src="dashboards/screenshots/cohorts.png" width="49%" alt="Retention по когортам" />
  <img src="dashboards/screenshots/rfm_segments.png" width="49%" alt="RFM-сегменты" />
</p>

**Юнит-экономика** (синтетические расходы). `direct` и `organic_search` — самые эффективные (LTV/CAC > 10). `paid_search` — на границе (LTV/CAC ≈ 3). Убыточных каналов нет.

<p align="center">
  <img src="dashboards/screenshots/unit_economics.png" width="70%" alt="Юнит-экономика" />
</p>

**Прогноз.** Линейная регрессия (тренд + сезонность через sin/cos): MAPE ~18%, R² ~0.5. Прогноз на 3 месяца — в `notebooks/05_regression.ipynb`.

**A/B-тест (симуляция).** Промо на «At Risk» (n=5000/группа): 5% → 8%, p < 0.001. **Но при типичных параметрах (AOV=150, маржа 30%, промо=20 BRL) кампания убыточна** (−186k BRL). Статистическая значимость ≠ бизнес-выгода.

## Рекомендации

1. **Масштабировать** `organic_search` и `direct` — низкий CAC, высокий LTV/CAC.
2. **Не отключать** `paid_search`, но следить за CAC — при росте цен канал уйдёт в минус.
3. **Главный рычаг — retention**, не привлечение: рост доли повторных покупок с 3% до 10% = ~2× LTV при том же CAC. Конкретно: onboarding + скидка на 2-й заказ, win-back на сегмент «At Risk».
4. **Не раскатывать** массовое промо — считать profit, а не только lift.

## Ограничения

- Нет реальных маркетинговых расходов — синтетика.
- Нет A/B в исходных данных — симуляция.
- `geolocation` не загружали (лимит Supabase 500 MB) — работаем по `customer_state`.
- Линейная регрессия не ловит аномалии, для продакшена — Prophet/ARIMA.

---

<details>
<summary>Дополнительные графики (прогноз, A/B)</summary>

<p align="center">
  <img src="dashboards/screenshots/forecast.png" width="49%" alt="Прогноз" />
  <img src="dashboards/screenshots/ab_test.png" width="49%" alt="A/B-тест" />
</p>

</details>