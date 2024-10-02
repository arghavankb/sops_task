from fastapi import FastAPI
import asyncio
from .routes import router
from .db import init_db

# FastAPI app is defined
app = FastAPI()

app.include_router(router)


@app.on_event("startup")
async def main():
    await init_db()


if __name__ == "__main__":
    asyncio.run(main())






