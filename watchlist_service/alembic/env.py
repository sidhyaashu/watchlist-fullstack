import os
import sys
from pathlib import Path

# Ensure the watchlist_service root is on sys.path so 'app' is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from logging.config import fileConfig
from dotenv import load_dotenv

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Load environment variables from .env (resolved relative to this file's location)
_service_root = Path(__file__).resolve().parents[1]
load_dotenv(_service_root / ".env")

# Import Base and all models so their tables are registered for autogenerate
from app.db.base import Base  # noqa: F401
import app.models.watchlist      # noqa: F401
import app.models.watchlist_item  # noqa: F401

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# Override sqlalchemy.url with the correct sync URL for Alembic
# Prefer ALEMBIC_DATABASE_URL (psycopg2), fall back to converting DATABASE_URL
_db_url = os.getenv("ALEMBIC_DATABASE_URL") or os.getenv("DATABASE_URL", "")
if _db_url:
    # Ensure we're using the sync psycopg2 driver, not asyncpg
    _db_url = _db_url.replace("postgresql+asyncpg", "postgresql").replace("+asyncpg", "")
    config.set_main_option("sqlalchemy.url", _db_url)

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def include_object(object, name, type_, reflected, compare_to):
    """
    Only include objects that are in our metadata.
    This avoids dropping tables from other services in a shared DB.
    """
    if type_ == "table" and reflected and name not in target_metadata.tables:
        return False
    return True



def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table="alembic_version_watchlist",
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            version_table="alembic_version_watchlist",
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
