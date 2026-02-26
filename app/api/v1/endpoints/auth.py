from fastapi import APIRouter, Header, HTTPException, status

from app.api.deps import AuthServiceDep, CurrentUser
from app.config import settings
from app.schemas.auth import OAuthLogin, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/oauth-login", response_model=TokenResponse)
async def oauth_login(
    data: OAuthLogin,
    service: AuthServiceDep,
    x_oauth_bridge_secret: str = Header(...),
) -> TokenResponse:
    if not settings.OAUTH_BRIDGE_SECRET or x_oauth_bridge_secret != settings.OAUTH_BRIDGE_SECRET:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid bridge secret")
    token = await service.oauth_login(
        email=data.email, full_name=data.full_name, oauth_provider=data.oauth_provider
    )
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def me(current_user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(current_user)
