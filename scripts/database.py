#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, declarative_base
import logging

load_dotenv()
logger = logging.getLogger(__name__)

try:
    import streamlit as st
    DB_HOST     = st.secrets["DB_HOST"].strip()
    DB_PORT     = int(st.secrets["DB_PORT"])
    DB_USER     = st.secrets["DB_USER"].strip()
    DB_PASSWORD = st.secrets["DB_PASSWORD"].strip()
    DB_NAME     = st.secrets["DB_NAME"].strip()
except:
    DB_HOST     = os.getenv('DB_HOST', 'db.ezchuppodybddecvzxht.supabase.co').strip()
    DB_PORT     = int(os.getenv('DB_PORT', '5432'))
    DB_USER     = os.getenv('DB_USER', 'postgres').strip()
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'Mars2905@123').strip()
    DB_NAME     = os.getenv('DB_NAME', 'postgres').strip()

# URL.create maneja caracteres especiales como @ en la contraseña
DATABASE_URL = URL.create(
    drivername = "postgresql+psycopg2",
    username   = DB_USER,
    password   = DB_PASSWORD,
    host       = DB_HOST,
    port       = DB_PORT,
    database   = DB_NAME
)

engine       = create_engine(DATABASE_URL, echo=False)
Base         = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
metadata     = MetaData()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            logger.info("✅ Conexión a PostgreSQL exitosa")
            return True
    except Exception as e:
        logger.error(f"❌ Error conectando a PostgreSQL: {str(e)}")
        return False

def create_all_tables():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tablas creadas exitosamente")
    except Exception as e:
        logger.error(f"❌ Error creando tablas: {str(e)}")