#!/usr/bin/env python3
import requests
import json
import pandas as pd
import time
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/anime_etl.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ─── CONFIGURACIÓN ────────────────────────────────────────────
BASE_URL   = "https://api.jikan.moe/v4"
PAGINAS    = 2  # 2 páginas × 25 resultados = 50 por categoría

# ─── EXTRACT ──────────────────────────────────────────────────
def extraer_top(categoria: str, paginas: int) -> list:
    """Extrae el top de anime o manga desde Jikan."""
    resultados = []
    for pagina in range(1, paginas + 1):
        try:
            url = f"{BASE_URL}/top/{categoria}"
            params = {"page": pagina}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            items = data.get("data", [])
            resultados.extend(items)
            logger.info(f"✅ Top {categoria} - página {pagina}: {len(items)} registros")
            time.sleep(1)
        except Exception as e:
            logger.error(f"❌ Error extrayendo {categoria} página {pagina}: {e}")
    return resultados

def extraer_personajes(paginas: int) -> list:
    """Extrae personajes ordenados por favoritos."""
    resultados = []
    for pagina in range(1, paginas + 1):
        try:
            url = f"{BASE_URL}/characters"
            params = {"page": pagina, "order_by": "favorites", "sort": "desc"}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            items = data.get("data", [])
            resultados.extend(items)
            logger.info(f"✅ Personajes - página {pagina}: {len(items)} registros")
            time.sleep(1)
        except Exception as e:
            logger.error(f"❌ Error extrayendo personajes página {pagina}: {e}")
    return resultados

# ─── TRANSFORM ────────────────────────────────────────────────
def transformar_anime(raw: list) -> pd.DataFrame:
    df = pd.DataFrame(raw)
    df = df[["mal_id", "title", "title_english", "type", "episodes",
             "status", "score", "rank", "popularity", "favorites",
             "synopsis", "year", "genres"]].copy()
    df["genres"] = df["genres"].apply(
        lambda g: ", ".join([x["name"] for x in g]) if isinstance(g, list) else ""
    )
    df["episodes"] = pd.to_numeric(df["episodes"], errors="coerce")
    df["score"]    = pd.to_numeric(df["score"],    errors="coerce")
    df["year"]     = pd.to_numeric(df["year"],     errors="coerce")
    df["title_english"].fillna(df["title"], inplace=True)
    df["synopsis"].fillna("Sin sinopsis", inplace=True)
    df.drop_duplicates(subset="mal_id", inplace=True)
    df.reset_index(drop=True, inplace=True)
    logger.info(f"✅ Anime transformado: {len(df)} registros")
    return df

def transformar_manga(raw: list) -> pd.DataFrame:
    df = pd.DataFrame(raw)
    df = df[["mal_id", "title", "title_english", "type", "chapters",
             "volumes", "status", "score", "rank", "popularity",
             "favorites", "synopsis", "genres"]].copy()
    df["genres"] = df["genres"].apply(
        lambda g: ", ".join([x["name"] for x in g]) if isinstance(g, list) else ""
    )
    df["chapters"] = pd.to_numeric(df["chapters"], errors="coerce")
    df["volumes"]  = pd.to_numeric(df["volumes"],  errors="coerce")
    df["score"]    = pd.to_numeric(df["score"],    errors="coerce")
    df["title_english"].fillna(df["title"], inplace=True)
    df["synopsis"].fillna("Sin sinopsis", inplace=True)
    df.drop_duplicates(subset="mal_id", inplace=True)
    df.reset_index(drop=True, inplace=True)
    logger.info(f"✅ Manga transformado: {len(df)} registros")
    return df

def transformar_personajes(raw: list) -> pd.DataFrame:
    df = pd.DataFrame(raw)
    df = df[["mal_id", "name", "name_kanji", "favorites", "about"]].copy()
    df["name_kanji"].fillna("", inplace=True)
    df["about"].fillna("Sin descripción", inplace=True)
    df["favorites"] = pd.to_numeric(df["favorites"], errors="coerce").fillna(0).astype(int)
    df.drop_duplicates(subset="mal_id", inplace=True)
    df.reset_index(drop=True, inplace=True)
    logger.info(f"✅ Personajes transformados: {len(df)} registros")
    return df

# ─── LOAD ─────────────────────────────────────────────────────
def guardar(df: pd.DataFrame, nombre: str):
    df.to_csv(f"data/{nombre}.csv", index=False, encoding="utf-8")
    df.to_json(f"data/{nombre}.json", orient="records", force_ascii=False, indent=2)
    logger.info(f"💾 Guardado: data/{nombre}.csv y data/{nombre}.json")

# ─── MAIN ─────────────────────────────────────────────────────
if __name__ == "__main__":
    logger.info("🚀 Iniciando ETL Anime/Manga - Jikan API")
    inicio = datetime.now()

    # EXTRACT
    raw_anime      = extraer_top("anime",  PAGINAS)
    raw_manga      = extraer_top("manga",  PAGINAS)
    raw_personajes = extraer_personajes(PAGINAS)

    # TRANSFORM
    df_anime      = transformar_anime(raw_anime)
    df_manga      = transformar_manga(raw_manga)
    df_personajes = transformar_personajes(raw_personajes)

    # LOAD
    guardar(df_anime,      "anime")
    guardar(df_manga,      "manga")
    guardar(df_personajes, "personajes")

    # RESUMEN
    fin = datetime.now()
    print("\n" + "="*55)
    print("         RESUMEN ETL ANIME/MANGA")
    print("="*55)
    print(f"  🎬 Anime:      {len(df_anime):>3} registros")
    print(f"  📚 Manga:      {len(df_manga):>3} registros")
    print(f"  👤 Personajes: {len(df_personajes):>3} registros")
    print(f"  ⏱️  Duración:   {(fin - inicio).seconds} segundos")
    print("="*55)
    print("\nTop 5 Anime por score:")
    print(df_anime[["rank","title","score","genres"]].head().to_string(index=False))
    print("\nTop 5 Manga por score:")
    print(df_manga[["rank","title","score","genres"]].head().to_string(index=False))
    print("\nTop 5 Personajes por favoritos:")
    print(df_personajes[["name","favorites"]].head().to_string(index=False))