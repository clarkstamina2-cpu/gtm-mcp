"""
Suíte de testes do servidor MCP do Google Tag Manager.

Uso:
  MCP_URL=http://localhost:8000 MCP_TOKEN=xxx python test_server.py

As chamadas reais ao GTM são SOMENTE de leitura (list/get). Nada é criado, alterado, publicado ou excluído.
"""
import asyncio
import json
import os

import httpx
from fastmcp import Client

BASE = os.environ.get("MCP_URL", "http://localhost:8000").rstrip("/")
TOKEN = os.environ["MCP_TOKEN"]
EXPECTED_TOOLS = 67


def data_of(result):
    if result.data is not None:
        return result.data
    return json.loads("".join(getattr(c, "text", "") for c in result.content))


async def main():
    async with httpx.AsyncClient() as h:
        r = await h.get(f"{BASE}/health")
        assert r.status_code == 200, f"/health falhou: {r.status_code}"
        print(f"OK  /health público -> {r.json()}")
        r = await h.post(f"{BASE}/mcp", json={})
        assert r.status_code == 401, f"sem token deveria ser 401, veio {r.status_code}"
        print("OK  sem token -> 401")
        r = await h.post(f"{BASE}/mcp?token=errado", json={})
        assert r.status_code == 401, f"token errado deveria ser 401, veio {r.status_code}"
        print("OK  token errado -> 401")
        r = await h.post(f"{BASE}/mcp", json={}, headers={"Authorization": f"Bearer {TOKEN}"})
        assert r.status_code == 401, f"token só no header deveria ser 401, veio {r.status_code}"
        print("OK  token só no header -> 401 (apenas ?token= é aceito)")

    async with Client(f"{BASE}/mcp?token={TOKEN}") as c:
        tools = [t.name for t in await c.list_tools()]
        assert len(tools) == EXPECTED_TOOLS, f"esperava {EXPECTED_TOOLS} tools, vieram {len(tools)}"
        assert len(set(tools)) == len(tools), "há tools duplicadas"
        print(f"OK  token certo -> {len(tools)} tools registradas")

        accounts = data_of(await c.call_tool("list_gtm_accounts", {}))
        accounts = accounts.get("result", accounts) if isinstance(accounts, dict) else accounts
        assert isinstance(accounts, list) and accounts, "list_gtm_accounts não retornou contas"
        print(f"OK  list_gtm_accounts (GTM real) -> {len(accounts)} conta(s)")

        acc_id = str(accounts[0].get("account_id") or accounts[0].get("accountId"))
        containers = data_of(await c.call_tool("list_gtm_containers", {"account_id": acc_id}))
        containers = containers.get("result", containers) if isinstance(containers, dict) else containers
        assert isinstance(containers, list), "list_gtm_containers retorno inesperado"
        print(f"OK  list_gtm_containers (GTM real) -> {len(containers)} contêiner(es)")

        if containers:
            cont_id = str(containers[0].get("container_id") or containers[0].get("containerId"))
            ws = data_of(await c.call_tool("list_gtm_workspaces", {"account_id": acc_id, "container_id": cont_id}))
            print("OK  list_gtm_workspaces (GTM real)")

        try:
            await c.call_tool("get_gtm_account", {"account_id": "0000000"})
            raise AssertionError("conta inexistente deveria dar erro")
        except AssertionError:
            raise
        except Exception as e:
            print(f"OK  conta inexistente -> erro claro ({str(e)[:70]})")

    print("\nTODOS OS TESTES PASSARAM")


asyncio.run(main())
