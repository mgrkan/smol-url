from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel
import redis.asyncio as redis
import shortuuid
import validators

app = FastAPI()
redis_client = redis.Redis(host='redis', db=0)
rate_limiter = redis.Redis(host='redis', db=1)

@app.middleware("http")
async def rate_limit(request: Request, call_next):
    client_ip = request.client.host
    key = f"ratelimit:{client_ip}"

    count = await rate_limiter.incr(key)
    if count == 1:
        await rate_limiter.expire(key, 10) #10 sec window

    if count > 5:
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})

    response = await call_next(request)
    return response


@app.get("/")
async def read_root():
    return {"message": "Hello World"}

class URL(BaseModel):
    target_url: str

@app.post("/shorten")
async def shorten_url(url: URL):
    if not validators.url(url.target_url):
        return {"error": "Invalid URL"}
    short_id = shortuuid.uuid()[:8]
    await redis_client.set(short_id, url.target_url)
    await redis_client.set(f"visit:{short_id}", 0)
    # expires in 2 hours
    await redis_client.expire(short_id, 60 * 60 * 2)
    await redis_client.expire(f"visit:{short_id}", 60 * 60 * 2)

    return {"short_id": short_id}

@app.get("/{short_id}")
async def redirect_to_url(short_id: str):
    url = await redis_client.get(short_id)
    if url:
        await redis_client.incr(f"visit:{short_id}")
        return RedirectResponse(url=url.decode('utf-8'))
    return {"error": "URL not found"}

@app.get("/stats/{short_id}")
async def get_stats(short_id: str):
    url = await redis_client.get(short_id)
    if url:
        return {"url": url.decode('utf-8'), "visits": await redis_client.get(f"visit:{short_id}")}
    return {"error": "URL not found"}