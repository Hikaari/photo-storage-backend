
from fastapi import FastAPI
from starlette_prometheus import PrometheusMiddleware, metrics

from src.api.v1 import auth, photos, hashtags

app = FastAPI()

app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", metrics)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(photos.router, prefix="/api/v1/photos", tags=["photos"])
app.include_router(hashtags.router, prefix="/api/v1/hashtags", tags=["hashtags"])

@app.get("/health")
def health():
    return {"status": "ok"}
