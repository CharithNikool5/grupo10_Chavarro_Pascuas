#!/usr/bin/env python3
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import os

# ─── ESTILO PROFESIONAL ───────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor'  : '#0f0f1a',
    'axes.facecolor'    : '#1a1a2e',
    'axes.edgecolor'    : '#444466',
    'axes.labelcolor'   : '#e0e0ff',
    'axes.titlecolor'   : '#ffffff',
    'axes.titlesize'    : 14,
    'axes.labelsize'    : 11,
    'axes.grid'         : True,
    'grid.color'        : '#2a2a4a',
    'grid.linestyle'    : '--',
    'grid.alpha'        : 0.6,
    'xtick.color'       : '#a0a0cc',
    'ytick.color'       : '#a0a0cc',
    'xtick.labelsize'   : 9,
    'ytick.labelsize'   : 9,
    'text.color'        : '#e0e0ff',
    'font.family'       : 'DejaVu Sans',
    'legend.facecolor'  : '#1a1a2e',
    'legend.edgecolor'  : '#444466',
    'legend.fontsize'   : 9,
})

COLORES_ANIME     = ['#e94560', '#e8615a', '#e07060', '#d88060', '#cf9060']
COLORES_MANGA     = ['#0f3460', '#16498a', '#1e5fa8', '#2675c5', '#2e8be0']
COLORES_PERSONAJE = ['#533483', '#6a42a8', '#8250cc', '#9a5fe8', '#b06dff']
COLOR_ACENTO      = '#e94560'
COLOR_SECUNDARIO  = '#16213e'

os.makedirs("data", exist_ok=True)

# ─── CARGAR DATOS ─────────────────────────────────────────────
def cargar_datos():
    if not os.path.exists("data/anime.csv"):
        print("❌ No se encontraron datos. Ejecuta primero: python3 -m scripts.anime_etl")
        exit()
    anime      = pd.read_csv("data/anime.csv")
    manga      = pd.read_csv("data/manga.csv")
    personajes = pd.read_csv("data/personajes.csv")
    print(f"✅ Datos cargados — Anime: {len(anime)} | Manga: {len(manga)} | Personajes: {len(personajes)}")
    return anime, manga, personajes

# ─── GRÁFICA 1: TOP 15 ANIME POR SCORE ────────────────────────
def grafica_top15_anime(df):
    top = df.nlargest(15, "score")[["title", "score", "type"]].dropna().iloc[::-1]

    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor('#0f0f1a')

    colores = [COLORES_ANIME[i % len(COLORES_ANIME)] for i in range(len(top))]
    bars    = ax.barh(top["title"], top["score"], color=colores,
                      height=0.65, edgecolor='#ffffff22', linewidth=0.5)

    ax.set_xlim(8.5, top["score"].max() + 0.15)
    ax.set_xlabel("Score MyAnimeList", fontsize=11)
    ax.set_title("🎬 Top 15 Anime — Mejor Puntuados", fontsize=15, fontweight='bold', pad=15)

    for bar, (_, row) in zip(bars, top.iterrows()):
        ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height() / 2,
                f"{row['score']:.2f}", va='center', ha='left',
                fontsize=9, color='#ffffff', fontweight='bold')
        ax.text(bar.get_x() + 0.02, bar.get_y() + bar.get_height() / 2,
                f"[{row['type']}]", va='center', ha='left',
                fontsize=7, color='#ffffff88')

    ax.spines[['top', 'right']].set_visible(False)
    plt.tight_layout(pad=2)
    plt.savefig("data/top15_anime.png", dpi=150, bbox_inches='tight', facecolor='#0f0f1a')
    print("💾 Guardado: data/top15_anime.png")
    plt.close()

# ─── GRÁFICA 2: TOP 15 MANGA POR SCORE ────────────────────────
def grafica_top15_manga(df):
    top = df.nlargest(15, "score")[["title", "score", "type"]].dropna().iloc[::-1]

    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor('#0f0f1a')

    colores = [COLORES_MANGA[i % len(COLORES_MANGA)] for i in range(len(top))]
    bars    = ax.barh(top["title"], top["score"], color=colores,
                      height=0.65, edgecolor='#ffffff22', linewidth=0.5)

    ax.set_xlim(8.5, top["score"].max() + 0.15)
    ax.set_xlabel("Score MyAnimeList", fontsize=11)
    ax.set_title("📚 Top 15 Manga — Mejor Puntuados", fontsize=15, fontweight='bold', pad=15)

    for bar, (_, row) in zip(bars, top.iterrows()):
        ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height() / 2,
                f"{row['score']:.2f}", va='center', ha='left',
                fontsize=9, color='#ffffff', fontweight='bold')
        ax.text(bar.get_x() + 0.02, bar.get_y() + bar.get_height() / 2,
                f"[{row['type']}]", va='center', ha='left',
                fontsize=7, color='#ffffff88')

    ax.spines[['top', 'right']].set_visible(False)
    plt.tight_layout(pad=2)
    plt.savefig("data/top15_manga.png", dpi=150, bbox_inches='tight', facecolor='#0f0f1a')
    print("💾 Guardado: data/top15_manga.png")
    plt.close()

# ─── GRÁFICA 3: TOP 15 PERSONAJES ─────────────────────────────
def grafica_top15_personajes(df):
    top = df.nlargest(15, "favorites")[["name", "favorites"]].iloc[::-1]

    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor('#0f0f1a')

    colores = [COLORES_PERSONAJE[i % len(COLORES_PERSONAJE)] for i in range(len(top))]
    bars    = ax.barh(top["name"], top["favorites"], color=colores,
                      height=0.65, edgecolor='#ffffff22', linewidth=0.5)

    ax.set_xlabel("Cantidad de Favoritos", fontsize=11)
    ax.set_title("👤 Top 15 Personajes — Más Populares", fontsize=15, fontweight='bold', pad=15)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

    for bar, (_, row) in zip(bars, top.iterrows()):
        ax.text(bar.get_width() + 500, bar.get_y() + bar.get_height() / 2,
                f"{int(row['favorites']):,}", va='center', ha='left',
                fontsize=9, color='#ffffff', fontweight='bold')

    ax.spines[['top', 'right']].set_visible(False)
    plt.tight_layout(pad=2)
    plt.savefig("data/top15_personajes.png", dpi=150, bbox_inches='tight', facecolor='#0f0f1a')
    print("💾 Guardado: data/top15_personajes.png")
    plt.close()

# ─── GRÁFICA 4: GÉNEROS MÁS FRECUENTES ────────────────────────
def grafica_generos(df_anime, df_manga):
    def contar_generos(df):
        return pd.Series(
            [g for row in df["genres"].dropna() for g in row.split(", ") if g]
        ).value_counts().head(12)

    gen_anime = contar_generos(df_anime)
    gen_manga = contar_generos(df_manga)
    todos     = pd.concat([gen_anime, gen_manga], axis=1, keys=["Anime", "Manga"]).fillna(0)

    fig, ax = plt.subplots(figsize=(14, 7))
    fig.patch.set_facecolor('#0f0f1a')

    x     = np.arange(len(todos))
    ancho = 0.38

    ax.bar(x - ancho/2, todos["Anime"], width=ancho, label="Anime",
           color=COLOR_ACENTO, edgecolor='#ffffff22', linewidth=0.5)
    ax.bar(x + ancho/2, todos["Manga"], width=ancho, label="Manga",
           color=COLORES_MANGA[1], edgecolor='#ffffff22', linewidth=0.5)

    ax.set_xticks(x)
    ax.set_xticklabels(todos.index, rotation=35, ha='right', fontsize=9)
    ax.set_ylabel("Cantidad de títulos", fontsize=11)
    ax.set_title("🎭 Géneros más frecuentes — Anime vs Manga", fontsize=15, fontweight='bold', pad=15)
    ax.legend()
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.spines[['top', 'right']].set_visible(False)

    plt.tight_layout(pad=2)
    plt.savefig("data/generos_comparativa.png", dpi=150, bbox_inches='tight', facecolor='#0f0f1a')
    print("💾 Guardado: data/generos_comparativa.png")
    plt.close()

# ─── GRÁFICA 5: COMPARATIVA ANIME VS MANGA ────────────────────
def grafica_comparativa(df_anime, df_manga):
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.patch.set_facecolor('#0f0f1a')
    fig.suptitle("📊 Comparativa General — Anime vs Manga", fontsize=16,
                 fontweight='bold', color='white', y=1.02)

    metricas = {
        "Score Promedio"     : (df_anime["score"].mean(),      df_manga["score"].mean()),
        "Favoritos Promedio" : (df_anime["favorites"].mean(),  df_manga["favorites"].mean()),
        "Popularidad Media"  : (df_anime["popularity"].mean(), df_manga["popularity"].mean()),
    }

    for ax, (titulo, (val_anime, val_manga)) in zip(axes, metricas.items()):
        categorias = ["Anime", "Manga"]
        valores    = [val_anime, val_manga]
        colores    = [COLOR_ACENTO, COLORES_MANGA[1]]

        bars = ax.bar(categorias, valores, color=colores, width=0.5,
                      edgecolor='#ffffff22', linewidth=0.5)
        ax.set_title(titulo, fontsize=12, fontweight='bold', pad=10)
        ax.spines[['top', 'right']].set_visible(False)

        for bar, val in zip(bars, valores):
            fmt = f"{val:,.0f}" if val > 100 else f"{val:.2f}"
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + bar.get_height() * 0.02,
                    fmt, ha='center', va='bottom', fontsize=11,
                    fontweight='bold', color='white')

        ax.set_ylim(0, max(valores) * 1.2)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

    plt.tight_layout(pad=2)
    plt.savefig("data/comparativa_anime_manga.png", dpi=150, bbox_inches='tight', facecolor='#0f0f1a')
    print("💾 Guardado: data/comparativa_anime_manga.png")
    plt.close()

# ─── MAIN ─────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "="*55)
    print("       GENERANDO VISUALIZACIONES PROFESIONALES")
    print("="*55 + "\n")

    anime, manga, personajes = cargar_datos()

    grafica_top15_anime(anime)
    grafica_top15_manga(manga)
    grafica_top15_personajes(personajes)
    grafica_generos(anime, manga)
    grafica_comparativa(anime, manga)

    print("\n" + "="*55)
    print("  ✅ 5 gráficas generadas en data/")
    print("="*55)
    print("  📊 data/top15_anime.png")
    print("  📊 data/top15_manga.png")
    print("  📊 data/top15_personajes.png")
    print("  📊 data/generos_comparativa.png")
    print("  📊 data/comparativa_anime_manga.png")
    print("="*55 + "\n")