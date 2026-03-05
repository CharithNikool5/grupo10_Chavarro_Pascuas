#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from scripts.database import SessionLocal
from scripts.models import Anime, Manga, Personaje, MetricasETL
from sqlalchemy import func
import pandas as pd

db = SessionLocal()

# ─── ANIME ────────────────────────────────────────────────────
def top10_anime():
    registros = db.query(Anime.rank, Anime.title, Anime.score,
                         Anime.type, Anime.episodes, Anime.year)\
                  .order_by(Anime.rank).limit(10).all()
    df = pd.DataFrame(registros, columns=["Rank", "Título", "Score", "Tipo", "Episodios", "Año"])
    df["Score"]     = df["Score"].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
    df["Episodios"] = df["Episodios"].apply(lambda x: int(x) if pd.notna(x) else "?")
    df["Año"]       = df["Año"].apply(lambda x: int(x) if pd.notna(x) else "?")
    print("\n🎬 TOP 10 ANIME POR SCORE:")
    print("-" * 80)
    print(df.to_string(index=False))

def estadisticas_anime():
    total    = db.query(func.count(Anime.id)).scalar()
    avg_score= db.query(func.avg(Anime.score)).scalar()
    max_score= db.query(func.max(Anime.score)).scalar()
    min_score= db.query(func.min(Anime.score)).scalar()
    avg_ep   = db.query(func.avg(Anime.episodes)).scalar()
    total_fav= db.query(func.sum(Anime.favorites)).scalar()

    print("\n📊 ESTADÍSTICAS GENERALES DE ANIME:")
    print("-" * 40)
    print(f"  Total registros    : {total:,}")
    print(f"  Score promedio     : {avg_score:.2f}")
    print(f"  Score máximo       : {max_score:.2f}")
    print(f"  Score mínimo       : {min_score:.2f}")
    print(f"  Episodios promedio : {avg_ep:.1f}")
    print(f"  Total favoritos    : {int(total_fav):,}")

def anime_por_tipo():
    registros = db.query(Anime.type, func.count(Anime.id).label("cantidad"),
                         func.avg(Anime.score).label("score_promedio"))\
                  .group_by(Anime.type)\
                  .order_by(func.count(Anime.id).desc()).all()
    df = pd.DataFrame(registros, columns=["Tipo", "Cantidad", "Score Promedio"])
    df["Score Promedio"] = df["Score Promedio"].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
    print("\n🎞️  ANIME POR TIPO:")
    print("-" * 40)
    print(df.to_string(index=False))

def anime_por_estado():
    registros = db.query(Anime.status, func.count(Anime.id).label("cantidad"))\
                  .group_by(Anime.status)\
                  .order_by(func.count(Anime.id).desc()).all()
    df = pd.DataFrame(registros, columns=["Estado", "Cantidad"])
    print("\n📡 ANIME POR ESTADO (Airing/Finished):")
    print("-" * 40)
    print(df.to_string(index=False))

# ─── MANGA ────────────────────────────────────────────────────
def top10_manga():
    registros = db.query(Manga.rank, Manga.title, Manga.score,
                         Manga.type, Manga.chapters, Manga.volumes)\
                  .order_by(Manga.rank).limit(10).all()
    df = pd.DataFrame(registros, columns=["Rank", "Título", "Score", "Tipo", "Capítulos", "Volúmenes"])
    df["Score"]     = df["Score"].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
    df["Capítulos"] = df["Capítulos"].apply(lambda x: int(x) if pd.notna(x) else "?")
    df["Volúmenes"] = df["Volúmenes"].apply(lambda x: int(x) if pd.notna(x) else "?")
    print("\n📚 TOP 10 MANGA POR SCORE:")
    print("-" * 80)
    print(df.to_string(index=False))

def estadisticas_manga():
    total     = db.query(func.count(Manga.id)).scalar()
    avg_score = db.query(func.avg(Manga.score)).scalar()
    max_score = db.query(func.max(Manga.score)).scalar()
    min_score = db.query(func.min(Manga.score)).scalar()
    total_fav = db.query(func.sum(Manga.favorites)).scalar()

    print("\n📊 ESTADÍSTICAS GENERALES DE MANGA:")
    print("-" * 40)
    print(f"  Total registros : {total:,}")
    print(f"  Score promedio  : {avg_score:.2f}")
    print(f"  Score máximo    : {max_score:.2f}")
    print(f"  Score mínimo    : {min_score:.2f}")
    print(f"  Total favoritos : {int(total_fav):,}")

# ─── PERSONAJES ───────────────────────────────────────────────
def top10_personajes():
    registros = db.query(Personaje.name, Personaje.name_kanji, Personaje.favorites)\
                  .order_by(Personaje.favorites.desc()).limit(10).all()
    df = pd.DataFrame(registros, columns=["Personaje", "Nombre Kanji", "Favoritos"])
    df["Favoritos"] = df["Favoritos"].apply(lambda x: f"{int(x):,}")
    print("\n👤 TOP 10 PERSONAJES MÁS POPULARES:")
    print("-" * 60)
    print(df.to_string(index=False))

def estadisticas_personajes():
    total     = db.query(func.count(Personaje.id)).scalar()
    avg_fav   = db.query(func.avg(Personaje.favorites)).scalar()
    max_fav   = db.query(func.max(Personaje.favorites)).scalar()
    total_fav = db.query(func.sum(Personaje.favorites)).scalar()

    print("\n📊 ESTADÍSTICAS DE PERSONAJES:")
    print("-" * 40)
    print(f"  Total personajes   : {total:,}")
    print(f"  Favoritos promedio : {avg_fav:,.0f}")
    print(f"  Máximo favoritos   : {int(max_fav):,}")
    print(f"  Total favoritos    : {int(total_fav):,}")

# ─── GÉNEROS ──────────────────────────────────────────────────
def top_generos_anime():
    registros = db.query(Anime.genres).all()
    todos = []
    for r in registros:
        if r.genres:
            todos.extend([g.strip() for g in r.genres.split(",") if g.strip()])
    serie = pd.Series(todos).value_counts().head(10)
    print("\n🎭 TOP 10 GÉNEROS MÁS FRECUENTES EN ANIME:")
    print("-" * 40)
    for i, (genero, cantidad) in enumerate(serie.items(), 1):
        barra = "█" * int(cantidad / serie.max() * 20)
        print(f"  {i:>2}. {genero:<25} {barra} {cantidad}")

# ─── MÉTRICAS ETL ─────────────────────────────────────────────
def metricas_etl():
    metricas = db.query(MetricasETL)\
                 .order_by(MetricasETL.fecha_ejecucion.desc())\
                 .limit(5).all()
    print("\n📈 ÚLTIMAS EJECUCIONES DEL ETL:")
    print("-" * 75)
    print(f"  {'Fecha':<25} {'Estado':<10} {'Extraídos':>10} {'Guardados':>10} {'Tiempo':>10}")
    print("  " + "-" * 70)
    for m in metricas:
        print(f"  {str(m.fecha_ejecucion):<25} {m.estado:<10} "
              f"{m.registros_extraidos:>10,} {m.registros_guardados:>10,} "
              f"{m.tiempo_ejecucion_segundos:>9.2f}s")

# ─── MAIN ─────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        print("\n" + "="*75)
        print("              ANÁLISIS COMPLETO — ANIME / MANGA / PERSONAJES")
        print("="*75)

        # Anime
        top10_anime()
        estadisticas_anime()
        anime_por_tipo()
        anime_por_estado()

        # Manga
        top10_manga()
        estadisticas_manga()

        # Personajes
        top10_personajes()
        estadisticas_personajes()

        # Géneros
        top_generos_anime()

        # Métricas
        metricas_etl()

        print("\n" + "="*75 + "\n")

    finally:
        db.close()