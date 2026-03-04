#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
sys.path.insert(0, '.')

from scripts.database import SessionLocal
from scripts.models import Anime, Manga, Personaje, MetricasETL

st.set_page_config(
    page_title="Dashboard Interactivo — Anime & Manga",
    page_icon="🎌",
    layout="wide"
)

# ─── CSS PERSONALIZADO ────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0f0f1a; }
    .stMetric { background-color: #1a1a2e; padding: 10px; border-radius: 8px; }
    .stTabs [data-baseweb="tab"] { font-size: 16px; font-weight: bold; }
    div[data-testid="metric-container"] {
        background-color: #1a1a2e;
        border: 1px solid #444466;
        border-radius: 8px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎛️ Dashboard Interactivo — Anime & Manga")

# ─── CARGAR DATOS ─────────────────────────────────────────────
@st.cache_data
def cargar_datos():
    with SessionLocal() as session:
        anime      = pd.read_sql(session.query(Anime).statement,      session.bind)
        manga      = pd.read_sql(session.query(Manga).statement,      session.bind)
        personajes = pd.read_sql(session.query(Personaje).statement,  session.bind)
    return anime, manga, personajes

anime, manga, personajes = cargar_datos()

# ─── SIDEBAR CONTROLES ────────────────────────────────────────
st.sidebar.markdown("## 🔧 Controles")

# Filtro score
score_min, score_max = st.sidebar.slider(
    "⭐ Rango de Score:",
    min_value=0.0, max_value=10.0,
    value=(6.0, 10.0), step=0.1
)

# Filtro tipo anime
tipos_disponibles = anime["type"].dropna().unique().tolist()
tipos_seleccionados = st.sidebar.multiselect(
    "🎬 Tipo de Anime:",
    options=tipos_disponibles,
    default=tipos_disponibles
)

# Filtro año
años_disponibles = sorted(anime["year"].dropna().unique().astype(int).tolist())
if años_disponibles:
    año_min, año_max = st.sidebar.select_slider(
        "📅 Rango de Año:",
        options=años_disponibles,
        value=(min(años_disponibles), max(años_disponibles))
    )
else:
    año_min, año_max = 1990, 2024

# Filtro géneros
todos_generos = sorted(set([
    g.strip()
    for row in anime["genres"].dropna()
    for g in row.split(",") if g.strip()
]))
generos_seleccionados = st.sidebar.multiselect(
    "🎭 Géneros:",
    options=todos_generos,
    default=[]
)

# Aplicar filtros
anime_filtrado = anime[
    (anime["score"] >= score_min) &
    (anime["score"] <= score_max) &
    (anime["type"].isin(tipos_seleccionados))
]

if años_disponibles:
    anime_filtrado = anime_filtrado[
        (anime_filtrado["year"] >= año_min) &
        (anime_filtrado["year"] <= año_max)
    ]

if generos_seleccionados:
    anime_filtrado = anime_filtrado[
        anime_filtrado["genres"].apply(
            lambda g: any(gen in str(g) for gen in generos_seleccionados)
            if pd.notna(g) else False
        )
    ]

manga_filtrado = manga[
    (manga["score"] >= score_min) &
    (manga["score"] <= score_max)
]

# ─── KPIs ─────────────────────────────────────────────────────
st.markdown("### 📊 Indicadores Clave")
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric("🎬 Anime Filtrados",    f"{len(anime_filtrado):,}",
              delta=f"{len(anime_filtrado) - len(anime):,}")
with col2:
    st.metric("📚 Manga Filtrados",    f"{len(manga_filtrado):,}",
              delta=f"{len(manga_filtrado) - len(manga):,}")
with col3:
    st.metric("⭐ Score Máx Anime",    f"{anime_filtrado['score'].max():.2f}" if not anime_filtrado.empty else "N/A")
with col4:
    st.metric("⭐ Score Prom Anime",   f"{anime_filtrado['score'].mean():.2f}" if not anime_filtrado.empty else "N/A")
with col5:
    st.metric("❤️ Favs Prom Anime",   f"{anime_filtrado['favorites'].mean():,.0f}" if not anime_filtrado.empty else "N/A")
with col6:
    st.metric("👤 Personajes",         f"{len(personajes):,}")

st.markdown("---")

# ─── GRÁFICAS INTERACTIVAS ────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    if not anime_filtrado.empty:
        top = anime_filtrado.nlargest(15, "score")
        fig = px.bar(
            top, x="score", y="title",
            orientation="h",
            title="🎬 Top 15 Anime Filtrados por Score",
            color="score",
            color_continuous_scale="reds",
            hover_data=["type", "year", "episodes"],
            labels={"score": "Score", "title": "Anime"}
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=450)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No hay anime con los filtros seleccionados")

with col2:
    if not manga_filtrado.empty:
        top = manga_filtrado.nlargest(15, "score")
        fig = px.bar(
            top, x="score", y="title",
            orientation="h",
            title="📚 Top 15 Manga Filtrados por Score",
            color="score",
            color_continuous_scale="blues",
            hover_data=["type", "chapters"],
            labels={"score": "Score", "title": "Manga"}
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=450)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No hay manga con los filtros seleccionados")

col1, col2 = st.columns(2)

with col1:
    if not anime_filtrado.empty:
        fig = px.scatter(
            anime_filtrado.dropna(subset=["score", "popularity", "favorites"]),
            x="popularity", y="score",
            size="favorites",
            color="type",
            hover_name="title",
            title="🎯 Score vs Popularidad",
            labels={"popularity": "Popularidad", "score": "Score"},
            size_max=30
        )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    generos_conteo = pd.Series([
        g.strip()
        for row in anime_filtrado["genres"].dropna()
        for g in row.split(",") if g.strip()
    ]).value_counts().head(10).reset_index()
    generos_conteo.columns = ["Género", "Cantidad"]

    fig = px.pie(
        generos_conteo, values="Cantidad", names="Género",
        title="🎭 Distribución de Géneros (filtrado)",
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ─── TABLAS INTERACTIVAS ──────────────────────────────────────
st.subheader("📋 Explorador de Datos")
tab1, tab2, tab3 = st.tabs(["🎬 Anime", "📚 Manga", "👤 Personajes"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        mostrar_todos = st.checkbox("Mostrar todos", value=False, key="all_anime")
    with col2:
        columnas = st.multiselect(
            "Columnas:",
            ["rank", "title", "type", "score", "episodes", "year", "genres", "status", "favorites"],
            default=["rank", "title", "type", "score", "episodes", "year", "genres"],
            key="cols_anime"
        )

    df_show = anime_filtrado if mostrar_todos else anime_filtrado.head(50)
    st.dataframe(df_show[columnas].sort_values("rank") if columnas else df_show,
                 use_container_width=True, height=400)

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        mostrar_todos = st.checkbox("Mostrar todos", value=False, key="all_manga")
    with col2:
        columnas = st.multiselect(
            "Columnas:",
            ["rank", "title", "type", "score", "chapters", "volumes", "genres", "status", "favorites"],
            default=["rank", "title", "type", "score", "chapters", "genres"],
            key="cols_manga"
        )

    df_show = manga_filtrado if mostrar_todos else manga_filtrado.head(50)
    st.dataframe(df_show[columnas].sort_values("rank") if columnas else df_show,
                 use_container_width=True, height=400)

with tab3:
    busqueda = st.text_input("🔍 Buscar personaje por nombre:")
    if busqueda:
        resultado = personajes[personajes["name"].str.contains(busqueda, case=False, na=False)]
        st.dataframe(resultado[["name", "name_kanji", "favorites", "about"]],
                     use_container_width=True)
    else:
        st.dataframe(
            personajes[["name", "name_kanji", "favorites"]].nlargest(50, "favorites"),
            use_container_width=True, height=400
        )

st.markdown("---")

# ─── DESCARGAR DATOS ──────────────────────────────────────────
st.subheader("⬇️ Descargar Datos")
col1, col2, col3 = st.columns(3)

with col1:
    st.download_button(
        label="⬇️ Descargar Anime CSV",
        data=anime_filtrado.to_csv(index=False),
        file_name="anime_filtrado.csv",
        mime="text/csv"
    )
with col2:
    st.download_button(
        label="⬇️ Descargar Manga CSV",
        data=manga_filtrado.to_csv(index=False),
        file_name="manga_filtrado.csv",
        mime="text/csv"
    )
with col3:
    st.download_button(
        label="⬇️ Descargar Personajes CSV",
        data=personajes.to_csv(index=False),
        file_name="personajes.csv",
        mime="text/csv"
    )