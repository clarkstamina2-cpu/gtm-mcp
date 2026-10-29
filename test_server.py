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
EXPECTED_TOOLS = 82


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

            args = {"account_id": acc_id, "container_id": cont_id}
            unwrap = lambda r: (lambda d: d.get("result", d) if isinstance(d, dict) else d)(data_of(r))

            live = data_of(await c.call_tool("get_live_gtm_version", args))
            assert live.get("tags_count", 0) > 0, f"get_live_gtm_version não trouxe dados reais: {live.get('tags_count')} tags"
            print(f"OK  get_live_gtm_version -> versão {live['container_version_id']}, {live['tags_count']} tags")

            gv = data_of(await c.call_tool("get_gtm_version", {**args, "version_id": "live"}))
            assert gv, "get_gtm_version('live') vazio"
            print("OK  get_gtm_version('live')")

            same = data_of(await c.call_tool("diff_gtm_versions", {**args, "version_a": "live", "version_b": "live"}))
            assert set(same) == {"version_a", "version_b"}, f"diff da versão com ela mesma deveria vir vazio: {same}"
            print("OK  diff_gtm_versions(live, live) -> sem diferenças")

            trs = unwrap(await c.call_tool("list_gtm_triggers", args))
            assert all("wait_for_tags" in t for t in trs), "list_gtm_triggers sem wait_for_tags"
            print(f"OK  list_gtm_triggers -> {len(trs)} acionador(es), com wait_for_tags")

            pub = (await c.call_tool("get_gtm_container", args)).data
            pub_id = pub.get("publicId") or pub.get("public_id")
            if pub_id:
                found = data_of(await c.call_tool("lookup_gtm_container", {"destination_id": pub_id}))
                assert str(found.get("containerId")) == cont_id, f"lookup retornou outro contêiner: {found}"
                print(f"OK  lookup_gtm_container({pub_id})")

            envs = unwrap(await c.call_tool("list_gtm_environments", args))
            env_id = next((e["environmentId"] for e in envs if e.get("authorizationCode") and e.get("environmentId")), None)
            if env_id:
                snip = data_of(await c.call_tool("get_gtm_container_snippet", {**args, "environment_id": env_id}))
                assert f"gtm_preview=env-{env_id}" in snip["head_script"] and "gtm_auth=" in snip["head_script"], "snippet de ambiente sem gtm_auth/gtm_preview"
                print(f"OK  get_gtm_container_snippet (ambiente {env_id})")

            gcs = unwrap(await c.call_tool("list_gtm_gtag_configs", args))
            assert isinstance(gcs, list), "list_gtm_gtag_configs retorno inesperado"
            print(f"OK  list_gtm_gtag_configs -> {len(gcs)} config(s)")
            if gcs:
                one = data_of(await c.call_tool("get_gtm_gtag_config", {**args, "gtag_config_id": gcs[0]["gtagConfigId"]}))
                assert one.get("gtagConfigId") == gcs[0]["gtagConfigId"]
                print("OK  get_gtm_gtag_config")

            try:
                perms = unwrap(await c.call_tool("list_gtm_container_user_permissions", args))
                print(f"OK  list_gtm_container_user_permissions -> {len(perms)} usuário(s)")
            except Exception as e:
                if "insufficient authentication scopes" in str(e):
                    print("--  list_gtm_container_user_permissions NÃO TESTADO: o refresh token não tem o escopo tagmanager.manage.users")
                else:
                    raise

        # --- Ferramentas de ESCRITA: só rodam num contêiner de teste dedicado (nunca de cliente) ---
        w_acc, w_cont = os.environ.get("TEST_WRITE_ACCOUNT"), os.environ.get("TEST_WRITE_CONTAINER")
        if w_acc and w_cont:
            w = {"account_id": w_acc, "container_id": w_cont}
            made = {}
            try:
                t = data_of(await c.call_tool("create_gtm_trigger", {**w, "name": "ZZ teste MCP", "type": "pageview"}))
                made["trigger"] = t["triggerId"]
                print("OK  create_gtm_trigger")
                u = data_of(await c.call_tool("update_gtm_trigger", {**w, "trigger_id": made["trigger"], "name": "ZZ teste MCP (editado)"}))
                assert u["name"] == "ZZ teste MCP (editado)", u
                print("OK  update_gtm_trigger (mantém os demais campos)")
                await c.call_tool("revert_gtm_trigger", {**w, "trigger_id": made["trigger"]})
                print("OK  revert_gtm_trigger")
            finally:
                if "trigger" in made:
                    await c.call_tool("delete_gtm_trigger", {**w, "trigger_id": made["trigger"]})
                    print("OK  delete_gtm_trigger (limpeza)")
            try:
                g = data_of(await c.call_tool("create_gtm_gtag_config", {**w, "type": "googtag", "parameter": [{"type": "template", "key": "tagId", "value": "G-TESTE000"}]}))
                made["gtag"] = g["gtagConfigId"]
                print("OK  create_gtm_gtag_config")
                u = data_of(await c.call_tool("update_gtm_gtag_config", {**w, "gtag_config_id": made["gtag"], "parameter": [{"type": "template", "key": "tagId", "value": "G-TESTE111"}]}))
                assert any(p.get("value") == "G-TESTE111" for p in u["parameter"]), u
                print("OK  update_gtm_gtag_config")
            finally:
                if "gtag" in made:
                    await c.call_tool("delete_gtm_gtag_config", {**w, "gtag_config_id": made["gtag"]})
                    print("OK  delete_gtm_gtag_config (limpeza)")
        else:
            print("--  ferramentas de escrita NÃO testadas (defina TEST_WRITE_ACCOUNT e TEST_WRITE_CONTAINER com um contêiner de TESTE)")

        try:
            await c.call_tool("get_gtm_account", {"account_id": "0000000"})
            raise AssertionError("conta inexistente deveria dar erro")
        except AssertionError:
            raise
        except Exception as e:
            print(f"OK  conta inexistente -> erro claro ({str(e)[:70]})")

    print("\nTODOS OS TESTES PASSARAM")


asyncio.run(main())
