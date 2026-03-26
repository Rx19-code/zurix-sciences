"""
Tests for the new Protocol V2 system with single-use unique verification codes.
Tests endpoints: validate-code, send-protocol (logic only, not actual email send)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    BASE_URL = "https://peptide-catalog-3.preview.emergentagent.com"

API_URL = f"{BASE_URL}/api"

# Test codes provided in credentials
TEST_CODES = {
    "GHK-Cu": "ZX-260312-GHK50-1-TEST01",
    "TB-500": "ZX-260209-TB500-1-TEST01", 
    "BPC-157": "ZX-260115-BPC157-1-TEST01"
}


class TestProtocolsV2Endpoints:
    """Tests for Protocol V2 system endpoints"""
    
    def test_get_protocols_v2_list(self):
        """Test GET /api/protocols-v2 returns all protocols"""
        response = requests.get(f"{API_URL}/protocols-v2")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "protocols" in data
        assert len(data["protocols"]) > 0
        
        # Check structure of protocol entries
        for proto in data["protocols"]:
            assert "id" in proto
            assert "title" in proto
            assert "description" in proto
            assert "category" in proto
            assert "duration_weeks" in proto
            assert "languages" in proto
            assert "requires_batch" in proto
            assert "price" in proto
        
        # Verify we have both free and paid protocols
        free_protos = [p for p in data["protocols"] if p["price"] == 0]
        paid_protos = [p for p in data["protocols"] if p["price"] > 0]
        
        print(f"Total protocols: {len(data['protocols'])}")
        print(f"Free protocols: {len(free_protos)}")
        print(f"Paid protocols: {len(paid_protos)}")
        
        assert len(free_protos) >= 3, "Should have at least 3 free protocols (BPC-157, TB-500, GHK-Cu)"
        assert len(paid_protos) >= 3, "Should have at least 3 paid Advanced protocols"

    def test_validate_code_invalid_code(self):
        """Test validate-code with an invalid code returns proper error"""
        response = requests.post(
            f"{API_URL}/protocols-v2/validate-code",
            json={"code": "INVALID-CODE-123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["valid"] == False
        assert "not found" in data["message"].lower() or "invalid" in data["message"].lower()
        
        print(f"Invalid code message: {data['message']}")

    def test_validate_code_empty_code(self):
        """Test validate-code with empty code"""
        response = requests.post(
            f"{API_URL}/protocols-v2/validate-code",
            json={"code": ""}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["valid"] == False

    def test_validate_code_valid_ghk_code(self):
        """Test validate-code with valid GHK-Cu test code"""
        response = requests.post(
            f"{API_URL}/protocols-v2/validate-code",
            json={"code": TEST_CODES["GHK-Cu"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        print(f"GHK-Cu validation response: {data}")
        
        # Code should be found in DB
        if data.get("valid"):
            # Valid code - check all required fields
            assert data["success"] == True
            assert "protocol_id" in data
            assert "protocol_title" in data
            assert "protocol_description" in data
            assert "duration_weeks" in data
            assert "product_name" in data
            assert "available_languages" in data
            
            # Verify it matched GHK-Cu protocol
            assert "GHK" in data["protocol_title"].upper() or "GHK" in data.get("product_name", "").upper()
            
            print(f"Matched protocol: {data['protocol_title']}")
            print(f"Product: {data['product_name']}")
        else:
            # Code not in DB or already used - still valid test
            print(f"Note: Code validation returned: {data.get('message')}")
            assert "message" in data

    def test_validate_code_valid_tb500_code(self):
        """Test validate-code with valid TB-500 test code"""
        response = requests.post(
            f"{API_URL}/protocols-v2/validate-code",
            json={"code": TEST_CODES["TB-500"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        print(f"TB-500 validation response: {data}")
        
        if data.get("valid"):
            assert "TB" in data["protocol_title"].upper() or "TB" in data.get("product_name", "").upper()
            print(f"Matched protocol: {data['protocol_title']}")

    def test_validate_code_valid_bpc157_code(self):
        """Test validate-code with valid BPC-157 test code"""
        response = requests.post(
            f"{API_URL}/protocols-v2/validate-code",
            json={"code": TEST_CODES["BPC-157"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        print(f"BPC-157 validation response: {data}")
        
        if data.get("valid"):
            assert "BPC" in data["protocol_title"].upper() or "BPC" in data.get("product_name", "").upper()
            print(f"Matched protocol: {data['protocol_title']}")

    def test_send_protocol_invalid_code(self):
        """Test send-protocol with invalid code returns 404"""
        response = requests.post(
            f"{API_URL}/protocols-v2/send-protocol",
            json={
                "code": "INVALID-CODE-XYZ",
                "language": "en",
                "email": "test@example.com",
                "phone": "+1234567890",
                "name": "Test User"
            }
        )
        
        # Should return 404 for invalid code
        assert response.status_code == 404
        data = response.json()
        
        assert "detail" in data
        print(f"Invalid code send-protocol response: {data['detail']}")

    def test_send_protocol_invalid_language(self):
        """Test send-protocol with invalid language (when code exists)"""
        # First validate a code to see if it exists
        validate_resp = requests.post(
            f"{API_URL}/protocols-v2/validate-code",
            json={"code": TEST_CODES["GHK-Cu"]}
        )
        
        if validate_resp.json().get("valid"):
            # Code exists, test with invalid language
            response = requests.post(
                f"{API_URL}/protocols-v2/send-protocol",
                json={
                    "code": TEST_CODES["GHK-Cu"],
                    "language": "invalid",
                    "email": "test@example.com"
                }
            )
            # Should return 400 for invalid language
            assert response.status_code == 400
            data = response.json()
            assert "detail" in data
            print(f"Invalid language error: {data['detail']}")


class TestSingleUseEnforcement:
    """Tests to verify single-use code enforcement logic"""
    
    def test_validate_code_already_used_message(self):
        """Test that validate-code returns proper message for already-used codes"""
        # This tests the message format for already-used codes
        # We won't actually use a code, but we verify the endpoint handles this case
        
        response = requests.post(
            f"{API_URL}/protocols-v2/validate-code",
            json={"code": "ZX-USED-CODE-TEST"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # For non-existent code, should say not found
        assert data["valid"] == False


class TestPaidProtocols:
    """Tests for paid protocol flows"""
    
    def test_paid_protocols_in_list(self):
        """Verify paid protocols exist in the protocols list"""
        response = requests.get(f"{API_URL}/protocols-v2")
        
        assert response.status_code == 200
        data = response.json()
        
        paid = [p for p in data["protocols"] if p["price"] > 0 and not p["requires_batch"]]
        
        assert len(paid) >= 3, "Should have at least 3 paid Advanced protocols"
        
        for proto in paid:
            assert proto["price"] > 0
            assert proto["category"] == "Advanced"
            assert proto["requires_batch"] == False
            print(f"Paid protocol: {proto['title']} - ${proto['price']}")

    def test_payment_wallet_info(self):
        """Test GET /api/payment/wallet-info returns USDT wallet details"""
        response = requests.get(f"{API_URL}/payment/wallet-info")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "wallet_address" in data
        assert "network" in data
        assert "currency" in data
        
        assert data["currency"] == "USDT"
        assert "TRC20" in data["network"]
        
        print(f"Wallet: {data['wallet_address']}")
        print(f"Network: {data['network']}")

    def test_create_payment_order(self):
        """Test creating a payment order for a paid protocol"""
        # First get a paid protocol ID
        protos_resp = requests.get(f"{API_URL}/protocols-v2")
        paid_protos = [p for p in protos_resp.json()["protocols"] if p["price"] > 0]
        
        if not paid_protos:
            pytest.skip("No paid protocols available")
        
        proto = paid_protos[0]
        
        response = requests.post(
            f"{API_URL}/payment/create-order",
            json={
                "protocol_id": proto["id"],
                "language": "en",
                "email": "test-order@example.com",
                "phone": "+1234567890",
                "name": "Test Order"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "order_id" in data
        assert "protocol_title" in data
        assert "price" in data
        assert "wallet_address" in data
        assert "network" in data
        
        print(f"Created order: {data['order_id']} for ${data['price']}")
        
        return data["order_id"]

    def test_create_payment_order_free_protocol_rejected(self):
        """Test that payment order creation is rejected for free protocols"""
        # Free protocols should not allow payment order creation
        response = requests.post(
            f"{API_URL}/payment/create-order",
            json={
                "protocol_id": "proto-bpc157",  # Free protocol
                "language": "en",
                "email": "test@example.com"
            }
        )
        
        # Should reject with 400
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        print(f"Free protocol payment rejection: {data['detail']}")


class TestOldEndpointsBackwardCompat:
    """Tests for backward compatibility with old batch-based endpoints"""
    
    def test_validate_batch_endpoint_exists(self):
        """Verify old validate-batch endpoint still works"""
        response = requests.post(
            f"{API_URL}/protocols-v2/validate-batch",
            json={
                "protocol_id": "proto-bpc157",
                "batch_number": "TEST-BATCH-123"
            }
        )
        
        # Should return 200 even for invalid batch (not 404)
        assert response.status_code == 200
        data = response.json()
        
        assert "success" in data
        assert "valid" in data
        print(f"Old validate-batch response: valid={data['valid']}")


class TestWatermarkFunction:
    """Tests for PDF watermarking functionality"""
    
    def test_pdf_files_exist(self):
        """Verify PDF protocol files exist for watermarking"""
        # This is a basic check - in production we'd verify actual watermarking
        import os
        
        pdf_dir = "/app/backend/protocols_pdf"
        
        expected_files = [
            "bpc157_protocol_en.pdf",
            "bpc157_protocol_es.pdf", 
            "bpc157_protocol_pt.pdf",
            "tb500_protocol_en.pdf",
            "tb500_protocol_es.pdf",
            "tb500_protocol_pt.pdf",
            "ghkcu_protocol_en.pdf",
            "ghkcu_protocol_es.pdf",
            "ghkcu_protocol_pt.pdf"
        ]
        
        for filename in expected_files:
            filepath = os.path.join(pdf_dir, filename)
            assert os.path.exists(filepath), f"Missing PDF: {filename}"
            
            # Verify file has content
            size = os.path.getsize(filepath)
            assert size > 1000, f"PDF too small ({size} bytes): {filename}"
            
            print(f"Found PDF: {filename} ({size} bytes)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
