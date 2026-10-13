import hmac
import logging
import os
import sys
from urllib.parse import parse_qs

import uvicorn
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("gtm_mcp.server")

# Falha ao iniciar se faltar variável obrigatória (configurar no Easypanel).
REQUIRED_ENV = ("MCP_TOKEN", "GTM_CLIENT_ID", "GTM_CLIENT_SECRET", "GTM_REFRESH_TOKEN")
_missing = [name for name in REQUIRED_ENV if not os.environ.get(name, "").strip()]
if _missing:
    sys.exit(f"ERRO: variável(is) de ambiente obrigatória(s) ausente(s): {', '.join(_missing)} (configure no Easypanel).")

MCP_TOKEN = os.environ["MCP_TOKEN"].strip()
PORT = int(os.environ.get("PORT", "8000"))
HOST = os.environ.get("HOST", "0.0.0.0")
PUBLIC_PATHS = {"/health"}

from gtm_mcp.coordinator import mcp  # noqa: E402

# Registra todas as tools do GTM
from gtm_mcp.tools import (  # noqa: E402,F401
    accounts,
    containers,
    workspaces,
    tags,
    triggers,
    variables,
    folders,
    templates,
    zones,
    versions,
)


@mcp.custom_route("/health", methods=["GET"])
async def health(_: Request) -> JSONResponse:
    return JSONResponse({"status": "ok", "transport": "streamable-http", "endpoint": "/mcp"})


class TokenNaURL:
    """Middleware ASGI puro (não interfere no streaming) que valida o token na URL: /mcp?token=<MCP_TOKEN>."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope["path"] not in PUBLIC_PATHS:
            qs = parse_qs(scope.get("query_string", b"").decode())
            token = (qs.get("token") or [""])[0]
            # Comparação em tempo constante; nunca logar a URL completa (contém o token)
            if not hmac.compare_digest(token.encode(), MCP_TOKEN.encode()):
                client = scope.get("client") or ("desconhecido",)
                logger.warning(f"[401] Acesso bloqueado em {scope['path']} (IP: {client[0]}) - token ausente ou invalido")
                await JSONResponse({"error": "unauthorized"}, status_code=401)(scope, receive, send)
                return
        await self.app(scope, receive, send)


app = mcp.http_app(path="/mcp", middleware=[Middleware(TokenNaURL)], stateless_http=True)


def run_server() -> None:
    logger.info(f"Iniciando Google Tag Manager MCP (Streamable HTTP) em http://{HOST}:{PORT}/mcp")
    uvicorn.run(app, host=HOST, port=PORT, proxy_headers=True, forwarded_allow_ips="*")


if __name__ == "__main__":
    run_server()
