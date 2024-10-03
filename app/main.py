from fastapi import FastAPI
import asyncio
from .routes import router
from .db import init_db

# FastAPI app is defined
app = FastAPI()

app.include_router(router)

@app.on_event("startup")
async def startup_event():
    await init_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)





