from fastapi import Header, HTTPException
from typing import Annotated
import uuid

async def get_current_user(x_auth_sub: Annotated[str | None, Header()] = None) -> uuid.UUID:
    if not x_auth_sub:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )
    try:
        return uuid.UUID(x_auth_sub)
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        ) 