import httpx
from fastapi import Request
from starlette.responses import StreamingResponse
from app.services.proxy_service import _build_identity_headers


async def stream_request(
    request: Request,
    target_url: str,
    path: str,
) -> StreamingResponse:
    """
    Stream a response chunk-by-chunk from a downstream AI/LLM service.
    Supports SSE (text/event-stream). Does NOT buffer the response.
    """
    url = f"{target_url}{path}"
    headers = _build_identity_headers(request)

    # For streaming, remove Transfer-Encoding to avoid protocol conflicts
    headers.pop("transfer-encoding", None)

    body = await request.body()

    async def event_generator():
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                method=request.method,
                url=url,
                headers=headers,
                params=request.query_params,
                content=body,
            ) as response:
                async for chunk in response.aiter_bytes():
                    yield chunk

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )