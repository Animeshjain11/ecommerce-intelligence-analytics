import os
from urllib.parse import quote_plus

import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()


def get_setting(key, default=None):
    try:
        value = st.secrets.get(key)
        if value is not None:
            return value
    except Exception:
        pass

    return os.getenv(key, default)


@st.cache_resource
def get_engine():
    user = get_setting("DB_USER", "postgres")
    password = get_setting("DB_PASSWORD")
    host = get_setting("DB_HOST", "localhost")
    port = get_setting("DB_PORT", "5432")
    database = get_setting("DB_NAME", "ecommerce_analytics")

    if not password:
        raise ValueError("DB_PASSWORD environment variable or Streamlit secret is missing.")

    connection_url = (
        f"postgresql+psycopg2://{quote_plus(user)}:"
        f"{quote_plus(password)}@{host}:{port}/{database}"
    )

    return create_engine(connection_url, pool_pre_ping=True)


def test_connection():
    engine = get_engine()
    with engine.connect() as connection:
        return connection.execute(text("SELECT 1")).scalar()
