from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import init_db
from router import auth, post


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application start")
    await init_db()

    yield
    print("Application shutdown")

app = FastAPI(title="Blog_Post", lifespan=lifespan)

app.include_router(auth.router)
app.include_router(post.router)


@app.get("/")
def read():
    return {"Message": "Hello..."}
