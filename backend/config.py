import os

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "lyrics123")
DB_HOST = os.getenv("DB_HOST", "localhost")  # Use host.docker.internal for Docker
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "lyrics_db")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Debug: Print the connection string (remove in production)
print(f"Connecting to: {DATABASE_URL}")