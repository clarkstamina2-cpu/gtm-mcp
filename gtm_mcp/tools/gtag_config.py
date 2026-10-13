from typing import Any, Dict, List, Optional
from gtm_mcp.coordinator import mcp
from gtm_mcp.auth import gtm_request
from gtm_mcp.tools.workspaces import _get_default_workspace_id


def _base(account_id: str, container_id: str, workspace_id: Optional[str]) -> str:
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)
    return f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/gtag_config"


@mcp.tool()
def list_gtm_gtag_configs(
    account_id: str, container_id: str, workspace_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Lists all Google tag configurations (gtag_config) in a GTM workspace (e.g. GA4 / Google Ads Google tag settings).

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        workspace_id: Optional workspace ID. If omitted, uses the default workspace.
    """
    res = gtm_request(_base(account_id, container_id, workspace_id))
    return res.get("gtagConfig", [])


@mcp.tool()
def get_gtm_gtag_config(
    account_id: str,
    container_id: str,
    gtag_config_id: str,
    workspace_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Gets a specific Google tag configuration (gtag_config).

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        gtag_config_id: The Google tag config ID.
        workspace_id: Optional workspace ID.
    """
    return gtm_request(f"{_base(account_id, container_id, workspace_id)}/{str(gtag_config_id).strip()}")


@mcp.tool()
def create_gtm_gtag_config(
    account_id: str,
    container_id: str,
    type: str,
    parameter: Optional[List[Dict[str, Any]]] = None,
    workspace_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Creates a Google tag configuration (gtag_config) in a GTM workspace.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        type: The Google tag config type (e.g. 'googtag').
        parameter: List of parameters (e.g. [{'type': 'template', 'key': 'tagId', 'value': 'G-XXXXXXX'}]).
        workspace_id: Optional workspace ID.
    """
    body = {"type": type, "parameter": parameter or []}
    return gtm_request(_base(account_id, container_id, workspace_id), method="POST", json_body=body)


@mcp.tool()
def update_gtm_gtag_config(
    account_id: str,
    container_id: str,
    gtag_config_id: str,
    parameter: Optional[List[Dict[str, Any]]] = None,
    workspace_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Updates a Google tag configuration (gtag_config). Only the fields you pass are changed.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        gtag_config_id: The Google tag config ID to update.
        parameter: Optional new parameter list (replaces the current one).
        workspace_id: Optional workspace ID.
    """
    path = f"{_base(account_id, container_id, workspace_id)}/{str(gtag_config_id).strip()}"
    existing = gtm_request(path)
    if parameter is not None:
        existing["parameter"] = parameter
    return gtm_request(path, method="PUT", json_body=existing)


@mcp.tool()
def delete_gtm_gtag_config(
    account_id: str,
    container_id: str,
    gtag_config_id: str,
    workspace_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Deletes a Google tag configuration (gtag_config) from a GTM workspace.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        gtag_config_id: The Google tag config ID to delete.
        workspace_id: Optional workspace ID.
    """
    clean_id = str(gtag_config_id).strip()
    gtm_request(f"{_base(account_id, container_id, workspace_id)}/{clean_id}", method="DELETE")
    return {"status": "deleted", "gtag_config_id": clean_id}
