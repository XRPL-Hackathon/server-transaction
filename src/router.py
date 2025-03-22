from fastapi import APIRouter

from src.main.health.router import HealthAPIRouter
from src.main.payments.router import PaymentsAPIRouter


router = APIRouter(
    prefix="",
)

router.include_router(HealthAPIRouter.router)
router.include_router(PaymentsAPIRouter.router)