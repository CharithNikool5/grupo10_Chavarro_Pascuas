#!/usr/bin/env python3
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from scripts.database import Base

class Anime(Base):
    """Modelo para datos de anime"""
    __tablename__ = "anime"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    mal_id        = Column(Integer, unique=True, nullable=False, index=True)
    title         = Column(String(255), nullable=False)
    title_english = Column(String(255), nullable=True)
    type          = Column(String(50),  nullable=True)
    episodes      = Column(Integer,     nullable=True)
    status        = Column(String(100), nullable=True)
    score         = Column(Float,       nullable=True)
    rank          = Column(Integer,     nullable=True)
    popularity    = Column(Integer,     nullable=True)
    favorites     = Column(Integer,     nullable=True)
    synopsis      = Column(Text,        nullable=True)
    year          = Column(Integer,     nullable=True)
    genres        = Column(String(500), nullable=True)
    fecha_carga   = Column(DateTime,    default=datetime.utcnow)

    def __repr__(self):
        return f"<Anime {self.title} | Score: {self.score}>"


class Manga(Base):
    """Modelo para datos de manga"""
    __tablename__ = "manga"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    mal_id        = Column(Integer, unique=True, nullable=False, index=True)
    title         = Column(String(255), nullable=False)
    title_english = Column(String(255), nullable=True)
    type          = Column(String(50),  nullable=True)
    chapters      = Column(Integer,     nullable=True)
    volumes       = Column(Integer,     nullable=True)
    status        = Column(String(100), nullable=True)
    score         = Column(Float,       nullable=True)
    rank          = Column(Integer,     nullable=True)
    popularity    = Column(Integer,     nullable=True)
    favorites     = Column(Integer,     nullable=True)
    synopsis      = Column(Text,        nullable=True)
    genres        = Column(String(500), nullable=True)
    fecha_carga   = Column(DateTime,    default=datetime.utcnow)

    def __repr__(self):
        return f"<Manga {self.title} | Score: {self.score}>"


class Personaje(Base):
    """Modelo para personajes"""
    __tablename__ = "personajes"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    mal_id      = Column(Integer, unique=True, nullable=False, index=True)
    name        = Column(String(255), nullable=False)
    name_kanji  = Column(String(255), nullable=True)
    favorites   = Column(Integer,     nullable=True)
    about       = Column(Text,        nullable=True)
    fecha_carga = Column(DateTime,    default=datetime.utcnow)

    def __repr__(self):
        return f"<Personaje {self.name} | Favoritos: {self.favorites}>"


class MetricasETL(Base):
    """Modelo para registrar métricas de cada ejecución"""
    __tablename__ = "metricas_etl"

    id                          = Column(Integer,  primary_key=True, autoincrement=True)
    fecha_ejecucion             = Column(DateTime, default=datetime.utcnow, index=True)
    registros_extraidos         = Column(Integer,  nullable=False)
    registros_guardados         = Column(Integer,  nullable=False)
    registros_fallidos          = Column(Integer,  default=0)
    tiempo_ejecucion_segundos   = Column(Float,    nullable=False)
    estado                      = Column(String(50),  nullable=False)  # SUCCESS, PARTIAL, FAILED
    mensaje                     = Column(String(500), nullable=True)

    def __repr__(self):
        return f"<MetricasETL {self.fecha_ejecucion} | {self.estado}>"