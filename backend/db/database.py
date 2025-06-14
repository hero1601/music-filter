from contextlib import asynccontextmanager
from databases import Database
from services import semantic_search
from config import DATABASE_URL

database = Database(DATABASE_URL)

@asynccontextmanager
async def lifespan(app):
    await database.connect()
    await semantic_search.build_embeddings(database)
    yield
    await database.disconnect()