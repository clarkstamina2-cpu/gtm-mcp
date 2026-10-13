from typing import Any, Dict, List, Optional
from gtm_mcp.coordinator import mcp
from gtm_mcp.auth import gtm_request
from gtm_mcp.tools.workspaces import _get_default_workspace_id


@mcp.tool()
def list_gtm_folders(
    account_id: str, container_id: str, workspace_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Lists all organizational Folders in a GTM workspace.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        workspace_id: Optional workspace ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)
    res = gtm_request(f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/folders")
    return res.get("folder", [])


@mcp.tool()
def get_gtm_folder(
    account_id: str, container_id: str, folder_id: str, workspace_id: Optional[str] = None
) -> Dict[str, Any]:
    """Gets details of a specific GTM Folder.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        folder_id: The Folder ID.
        workspace_id: Optional workspace ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    clean_fold = str(folder_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)
    return gtm_request(f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/folders/{clean_fold}")


@mcp.tool()
def create_gtm_folder(
    account_id: str, container_id: str, name: str, workspace_id: Optional[str] = None
) -> Dict[str, Any]:
    """Creates a new organizational Folder in a GTM workspace (e.g. 'Google Ads', 'GA4 E-commerce', 'Meta Pixel').

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        name: Folder name.
        workspace_id: Optional workspace ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)
    body = {"name": name}
    return gtm_request(
        f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/folders",
        method="POST",
        json_body=body,
    )


@mcp.tool()
def update_gtm_folder(
    account_id: str, container_id: str, folder_id: str, name: str, workspace_id: Optional[str] = None
) -> Dict[str, Any]:
    """Updates the name of an existing GTM Folder.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        folder_id: The Folder ID.
        name: New folder name.
        workspace_id: Optional workspace ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    clean_fold = str(folder_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)
    existing = gtm_request(f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/folders/{clean_fold}")
    existing["name"] = name
    return gtm_request(
        f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/folders/{clean_fold}",
        method="PUT",
        json_body=existing,
    )


@mcp.tool()
def delete_gtm_folder(
    account_id: str, container_id: str, folder_id: str, workspace_id: Optional[str] = None
) -> Dict[str, Any]:
    """Deletes an organizational Folder from a GTM workspace.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        folder_id: The Folder ID.
        workspace_id: Optional workspace ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    clean_fold = str(folder_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)
    gtm_request(
        f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/folders/{clean_fold}",
        method="DELETE",
    )
    return {"status": "deleted", "folder_id": clean_fold}


@mcp.tool()
def list_gtm_folder_entities(
    account_id: str, container_id: str, folder_id: str, workspace_id: Optional[str] = None
) -> Dict[str, Any]:
    """Lists all Tags, Triggers, and Variables grouped inside a specific GTM Folder.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        folder_id: The Folder ID.
        workspace_id: Optional workspace ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    clean_fold = str(folder_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)
    return gtm_request(
        f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/folders/{clean_fold}:entities"
    )


@mcp.tool()
def move_entities_to_gtm_folder(
    account_id: str,
    container_id: str,
    folder_id: str,
    tag_ids: Optional[List[str]] = None,
    trigger_ids: Optional[List[str]] = None,
    variable_ids: Optional[List[str]] = None,
    workspace_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Moves multiple Tags, Triggers, and/or Variables into a specific Folder for organization.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        folder_id: Destination Folder ID.
        tag_ids: Optional list of Tag IDs to move.
        trigger_ids: Optional list of Trigger IDs to move.
        variable_ids: Optional list of Variable IDs to move.
        workspace_id: Optional workspace ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    clean_fold = str(folder_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)

    body = {
        "tag": [{"tagId": tid} for tid in (tag_ids or [])],
        "trigger": [{"triggerId": trid} for trid in (trigger_ids or [])],
        "variable": [{"variableId": vid} for vid in (variable_ids or [])],
    }

    gtm_request(
        f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/folders/{clean_fold}:move_entities_to_folder",
        method="POST",
        json_body=body,
    )
    return {"status": "moved", "folder_id": clean_fold}
