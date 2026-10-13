from typing import Any, Dict, List, Optional
from gtm_mcp.coordinator import mcp
from gtm_mcp.auth import gtm_request
from gtm_mcp.tools.workspaces import _get_default_workspace_id


@mcp.tool()
def list_gtm_variables(
    account_id: str, container_id: str, workspace_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Lists all user-defined Variables in a GTM workspace (e.g. Constant, dataLayer, JavaScript, DOM, etc.).

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        workspace_id: Optional workspace ID. If omitted, uses default workspace.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)

    res = gtm_request(f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/variables")
    variables = res.get("variable", [])
    return [
        {
            "variable_id": v.get("variableId"),
            "name": v.get("name"),
            "type": v.get("type"),  # e.g. 'c' (constant), 'v' (data layer), 'jsm' (custom js)
            "parameter": v.get("parameter", []),
            "path": v.get("path"),
        }
        for v in variables
    ]


@mcp.tool()
def get_gtm_variable(
    account_id: str, container_id: str, variable_id: str, workspace_id: Optional[str] = None
) -> Dict[str, Any]:
    """Gets details and parameters of a specific GTM Variable.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        variable_id: The Variable ID.
        workspace_id: Optional workspace ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    clean_var = str(variable_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)

    return gtm_request(f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/variables/{clean_var}")


@mcp.tool()
def create_gtm_variable(
    account_id: str,
    container_id: str,
    name: str,
    type: str,
    parameter: Optional[List[Dict[str, Any]]] = None,
    workspace_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Creates a new user-defined Variable in a GTM workspace.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        name: Name for the Variable (e.g. 'GA4 Measurement ID', 'DLV - ecommerce.value').
        type: GTM Variable type (e.g. 'c' for Constant, 'v' for Data Layer Variable, 'jsm' for Custom JS).
        parameter: List of variable parameters.
        workspace_id: Optional workspace ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)

    body = {
        "name": name,
        "type": type,
        "parameter": parameter or [],
    }

    return gtm_request(
        f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/variables",
        method="POST",
        json_body=body,
    )


@mcp.tool()
def update_gtm_variable(
    account_id: str,
    container_id: str,
    variable_id: str,
    name: Optional[str] = None,
    parameter: Optional[List[Dict[str, Any]]] = None,
    workspace_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Updates an existing user-defined Variable in a GTM workspace.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        variable_id: The Variable ID.
        name: Optional new name.
        parameter: Optional new parameters.
        workspace_id: Optional workspace ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    clean_var = str(variable_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)

    existing = gtm_request(f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/variables/{clean_var}")
    if name is not None:
        existing["name"] = name
    if parameter is not None:
        existing["parameter"] = parameter

    return gtm_request(
        f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/variables/{clean_var}",
        method="PUT",
        json_body=existing,
    )


@mcp.tool()
def delete_gtm_variable(
    account_id: str, container_id: str, variable_id: str, workspace_id: Optional[str] = None
) -> Dict[str, Any]:
    """Deletes a Variable from a GTM workspace.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        variable_id: The Variable ID to delete.
        workspace_id: Optional workspace ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    clean_var = str(variable_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)

    gtm_request(
        f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/variables/{clean_var}",
        method="DELETE",
    )
    return {"status": "deleted", "variable_id": clean_var}


@mcp.tool()
def list_gtm_builtin_variables(
    account_id: str, container_id: str, workspace_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Lists all active Built-in Variables (variáveis integradas como Click URL, Page URL, Event, Form Classes, etc.) in a workspace.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        workspace_id: Optional workspace ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)

    res = gtm_request(f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/built_in_variables")
    return res.get("builtInVariable", [])


@mcp.tool()
def enable_gtm_builtin_variables(
    account_id: str,
    container_id: str,
    variable_types: List[str],
    workspace_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Enables one or more Built-in Variables in a GTM workspace (e.g. ['clickUrl', 'pageUrl', 'event', 'formId', 'clickElement']).

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        variable_types: List of built-in variable type names to activate.
        workspace_id: Optional workspace ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)

    types_param = ",".join(variable_types)
    res = gtm_request(
        f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/built_in_variables",
        method="POST",
        params={"type": types_param},
    )
    return res.get("builtInVariable", [])


@mcp.tool()
def disable_gtm_builtin_variable(
    account_id: str,
    container_id: str,
    variable_type: str,
    workspace_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Disables a Built-in Variable in a GTM workspace.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        variable_type: Built-in variable type name to deactivate (e.g. 'clickUrl').
        workspace_id: Optional workspace ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    clean_type = str(variable_type).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)

    gtm_request(
        f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/built_in_variables",
        method="DELETE",
        params={"type": clean_type},
    )
    return {"status": "disabled", "type": clean_type}


@mcp.tool()
def revert_gtm_variable(
    account_id: str, container_id: str, variable_id: str, workspace_id: Optional[str] = None
) -> Dict[str, Any]:
    """Reverts the changes made to a Variable in the workspace, restoring the last published version.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        variable_id: The Variable ID to revert.
        workspace_id: Optional workspace ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    clean_id = str(variable_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)
    return gtm_request(
        f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/variables/{clean_id}:revert",
        method="POST",
    )

@mcp.tool()
def revert_gtm_builtin_variable(
    account_id: str, container_id: str, variable_type: str, workspace_id: Optional[str] = None
) -> Dict[str, Any]:
    """Reverts a Built-in Variable to its last published state (enabled/disabled) in the workspace.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        variable_type: The built-in variable type (e.g. 'clickUrl', 'pageUrl', 'formId').
        workspace_id: Optional workspace ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)
    return gtm_request(
        f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/built_in_variables:revert",
        method="POST",
        params={"type": variable_type.strip()},
    )