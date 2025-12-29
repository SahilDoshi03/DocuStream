from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.nango import nango_service

router = APIRouter()


class ConnectTokenResponse(BaseModel):
    token: str


@router.get("/connect-token", response_model=ConnectTokenResponse)
def get_connect_token(user_id: str = "test-user-1"):
    try:
        token = nango_service.create_connect_session(user_id)
        if not token:
            raise Exception("Token is None (check server logs for API error)")
        return {"token": token}
    except Exception as e:
        # Re-raise with detail for debugging
        raise HTTPException(status_code=500, detail=str(e))
