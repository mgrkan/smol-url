from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import redis
import shortuuid
import validators

app = FastAPI()
redis_client = redis.Redis(host='redis', db=0)

@app.get("/")
def read_root():
    return {"message": "Hello World"}

class URL(BaseModel):
    target_url: str

@app.post("/shorten")
def shorten_url(url: URL):
    if not validators.url(url.target_url):
        return {"error": "Invalid URL"}
    short_id = shortuuid.uuid()[:8]
    redis_client.set(short_id, url.target_url)
    redis_client.set(f"visit:{short_id}", 0)
    return {"short_id": short_id}

@app.get("/{short_id}")
def redirect_to_url(short_id: str):
    url = redis_client.get(short_id)
    if url:
        redis_client.incr(f"visit:{short_id}")
        return RedirectResponse(url=url.decode('utf-8'))
    return {"error": "URL not found"}

@app.get("/stats/{short_id}")
def get_stats(short_id: str):
    url = redis_client.get(short_id)
    if url:
        return {"url": url.decode('utf-8'), "visits": redis_client.get(f"visit:{short_id}")}
    return {"error": "URL not found"}