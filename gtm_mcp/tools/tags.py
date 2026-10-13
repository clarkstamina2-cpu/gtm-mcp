from typing import Any, Dict, List, Optional
from gtm_mcp.coordinator import mcp
from gtm_mcp.auth import gtm_request


def _get_default_workspace_id(account_id: str, container_id: str) -> str:
    """Helper to get default workspace if not provided."""
    res = gtm_request(f"accounts/{account_id}/containers/{container_id}/workspaces")
    workspaces = res.get("workspace", [])
    if not workspaces:
        raise ValueError(f"No workspaces found for container {container_id}")
    return workspaces[0]["workspaceId"]


@mcp.tool()
def list_gtm_tags(
    account_id: str, container_id: str, workspace_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Lists all Tags in a GTM container workspace (e.g. Google Ads Conversion Tracking, GA4, Meta Pixel, Custom HTML, etc.).

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        workspace_id: Optional workspace ID. If omitted, uses the default workspace.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)

    res = gtm_request(f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/tags")
    tags = res.get("tag", [])
    return [
        {
            "tag_id": t.get("tagId"),
            "name": t.get("name"),
            "type": t.get("type"),  # e.g. 'gaaw_tag', 'awct', 'html', 'sp'
            "firing_trigger_id": t.get("firingTriggerId", []),
            "blocking_trigger_id": t.get("blockingTriggerId", []),
            "paused": t.get("paused", False),
            "parameter": t.get("parameter", []),
            "path": t.get("path"),
        }
        for t in tags
    ]


@mcp.tool()
def get_gtm_tag(
    account_id: str, container_id: str, tag_id: str, workspace_id: Optional[str] = None
) -> Dict[str, Any]:
    """Gets detailed configuration and parameters of a specific GTM Tag.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        tag_id: The Tag ID.
        workspace_id: Optional workspace ID. If omitted, uses the default workspace.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    clean_tag = str(tag_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)

    return gtm_request(f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/tags/{clean_tag}")


@mcp.tool()
def create_gtm_tag(
    account_id: str,
    container_id: str,
    name: str,
    type: str,
    parameter: Optional[List[Dict[str, Any]]] = None,
    firing_trigger_ids: Optional[List[str]] = None,
    blocking_trigger_ids: Optional[List[str]] = None,
    workspace_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Creates a new Tag in a GTM container workspace.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        name: Name for the Tag (e.g. 'Google Ads - Lead Conversion').
        type: GTM Tag type (e.g. 'awct' for Google Ads Conversion, 'gaaw_tag' for GA4 Event, 'html' for Custom HTML).
        parameter: List of tag parameters/configurations (e.g. [{'type': 'template', 'key': 'conversionId', 'value': '12345'}]).
        firing_trigger_ids: List of trigger IDs that fire this tag.
        blocking_trigger_ids: Optional list of exception trigger IDs.
        workspace_id: Optional workspace ID. If omitted, uses default workspace.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)

    body = {
        "name": name,
        "type": type,
        "parameter": parameter or [],
        "firingTriggerId": firing_trigger_ids or [],
        "blockingTriggerId": blocking_trigger_ids or [],
    }

    return gtm_request(
        f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/tags",
        method="POST",
        json_body=body,
    )


@mcp.tool()
def update_gtm_tag(
    account_id: str,
    container_id: str,
    tag_id: str,
    name: Optional[str] = None,
    paused: Optional[bool] = None,
    parameter: Optional[List[Dict[str, Any]]] = None,
    firing_trigger_ids: Optional[List[str]] = None,
    workspace_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Updates an existing GTM Tag (e.g. pause/unpause, update parameters or triggers).

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        tag_id: The Tag ID to update.
        name: Optional new name.
        paused: Set True to pause or False to activate.
        parameter: Optional new parameter list.
        firing_trigger_ids: Optional new firing trigger IDs.
        workspace_id: Optional workspace ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    clean_tag = str(tag_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)

    existing = gtm_request(f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/tags/{clean_tag}")

    if name is not None:
        existing["name"] = name
    if paused is not None:
        existing["paused"] = paused
    if parameter is not None:
        existing["parameter"] = parameter
    if firing_trigger_ids is not None:
        existing["firingTriggerId"] = firing_trigger_ids

    return gtm_request(
        f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/tags/{clean_tag}",
        method="PUT",
        json_body=existing,
    )


@mcp.tool()
def delete_gtm_tag(
    account_id: str, container_id: str, tag_id: str, workspace_id: Optional[str] = None
) -> Dict[str, Any]:
    """Deletes a Tag from a GTM container workspace.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        tag_id: The Tag ID to delete.
        workspace_id: Optional workspace ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    clean_tag = str(tag_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)

    gtm_request(
        f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/tags/{clean_tag}",
        method="DELETE",
    )
    return {"status": "deleted", "tag_id": clean_tag}


@mcp.tool()
def revert_gtm_tag(
    account_id: str, container_id: str, tag_id: str, workspace_id: Optional[str] = None
) -> Dict[str, Any]:
    """Reverts the changes made to a Tag in the workspace, restoring the last published version.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        tag_id: The Tag ID to revert.
        workspace_id: Optional workspace ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    clean_id = str(tag_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)
    return gtm_request(
        f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/tags/{clean_id}:revert",
        method="POST",
    )