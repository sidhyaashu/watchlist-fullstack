from fastapi import HTTPException
from app.core.exceptions import BadRequestException, NotFoundException, UnauthorizedException


async def handle_service_error(coro):
    """
    Awaits a service coroutine and maps domain exceptions to clean HTTP responses.
    Keeps API handlers thin — no try/except sprawl across routes.
    """
    try:
        return await coro
    except BadRequestException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedException:
        raise HTTPException(status_code=403, detail="Forbidden")
