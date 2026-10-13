from typing import Any, Dict, List, Optional
from gtm_mcp.coordinator import mcp
from gtm_mcp.auth import gtm_request


@mcp.tool()
def list_gtm_accounts() -> List[Dict[str, Any]]:
    """Returns all Google Tag Manager accounts accessible by the authenticated user.

    Use this tool to find account IDs and names for all agency clients.
    """
    res = gtm_request("accounts")
    accounts = res.get("account", [])
    return [
        {
            "account_id": a.get("accountId"),
            "name": a.get("name"),
            "share_data": a.get("shareData", False),
            "path": a.get("path"),
        }
        for a in accounts
    ]


@mcp.tool()
def get_gtm_account(account_id: str) -> Dict[str, Any]:
    """Gets details of a specific GTM account.

    Args:
        account_id: The GTM account ID (e.g. '6004238812').
    """
    clean_id = str(account_id).strip()
    return gtm_request(f"accounts/{clean_id}")


@mcp.tool()
def update_gtm_account(
    account_id: str, name: str, share_data: Optional[bool] = None
) -> Dict[str, Any]:
    """Updates a GTM account name or data sharing settings.

    Args:
        account_id: The GTM account ID.
        name: The new name of the account.
        share_data: Whether to share data anonymously with Google.
    """
    clean_id = str(account_id).strip()
    existing = gtm_request(f"accounts/{clean_id}")
    existing["name"] = name
    if share_data is not None:
        existing["shareData"] = share_data
    return gtm_request(f"accounts/{clean_id}", method="PUT", json_body=existing)


@mcp.tool()
def list_gtm_account_user_permissions(account_id: str) -> List[Dict[str, Any]]:
    """Lists all user permissions for a GTM account.

    Args:
        account_id: The GTM account ID.
    """
    clean_id = str(account_id).strip()
    res = gtm_request(f"accounts/{clean_id}/user_permissions")
    return res.get("userPermission", [])


@mcp.tool()
def get_gtm_account_user_permission(
    account_id: str, user_permission_id: str
) -> Dict[str, Any]:
    """Gets a specific user's permissions on a GTM account.

    Args:
        account_id: The GTM account ID.
        user_permission_id: The user permission ID (or email).
    """
    clean_acc = str(account_id).strip()
    clean_perm = str(user_permission_id).strip()
    return gtm_request(f"accounts/{clean_acc}/user_permissions/{clean_perm}")


@mcp.tool()
def create_gtm_account_user_permission(
    account_id: str,
    email_address: str,
    account_access_permission: str = "user",
    container_access: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Adds a new user to a GTM account with specified permissions.

    Args:
        account_id: The GTM account ID.
        email_address: The user's Google email address.
        account_access_permission: 'admin', 'user', or 'noAccess'.
        container_access: Optional list of container permissions (e.g. [{'containerId': '123', 'permission': 'publish'}]).
    """
    clean_acc = str(account_id).strip()
    body = {
        "emailAddress": email_address.strip(),
        "accountAccess": {"permission": account_access_permission},
        "containerAccess": container_access or [],
    }
    return gtm_request(
        f"accounts/{clean_acc}/user_permissions", method="POST", json_body=body
    )


@mcp.tool()
def update_gtm_account_user_permission(
    account_id: str,
    user_permission_id: str,
    account_access_permission: Optional[str] = None,
    container_access: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Updates an existing user's permissions on a GTM account.

    Args:
        account_id: The GTM account ID.
        user_permission_id: The user permission ID.
        account_access_permission: Optional new account permission ('admin', 'user', 'noAccess').
        container_access: Optional updated container access list.
    """
    clean_acc = str(account_id).strip()
    clean_perm = str(user_permission_id).strip()
    existing = gtm_request(f"accounts/{clean_acc}/user_permissions/{clean_perm}")
    if account_access_permission:
        existing.setdefault("accountAccess", {})["permission"] = account_access_permission
    if container_access is not None:
        existing["containerAccess"] = container_access
    return gtm_request(
        f"accounts/{clean_acc}/user_permissions/{clean_perm}",
        method="PUT",
        json_body=existing,
    )


@mcp.tool()
def delete_gtm_account_user_permission(
    account_id: str, user_permission_id: str
) -> Dict[str, Any]:
    """Removes a user's permissions from a GTM account.

    Args:
        account_id: The GTM account ID.
        user_permission_id: The user permission ID.
    """
    clean_acc = str(account_id).strip()
    clean_perm = str(user_permission_id).strip()
    gtm_request(f"accounts/{clean_acc}/user_permissions/{clean_perm}", method="DELETE")
    return {"status": "deleted", "user_permission_id": clean_perm}
