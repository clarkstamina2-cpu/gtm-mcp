from typing import Any, Dict, List, Optional
from gtm_mcp.coordinator import mcp
from gtm_mcp.auth import gtm_request


def _get_default_workspace_id(account_id: str, container_id: str) -> str:
    res = gtm_request(f"accounts/{account_id}/containers/{container_id}/workspaces")
    workspaces = res.get("workspace", [])
    if not workspaces:
        raise ValueError(f"No workspaces found for container {container_id}")
    return workspaces[0]["workspaceId"]


@mcp.tool()
def list_gtm_workspaces(
    account_id: str, container_id: str
) -> List[Dict[str, Any]]:
    """Lists all workspaces in a GTM container.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    res = gtm_request(f"accounts/{clean_acc}/containers/{clean_cont}/workspaces")
    return res.get("workspace", [])


@mcp.tool()
def get_gtm_workspace(
    account_id: str, container_id: str, workspace_id: str
) -> Dict[str, Any]:
    """Gets details of a specific GTM workspace.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        workspace_id: The Workspace ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    clean_ws = str(workspace_id).strip()
    return gtm_request(
        f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{clean_ws}"
    )


@mcp.tool()
def create_gtm_workspace(
    account_id: str,
    container_id: str,
    name: str,
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """Creates a new workspace in a GTM container (e.g. for team branch / separate campaign setups).

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        name: Name for the new workspace (e.g. 'Campanha Black Friday').
        description: Optional workspace description.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    body = {"name": name, "description": description or ""}
    return gtm_request(
        f"accounts/{clean_acc}/containers/{clean_cont}/workspaces",
        method="POST",
        json_body=body,
    )


@mcp.tool()
def update_gtm_workspace(
    account_id: str,
    container_id: str,
    workspace_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """Updates a GTM workspace name or description.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        workspace_id: The Workspace ID.
        name: Optional new workspace name.
        description: Optional new description.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    clean_ws = str(workspace_id).strip()
    existing = gtm_request(
        f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{clean_ws}"
    )
    if name is not None:
        existing["name"] = name
    if description is not None:
        existing["description"] = description
    return gtm_request(
        f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{clean_ws}",
        method="PUT",
        json_body=existing,
    )


@mcp.tool()
def delete_gtm_workspace(
    account_id: str, container_id: str, workspace_id: str
) -> Dict[str, Any]:
    """Deletes a GTM workspace.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        workspace_id: The Workspace ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    clean_ws = str(workspace_id).strip()
    gtm_request(
        f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{clean_ws}",
        method="DELETE",
    )
    return {"status": "deleted", "workspace_id": clean_ws}


@mcp.tool()
def get_gtm_workspace_status(
    account_id: str, container_id: str, workspace_id: Optional[str] = None
) -> Dict[str, Any]:
    """Gets the status of a GTM workspace, including modified entities, pending changes, and conflicts.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        workspace_id: Optional workspace ID. If omitted, uses default workspace.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    ws_id = (
        str(workspace_id).strip()
        if workspace_id
        else _get_default_workspace_id(clean_acc, clean_cont)
    )
    return gtm_request(
        f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/status"
    )


@mcp.tool()
def sync_gtm_workspace(
    account_id: str, container_id: str, workspace_id: Optional[str] = None
) -> Dict[str, Any]:
    """Synchronizes a GTM workspace with the latest published container version.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        workspace_id: Optional workspace ID. If omitted, uses default workspace.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    ws_id = (
        str(workspace_id).strip()
        if workspace_id
        else _get_default_workspace_id(clean_acc, clean_cont)
    )
    return gtm_request(
        f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}:sync",
        method="POST",
    )
