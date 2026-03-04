#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import func
import sys
sys.path.insert(0, '.')

from scripts.database import SessionLocal
from scripts.models import Anime, Manga, Personaje, MetricasETL

st.set_page_config(
    page_title="Dashboard Avanzado — Anime & Manga",
    page_icon="🎌",
    layout="wide"
)

st.title("🎌 Dashboard Avanzado — Anime & Manga")
st.markdown("---")

db = SessionLocal()

# ─── CARGAR DATOS ─────────────────────────────────────────────
@st.cache_data
def cargar_datos():
    with SessionLocal() as session:
        anime      = pd.read_sql(session.query(Anime).statement,     session.bind)
        manga      = pd.read_sql(session.query(Manga).statement,     session.bind)
        personajes = pd.read_sql(session.query(Personaje).statement, session.bind)
        metricas   = pd.read_sql(session.query(MetricasETL).statement, session.bind)
    return anime, manga, personajes, metricas

anime, manga, personajes, metricas = cargar_datos()

# ─── PESTAÑAS ─────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Vista General",
    "🔍 Análisis Profundo",
    "👤 Personajes",
    "📈 Métricas ETL"
])

# ══════════════════════════════════════════════════════════════
# TAB 1 — VISTA GENERAL
# ══════════════════════════════════════════════════════════════
with tab1:
    st.subheader("Resumen General")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🎬 Anime",      f"{len(anime):,}")
    with col2:
        st.metric("📚 Manga",      f"{len(manga):,}")
    with col3:
        st.metric("👤 Personajes", f"{len(personajes):,}")
    with col4:
        total = len(anime) + len(manga) + len(personajes)
        st.metric("📦 Total Registros", f"{total:,}")

    st.markdown("---")

    col1, col2 = st.columns(2)

    # Score promedio por tipo de anime
    with col1:
        score_tipo = anime.groupby("type")["score"].mean().reset_index()
        score_tipo.columns = ["Tipo", "Score Promedio"]
        score_tipo = score_tipo.dropna().sort_values("Score Promedio", ascending=False)
        fig = px.bar(
            score_tipo, x="Tipo", y="Score Promedio",
            title="⭐ Score Promedio por Tipo de Anime",
            color="Score Promedio",
            color_continuous_scale="reds",
            text=score_tipo["Score Promedio"].apply(lambda x: f"{x:.2f}")
        )
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    # Anime por estado
    with col2:
        estado_count = anime["status"].value_counts().reset_index()
        estado_count.columns = ["Estado", "Cantidad"]
        fig = px.pie(
            estado_count, values="Cantidad", names="Estado",
            title="📡 Anime por Estado",
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    # Anime por año
    with col1:
        anime_year = anime.dropna(subset=["year"])
        anime_year = anime_year[anime_year["year"] >= 1990]
        year_count = anime_year.groupby("year").agg(
            cantidad=("mal_id", "count"),
            score_prom=("score", "mean")
        ).reset_index()
        fig = px.bar(
            year_count, x="year", y="cantidad",
            title="📅 Anime por Año de Estreno",
            color="score_prom",
            color_continuous_scale="reds",
            labels={"year": "Año", "cantidad": "Cantidad", "score_prom": "Score Prom."}
        )
        st.plotly_chart(fig, use_container_width=True)

    # Manga por tipo
    with col2:
        manga_tipo = manga["type"].value_counts().reset_index()
        manga_tipo.columns = ["Tipo", "Cantidad"]
        fig = px.pie(
            manga_tipo, values="Cantidad", names="Tipo",
            title="📚 Manga por Tipo",
            color_discrete_sequence=px.colors.sequential.Blues_r
        )
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 2 — ANÁLISIS PROFUNDO
# ══════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Análisis Profundo")

    col1, col2 = st.columns(2)

    # Scatter score vs popularidad
    with col1:
        fig = px.scatter(
            anime.dropna(subset=["score", "popularity", "favorites"]),
            x="popularity", y="score",
            size="favorites",
            color="type",
            hover_name="title",
            title="🎯 Score vs Popularidad (Anime)",
            labels={"popularity": "Popularidad", "score": "Score", "type": "Tipo"},
            size_max=30
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.scatter(
            manga.dropna(subset=["score", "popularity", "favorites"]),
            x="popularity", y="score",
            size="favorites",
            color="type",
            hover_name="title",
            title="🎯 Score vs Popularidad (Manga)",
            labels={"popularity": "Popularidad", "score": "Score", "type": "Tipo"},
            size_max=30
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Géneros comparativa
    def contar_generos(df):
        return pd.Series([
            g.strip()
            for row in df["genres"].dropna()
            for g in row.split(",") if g.strip()
        ]).value_counts().head(15)

    gen_anime = contar_generos(anime).reset_index()
    gen_anime.columns = ["Género", "Cantidad"]
    gen_manga = contar_generos(manga).reset_index()
    gen_manga.columns = ["Género", "Cantidad"]

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            gen_anime, x="Cantidad", y="Género",
            orientation="h",
            title="🎭 Top 15 Géneros — Anime",
            color="Cantidad",
            color_continuous_scale="reds"
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(
            gen_manga, x="Cantidad", y="Género",
            orientation="h",
            title="🎭 Top 15 Géneros — Manga",
            color="Cantidad",
            color_continuous_scale="blues"
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Box plot scores
    fig = px.box(
        pd.concat([
            anime[["score", "type"]].rename(columns={"type": "Tipo"}),
            manga[["score", "type"]].rename(columns={"type": "Tipo"})
        ]),
        x="Tipo", y="score", color="Tipo",
        title="📦 Distribución de Scores por Tipo",
        labels={"score": "Score"}
    )
    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 3 — PERSONAJES
# ══════════════════════════════════════════════════════════════
with tab3:
    st.subheader("Análisis de Personajes")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("👤 Total Personajes",    f"{len(personajes):,}")
    with col2:
        st.metric("❤️ Total Favoritos",     f"{int(personajes['favorites'].sum()):,}")
    with col3:
        st.metric("⭐ Favoritos Promedio",  f"{personajes['favorites'].mean():,.0f}")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        top20 = personajes.nlargest(20, "favorites")
        fig = px.bar(
            top20, x="favorites", y="name",
            orientation="h",
            title="👤 Top 20 Personajes más Populares",
            color="favorites",
            color_continuous_scale="purples",
            labels={"favorites": "Favoritos", "name": "Personaje"}
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        fig.update_xaxes(tickformat=",")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.histogram(
            personajes[personajes["favorites"] > 0],
            x="favorites",
            title="📊 Distribución de Favoritos",
            nbins=50,
            color_discrete_sequence=["#9a5fe8"],
            labels={"favorites": "Favoritos"}
        )
        fig.update_xaxes(tickformat=",")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("🔍 Buscar Personaje")
    busqueda = st.text_input("Escribe el nombre del personaje:")
    if busqueda:
        resultado = personajes[personajes["name"].str.contains(busqueda, case=False, na=False)]
        if not resultado.empty:
            st.dataframe(
                resultado[["name", "name_kanji", "favorites", "about"]],
                use_container_width=True
            )
        else:
            st.warning(f"No se encontró ningún personaje con '{busqueda}'")

# ══════════════════════════════════════════════════════════════
# TAB 4 — MÉTRICAS ETL
# ══════════════════════════════════════════════════════════════
with tab4:
    st.subheader("Métricas de Ejecución del ETL")

    if not metricas.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🔄 Ejecuciones",       f"{len(metricas):,}")
        with col2:
            st.metric("✅ Exitosas",           f"{len(metricas[metricas['estado'] == 'SUCCESS']):,}")
        with col3:
            st.metric("⏱️ Tiempo Prom.",       f"{metricas['tiempo_ejecucion_segundos'].mean():.1f}s")

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(
                metricas.sort_values("fecha_ejecucion"),
                x="fecha_ejecucion", y="registros_guardados",
                color="estado",
                title="💾 Registros Guardados por Ejecución",
                labels={"fecha_ejecucion": "Fecha", "registros_guardados": "Registros"},
                color_discrete_map={"SUCCESS": "#2ecc71", "PARTIAL": "#f39c12", "FAILED": "#e74c3c"}
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.scatter(
                metricas,
                x="fecha_ejecucion", y="tiempo_ejecucion_segundos",
                size="registros_guardados",
                color="estado",
                title="⏱️ Duración de Ejecuciones",
                labels={"fecha_ejecucion": "Fecha", "tiempo_ejecucion_segundos": "Segundos"},
                color_discrete_map={"SUCCESS": "#2ecc71", "PARTIAL": "#f39c12", "FAILED": "#e74c3c"}
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.dataframe(
            metricas[["fecha_ejecucion", "estado", "registros_extraidos",
                      "registros_guardados", "registros_fallidos",
                      "tiempo_ejecucion_segundos"]]
            .sort_values("fecha_ejecucion", ascending=False),
            use_container_width=True
        )
    else:
        st.info("No hay métricas registradas aún. Ejecuta el ETL primero.")