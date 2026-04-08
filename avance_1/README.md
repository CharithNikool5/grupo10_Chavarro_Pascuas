
# Fase 1 — ETL Anime/Manga + Dashboards Streamlit

## ¿Qué se hizo?

Pipeline ETL completo que extrae datos de la API Jikan (MyAnimeList),

los transforma y carga en PostgreSQL (Supabase) con visualización

interactiva en Streamlit Cloud.

## Tecnologías

- Python 3.12

- Jikan API (MyAnimeList)

- PostgreSQL (Supabase)

- SQLAlchemy + Alembic

- Streamlit + Plotly

## Datos extraídos

- 500 registros de Anime

- 498 registros de Manga

- 500 Personajes

## Dashboards

- dashboard_app.py → Dashboard básico

- dashboard_advanced.py → Dashboard avanzado con pestañas

- dashboard_interactive.py → Dashboard interactivo con filtros

## Cómo ejecutar

```bash

cd fase1_etl

pip install -r requirements.txt

python3 -m scripts.anime_etl_db

streamlit run dashboard_interactive.py

```

