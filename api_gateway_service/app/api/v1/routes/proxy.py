from fastapi import APIRouter, Request, HTTPException
from app.services.routing_service import resolve_service
from app.services.proxy_service import forward_request
from app.services.streaming_proxy_service import stream_request

router = APIRouter()


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(request: Request, path: str):

    full_path = f"/api/v1/{path}"

    service_url, prefix = resolve_service(full_path)

    if not service_url:
        raise HTTPException(status_code=404, detail="Service not found")

    # 🔥 Detect AI streaming endpoints
    if full_path.startswith("/api/v1/ai"):
        return await stream_request(request, service_url, full_path)

    # normal request
    return await forward_request(request, service_url, full_path)