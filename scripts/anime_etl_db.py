#!/usr/bin/env python3
import requests
import time
from datetime import datetime
import logging
from sqlalchemy.exc import IntegrityError

from scripts.database import SessionLocal
from scripts.models import Anime, Manga, Personaje, MetricasETL

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/anime_etl_db.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

BASE_URL  = "https://api.jikan.moe/v4"
PAGINAS   = 20  # 20 páginas × 25 registros = 500 por categoría

class AnimeETL:
    def __init__(self):
        self.db                  = SessionLocal()
        self.tiempo_inicio       = time.time()
        self.registros_extraidos = 0
        self.registros_guardados = 0
        self.registros_fallidos  = 0

    # ─── EXTRACT ──────────────────────────────────────────────
    def extraer_top(self, categoria: str) -> list:
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

                # Si no hay más datos, detener
                if not items:
                    logger.info(f"ℹ️  No hay más datos en {categoria} página {pagina}, deteniendo.")
                    break

                resultados.extend(items)
                self.registros_extraidos += len(items)
                logger.info(f"✅ Top {categoria} página {pagina}/{PAGINAS}: {len(items)} registros")

                # Respetar límite de Jikan: 3 req/seg
                time.sleep(0.5)

            except requests.exceptions.HTTPError as e:
                # Si la API responde 400/404 es porque ya no hay más páginas
                if e.response.status_code in [400, 404]:
                    logger.info(f"ℹ️  Fin de datos para {categoria} en página {pagina}")
                    break
                logger.error(f"❌ HTTP Error en {categoria} página {pagina}: {e}")
                self.registros_fallidos += 1
                time.sleep(2)
            except Exception as e:
                logger.error(f"❌ Error extrayendo {categoria} página {pagina}: {e}")
                self.registros_fallidos += 1
                time.sleep(2)

        logger.info(f"📦 Total extraído de {categoria}: {len(resultados)} registros")
        return resultados

    def extraer_personajes(self) -> list:
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
                    logger.info(f"ℹ️  No hay más personajes en página {pagina}, deteniendo.")
                    break

                resultados.extend(items)
                self.registros_extraidos += len(items)
                logger.info(f"✅ Personajes página {pagina}/{PAGINAS}: {len(items)} registros")
                time.sleep(0.5)

            except requests.exceptions.HTTPError as e:
                if e.response.status_code in [400, 404]:
                    logger.info(f"ℹ️  Fin de datos personajes en página {pagina}")
                    break
                logger.error(f"❌ HTTP Error personajes página {pagina}: {e}")
                self.registros_fallidos += 1
                time.sleep(2)
            except Exception as e:
                logger.error(f"❌ Error extrayendo personajes página {pagina}: {e}")
                self.registros_fallidos += 1
                time.sleep(2)

        logger.info(f"📦 Total personajes extraídos: {len(resultados)}")
        return resultados

    # ─── TRANSFORM + LOAD ─────────────────────────────────────
    def cargar_anime(self, raw: list):
        for item in raw:
            try:
                existe = self.db.query(Anime).filter_by(mal_id=item["mal_id"]).first()
                if existe:
                    continue

                genres = ", ".join([g["name"] for g in item.get("genres", [])])

                registro = Anime(
                    mal_id        = item.get("mal_id"),
                    title         = item.get("title"),
                    title_english = item.get("title_english") or item.get("title"),
                    type          = item.get("type"),
                    episodes      = item.get("episodes"),
                    status        = item.get("status"),
                    score         = item.get("score"),
                    rank          = item.get("rank"),
                    popularity    = item.get("popularity"),
                    favorites     = item.get("favorites"),
                    synopsis      = item.get("synopsis") or "Sin sinopsis",
                    year          = item.get("year"),
                    genres        = genres
                )
                self.db.add(registro)
                self.db.commit()
                self.registros_guardados += 1

            except IntegrityError:
                self.db.rollback()
            except Exception as e:
                self.db.rollback()
                logger.error(f"❌ Error guardando anime {item.get('title')}: {e}")
                self.registros_fallidos += 1

    def cargar_manga(self, raw: list):
        for item in raw:
            try:
                existe = self.db.query(Manga).filter_by(mal_id=item["mal_id"]).first()
                if existe:
                    continue

                genres = ", ".join([g["name"] for g in item.get("genres", [])])

                registro = Manga(
                    mal_id        = item.get("mal_id"),
                    title         = item.get("title"),
                    title_english = item.get("title_english") or item.get("title"),
                    type          = item.get("type"),
                    chapters      = item.get("chapters"),
                    volumes       = item.get("volumes"),
                    status        = item.get("status"),
                    score         = item.get("score"),
                    rank          = item.get("rank"),
                    popularity    = item.get("popularity"),
                    favorites     = item.get("favorites"),
                    synopsis      = item.get("synopsis") or "Sin sinopsis",
                    genres        = genres
                )
                self.db.add(registro)
                self.db.commit()
                self.registros_guardados += 1

            except IntegrityError:
                self.db.rollback()
            except Exception as e:
                self.db.rollback()
                logger.error(f"❌ Error guardando manga {item.get('title')}: {e}")
                self.registros_fallidos += 1

    def cargar_personajes(self, raw: list):
        for item in raw:
            try:
                existe = self.db.query(Personaje).filter_by(mal_id=item["mal_id"]).first()
                if existe:
                    continue

                registro = Personaje(
                    mal_id     = item.get("mal_id"),
                    name       = item.get("name"),
                    name_kanji = item.get("name_kanji") or "",
                    favorites  = item.get("favorites") or 0,
                    about      = item.get("about") or "Sin descripción"
                )
                self.db.add(registro)
                self.db.commit()
                self.registros_guardados += 1

            except IntegrityError:
                self.db.rollback()
            except Exception as e:
                self.db.rollback()
                logger.error(f"❌ Error guardando personaje {item.get('name')}: {e}")
                self.registros_fallidos += 1

    # ─── MÉTRICAS ─────────────────────────────────────────────
    def guardar_metricas(self, estado: str):
        try:
            tiempo = time.time() - self.tiempo_inicio
            metrica = MetricasETL(
                registros_extraidos       = self.registros_extraidos,
                registros_guardados       = self.registros_guardados,
                registros_fallidos        = self.registros_fallidos,
                tiempo_ejecucion_segundos = tiempo,
                estado                    = estado,
                mensaje                   = f"Extraídos: {self.registros_extraidos} | Guardados: {self.registros_guardados} | Fallidos: {self.registros_fallidos}"
            )
            self.db.add(metrica)
            self.db.commit()
            logger.info(f"📈 Métricas guardadas: {metrica.mensaje}")
        except Exception as e:
            logger.error(f"❌ Error guardando métricas: {e}")

    # ─── EJECUTAR ─────────────────────────────────────────────
    def ejecutar(self):
        try:
            logger.info("🚀 Iniciando ETL Anime/Manga → PostgreSQL (máxima extracción)")

            # EXTRACT
            raw_anime      = self.extraer_top("anime")
            raw_manga      = self.extraer_top("manga")
            raw_personajes = self.extraer_personajes()

            # TRANSFORM + LOAD
            logger.info("💾 Cargando anime en PostgreSQL...")
            self.cargar_anime(raw_anime)

            logger.info("💾 Cargando manga en PostgreSQL...")
            self.cargar_manga(raw_manga)

            logger.info("💾 Cargando personajes en PostgreSQL...")
            self.cargar_personajes(raw_personajes)

            estado = "SUCCESS" if self.registros_fallidos == 0 else "PARTIAL"
            self.guardar_metricas(estado)

            tiempo_total = time.time() - self.tiempo_inicio
            print("\n" + "="*55)
            print("    RESUMEN ETL ANIME/MANGA → PostgreSQL")
            print("="*55)
            print(f"  📥 Extraídos : {self.registros_extraidos:>5}")
            print(f"  💾 Guardados : {self.registros_guardados:>5}")
            print(f"  ❌ Fallidos  : {self.registros_fallidos:>5}")
            print(f"  ⏱️  Duración  : {tiempo_total:.2f} segundos")
            print(f"  ✅ Estado    : {estado}")
            print("="*55)

        except Exception as e:
            logger.error(f"❌ Error en ETL: {e}")
            self.guardar_metricas("FAILED")
        finally:
            self.db.close()

if __name__ == "__main__":
    etl = AnimeETL()
    etl.ejecutar()