from fastapi import APIRouter, Header, HTTPException, Request, status

from app.api.deps import CurrentUser, PaymentServiceDep
from app.schemas.payment import (
    CreateCheckoutRequest,
    CreateCheckoutResponse,
    SubscriptionStatusResponse,
    SubscriptionTier,
)

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/checkout", response_model=CreateCheckoutResponse)
async def create_checkout(
    data: CreateCheckoutRequest,
    service: PaymentServiceDep,
    current_user: CurrentUser,
) -> CreateCheckoutResponse:
    if data.tier not in (SubscriptionTier.PAID, SubscriptionTier.PREMIUM):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tier. Choose 'paid' or 'premium'.",
        )
    result = await service.create_subscription(current_user, data.tier)
    return CreateCheckoutResponse(**result)


@router.post("/webhook", status_code=200)
async def razorpay_webhook(
    request: Request,
    service: PaymentServiceDep,
    x_razorpay_signature: str = Header(""),
) -> dict:
    body = await request.body()
    try:
        await service.handle_webhook(body, x_razorpay_signature)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return {"status": "ok"}


@router.get("/status", response_model=SubscriptionStatusResponse)
async def subscription_status(
    service: PaymentServiceDep,
    current_user: CurrentUser,
) -> SubscriptionStatusResponse:
    result = service.get_status(current_user)
    return SubscriptionStatusResponse(**result)
