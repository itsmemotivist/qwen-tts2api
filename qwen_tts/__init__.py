import os
import logging
import aiofiles
import aiohttp
from aiohttp import web
from gradio_client import Client

logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(levelname)s: %(message)s')
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.INFO)
BASE_URL = os.getenv("BASE_URL") or "https://qwen-qwen3-tts-demo.ms.show"
HTTP_PORT = int(os.getenv("HTTP_PORT") or 80)
USER_AGENT = "Mozilla/5.0 AppleWebKit/537.36 Chrome/143 Safari/537"

SESSION = None
DEFAULT_VOICE = "Vivian / 十三"
VOICE_LIST = None
LANGUAGE_LIST = None

def get_client():
    return Client(BASE_URL)

async def init_session(app):
    global SESSION
    SESSION = aiohttp.ClientSession(
        base_url=BASE_URL,
    )

async def api_request(api, json=None, headers=None, **kwargs):
    _LOGGER.info("%s: %s", api, json)
    return await SESSION.post(
        api,
        json=json,
        headers={
            aiohttp.hdrs.USER_AGENT: USER_AGENT,
            aiohttp.hdrs.REFERER: BASE_URL,
            **(headers or {}),
        },
        **kwargs,
    )

async def get_models(request):
    models = [
        {"id": "qwen-tts"},
    ]
    await get_voices()
    global DEFAULT_VOICE
    if VOICE_LIST and DEFAULT_VOICE not in VOICE_LIST:
        DEFAULT_VOICE = list(VOICE_LIST.values())[0]
    return web.json_response({"data": models, "voices": VOICE_LIST, "languages": LANGUAGE_LIST})

async def get_voices():
    global VOICE_LIST, LANGUAGE_LIST
    if VOICE_LIST:
        return VOICE_LIST
    VOICE_LIST = {}
    LANGUAGE_LIST = {}
    gradio = Client(BASE_URL)
    for endpoint in gradio.endpoints.values():
        for param in endpoint.parameters_info or []:
            name = param.get("parameter_name")
            for val in param.get("type", {}).get("enum", []):
                vid = str(val).lower().split("/")[0].strip()
                if name == "voice_display":
                    VOICE_LIST.setdefault(vid, val)
                if name == "language_display":
                    LANGUAGE_LIST.setdefault(vid, val)
    return VOICE_LIST

async def audio_speech(request):
    if not await check_auth(request):
        return web.json_response({"error": "Unauthorized"}, status=401)
    payload = await request.json() if request.content_type == "application/json" else request.query
    text = payload.get("input", "")
    if not text:
        return web.json_response({"error": "No input text"}, status=400)
    voice_id = payload.get("voice")
    voice_name = (await get_voices()).get(voice_id) or DEFAULT_VOICE
    gradio = Client(BASE_URL)
    audio_path = gradio.predict(
        api_name="/tts_interface",
        text=text,
        voice_display=voice_name,
    )
    gradio.close()

    if not audio_path or not os.path.exists(audio_path):
        return web.json_response({"error": "No audio"}, status=500)
    _LOGGER.info("Audio from %s for text: %s %s", voice_name, text, audio_path)

    resp = web.StreamResponse(status=200, headers={
        aiohttp.hdrs.CONTENT_TYPE: "audio/wav",
    })
    await resp.prepare(request)

    try:
        async with aiofiles.open(audio_path, "rb") as f:
            while True:
                chunk = await f.read(1024)
                if not chunk:
                    break
                await resp.write(chunk)
    except Exception:
        _LOGGER.error("Error reading audio file", exc_info=True)

    await resp.write_eof()
    os.remove(audio_path)
    return resp

async def check_auth(request):
    if apikey := os.getenv("API_KEY"):
        auth_header = request.headers.get("Authorization", "")
        if auth_header not in [apikey, f"Bearer {apikey}"]:
            return False
    return True


@web.middleware
async def cors_auth_middleware(request, handler):
    request.response_factory = lambda: web.StreamResponse()
    response = await handler(request)
    response.headers[aiohttp.hdrs.ACCESS_CONTROL_ALLOW_ORIGIN] = "*"
    response.headers[aiohttp.hdrs.ACCESS_CONTROL_ALLOW_METHODS] = "GET, POST, OPTIONS"
    response.headers[aiohttp.hdrs.ACCESS_CONTROL_ALLOW_HEADERS] = "Content-Type, Authorization"
    return response

async def on_cleanup(app):
    if SESSION:
        await SESSION.close()

def main():
    app = web.Application(logger=_LOGGER, middlewares=[cors_auth_middleware])
    app.on_startup.append(init_session)

    app.router.add_get("/v1/models", get_models)
    app.router.add_route("*", "/v1/audio/speech", audio_speech)

    app.on_cleanup.append(on_cleanup)
    web.run_app(app, host="0.0.0.0", port=HTTP_PORT)

if __name__ == "__main__":
    main()
