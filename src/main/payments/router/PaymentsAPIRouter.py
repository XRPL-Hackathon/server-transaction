from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool
from src.main.payments.dto.PaymentsRequestDto import PaymentsRequestDto
from src.main.payments.service.PaymentsService import PaymentsService
from src.main.auth.dependencies import get_current_user
import uuid

router = APIRouter(
    prefix="/payments",
    tags=["payments"],
)

@router.post("/_request")
async def request_payment(
    request: PaymentsRequestDto,
    user_id: uuid.UUID = Depends(get_current_user),
    payments_service: PaymentsService = Depends()
):
    return await run_in_threadpool(
        payments_service.request_payment, str(user_id), request.file_id
    )