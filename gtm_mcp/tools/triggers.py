from typing import Any, Dict, List, Optional
from gtm_mcp.coordinator import mcp
from gtm_mcp.auth import gtm_request
from gtm_mcp.tools.tags import _get_default_workspace_id

def _param_value(param: Optional[Dict[str, Any]]) -> Optional[str]:
    return (param or {}).get("value")


def _apply_link_click_settings(
    body: Dict[str, Any],
    wait_for_tags: Optional[bool],
    wait_for_tags_timeout: Optional[int],
    check_validation: Optional[bool],
) -> None:
    if wait_for_tags is not None:
        body["waitForTags"] = {"type": "boolean", "value": str(wait_for_tags).lower()}
        if wait_for_tags and wait_for_tags_timeout is None and not _param_value(body.get("waitForTagsTimeout")):
            wait_for_tags_timeout = 2000
    if wait_for_tags_timeout is not None:
        body["waitForTagsTimeout"] = {"type": "template", "value": str(int(wait_for_tags_timeout))}
    if check_validation is not None:
        body["checkValidation"] = {"type": "boolean", "value": str(check_validation).lower()}


@mcp.tool()
def list_gtm_triggers(
    account_id: str, container_id: str, workspace_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Lists all Triggers (Acionadores) in a GTM container workspace (e.g. Page Views, Custom Events, Form Submissions, Clicks, etc.).

    Conditions come back exactly as GTM stores them: 'ignore_case' / 'negate' appear inside each condition's
    'parameter' list only when they are on (missing = false). For link click / form triggers, wait_for_tags,
    wait_for_tags_timeout and check_validation show the stored value; None means not set, which GTM treats as off.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        workspace_id: Optional workspace ID. If omitted, uses default workspace.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)

    res = gtm_request(f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/triggers")
    triggers = res.get("trigger", [])
    return [
        {
            "trigger_id": t.get("triggerId"),
            "name": t.get("name"),
            "type": t.get("type"),  # e.g. 'pageview', 'customEvent', 'click', 'formSubmission'
            "custom_event_filter": t.get("customEventFilter", []),
            "filter": t.get("filter", []),
            "auto_event_filter": t.get("autoEventFilter", []),
            "wait_for_tags": _param_value(t.get("waitForTags")),
            "wait_for_tags_timeout": _param_value(t.get("waitForTagsTimeout")),
            "check_validation": _param_value(t.get("checkValidation")),
            "path": t.get("path"),
        }
        for t in triggers
    ]


@mcp.tool()
def get_gtm_trigger(
    account_id: str, container_id: str, trigger_id: str, workspace_id: Optional[str] = None
) -> Dict[str, Any]:
    """Gets details and rules of a specific GTM Trigger.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        trigger_id: The Trigger ID.
        workspace_id: Optional workspace ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    clean_trig = str(trigger_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)

    return gtm_request(f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/triggers/{clean_trig}")


@mcp.tool()
def create_gtm_trigger(
    account_id: str,
    container_id: str,
    name: str,
    type: str,
    custom_event_filter: Optional[List[Dict[str, Any]]] = None,
    filter: Optional[List[Dict[str, Any]]] = None,
    auto_event_filter: Optional[List[Dict[str, Any]]] = None,
    wait_for_tags: Optional[bool] = None,
    wait_for_tags_timeout: Optional[int] = None,
    check_validation: Optional[bool] = None,
    workspace_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Creates a new Trigger (Acionador) in a GTM workspace.

    Condition format: {'type': 'contains'|'equals'|'startsWith'|'endsWith'|'matchRegex'|'cssSelector'|...,
    'parameter': [{'type': 'template', 'key': 'arg0', 'value': '{{Click URL}}'},
                  {'type': 'template', 'key': 'arg1', 'value': 'whatsapp'}]}.
    Optional flags go in the same 'parameter' list: {'type': 'boolean', 'key': 'ignore_case', 'value': 'true'}
    (GTM only honors it on 'matchRegex'; the other types are always case-sensitive) and
    {'type': 'boolean', 'key': 'negate', 'value': 'true'} (the "does not ..." variants). Missing flag = false.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        name: Name for the Trigger (e.g. 'Event - Click WhatsApp', 'Page View - Obrigado').
        type: GTM Trigger type (e.g. 'pageview', 'customEvent', 'linkClick', 'click', 'formSubmission').
        custom_event_filter: Rules for custom events.
        filter: Filter conditions for when the trigger fires (see the condition format above).
        auto_event_filter: Optional "enable this trigger when" conditions (link click / form triggers).
        wait_for_tags: Link click / form only. True = hold the navigation until the tags fire ("Wait for tags").
            Use it when the link opens in the same tab, or the page may leave before the conversion is sent.
        wait_for_tags_timeout: Max wait in ms (GTM default 2000). Set to 2000 automatically when wait_for_tags=True.
        check_validation: Link click / form only. True = fire only if the click/submit was not blocked ("Check validation").
        workspace_id: Optional workspace ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)

    body = {
        "name": name,
        "type": type,
        "customEventFilter": custom_event_filter or [],
        "filter": filter or [],
    }
    if auto_event_filter is not None:
        body["autoEventFilter"] = auto_event_filter
    _apply_link_click_settings(body, wait_for_tags, wait_for_tags_timeout, check_validation)

    return gtm_request(
        f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/triggers",
        method="POST",
        json_body=body,
    )


@mcp.tool()
def delete_gtm_trigger(
    account_id: str, container_id: str, trigger_id: str, workspace_id: Optional[str] = None
) -> Dict[str, Any]:
    """Deletes a Trigger from a GTM workspace.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        trigger_id: The Trigger ID to delete.
        workspace_id: Optional workspace ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    clean_trig = str(trigger_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)

    gtm_request(
        f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/triggers/{clean_trig}",
        method="DELETE",
    )
    return {"status": "deleted", "trigger_id": clean_trig}


@mcp.tool()
def update_gtm_trigger(
    account_id: str,
    container_id: str,
    trigger_id: str,
    name: Optional[str] = None,
    custom_event_filter: Optional[List[Dict[str, Any]]] = None,
    filter: Optional[List[Dict[str, Any]]] = None,
    auto_event_filter: Optional[List[Dict[str, Any]]] = None,
    wait_for_tags: Optional[bool] = None,
    wait_for_tags_timeout: Optional[int] = None,
    check_validation: Optional[bool] = None,
    workspace_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Updates an existing Trigger (Acionador). Only the fields you pass are changed; everything else is kept.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        trigger_id: The Trigger ID to update.
        name: Optional new name.
        custom_event_filter: Optional new custom event rules (replaces the current list).
        filter: Optional new filter conditions (replaces the current list). Same condition format as
            create_gtm_trigger, including the 'ignore_case' / 'negate' flags.
        auto_event_filter: Optional new auto-event filter (replaces the current list).
        wait_for_tags: Link click / form only. True turns on "Wait for tags" (timeout defaults to 2000 ms).
        wait_for_tags_timeout: Optional max wait in ms.
        check_validation: Link click / form only. True turns on "Check validation".
        workspace_id: Optional workspace ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    clean_trig = str(trigger_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)
    path = f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/triggers/{clean_trig}"

    existing = gtm_request(path)
    if name is not None:
        existing["name"] = name
    if custom_event_filter is not None:
        existing["customEventFilter"] = custom_event_filter
    if filter is not None:
        existing["filter"] = filter
    if auto_event_filter is not None:
        existing["autoEventFilter"] = auto_event_filter
    _apply_link_click_settings(existing, wait_for_tags, wait_for_tags_timeout, check_validation)

    return gtm_request(path, method="PUT", json_body=existing)


@mcp.tool()
def revert_gtm_trigger(
    account_id: str, container_id: str, trigger_id: str, workspace_id: Optional[str] = None
) -> Dict[str, Any]:
    """Reverts the changes made to a Trigger in the workspace, restoring the last published version.

    Args:
        account_id: The GTM account ID.
        container_id: The GTM container ID.
        trigger_id: The Trigger ID to revert.
        workspace_id: Optional workspace ID.
    """
    clean_acc = str(account_id).strip()
    clean_cont = str(container_id).strip()
    clean_trig = str(trigger_id).strip()
    ws_id = str(workspace_id).strip() if workspace_id else _get_default_workspace_id(clean_acc, clean_cont)
    return gtm_request(
        f"accounts/{clean_acc}/containers/{clean_cont}/workspaces/{ws_id}/triggers/{clean_trig}:revert",
        method="POST",
    )