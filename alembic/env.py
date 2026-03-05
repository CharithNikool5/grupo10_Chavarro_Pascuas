import os
import sys
from dotenv import load_dotenv
from sqlalchemy import pool
from alembic import context

load_dotenv()
sys.path.insert(0, '.')

from scripts.database import engine, Base
from scripts.models import Anime, Manga, Personaje, MetricasETL

config = context.config
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    from scripts.database import DATABASE_URL
    context.configure(
        url=str(DATABASE_URL),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
