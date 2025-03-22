import asyncio
from xrpl.wallet import Wallet
from xrpl.utils import xrp_to_drops
from xrpl.asyncio.clients import AsyncJsonRpcClient
from src.main.payments.repository.PaymentsRepository import PaymentsRepository
from src.main.config.XrplConfig import client
from fastapi import HTTPException
from datetime import datetime, UTC
from src.main.config.XrplConfig import client as sync_client
from xrpl.clients import JsonRpcClient
from xrpl.transaction import (
    autofill_and_sign,
    submit_and_wait,
    XRPLReliableSubmissionException,
)
from xrpl.models.transactions import Transaction, Payment

client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")

NET_DISCOUNT_RATE = {
    "bronze": 0,
    "silver": 0.05,
    "gold": 0.10,
    "platinum": 0.20
}

def submit_transaction(
        client: JsonRpcClient,
        wallet: Wallet,
        transaction: Transaction,
        check_fee: bool = True,
) -> dict:
    signed_tx = autofill_and_sign(
        transaction=transaction,
        client=client,
        wallet=wallet,
        check_fee=check_fee,
    )

    signed_tx.validate()

    response = submit_and_wait(transaction=signed_tx, client=client, wallet=wallet)

    if not response.is_successful():
        raise XRPLReliableSubmissionException(response.result)

    return response.result    


class PaymentsService:
    def __init__(self):
        self.payments_repository = PaymentsRepository()

    # XRPL 결제 요청 처리
    def request_payment(self, user_id: str, file_id: str):
        if self.payments_repository.is_transaction_exist(user_id, file_id):
            raise HTTPException(status_code=409, detail="이미 결제한 항목입니다.")
        
        # 사용자 XRPL 지갑 주소 가져오기
        wallet_data = self.payments_repository.get_user_wallet(user_id)
        if not wallet_data or "seed" not in wallet_data or "address" not in wallet_data:
            raise HTTPException(status_code=404, detail="사용자의 XRPL 지갑 정보가가 존재하지 않습니다.")
        
        sender_secret = wallet_data["seed"]
        sender_wallet_address = wallet_data["address"]

        print(f"[INFO] Sender wallet address: {sender_wallet_address}")
        
        # 파일 정보 조회 (가격 + 판매자 ID)
        file_info = self.payments_repository.get_file_info(file_id)
        if not file_info:
            return HTTPException(status_code=404, detail="파일 정보 없음")
        
        file_price = file_info["price"]
        seller_id = file_info["uploader_id"]
        
        # 판매자의 지갑 주소 가져오기
        receiver_wallet_address = self.payments_repository.get_user_wallet(seller_id)
        if not receiver_wallet_address:
            return HTTPException(status_cod=404, detail="판매자의 XRPL 지갑 없음")
        
        receiver_wallet_address = receiver_wallet_address["address"]
        
        user_profile = self.payments_repository.get_user_profile(user_id)
        profile = user_profile.get("profile", {})
        user_rlusd = profile.get("rlusd", 0)
        nft_rank = profile.get("nft_rank", "bronze").lower()
        max_discount_rate = NET_DISCOUNT_RATE.get(nft_rank, 0)

        max_rlusd_usable = int(file_price * max_discount_rate)
        use_rlusd = min(user_rlusd, max_rlusd_usable)
        discounted_price = file_price - use_rlusd
        
        sender_wallet = Wallet.from_seed(sender_secret)

        from xrpl.models.requests import AccountInfo
        try:
            print(f"[CHECK] XRPL에 등록된 지갑인지 확인 중... {sender_wallet.classic_address}")
            info = client.request(AccountInfo(account=sender_wallet.classic_address))
            print(f"[SUCCESS] Account exists! info: {info.result}")
        except Exception as e:
            print(f"[FAIL] XRPL에 계정 없음 (actNotFound 가능성): {e}")
            raise HTTPException(status_code=500, detail=f"XRPL 지갑이 네트워크에 존재하지 않음: {e}")


        # 결제 트랜잭션 생성 및 전송
        payment_tx = Payment(
            account=sender_wallet.classic_address,
            amount=xrp_to_drops(discounted_price),
            destination=str(receiver_wallet_address)
        )

        # 동기적으로 autofill_and_sign 호출 (스레드에서 실행)
        try:
            print("[ACTION] 서명 및 전송 시작")

            result = submit_transaction(
                client=client,
                wallet=sender_wallet,
                transaction=payment_tx,
                check_fee=True
            )
        except XRPLReliableSubmissionException as e:

            print(f"[ERROR] XRPLReliableSubmissionException: {e}")

            raise HTTPException(status_code=400, detail=f"트랜잭션 실패: {str(e)}")
        except Exception as e:

            print(f"[ERROR] 기타 XRPL 오류: {e}")

            raise HTTPException(status_code=500, detail=f"XRPL 처리 중 오류: {e}")
        
        tx_hash = result.get("tx_json", {}).get("hash", "Unknown")
        
        self.payments_repository.update_user_rlusd(user_id, user_rlusd - use_rlusd)
        self.payments_repository.save_transaction({
            "user_id": user_id,
            "file_id": file_id,
            "transaction_hash": tx_hash,
            "price" : file_price,
            "amount": discounted_price,
            "discounted_amount": use_rlusd,
            "nft_rank": nft_rank,
            "timestamp": datetime.now(UTC)
        })

        return {
            "status": "success",
            "message": "결제 완료",
            "original_price": file_price,
            "discounted_price": discounted_price,
            "used_rlusd": use_rlusd,
            "nft_rank": nft_rank,
            "transaction_hash": tx_hash
        }
    
    def confirm_payment(self, file_id: str, payment_intent_id: str):
        return {
            "status": "success",
            "message": "결제 확인 완료"
        }