from dotenv import load_dotenv

load_dotenv()
import os
from urllib.parse import quote_plus

import streamlit as st
from sqlalchemy import create_engine, text


@st.cache_resource
def get_engine():
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_NAME", "ecommerce_analytics")

    if not password:
        raise ValueError("DB_PASSWORD environment variable is missing.")

    connection_url = (
        f"postgresql+psycopg2://{quote_plus(user)}:"
        f"{quote_plus(password)}@{host}:{port}/{database}"
    )

    return create_engine(
        connection_url,
        pool_pre_ping=True
    )


def test_connection():
    engine = get_engine()

    with engine.connect() as connection:
        return connection.execute(text("SELECT 1")).scalar()
