from fastapi import APIRouter

from src.main.health.router import HealthAPIRouter


router = APIRouter(
    prefix="",
)

router.include_router(HealthAPIRouter.router)