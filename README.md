# Google Tag Manager (GTM) MCP Server

Servidor MCP (Model Context Protocol) completo e exaustivo para o **Google Tag Manager API v2**.

Construído com **FastMCP**, via **Streamable HTTP (`/mcp`)**, no padrão de servidores MCP da Stamina. Compatível com Claude Web, Claude Desktop, Claude Code, ChatGPT e Antigravity.

---

## 🔒 Segurança

1. **Token na URL:** todo acesso ao `/mcp` exige `?token=<MCP_TOKEN>`. Sem token ou com token errado, a resposta é HTTP 401. O tráfego vai por HTTPS, então a URL viaja criptografada.
2. **Zero credenciais no Git:** `MCP_TOKEN` e as credenciais do Google (`GTM_CLIENT_ID`, `GTM_CLIENT_SECRET`, `GTM_REFRESH_TOKEN`) ficam só nas variáveis de ambiente do Easypanel.
3. **Falha ao iniciar:** se alguma variável obrigatória estiver ausente, o servidor não sobe e informa qual está faltando.
4. `/health` é público (para o healthcheck) e não expõe dados.

---
## 🛠️ Lista Completa de Ferramentas (80 Tools)

### 1. Contas & Permissões (Accounts & User Permissions)
- `list_gtm_accounts`: Lista todas as contas de clientes da agência.
- `get_gtm_account(account_id)`: Detalha uma conta específica.
- `update_gtm_account(account_id, name, share_data?)`: Atualiza nome ou preferências da conta.
- `list_gtm_account_user_permissions(account_id)`: Lista permissões de usuários na conta.
- `get_gtm_account_user_permission(account_id, user_permission_id)`: Detalha permissões de um usuário.
- `create_gtm_account_user_permission(account_id, email, permission, container_access?)`: Adiciona novo usuário à conta.
- `update_gtm_account_user_permission(account_id, user_permission_id, permission?, container_access?)`: Altera permissões de um usuário.
- `delete_gtm_account_user_permission(account_id, user_permission_id)`: Remove um usuário da conta.

### 2. Contêineres, Snippets & Ambientes (Containers & Environments)
- `list_gtm_containers(account_id)`: Lista contêineres (`GTM-XXXXXX`) de uma conta.
- `get_gtm_container(account_id, container_id)`: Detalha um contêiner.
- `lookup_gtm_container(destination_id)`: Busca rápida de contêiner por ID de destino (`GTM-XXXXXX`, `GT-XXXXXX`, `AW-XXXXXX`).
- `get_gtm_container_snippet(account_id, container_id, environment_id?)`: **Gera os códigos de rastreamento HTML/JS (<script> e <noscript>) para instalar no site do cliente.**
- `search_gtm_containers(query)`: **Busca inteligente** por nome de cliente ou código em todas as contas.
- `create_gtm_container(account_id, name, usage_context)`: Cria novo contêiner (Web, Server, AMP, etc.).
- `update_gtm_container(account_id, container_id, name?, usage_context?)`: Atualiza contêiner.
- `delete_gtm_container(account_id, container_id)`: Exclui um contêiner.
- `list_gtm_container_user_permissions(account_id, container_id)`: Lista os usuários com acesso a um contêiner (filtra as permissões da conta).
- `create_gtm_container_user_permission(account_id, container_id, email, permission)`: Concede acesso a um contêiner (se o usuário já existe na conta, só adiciona/atualiza o acesso a esse contêiner).
- `list_gtm_environments(account_id, container_id)`: Lista ambientes (Live, Staging, QA).
- `get_gtm_environment(account_id, container_id, environment_id)`: Detalha um ambiente.

### 3. Espaços de Trabalho (Workspaces)
- `list_gtm_workspaces(account_id, container_id)`: Lista workspaces do contêiner.
- `get_gtm_workspace(account_id, container_id, workspace_id)`: Detalha um workspace.
- `create_gtm_workspace(account_id, container_id, name, description?)`: Cria um workspace branch.
- `update_gtm_workspace(account_id, container_id, workspace_id, name?, description?)`: Atualiza workspace.
- `delete_gtm_workspace(account_id, container_id, workspace_id)`: Remove workspace.
- `get_gtm_workspace_status(account_id, container_id, workspace_id?)`: **Verifica alterações pendentes e conflitos com a versão de produção.**
- `sync_gtm_workspace(account_id, container_id, workspace_id?)`: Sincroniza workspace com a versão live mais recente.

### 4. Tags
- `list_gtm_tags(account_id, container_id, workspace_id?)`: Lista todas as Tags (Google Ads, GA4, Meta Pixel, HTML).
- `get_gtm_tag(account_id, container_id, tag_id, workspace_id?)`: Detalha regras e parâmetros de uma tag.
- `create_gtm_tag(...)`: Cria uma nova Tag.
- `update_gtm_tag(...)`: Atualiza ou pausa/ativa uma Tag.
- `delete_gtm_tag(account_id, container_id, tag_id, workspace_id?)`: Remove uma Tag.
- `revert_gtm_tag(account_id, container_id, tag_id, workspace_id?)`: Desfaz as alterações de uma Tag no workspace.

### 5. Acionadores (Triggers)
- `list_gtm_triggers(account_id, container_id, workspace_id?)`: Lista acionadores (Page View, Clique, Evento, etc.).
- `get_gtm_trigger(account_id, container_id, trigger_id, workspace_id?)`: Detalha regras de um acionador.
- `create_gtm_trigger(...)`: Cria um novo acionador.
- `update_gtm_trigger(account_id, container_id, trigger_id, name?, filter?, custom_event_filter?, auto_event_filter?, workspace_id?)`: Edita um acionador (só altera o que for informado).
- `delete_gtm_trigger(account_id, container_id, trigger_id, workspace_id?)`: Remove um acionador.
- `revert_gtm_trigger(account_id, container_id, trigger_id, workspace_id?)`: Desfaz as alterações de um acionador.

### 6. Variáveis & Variáveis Integradas (Variables & Built-in Variables)
- `list_gtm_variables(account_id, container_id, workspace_id?)`: Lista variáveis do usuário (dataLayer, constantes, etc.).
- `get_gtm_variable(account_id, container_id, variable_id, workspace_id?)`: Detalha uma variável.
- `create_gtm_variable(...)`: Cria uma nova variável.
- `update_gtm_variable(...)`: Atualiza uma variável.
- `revert_gtm_variable(account_id, container_id, variable_id, workspace_id?)`: Desfaz as alterações de uma variável.
- `delete_gtm_variable(account_id, container_id, variable_id, workspace_id?)`: Remove uma variável.
- `list_gtm_builtin_variables(account_id, container_id, workspace_id?)`: Lista variáveis integradas ativas.
- `enable_gtm_builtin_variables(account_id, container_id, variable_types, workspace_id?)`: Ativa variáveis nativas (ex: `clickUrl`, `pageUrl`, `formId`).
- `disable_gtm_builtin_variable(account_id, container_id, variable_type, workspace_id?)`: Desativa variável nativa.
- `revert_gtm_builtin_variable(account_id, container_id, variable_type, workspace_id?)`: Volta a variável nativa ao estado publicado.

### 7. Pastas de Organização (Folders)
- `list_gtm_folders(account_id, container_id, workspace_id?)`: Lista pastas.
- `get_gtm_folder(account_id, container_id, folder_id, workspace_id?)`: Detalha uma pasta.
- `create_gtm_folder(account_id, container_id, name, workspace_id?)`: Cria uma pasta de organização.
- `update_gtm_folder(...)`: Atualiza pasta.
- `delete_gtm_folder(...)`: Exclui pasta.
- `revert_gtm_folder(account_id, container_id, folder_id, workspace_id?)`: Desfaz as alterações de uma pasta.
- `list_gtm_folder_entities(...)`: Lista tudo que está dentro de uma pasta.
- `move_entities_to_gtm_folder(...)`: Move tags, acionadores e variáveis para uma pasta.

### 8. Modelos Personalizados (Custom Templates)
- `list_gtm_templates(account_id, container_id, workspace_id?)`: Lista modelos customizados.
- `get_gtm_template(account_id, container_id, template_id, workspace_id?)`: Detalha código do modelo.
- `create_gtm_template(...)`: Cria um novo modelo customizado.
- `update_gtm_template(account_id, container_id, template_id, name?, template_data?, workspace_id?)`: Edita nome e/ou código de um modelo.
- `delete_gtm_template(...)`: Remove modelo.
- `revert_gtm_template(account_id, container_id, template_id, workspace_id?)`: Desfaz as alterações de um modelo.

### 9. Zonas & Transformações Server-Side (Zones & Transformations)
- `list_gtm_zones`, `get_gtm_zone`: Gestão de zonas (GTM 360).

### 9.1 Configuração da Tag do Google (gtag_config)
- `list_gtm_gtag_configs`, `get_gtm_gtag_config`, `create_gtm_gtag_config`, `update_gtm_gtag_config`, `delete_gtm_gtag_config`: Configurações da tag do Google (GA4 / Google Ads).
- `list_gtm_transformations`, `get_gtm_transformation`: Gestão de transformações de dados Server-side.

### 10. Versões & Publicação (Versions & Live Production)
- `get_live_gtm_version(account_id, container_id)`: **Audita a versão atualmente ao vivo no site do cliente.**
- `list_gtm_versions(account_id, container_id)`: Histórico de versões publicadas.
- `get_gtm_version(account_id, container_id, version_id)`: Inspeciona uma versão específica do histórico.
- `create_gtm_version(...)`: Cria nova versão a partir do workspace (equivalente a clicar em 'Enviar' no GTM).
- `publish_gtm_version(account_id, container_id, version_id)`: **Publica a versão em produção imediatamente.**
- `set_latest_gtm_version(...)`: Define como versão mais recente.
- `undelete_gtm_version(...)`: Restaura versão excluída.
- `delete_gtm_version(...)`: Remove versão do histórico.

---

## ⚙️ Deploy no Easypanel

1. Serviço **App**, fonte GitHub, build via **Dockerfile**.
2. Aba **Environment**:
```env
MCP_TOKEN=<token forte>
GTM_CLIENT_ID=seu_client_id_aqui.apps.googleusercontent.com
GTM_CLIENT_SECRET=seu_client_secret_aqui
GTM_REFRESH_TOKEN=seu_refresh_token_aqui
```
Gerar o token: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
3. Aba **Domains**: domínio com HTTPS ligado, porta interna `8000`.
4. Confira `https://<dominio>/health`.

---

## 🚀 Como Conectar

URL final: `https://<dominio>/mcp?token=<MCP_TOKEN>`

### Claude Web (claude.ai) e ChatGPT
Conector personalizado com a URL acima.

### Claude Desktop / Claude Code / Antigravity
```json
{
  "mcpServers": {
    "google-tag-manager": {
      "url": "https://<dominio>/mcp?token=<MCP_TOKEN>"
    }
  }
}
```
Se o cliente só aceitar stdio, use a ponte: `npx -y mcp-remote "https://<dominio>/mcp?token=<MCP_TOKEN>"`.

---

## 🧪 Testes

```bash
pip install httpx
MCP_URL=https://<dominio> MCP_TOKEN=xxx python test_server.py
```
As chamadas reais ao GTM são somente de leitura.

---

## ⚠️ Escopos do token do Google

O `GTM_REFRESH_TOKEN` precisa ter os escopos OAuth das ferramentas que você quer usar. Com apenas `tagmanager.edit.containers` funcionam tags, acionadores, variáveis, pastas, modelos, gtag_config, workspaces e leitura de versões.

| Escopo | Libera |
|---|---|
| `tagmanager.manage.users` | Ferramentas de permissão de usuários (conta e contêiner) |
| `tagmanager.edit.containerversions` | Criar, excluir e restaurar versões |
| `tagmanager.publish` | `publish_gtm_version` |
| `tagmanager.delete.containers` | `delete_gtm_container` |
| `tagmanager.manage.accounts` | `update_gtm_account` |