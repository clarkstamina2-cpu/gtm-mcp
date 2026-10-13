"""
Gera um novo GTM_REFRESH_TOKEN com todos os escopos que as ferramentas do MCP precisam.

Uso (no seu computador, na pasta do projeto):
    python scripts/gerar_refresh_token.py
    python scripts/gerar_refresh_token.py --no-browser   (só mostra o link, para abrir em outro navegador/perfil)
    python scripts/gerar_refresh_token.py --manual       (outra pessoa autoriza no computador dela e te envia o endereço
                                                          da página de erro; você cola aqui)

O que acontece:
  1. Lê GTM_CLIENT_ID e GTM_CLIENT_SECRET do ambiente ou do arquivo .env local.
  2. Abre o navegador na tela de consentimento do Google. Entre com a conta que tem acesso às contas do GTM
     e clique em Permitir.
  3. Troca o código pelo token e GRAVA o GTM_REFRESH_TOKEN no .env local (ele NÃO é impresso na tela).
  4. Mostra quais escopos o Google concedeu.

Depois, copie o GTM_REFRESH_TOKEN do .env para as variáveis de ambiente do Easypanel e faça o deploy.
Só usa a biblioteca padrão do Python. Nenhuma credencial fica neste arquivo.
"""
import json
import os
import re
import secrets
import sys
import threading
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

PORT = 8085
REDIRECT_URI = f"http://localhost:{PORT}/"
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"

# Remova daqui os escopos que você não quer liberar (as ferramentas correspondentes passam a dar 403).
SCOPES = [
    "https://www.googleapis.com/auth/tagmanager.edit.containers",         # tags, acionadores, variáveis, modelos, gtag_config...
    "https://www.googleapis.com/auth/tagmanager.edit.containerversions",  # criar, excluir e restaurar versões
    "https://www.googleapis.com/auth/tagmanager.publish",                 # publish_gtm_version
    "https://www.googleapis.com/auth/tagmanager.manage.users",            # permissões de usuários (conta e contêiner)
    "https://www.googleapis.com/auth/tagmanager.manage.accounts",         # update_gtm_account
    # Propositalmente NÃO pedimos "tagmanager.delete.containers": o MCP não deve conseguir excluir contêineres
    # (delete_gtm_container fica sem permissão e devolve 403).
]


def read_env_file() -> dict:
    values = {}
    if ENV_FILE.is_file():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                values[k.strip()] = v.strip().strip("'\"")
    return values


def get_setting(name: str, file_values: dict) -> str:
    value = os.environ.get(name) or file_values.get(name, "")
    if not value:
        sys.exit(f"ERRO: {name} não encontrado no ambiente nem no .env.")
    return value


def wait_for_code(state: str) -> str:
    result = {}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if "code" in query and query.get("state", [""])[0] == state:
                result["code"] = query["code"][0]
                message = "Autorizado! Pode fechar esta aba e voltar ao terminal."
            else:
                result["error"] = query.get("error", ["resposta inválida"])[0]
                message = f"Falhou: {result['error']}. Volte ao terminal."
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(f"<html><body style='font-family:sans-serif'><h2>{message}</h2></body></html>".encode("utf-8"))

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", PORT), Handler)
    server.timeout = 300
    thread = threading.Thread(target=server.handle_request)
    thread.start()
    thread.join(timeout=305)
    server.server_close()
    if "code" not in result:
        sys.exit(f"ERRO: autorização não concluída ({result.get('error', 'tempo esgotado')}).")
    return result["code"]


def ask_for_pasted_url(state: str) -> str:
    """Modo --manual: outra pessoa autoriza no computador dela e envia o endereço da página que deu erro
    (http://localhost:8085/?state=...&code=...). Cole esse endereço aqui."""
    print("Envie o link acima para quem tem acesso ao GTM. Depois de clicar em Permitir, o navegador dela vai mostrar")
    print("uma página de erro ('Não foi possível acessar o site'). É normal: peça para ela copiar o ENDEREÇO COMPLETO")
    print("dessa página (começa com http://localhost:8085/?state=...) e te enviar.\n", flush=True)
    pasted = input("Cole aqui o endereço completo e tecle Enter: ").strip()
    query = urllib.parse.parse_qs(urllib.parse.urlparse(pasted).query)
    if query.get("state", [""])[0] != state:
        sys.exit("ERRO: o endereço colado não corresponde a este link (state diferente). Gere o link de novo e refaça.")
    if "code" not in query:
        sys.exit(f"ERRO: o endereço não tem código de autorização ({query.get('error', ['sem erro informado'])[0]}).")
    return query["code"][0]


def save_refresh_token(token: str) -> None:
    text = ENV_FILE.read_text(encoding="utf-8") if ENV_FILE.is_file() else ""
    if re.search(r"^GTM_REFRESH_TOKEN=.*$", text, flags=re.M):
        text = re.sub(r"^GTM_REFRESH_TOKEN=.*$", lambda _: f"GTM_REFRESH_TOKEN={token}", text, flags=re.M)
    else:
        text = text.rstrip("\n") + f"\nGTM_REFRESH_TOKEN={token}\n"
    ENV_FILE.write_text(text, encoding="utf-8")


def main() -> None:
    file_values = read_env_file()
    client_id = get_setting("GTM_CLIENT_ID", file_values)
    client_secret = get_setting("GTM_CLIENT_SECRET", file_values)

    state = secrets.token_urlsafe(16)
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(
        {
            "client_id": client_id,
            "redirect_uri": REDIRECT_URI,
            "response_type": "code",
            "scope": " ".join(SCOPES),
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        }
    )
    manual = "--manual" in sys.argv
    if manual:
        print("Link de autorização (envie para quem tem acesso ao GTM):")
        print("\n" + auth_url + "\n", flush=True)
    elif "--no-browser" in sys.argv:
        print("Abra este endereço no navegador DESTE computador (use o navegador/perfil da conta que tem acesso ao GTM):")
        print("\n" + auth_url + "\n", flush=True)
    else:
        print("Abrindo o navegador para autorizar. Entre com a conta que tem acesso ao GTM e clique em Permitir.")
        print("Se o navegador não abrir, copie este endereço:\n" + auth_url + "\n", flush=True)
        webbrowser.open(auth_url)

    code = ask_for_pasted_url(state) if manual else wait_for_code(state)
    payload = urllib.parse.urlencode(
        {
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
        }
    ).encode("utf-8")
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=payload, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            tokens = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        sys.exit(f"ERRO ao trocar o código pelo token: {e.read().decode('utf-8')}")

    refresh_token = tokens.get("refresh_token")
    if not refresh_token:
        sys.exit("ERRO: o Google não devolveu refresh_token. Tente de novo.")

    granted = set(tokens.get("scope", "").split())
    save_refresh_token(refresh_token)
    print(f"Novo GTM_REFRESH_TOKEN gravado em {ENV_FILE} (não foi impresso na tela).\n")
    for scope in SCOPES:
        print(("  concedido  " if scope in granted else "  FALTANDO   ") + scope.rsplit("/", 1)[-1])
    missing = [s for s in SCOPES if s not in granted]
    if missing:
        print("\nATENÇÃO: alguns escopos não foram concedidos; as ferramentas ligadas a eles continuarão dando 403.")
    print("\nPróximo passo: copie GTM_REFRESH_TOKEN do .env para o Easypanel e faça o deploy.")


if __name__ == "__main__":
    main()
