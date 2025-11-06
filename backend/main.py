
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services import optimize

app = FastAPI(title="AI Travel Clustering API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(optimize.router)

@app.get("/")
def root():
    return {"ok": True, "service": "clustering"}
