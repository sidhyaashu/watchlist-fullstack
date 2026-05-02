import httpx
from fastapi import Request, Response


def _build_identity_headers(request: Request) -> dict:
    """Build headers to inject into forwarded requests for downstream identity propagation."""
    headers = dict(request.headers)
    
    # Strip headers the Gateway has already processed to prevent leakage
    headers.pop("host", None)
    
    # We must preserve credentials when routing to the Auth Service so it can process 
    # logins, logouts, token refreshes, and profile fetches. We strip them for all other microservices.
    if not (request.url.path.startswith("/api/v1/auth") or request.url.path.startswith("/api/v1/user")):
        headers.pop("authorization", None)
        headers.pop("cookie", None)

    user_id = getattr(request.state, "user_id", None)
    scopes = getattr(request.state, "scopes", None)
    auth_type = getattr(request.state, "auth_type", None)
    request_id = getattr(request.state, "request_id", None)

    if user_id:
        headers["X-User-ID"] = str(user_id)
    if scopes:
        headers["X-Scopes"] = str(scopes)
    if auth_type:
        headers["X-Auth-Type"] = str(auth_type)
    if request_id:
        headers["X-Request-ID"] = str(request_id)

    # 🌐 Forward host and port for correct redirect URI generation
    headers["X-Forwarded-Host"] = request.headers.get("host", "localhost")
    headers["X-Forwarded-Port"] = str(request.url.port or (443 if request.url.scheme == "https" else 80))

    return headers


async def forward_request(
    request: Request,
    target_url: str,
    path: str,
) -> Response:
    """Forward a standard (non-streaming) HTTP request to a downstream service."""
    client: httpx.AsyncClient = request.app.state.client
    url = f"{target_url}{path}"
    headers = _build_identity_headers(request)
    content_type = request.headers.get("content-type", "")

    # ─── Multipart / file upload ──────────────────────────────────
    if "multipart/form-data" in content_type:
        # Remove Content-Type so httpx rebuilds it with the correct boundary
        headers.pop("content-type", None)
        form = await request.form()
        files = {}
        data = {}
        for key, value in form.multi_items():
            if hasattr(value, "read"):
                # SpooledUploadFile
                file_bytes = await value.read()
                files[key] = (value.filename, file_bytes, value.content_type)
            else:
                data[key] = value

        response = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            files=files or None,
            data=data or None,
            params=request.query_params,
        )

    # ─── Standard JSON / form-urlencoded / raw body ───────────────
    else:
        body = await request.body()
        response = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=body,
            params=request.query_params,
        )

    return Response(
        content=response.content if response.status_code not in (204, 304) else None,
        status_code=response.status_code,
        headers=dict(response.headers),
    )