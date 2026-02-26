from fastapi import APIRouter, Header, HTTPException, status

from app.api.deps import AuthServiceDep, CurrentUser
from app.config import settings
from app.schemas.auth import OAuthLogin, TokenResponse, UserCreate, UserLogin, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, service: AuthServiceDep) -> UserResponse:
    user = await service.register(
        email=data.email, password=data.password, full_name=data.full_name
    )
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, service: AuthServiceDep) -> TokenResponse:
    token = await service.login(email=data.email, password=data.password)
    return TokenResponse(access_token=token)


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
