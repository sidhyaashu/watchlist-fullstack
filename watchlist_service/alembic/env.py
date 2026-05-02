import asyncio
import os
import sys
from pathlib import Path
from logging.config import fileConfig

# Ensure the watchlist_service root is on sys.path so 'app' is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# Load environment variables from .env
_service_root = Path(__file__).resolve().parents[1]
load_dotenv(_service_root / ".env")

# Import Base and all models so their tables are registered for autogenerate
from app.db.base import Base  # noqa: F401
import app.watchlist.models.watchlist      # noqa: F401
import app.watchlist.models.watchlist_item  # noqa: F401

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def include_object(object, name, type_, reflected, compare_to):
    """
    Only include objects that are in our metadata.
    This avoids dropping tables from other services in a shared DB.
    """
    if type_ == "table" and reflected and name not in target_metadata.tables:
        return False
    return True

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    _db_url = os.getenv("DATABASE_URL", config.get_main_option("sqlalchemy.url"))
    context.configure(
        url=_db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table="alembic_version_watchlist",
        version_table_schema="app",
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection, 
        target_metadata=target_metadata,
        version_table="alembic_version_watchlist",
        version_table_schema="app",
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """In this scenario we need to create an async Engine"""
    _db_url = os.getenv("DATABASE_URL", config.get_main_option("sqlalchemy.url"))
    
    connectable = create_async_engine(
        _db_url,
        poolclass=pool.NullPool,
    )

    # Step 1: Create the schema in AUTOCOMMIT mode (DDL outside a transaction).
    # This is required because CREATE SCHEMA cannot run inside a transaction
    # that also creates tables within the same schema on PostgreSQL/asyncpg.
    async with connectable.connect() as connection:
        from sqlalchemy import text
        await connection.execute(text("CREATE SCHEMA IF NOT EXISTS app"))
        await connection.commit()

    # Step 2: Run the actual Alembic migrations (creates tables) in a fresh connection.
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
