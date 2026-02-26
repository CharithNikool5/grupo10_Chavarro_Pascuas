#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Para WSL que no tiene pantalla gráfica
import os

# ─── CARGAR DATOS ─────────────────────────────────────────────
def cargar_datos():
    anime      = pd.read_csv("data/anime.csv")
    manga      = pd.read_csv("data/manga.csv")
    personajes = pd.read_csv("data/personajes.csv")
    print("✅ Datos cargados correctamente")
    return anime, manga, personajes

# ─── GRÁFICAS ─────────────────────────────────────────────────
def grafica_top10_anime(df):
    """Top 10 anime por score."""
    top10 = df.nlargest(10, "score")[["title", "score"]].dropna()

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.barh(top10["title"], top10["score"], color="steelblue")
    ax.set_xlabel("Score")
    ax.set_title("🎬 Top 10 Anime por Score")
    ax.set_xlim(8, 10)
    ax.invert_yaxis()

    # Agregar valor al final de cada barra
    for bar, score in zip(bars, top10["score"]):
        ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
                f"{score:.2f}", va="center", fontsize=9)

    plt.tight_layout()
    plt.savefig("data/top10_anime.png", dpi=150)
    print("💾 Guardado: data/top10_anime.png")
    plt.close()

def grafica_top10_manga(df):
    """Top 10 manga por score."""
    top10 = df.nlargest(10, "score")[["title", "score"]].dropna()

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.barh(top10["title"], top10["score"], color="coral")
    ax.set_xlabel("Score")
    ax.set_title("📚 Top 10 Manga por Score")
    ax.set_xlim(8, 10)
    ax.invert_yaxis()

    for bar, score in zip(bars, top10["score"]):
        ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
                f"{score:.2f}", va="center", fontsize=9)

    plt.tight_layout()
    plt.savefig("data/top10_manga.png", dpi=150)
    print("💾 Guardado: data/top10_manga.png")
    plt.close()

def grafica_generos_anime(df):
    """Géneros más frecuentes en anime."""
    generos = df["genres"].dropna().str.split(", ").explode()
    top_generos = generos.value_counts().head(10)

    fig, ax = plt.subplots(figsize=(10, 6))
    top_generos.plot(kind="bar", ax=ax, color="mediumseagreen")
    ax.set_title("🎭 Top 10 Géneros más frecuentes en Anime")
    ax.set_xlabel("Género")
    ax.set_ylabel("Cantidad")
    ax.tick_params(axis='x', rotation=45)

    plt.tight_layout()
    plt.savefig("data/generos_anime.png", dpi=150)
    print("💾 Guardado: data/generos_anime.png")
    plt.close()

def grafica_top10_personajes(df):
    """Top 10 personajes por favoritos."""
    top10 = df.nlargest(10, "favorites")[["name", "favorites"]]

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.barh(top10["name"], top10["favorites"], color="mediumpurple")
    ax.set_xlabel("Favoritos")
    ax.set_title("👤 Top 10 Personajes más populares")
    ax.invert_yaxis()

    for bar, fav in zip(bars, top10["favorites"]):
        ax.text(bar.get_width() + 100, bar.get_y() + bar.get_height()/2,
                f"{fav:,}", va="center", fontsize=9)

    plt.tight_layout()
    plt.savefig("data/top10_personajes.png", dpi=150)
    print("💾 Guardado: data/top10_personajes.png")
    plt.close()

def grafica_distribucion_scores(df_anime, df_manga):
    """Comparación de distribución de scores anime vs manga."""
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.hist(df_anime["score"].dropna(), bins=15, alpha=0.6,
            color="steelblue", label="Anime")
    ax.hist(df_manga["score"].dropna(), bins=15, alpha=0.6,
            color="coral", label="Manga")

    ax.set_title("📊 Distribución de Scores: Anime vs Manga")
    ax.set_xlabel("Score")
    ax.set_ylabel("Cantidad")
    ax.legend()

    plt.tight_layout()
    plt.savefig("data/distribucion_scores.png", dpi=150)
    print("💾 Guardado: data/distribucion_scores.png")
    plt.close()

# ─── MAIN ─────────────────────────────────────────────────────
if __name__ == "__main__":
    # Verificar que existen los CSVs
    if not os.path.exists("data/anime.csv"):
        print("❌ No se encontraron los datos. Ejecuta primero anime_etl.py")
        exit()

    print("🚀 Generando visualizaciones...\n")

    anime, manga, personajes = cargar_datos()

    grafica_top10_anime(anime)
    grafica_top10_manga(manga)
    grafica_generos_anime(anime)
    grafica_top10_personajes(personajes)
    grafica_distribucion_scores(anime, manga)

    print("\n✅ Todas las gráficas guardadas en data/")
    print("\nArchivos generados:")
    print("  📊 data/top10_anime.png")
    print("  📊 data/top10_manga.png")
    print("  📊 data/generos_anime.png")
    print("  📊 data/top10_personajes.png")
    print("  📊 data/distribucion_scores.png")