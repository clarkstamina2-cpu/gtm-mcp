from typing import Any, Dict, List, Optional
from gtm_mcp.coordinator import mcp
from gtm_mcp.auth import gtm_request
from gtm_mcp.tools.workspaces import _get_default_workspace_id


@mcp.tool()
def list_gtm_versions(account_id: str, container_id: str) -> List[Dict[str, Any]]:
    """Lists published versions and history of a GTM container.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    res = gtm_request(f"accounts/{clean_acc}/containers/{clean_cont}/version_headers")
    headers = res.get("containerVersionHeader", [])
    return [
        {
            "container_version_id": h.get("containerVersionId"),
            "name": h.get("name", ""),
            "num_tags": h.get("numTags"),
            "num_triggers": h.get("numTriggers"),
            "num_variables": h.get("numVariables"),
            "deleted": h.get("deleted", False),
        }
        for h in headers
    ]


@mcp.tool()
def get_gtm_version(
    account_id: str, container_id: str, version_id: str
) -> Dict[str, Any]:
    """Gets complete details of a specific container version (tags, triggers, variables, macros).

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        version_id: The version ID (e.g. '1', '2', 'live').
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    clean_ver = str(version_id).strip()
    if clean_ver.lower() == "live":
        return gtm_request(f"accounts/{clean_acc}/containers/{clean_cont}/versions:live")
    return gtm_request(f"accounts/{clean_acc}/containers/{clean_cont}/versions/{clean_ver}")


@mcp.tool()
def get_live_gtm_version(account_id: str, container_id: str) -> Dict[str, Any]:
    """Retrieves the LIVE (currently active/published) container version with all live tags, triggers, and variables running on the website.

    Use this tool to audit exactly what is published and firing live on the client's site.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    res = gtm_request(f"accounts/{clean_acc}/containers/{clean_cont}/versions:live")
    
    # O endpoint versions:live devolve o ContainerVersion direto (sem a chave "containerVersion")
    cv = res.get("containerVersion", res)
    return {
        "container_version_id": cv.get("containerVersionId"),
        "name": cv.get("name"),
        "description": cv.get("description"),
        "tags_count": len(cv.get("tag", [])),
        "triggers_count": len(cv.get("trigger", [])),
        "variables_count": len(cv.get("variable", [])),
        "tags": [
            {
                "tag_id": t.get("tagId"),
                "name": t.get("name"),
                "type": t.get("type"),
                "paused": t.get("paused", False),
                "firing_trigger_id": t.get("firingTriggerId", []),
            }
            for t in cv.get("tag", [])
        ],
        "triggers": [
            {
                "trigger_id": tr.get("triggerId"),
                "name": tr.get("name"),
                "type": tr.get("type"),
            }
            for tr in cv.get("trigger", [])
        ],
        "variables": [
            {
                "variable_id": v.get("variableId"),
                "name": v.get("name"),
                "type": v.get("type"),
            }
            for v in cv.get("variable", [])
        ],
    }


@mcp.tool()
def create_gtm_version(
    account_id: str,
    container_id: str,
    name: str,
    notes: Optional[str] = None,
    workspace_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Creates a new container version from workspace changes (like clicking 'Submit' in GTM).

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        name: Version name (e.g. 'v1.2 - Added Google Ads Conversion Tags').
        notes: Optional release notes describing changes.
        workspace_id: Optional workspace ID. If omitted, uses default workspace.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)

    body = {
        "name": name,
        "notes": notes or "",
    }

    return gtm_request(
        f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}:create_version",
        method="POST",
        json_body=body,
    )


@mcp.tool()
def publish_gtm_version(
    account_id: str, container_id: str, version_id: str
) -> Dict[str, Any]:
    """Publishes a specific GTM container version live to production.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        version_id: The container version ID to publish (e.g. '3').
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    clean_ver = str(version_id).strip()

    return gtm_request(
        f"accounts/{clean_acc}/containers/{clean_cont}/versions/{clean_ver}:publish",
        method="POST",
    )


@mcp.tool()
def set_latest_gtm_version(
    account_id: str, container_id: str, version_id: str
) -> Dict[str, Any]:
    """Sets a container version as latest.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        version_id: The Version ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    clean_ver = str(version_id).strip()

    return gtm_request(
        f"accounts/{clean_acc}/containers/{clean_cont}/versions/{clean_ver}:set_latest",
        method="POST",
    )


@mcp.tool()
def undelete_gtm_version(
    account_id: str, container_id: str, version_id: str
) -> Dict[str, Any]:
    """Restores a deleted container version.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        version_id: The Version ID to restore.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    clean_ver = str(version_id).strip()

    return gtm_request(
        f"accounts/{clean_acc}/containers/{clean_cont}/versions/{clean_ver}:undelete",
        method="POST",
    )


@mcp.tool()
def delete_gtm_version(
    account_id: str, container_id: str, version_id: str
) -> Dict[str, Any]:
    """Deletes a container version from history.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        version_id: The Version ID to delete.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    clean_ver = str(version_id).strip()

    gtm_request(
        f"accounts/{clean_acc}/containers/{clean_cont}/versions/{clean_ver}",
        method="DELETE",
    )
    return {"status": "deleted", "version_id": clean_ver}
