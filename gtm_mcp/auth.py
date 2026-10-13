import os
import time
import urllib.request
import urllib.parse
import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("gtm_mcp.auth")

_access_token: Optional[str] = None
_token_expires_at: float = 0.0

GTM_API_BASE = "https://tagmanager.googleapis.com/tagmanager/v2"


def get_client_id() -> str:
    cid = os.environ.get("GTM_CLIENT_ID")
    if not cid:
        raise ValueError("GTM_CLIENT_ID environment variable not set.")
    return cid.strip()


def get_client_secret() -> str:
    secret = os.environ.get("GTM_CLIENT_SECRET")
    if not secret:
        raise ValueError("GTM_CLIENT_SECRET environment variable not set.")
    return secret.strip()


def get_refresh_token() -> str:
    token = os.environ.get("GTM_REFRESH_TOKEN")
    if not token:
        raise ValueError("GTM_REFRESH_TOKEN environment variable not set.")
    return token.strip()


def get_access_token() -> str:
    """Returns a valid Google OAuth access token, refreshing if necessary."""
    global _access_token, _token_expires_at

    now = time.time()
    if _access_token and now < (_token_expires_at - 60):
        return _access_token

    client_id = get_client_id()
    client_secret = get_client_secret()
    refresh_token = get_refresh_token()

    token_url = "https://oauth2.googleapis.com/token"
    payload = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }).encode("utf-8")

    req = urllib.request.Request(
        token_url,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
            _access_token = data["access_token"]
            expires_in = data.get("expires_in", 3600)
            _token_expires_at = now + expires_in
            logger.info("Successfully refreshed GTM access token.")
            return _access_token
    except Exception as e:
        logger.error(f"Failed to refresh OAuth token: {e}")
        raise RuntimeError(f"Could not refresh Google OAuth token: {e}")


def gtm_request(
    path: str,
    method: str = "GET",
    params: Optional[Dict[str, Any]] = None,
    json_body: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Makes an authenticated request to the Google Tag Manager API v2."""
    token = get_access_token()
    
    clean_path = path.lstrip("/")
    url = f"{GTM_API_BASE}/{clean_path}"

    if params:
        query_str = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
        if query_str:
            url = f"{url}?{query_str}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    data = None
    if json_body is not None:
        data = json.dumps(json_body).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read().decode("utf-8")
            if not content:
                return {}
            return json.loads(content)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        try:
            err_json = json.loads(error_body)
            msg = err_json.get("error", {}).get("message", error_body)
        except Exception:
            msg = error_body
        logger.error(f"GTM API Error HTTP {e.code} on {url}: {msg}")
        raise RuntimeError(f"GTM API Error ({e.code}): {msg}")
    except Exception as e:
        logger.error(f"HTTP Request failed on {url}: {e}")
        raise RuntimeError(f"Request failed: {e}")
