from typing import Any, Dict, List, Optional
from gtm_mcp.coordinator import mcp
from gtm_mcp.auth import gtm_request


@mcp.tool()
def list_gtm_containers(account_id: str) -> List[Dict[str, Any]]:
    """Returns all containers (Web, Server, AMP, etc.) for a specific GTM account.

    Args:
        account_id: The GTM account ID (e.g. '6004238812').
    """
    clean_acc = str(account_id).strip()
    res = gtm_request(f"accounts/{clean_acc}/containers")
    return res.get("container", [])


@mcp.tool()
def get_gtm_container(account_id: str, container_id: str) -> Dict[str, Any]:
    """Gets details and features of a specific GTM container.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    return gtm_request(f"accounts/{clean_acc}/containers/{clean_cont}")


@mcp.tool()
def lookup_gtm_container(destination_id: str) -> Dict[str, Any]:
    """Finds container information by destination ID or Tag ID (e.g., 'GTM-XXXXXX', 'GT-XXXXXX', or 'AW-XXXXXX').

    Args:
        destination_id: Destination/Tag ID (e.g. 'GTM-M7K9952').
    """
    clean_dest = str(destination_id).strip()
    # A API separa os parâmetros: tagId para 'GTM-...' e destinationId para os demais ('GT-', 'AW-'...)
    param = "tagId" if clean_dest.upper().startswith("GTM-") else "destinationId"
    return gtm_request("accounts/containers:lookup", params={param: clean_dest})


@mcp.tool()
def get_gtm_container_snippet(
    account_id: str, container_id: str, environment_id: Optional[str] = None
) -> Dict[str, Any]:
    """Retrieves the GTM installation code snippets (head <script> and body <noscript>) to paste on the client's website.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        environment_id: Optional environment ID (e.g. 'env-1').
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()

    container = gtm_request(f"accounts/{clean_acc}/containers/{clean_cont}")
    public_id = container.get("publicId", f"GTM-{clean_cont}")

    # A API v2 não tem endpoint de snippet por ambiente: o GTM monta o código do contêiner
    # acrescentando gtm_auth (código de autorização do ambiente) e gtm_preview=env-N.
    env_js = ""
    env_html = ""
    if environment_id:
        clean_env = str(environment_id).strip()
        if clean_env.lower().startswith("env-"):
            clean_env = clean_env[4:]
        env = gtm_request(f"accounts/{clean_acc}/containers/{clean_cont}/environments/{clean_env}")
        auth = env.get("authorizationCode", "")
        env_js = f"+'&gtm_auth={auth}&gtm_preview=env-{clean_env}&gtm_cookies_win=x'"
        env_html = f"&amp;gtm_auth={auth}&amp;gtm_preview=env-{clean_env}&amp;gtm_cookies_win=x"

    head_script = (
        f"<!-- Google Tag Manager -->\n"
        f"<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':\n"
        f"new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],\n"
        f"j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=\n"
        f"'https://www.googletagmanager.com/gtm.js?id='+i+dl{env_js};f.parentNode.insertBefore(j,f);\n"
        f"}})(window,document,'script','dataLayer','{public_id}');</script>\n"
        f"<!-- End Google Tag Manager -->"
    )

    body_script = (
        f"<!-- Google Tag Manager (noscript) -->\n"
        f"<noscript><iframe src=\"https://www.googletagmanager.com/ns.html?id={public_id}{env_html}\"\n"
        f"height=\"0\" width=\"0\" style=\"display:none;visibility:hidden\"></iframe></noscript>\n"
        f"<!-- End Google Tag Manager (noscript) -->"
    )

    return {
        "public_id": public_id,
        "container_id": clean_cont,
        "account_id": clean_acc,
        "head_script": head_script,
        "body_script": body_script,
        "tag_manager_url": container.get("tagManagerUrl", ""),
    }



@mcp.tool()
def search_gtm_containers(query: str) -> List[Dict[str, Any]]:
    """Searches for containers across ALL accessible GTM accounts by client name, container name, or GTM Public ID (e.g., 'GTM-XXXXXX').

    Args:
        query: The search term (e.g. 'Mareiro', 'GTM-NK8K2L', 'Predial').
    """
    q_lower = query.lower().strip()
    accounts_res = gtm_request("accounts")
    accounts = accounts_res.get("account", [])

    matches = []
    for acc in accounts:
        acc_id = acc.get("accountId")
        acc_name = acc.get("name", "")
        try:
            cont_res = gtm_request(f"accounts/{acc_id}/containers")
            for c in cont_res.get("container", []):
                cont_name = c.get("name", "")
                public_id = c.get("publicId", "")
                if (
                    q_lower in acc_name.lower()
                    or q_lower in cont_name.lower()
                    or q_lower in public_id.lower()
                ):
                    matches.append({
                        "account_name": acc_name,
                        "account_id": acc_id,
                        "container_name": cont_name,
                        "container_id": c.get("containerId"),
                        "public_id": public_id,
                        "usage_context": c.get("usageContext", []),
                        "tag_manager_url": c.get("tagManagerUrl", ""),
                    })
        except Exception:
            continue

    return matches


@mcp.tool()
def create_gtm_container(
    account_id: str, name: str, usage_context: List[str]
) -> Dict[str, Any]:
    """Creates a new GTM container under an account.

    Args:
        account_id: The GTM account ID.
        name: Name for the container (e.g. 'Website Principal' or domain 'www.cliente.com.br').
        usage_context: Target platform context (e.g. ['web'], ['server'], ['amp'], ['ios'], ['android']).
    """
    clean_acc = str(account_id).strip()
    body = {"name": name, "usageContext": usage_context}
    return gtm_request(
        f"accounts/{clean_acc}/containers", method="POST", json_body=body
    )


@mcp.tool()
def update_gtm_container(
    account_id: str,
    container_id: str,
    name: Optional[str] = None,
    usage_context: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Updates a GTM container's name or usage context.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        name: Optional new container name.
        usage_context: Optional new usage context list.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    existing = gtm_request(f"accounts/{clean_acc}/containers/{clean_cont}")
    if name is not None:
        existing["name"] = name
    if usage_context is not None:
        existing["usageContext"] = usage_context
    return gtm_request(
        f"accounts/{clean_acc}/containers/{clean_cont}",
        method="PUT",
        json_body=existing,
    )


@mcp.tool()
def delete_gtm_container(account_id: str, container_id: str) -> Dict[str, Any]:
    """Deletes a GTM container.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    gtm_request(f"accounts/{clean_acc}/containers/{clean_cont}", method="DELETE")
    return {"status": "deleted", "container_id": clean_cont}


@mcp.tool()
def list_gtm_container_user_permissions(
    account_id: str, container_id: str
) -> List[Dict[str, Any]]:
    """Lists the users who have access to a specific GTM container.

    The GTM API stores container access inside each account-level user permission, so this
    reads the account's user permissions and keeps only those with access to this container.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    res = gtm_request(f"accounts/{clean_acc}/user_permissions")
    result = []
    for perm in res.get("userPermission", []):
        access = [a for a in perm.get("containerAccess", []) if str(a.get("containerId")) == clean_cont]
        if access:
            result.append(
                {
                    "email_address": perm.get("emailAddress"),
                    "account_access": perm.get("accountAccess", {}).get("permission"),
                    "container_permission": access[0].get("permission"),
                    "path": perm.get("path"),
                }
            )
    return result


@mcp.tool()
def create_gtm_container_user_permission(
    account_id: str,
    container_id: str,
    email_address: str,
    permission: str = "read",
) -> Dict[str, Any]:
    """Grants a user permission to a specific GTM container.

    If the user already exists in the account, the container access is added or replaced
    (other containers and the account-level role are kept). Otherwise the user is added to the
    account with the 'user' role plus access to this container.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        email_address: Google email of the user.
        permission: 'noAccess', 'read', 'edit', 'approve', or 'publish'.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    email = email_address.strip()
    entry = {"containerId": clean_cont, "permission": permission}

    res = gtm_request(f"accounts/{clean_acc}/user_permissions")
    existing = next(
        (p for p in res.get("userPermission", []) if str(p.get("emailAddress", "")).lower() == email.lower()),
        None,
    )
    if existing:
        others = [a for a in existing.get("containerAccess", []) if str(a.get("containerId")) != clean_cont]
        existing["containerAccess"] = others + [entry]
        return gtm_request(existing["path"], method="PUT", json_body=existing)

    body = {
        "emailAddress": email,
        "accountAccess": {"permission": "user"},
        "containerAccess": [entry],
    }
    return gtm_request(f"accounts/{clean_acc}/user_permissions", method="POST", json_body=body)


@mcp.tool()
def list_gtm_environments(
    account_id: str, container_id: str
) -> List[Dict[str, Any]]:
    """Lists environments (e.g. Live, Staging, QA) in a GTM container.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    res = gtm_request(f"accounts/{clean_acc}/containers/{clean_cont}/environments")
    return res.get("environment", [])


@mcp.tool()
def get_gtm_environment(
    account_id: str, container_id: str, environment_id: str
) -> Dict[str, Any]:
    """Gets details of a specific environment in a GTM container.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        environment_id: The environment ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    clean_env = str(environment_id).strip()
    return gtm_request(
        f"accounts/{clean_acc}/containers/{clean_cont}/environments/{clean_env}"
    )
