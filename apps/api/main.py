from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import init_db
from routers import upload, chat, nango
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Database initialization
init_db()

# CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static Files (Uploads)
# Ensure directory exists again just in case
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Routers
app.include_router(upload.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(nango.router, prefix="/api/nango")

@app.get("/")
def read_root():
    return {"Hello": "DocuStream API"}

@app.get("/api/health")
def health_check():
    return {"status": "ok"}
