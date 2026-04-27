#!/usr/bin/env python3

from time import time

from fastapi import FastAPI, Request, HTTPException, WebSocket, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from authlib.integrations.starlette_client import OAuth

from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from starlette.websockets import WebSocketState

import asyncio
from secrets import token_urlsafe
from json import loads as json_loads

from rcon import get_rcon, send_message, read_message
from restart import restart

app = FastAPI(openapi_url=None)

app.add_middleware(SessionMiddleware, secret_key=token_urlsafe(32))

config = Config()

outh = OAuth(config)

outh.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=config("GOOGLE_OAUTH_CLIENT_ID"),
    client_secret=config("GOOGLE_OAUTH_CLIENT_SECRET"),
    client_kwargs=({"scope": "openid"})
)

WHITE_LIST = set(config("WHITE_LISTED_GOOGLE_OPEN_IDS").split(","))

ORIGINAL_PAGE = config("ORIGINAL_PAGE")

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def homepage(request: Request):
    token = request.cookies.get("token")
    if not token or token not in TOKENS:
        return RedirectResponse(url="/login")
    
    return templates.TemplateResponse(
        request=request, name="index.html", context={"original_page": ORIGINAL_PAGE}
    )

@app.websocket("/")
async def rcon_ws (websocket: WebSocket):
    token = websocket.cookies.get("token")
    if not token or token not in TOKENS:
        await websocket.close(code=4401)
        return

    try:
        async with get_rcon() as rcon:
            await websocket.accept()
            
            async def web_to_rcon():
                while True:
                    raw = await websocket.receive_text()
                    message = json_loads(raw).get("Message")
                    await send_message(rcon, message)

            async def rcon_to_web():
                while True:
                    message = await read_message(rcon)
                    await websocket.send_text(message)

            await asyncio.gather(web_to_rcon(), rcon_to_web())
    except:
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await websocket.close()

@app.get("/login")
async def login(request: Request):
    redirect_uri = str(request.url_for('auth')).replace('http:', 'https:')
    return await outh.google.authorize_redirect(request, redirect_uri)

TOKENS = {}

@app.get("/auth/google/callback")
async def auth(request: Request, response: Response):
    token = await outh.google.authorize_access_token(request)
    user_id = token.get("userinfo").get("sub")
    
    if user_id not in WHITE_LIST:
        raise HTTPException(status_code=403, detail=f"{user_id} isn't whitelisted")
    
    token = token_urlsafe(32)
    TOKENS[token] = user_id
    
    response = RedirectResponse(url="/")
    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
        max_age=86400,
        secure=True,
        samesite="lax"
    )
    
    return response

@app.post("/logout")
async def logout(request: Request):
    request.session.pop('authorised', None)
    return RedirectResponse(url="/login")

@app.post("/docker/restart")
async def restart_docker():
    await restart()
    return Response(status_code=201)

@app.post("/rcon/post")
async def rcon_post(request: Request):
    body = await request.json()
    message = body.get("message")
    if not message:
        raise HTTPException(status_code=400, detail="Missing message")

    responses = []

    rcon = await get_rcon().__aenter__()

    try:
        await send_message(rcon, message)

        while True:
            try:
                msg = await asyncio.wait_for(read_message(rcon), timeout=1)
                responses.append(msg)
            except asyncio.TimeoutError:
                return {"responses": responses}

    finally:
        asyncio.create_task(rcon.close())
