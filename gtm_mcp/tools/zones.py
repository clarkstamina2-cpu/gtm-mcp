from typing import Any, Dict, List, Optional
from gtm_mcp.coordinator import mcp
from gtm_mcp.auth import gtm_request
from gtm_mcp.tools.workspaces import _get_default_workspace_id


@mcp.tool()
def list_gtm_zones(
    account_id: str, container_id: str, workspace_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Lists all Zones (GTM 360 multi-container boundaries) in a workspace.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        workspace_id: Optional workspace ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)
    res = gtm_request(f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/zones")
    return res.get("zone", [])


@mcp.tool()
def get_gtm_zone(
    account_id: str, container_id: str, zone_id: str, workspace_id: Optional[str] = None
) -> Dict[str, Any]:
    """Gets details of a specific GTM Zone.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        zone_id: The Zone ID.
        workspace_id: Optional workspace ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    clean_z = str(zone_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)
    return gtm_request(f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/zones/{clean_z}")


@mcp.tool()
def list_gtm_transformations(
    account_id: str, container_id: str, workspace_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Lists all Transformations (Server-side data transformations) in a GTM workspace.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        workspace_id: Optional workspace ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)
    res = gtm_request(f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/transformations")
    return res.get("transformation", [])


@mcp.tool()
def get_gtm_transformation(
    account_id: str, container_id: str, transformation_id: str, workspace_id: Optional[str] = None
) -> Dict[str, Any]:
    """Gets details of a specific Server-Side Transformation in a GTM workspace.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        transformation_id: The Transformation ID.
        workspace_id: Optional workspace ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    clean_t = str(transformation_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)
    return gtm_request(f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/transformations/{clean_t}")
