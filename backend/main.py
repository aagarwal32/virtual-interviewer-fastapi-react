from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from db.database import create_tables
from routes import auth

# create tables

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# include routers
app.include_router(auth.router, prefix=settings.API_PREFIX)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    