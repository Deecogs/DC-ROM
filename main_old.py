# main.py
import uvicorn
from fastapi import FastAPI
from api.endpoints import router

app = FastAPI(
    title="ROM Calculator API",
    description="API for Range of Motion calculations using pose estimation",
    version="1.0.0"
)

app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "ROM Calculator API is running"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
# uvicorn main:app --reload --host 0.0.0.0 --port 8000