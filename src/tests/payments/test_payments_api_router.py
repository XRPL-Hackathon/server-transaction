# import pytest
# from unittest.mock import MagicMock, patch
# from src.main.payments.service.PaymentsService import PaymentsService

# # 테스트용 고정 값 -- 바꿔야 합니다.
# TEST_USER_ID = "11111111-2222-3333-6666-555555555555"
# TEST_FILE_ID = "67de75eca76bd4020aab2da5"
# TEST_SEED = "snYP7oArxKepd3GPDcrjMsJYiJeJB"  # 테스트넷 용 시드
# TEST_SELLER_ID = "11111111-2222-3333-4444-555555555555"
# TEST_SELLER_WALLET = "rKrLduwLhgCtgXaoqCQJJE1RRzRXPQ4UPR"

# @pytest.fixture
# def mock_repository():
#     repo = MagicMock()
#     # 거래 이력 없음
#     repo.is_transaction_exist.return_value = False

#     # 구매자 지갑 주소
#     repo.get_user_wallet.side_effect = lambda user_id: (
#         "rL2NkVRopQ7c3VsB6LfCrMF4ZBLzDRdGXg" if user_id == TEST_USER_ID else TEST_SELLER_WALLET
#     )

#     # 파일 정보
#     repo.get_file_info.return_value = {
#         "price": 10,
#         "uploader_id": TEST_SELLER_ID
#     }

#     # 유저 프로필
#     repo.get_user_profile.return_value = {
#         "profile": {
#             "rlusd": 5,
#             "nft_rank": "gold"
#         }
#     }

#     return repo

# @patch("src.main.payments.service.PaymentsService.reliable_submission")
# @patch("src.main.payments.service.PaymentsService.autofill_and_sign")
# def test_request_payment_success(mock_sign_tx, mock_submit_tx, mock_repository):
#     # XRPL 트랜잭션 결과 mocking
#     mock_submit_result = MagicMock()
#     mock_submit_result.result = {"engine_result": "tesSUCCESS", "tx_json": {"hash": "ABC123HASH"}}
#     mock_submit_tx.return_value = mock_submit_result

#     # 서명된 트랜잭션도 더미로 넘김
#     mock_sign_tx.return_value = MagicMock()

#     service = PaymentsService()
#     service.payments_repository = mock_repository

#     response = service.request_payment(TEST_USER_ID, TEST_FILE_ID, TEST_SEED)

#     assert response["status"] == "success"
#     assert response["original_price"] == 10
#     assert response["used_rlusd"] == 1  # 10% of 10
#     assert response["discounted_price"] == 9
#     assert response["nft_rank"] == "gold"
#     assert response["transaction_hash"] == "ABC123HASH"

#     # DB에 저장했는지 확인
#     mock_repository.update_user_rlusd.assert_called_once_with(TEST_USER_ID, 4)
#     mock_repository.save_transaction.assert_called_once()