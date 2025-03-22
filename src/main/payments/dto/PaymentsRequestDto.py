from pydantic import BaseModel

class PaymentsRequestDto(BaseModel):
    file_id: str