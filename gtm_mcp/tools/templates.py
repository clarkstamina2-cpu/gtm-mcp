from typing import Any, Dict, List, Optional
from gtm_mcp.coordinator import mcp
from gtm_mcp.auth import gtm_request
from gtm_mcp.tools.workspaces import _get_default_workspace_id


@mcp.tool()
def list_gtm_templates(
    account_id: str, container_id: str, workspace_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Lists all Custom Templates (modelos personalizados de tags/variáveis) in a GTM workspace.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        workspace_id: Optional workspace ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)
    res = gtm_request(f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/templates")
    return res.get("template", [])


@mcp.tool()
def get_gtm_template(
    account_id: str, container_id: str, template_id: str, workspace_id: Optional[str] = None
) -> Dict[str, Any]:
    """Gets details and code of a specific Custom Template.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        template_id: The Template ID.
        workspace_id: Optional workspace ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    clean_tpl = str(template_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)
    return gtm_request(f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/templates/{clean_tpl}")


@mcp.tool()
def create_gtm_template(
    account_id: str,
    container_id: str,
    name: str,
    template_data: str,
    workspace_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Creates a new Custom Template in a GTM workspace.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        name: Template name.
        template_data: Sandboxed JavaScript / template definition data.
        workspace_id: Optional workspace ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)
    body = {"name": name, "templateData": template_data}
    return gtm_request(
        f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/templates",
        method="POST",
        json_body=body,
    )


@mcp.tool()
def delete_gtm_template(
    account_id: str, container_id: str, template_id: str, workspace_id: Optional[str] = None
) -> Dict[str, Any]:
    """Deletes a Custom Template from a GTM workspace.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        template_id: The Template ID.
        workspace_id: Optional workspace ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    clean_tpl = str(template_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)
    gtm_request(
        f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/templates/{clean_tpl}",
        method="DELETE",
    )
    return {"status": "deleted", "template_id": clean_tpl}


@mcp.tool()
def update_gtm_template(
    account_id: str,
    container_id: str,
    template_id: str,
    name: Optional[str] = None,
    template_data: Optional[str] = None,
    workspace_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Updates an existing Custom Template (name and/or code). Only the fields you pass are changed.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        template_id: The Template ID to update.
        name: Optional new name.
        template_data: Optional new template definition (sandboxed JavaScript / template data).
        workspace_id: Optional workspace ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    clean_tpl = str(template_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)
    path = f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/templates/{clean_tpl}"

    existing = gtm_request(path)
    if name is not None:
        existing["name"] = name
    if template_data is not None:
        existing["templateData"] = template_data

    return gtm_request(path, method="PUT", json_body=existing)


@mcp.tool()
def revert_gtm_template(
    account_id: str, container_id: str, template_id: str, workspace_id: Optional[str] = None
) -> Dict[str, Any]:
    """Reverts the changes made to a Custom Template in the workspace, restoring the last published version.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        template_id: The Template ID to revert.
        workspace_id: Optional workspace ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    clean_tpl = str(template_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)
    return gtm_request(
        f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/templates/{clean_tpl}:revert",
        method="POST",
    )