from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json as json_file  # pyright: ignore[reportMissingImports]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/sports")
def get_sports():
    return json_file.load(open("work.json"))