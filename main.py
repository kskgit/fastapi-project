from fastapi import FastAPI

from app.router import main_router  # ルーターをインポート

app = FastAPI(title="FastAPI Project", version="0.1.0")

# ルーターを登録
app.include_router(main_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
