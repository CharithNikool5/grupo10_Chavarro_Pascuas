#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
sys.path.insert(0, '.')

from scripts.database import SessionLocal
from scripts.models import Anime, Manga, Personaje, MetricasETL
from sqlalchemy import func

# ─── CONFIGURACIÓN ────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Anime & Manga ETL",
    page_icon="🎌",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎌 Dashboard Anime & Manga — Jikan API ETL")
st.markdown("---")

db = SessionLocal()

try:
    # ─── CARGAR DATOS ─────────────────────────────────────────
    anime      = pd.read_sql(db.query(Anime).statement,      db.bind)
    manga      = pd.read_sql(db.query(Manga).statement,      db.bind)
    personajes = pd.read_sql(db.query(Personaje).statement,  db.bind)

    # ─── SIDEBAR ──────────────────────────────────────────────
    st.sidebar.title("🔧 Filtros")

    score_min = st.sidebar.slider(
        "⭐ Score mínimo:", 
        min_value=0.0, max_value=10.0, value=7.0, step=0.1
    )

    tipos_anime = st.sidebar.multiselect(
        "🎬 Tipo de Anime:",
        options=anime["type"].dropna().unique().tolist(),
        default=anime["type"].dropna().unique().tolist()
    )

    # Aplicar filtros
    anime_filtrado = anime[
        (anime["score"] >= score_min) &
        (anime["type"].isin(tipos_anime))
    ]
    manga_filtrado = manga[manga["score"] >= score_min]

    # ─── MÉTRICAS PRINCIPALES ─────────────────────────────────
    st.subheader("📈 Métricas Principales")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("🎬 Total Anime",      f"{len(anime):,}")
    with col2:
        st.metric("📚 Total Manga",      f"{len(manga):,}")
    with col3:
        st.metric("👤 Total Personajes", f"{len(personajes):,}")
    with col4:
        st.metric("⭐ Score Prom. Anime", f"{anime['score'].mean():.2f}")
    with col5:
        st.metric("⭐ Score Prom. Manga", f"{manga['score'].mean():.2f}")

    st.markdown("---")

    # ─── GRÁFICAS ─────────────────────────────────────────────
    st.subheader("📊 Visualizaciones")

    col1, col2 = st.columns(2)

    # Top 15 Anime por score
    with col1:
        top_anime = anime_filtrado.nlargest(15, "score")
        fig = px.bar(
            top_anime,
            x="score", y="title",
            orientation="h",
            title="🎬 Top 15 Anime por Score",
            color="score",
            color_continuous_scale="reds",
            labels={"score": "Score", "title": "Anime"}
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    # Top 15 Manga por score
    with col2:
        top_manga = manga_filtrado.nlargest(15, "score")
        fig = px.bar(
            top_manga,
            x="score", y="title",
            orientation="h",
            title="📚 Top 15 Manga por Score",
            color="score",
            color_continuous_scale="blues",
            labels={"score": "Score", "title": "Manga"}
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    # Top 15 Personajes por favoritos
    with col1:
        top_personajes = personajes.nlargest(15, "favorites")
        fig = px.bar(
            top_personajes,
            x="favorites", y="name",
            orientation="h",
            title="👤 Top 15 Personajes más Populares",
            color="favorites",
            color_continuous_scale="purples",
            labels={"favorites": "Favoritos", "name": "Personaje"}
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        fig.update_xaxes(tickformat=",")
        st.plotly_chart(fig, use_container_width=True)

    # Géneros más frecuentes
    with col2:
        generos = pd.Series([
            g.strip()
            for row in anime["genres"].dropna()
            for g in row.split(",") if g.strip()
        ]).value_counts().head(12).reset_index()
        generos.columns = ["Género", "Cantidad"]

        fig = px.bar(
            generos,
            x="Cantidad", y="Género",
            orientation="h",
            title="🎭 Top 12 Géneros más Frecuentes en Anime",
            color="Cantidad",
            color_continuous_scale="teal",
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Comparativa Anime vs Manga
    st.subheader("📊 Comparativa Anime vs Manga")
    col1, col2, col3 = st.columns(3)

    with col1:
        fig = px.histogram(
            pd.concat([
                anime[["score"]].assign(Tipo="Anime"),
                manga[["score"]].assign(Tipo="Manga")
            ]),
            x="score", color="Tipo",
            barmode="overlay",
            title="Distribución de Scores",
            opacity=0.7,
            color_discrete_map={"Anime": "#e94560", "Manga": "#0f3460"}
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.box(
            pd.concat([
                anime[["score", "favorites"]].assign(Tipo="Anime"),
                manga[["score", "favorites"]].assign(Tipo="Manga")
            ]),
            x="Tipo", y="score",
            color="Tipo",
            title="Distribución Score por Tipo",
            color_discrete_map={"Anime": "#e94560", "Manga": "#0f3460"}
        )
        st.plotly_chart(fig, use_container_width=True)

    with col3:
        comparativa = pd.DataFrame({
            "Métrica"  : ["Score Prom.", "Favoritos Prom.", "Popularidad Prom."],
            "Anime"    : [anime["score"].mean(), anime["favorites"].mean(), anime["popularity"].mean()],
            "Manga"    : [manga["score"].mean(), manga["favorites"].mean(), manga["popularity"].mean()]
        })
        fig = px.bar(
            comparativa.melt(id_vars="Métrica", var_name="Tipo", value_name="Valor"),
            x="Métrica", y="Valor", color="Tipo",
            barmode="group",
            title="Comparativa General",
            color_discrete_map={"Anime": "#e94560", "Manga": "#0f3460"}
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ─── TABLAS DE DATOS ──────────────────────────────────────
    st.subheader("📋 Datos Detallados")
    tab1, tab2, tab3 = st.tabs(["🎬 Anime", "📚 Manga", "👤 Personajes"])

    with tab1:
        st.dataframe(
            anime_filtrado[["rank", "title", "type", "score", "episodes", "year", "genres", "status"]]
            .sort_values("rank"),
            use_container_width=True, height=400
        )

    with tab2:
        st.dataframe(
            manga_filtrado[["rank", "title", "type", "score", "chapters", "volumes", "genres", "status"]]
            .sort_values("rank"),
            use_container_width=True, height=400
        )

    with tab3:
        st.dataframe(
            personajes[["name", "name_kanji", "favorites", "about"]]
            .sort_values("favorites", ascending=False),
            use_container_width=True, height=400
        )

finally:
    db.close()