#!/usr/bin/env python3
import requests
import json
import pandas as pd
import time
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/anime_etl.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

BASE_URL = "https://api.jikan.moe/v4"
PAGINAS  = 20  # 20 páginas × 25 = 500 registros máximo por categoría

# ─── EXTRACT ──────────────────────────────────────────────────
def extraer_top(categoria: str) -> list:
    resultados = []
    for pagina in range(1, PAGINAS + 1):
        try:
            response = requests.get(
                f"{BASE_URL}/top/{categoria}",
                params={"page": pagina},
                timeout=10
            )
            response.raise_for_status()
            data  = response.json()
            items = data.get("data", [])

            if not items:
                logger.info(f"ℹ️  Sin más datos en {categoria} página {pagina}, deteniendo.")
                break

            resultados.extend(items)
            logger.info(f"✅ Top {categoria} página {pagina}/{PAGINAS}: {len(items)} registros")
            time.sleep(0.5)

        except requests.exceptions.HTTPError as e:
            if e.response.status_code in [400, 404]:
                logger.info(f"ℹ️  Fin de datos {categoria} en página {pagina}")
                break
            logger.error(f"❌ HTTP Error {categoria} página {pagina}: {e}")
            time.sleep(2)
        except Exception as e:
            logger.error(f"❌ Error {categoria} página {pagina}: {e}")
            time.sleep(2)

    logger.info(f"📦 Total {categoria}: {len(resultados)} registros")
    return resultados

def extraer_personajes() -> list:
    resultados = []
    for pagina in range(1, PAGINAS + 1):
        try:
            response = requests.get(
                f"{BASE_URL}/characters",
                params={"page": pagina, "order_by": "favorites", "sort": "desc"},
                timeout=10
            )
            response.raise_for_status()
            data  = response.json()
            items = data.get("data", [])

            if not items:
                logger.info(f"ℹ️  Sin más personajes en página {pagina}, deteniendo.")
                break

            resultados.extend(items)
            logger.info(f"✅ Personajes página {pagina}/{PAGINAS}: {len(items)} registros")
            time.sleep(0.5)

        except requests.exceptions.HTTPError as e:
            if e.response.status_code in [400, 404]:
                logger.info(f"ℹ️  Fin de datos personajes en página {pagina}")
                break
            logger.error(f"❌ HTTP Error personajes página {pagina}: {e}")
            time.sleep(2)
        except Exception as e:
            logger.error(f"❌ Error personajes página {pagina}: {e}")
            time.sleep(2)

    logger.info(f"📦 Total personajes: {len(resultados)}")
    return resultados

# ─── TRANSFORM ────────────────────────────────────────────────
def transformar_anime(raw: list) -> pd.DataFrame:
    df = pd.DataFrame(raw)
    df = df[["mal_id", "title", "title_english", "type", "episodes",
             "status", "score", "rank", "popularity", "favorites",
             "synopsis", "year", "genres"]].copy()
    df["genres"]        = df["genres"].apply(lambda g: ", ".join([x["name"] for x in g]) if isinstance(g, list) else "")
    df["episodes"]      = pd.to_numeric(df["episodes"], errors="coerce")
    df["score"]         = pd.to_numeric(df["score"],    errors="coerce")
    df["year"]          = pd.to_numeric(df["year"],     errors="coerce")
    df["title_english"] = df["title_english"].fillna(df["title"])
    df["synopsis"]      = df["synopsis"].fillna("Sin sinopsis")
    df.drop_duplicates(subset="mal_id", inplace=True)
    df.reset_index(drop=True, inplace=True)
    logger.info(f"✅ Anime transformado: {len(df)} registros")
    return df

def transformar_manga(raw: list) -> pd.DataFrame:
    df = pd.DataFrame(raw)
    df = df[["mal_id", "title", "title_english", "type", "chapters",
             "volumes", "status", "score", "rank", "popularity",
             "favorites", "synopsis", "genres"]].copy()
    df["genres"]        = df["genres"].apply(lambda g: ", ".join([x["name"] for x in g]) if isinstance(g, list) else "")
    df["chapters"]      = pd.to_numeric(df["chapters"], errors="coerce")
    df["volumes"]       = pd.to_numeric(df["volumes"],  errors="coerce")
    df["score"]         = pd.to_numeric(df["score"],    errors="coerce")
    df["title_english"] = df["title_english"].fillna(df["title"])
    df["synopsis"]      = df["synopsis"].fillna("Sin sinopsis")
    df.drop_duplicates(subset="mal_id", inplace=True)
    df.reset_index(drop=True, inplace=True)
    logger.info(f"✅ Manga transformado: {len(df)} registros")
    return df

def transformar_personajes(raw: list) -> pd.DataFrame:
    df = pd.DataFrame(raw)
    df = df[["mal_id", "name", "name_kanji", "favorites", "about"]].copy()
    df["name_kanji"] = df["name_kanji"].fillna("")
    df["about"]      = df["about"].fillna("Sin descripción")
    df["favorites"]  = pd.to_numeric(df["favorites"], errors="coerce").fillna(0).astype(int)
    df.drop_duplicates(subset="mal_id", inplace=True)
    df.reset_index(drop=True, inplace=True)
    logger.info(f"✅ Personajes transformados: {len(df)} registros")
    return df

# ─── LOAD ─────────────────────────────────────────────────────
def guardar(df: pd.DataFrame, nombre: str):
    df.to_csv(f"data/{nombre}.csv",  index=False, encoding="utf-8")
    df.to_json(f"data/{nombre}.json", orient="records", force_ascii=False, indent=2)
    logger.info(f"💾 Guardado: data/{nombre}.csv y data/{nombre}.json")

# ─── MAIN ─────────────────────────────────────────────────────
if __name__ == "__main__":
    logger.info("🚀 Iniciando ETL Anime/Manga - Jikan API (máxima extracción)")
    inicio = datetime.now()

    # EXTRACT
    raw_anime      = extraer_top("anime")
    raw_manga      = extraer_top("manga")
    raw_personajes = extraer_personajes()

    # TRANSFORM
    df_anime      = transformar_anime(raw_anime)
    df_manga      = transformar_manga(raw_manga)
    df_personajes = transformar_personajes(raw_personajes)

    # LOAD
    guardar(df_anime,      "anime")
    guardar(df_manga,      "manga")
    guardar(df_personajes, "personajes")

    fin = datetime.now()
    print("\n" + "="*55)
    print("         RESUMEN ETL ANIME/MANGA")
    print("="*55)
    print(f"  🎬 Anime      : {len(df_anime):>4} registros")
    print(f"  📚 Manga      : {len(df_manga):>4} registros")
    print(f"  👤 Personajes : {len(df_personajes):>4} registros")
    print(f"  ⏱️  Duración   : {(fin - inicio).seconds} segundos")
    print("="*55)