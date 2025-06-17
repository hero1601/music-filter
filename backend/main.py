from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import songs, search
from db.database import lifespan

app = FastAPI(lifespan=lifespan)

app.include_router(songs.router)
app.include_router(search.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
