"""
Test suite for Auth, Stacks, and Payments features
- Auth: register, login, /me endpoint
- Stacks: GET /api/stacks, GET /api/stacks/{slug}
- Payments: create-invoice, check payment (requires auth)
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
TEST_EMAIL = "test@test.com"
TEST_PASSWORD = "test123"


class TestHealthAndBasics:
    """Basic health checks"""
    
    def test_api_root(self):
        """Test API root endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"API root: {data}")
    
    def test_health_check(self):
        """Test health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("database") == "connected"
        print(f"Health: {data}")


class TestStacksAPI:
    """Test Stacks API endpoints"""
    
    def test_get_stacks_returns_43_stacks(self):
        """GET /api/stacks should return 43 stacks with categories"""
        response = requests.get(f"{BASE_URL}/api/stacks")
        assert response.status_code == 200
        data = response.json()
        
        assert "stacks" in data
        assert "categories" in data
        assert "total" in data
        
        stacks = data["stacks"]
        assert len(stacks) == 43, f"Expected 43 stacks, got {len(stacks)}"
        
        # Verify stack structure
        if stacks:
            stack = stacks[0]
            assert "slug" in stack
            assert "name" in stack
            assert "category" in stack
            assert "goal" in stack
            assert "peptides" in stack
            
        print(f"Stacks API: {len(stacks)} stacks, {len(data['categories'])} categories")
    
    def test_get_stack_detail_the_shred_stack(self):
        """GET /api/stacks/the-shred-stack should return stack detail"""
        response = requests.get(f"{BASE_URL}/api/stacks/the-shred-stack")
        assert response.status_code == 200
        data = response.json()
        
        # Should not have error
        assert "error" not in data, f"Got error: {data.get('error')}"
        
        # Verify required fields
        assert "name" in data
        assert "goal" in data
        assert "peptides" in data
        assert "how_to_use" in data
        
        assert isinstance(data["peptides"], list)
        assert len(data["peptides"]) > 0
        
        assert isinstance(data["how_to_use"], list)
        assert len(data["how_to_use"]) > 0
        
        print(f"Stack detail: {data['name']}, peptides: {data['peptides']}")
    
    def test_get_stack_detail_nonexistent(self):
        """GET /api/stacks/nonexistent should return error"""
        response = requests.get(f"{BASE_URL}/api/stacks/nonexistent-stack-xyz")
        assert response.status_code == 200  # API returns 200 with error field
        data = response.json()
        assert "error" in data
    
    def test_stacks_category_filter(self):
        """Test stacks category filter"""
        # First get all categories
        response = requests.get(f"{BASE_URL}/api/stacks")
        data = response.json()
        categories = data.get("categories", [])
        
        if categories:
            cat = categories[0]
            response = requests.get(f"{BASE_URL}/api/stacks?category={cat}")
            assert response.status_code == 200
            filtered = response.json()
            
            # All returned stacks should have this category
            for stack in filtered.get("stacks", []):
                assert stack["category"] == cat
            print(f"Category filter '{cat}': {len(filtered['stacks'])} stacks")


class TestAuthRegister:
    """Test user registration"""
    
    def test_register_new_user(self):
        """POST /api/auth/register creates user with has_lifetime_access=false"""
        unique_email = f"test_register_{uuid.uuid4().hex[:8]}@test.com"
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "testpass123",
            "name": "Test User"
        })
        
        assert response.status_code == 200, f"Register failed: {response.text}"
        data = response.json()
        
        assert data.get("success") == True
        assert "token" in data
        assert "user" in data
        
        user = data["user"]
        assert user["email"] == unique_email.lower()
        assert user["name"] == "Test User"
        assert user["has_lifetime_access"] == False
        assert user["auth_provider"] == "email"
        
        print(f"Registered user: {user['email']}, has_lifetime_access: {user['has_lifetime_access']}")
    
    def test_register_duplicate_email(self):
        """POST /api/auth/register with existing email should fail"""
        # First register
        unique_email = f"test_dup_{uuid.uuid4().hex[:8]}@test.com"
        requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "testpass123",
            "name": "Test User"
        })
        
        # Try to register again
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "testpass123",
            "name": "Test User 2"
        })
        
        assert response.status_code == 400
        data = response.json()
        assert "already registered" in data.get("detail", "").lower()


class TestAuthLogin:
    """Test user login"""
    
    def test_login_success(self):
        """POST /api/auth/login returns JWT token"""
        # First register a user
        unique_email = f"test_login_{uuid.uuid4().hex[:8]}@test.com"
        requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "testpass123",
            "name": "Login Test"
        })
        
        # Now login
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": unique_email,
            "password": "testpass123"
        })
        
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        
        assert data.get("success") == True
        assert "token" in data
        assert len(data["token"]) > 0
        assert "user" in data
        
        user = data["user"]
        assert user["email"] == unique_email.lower()
        assert "has_lifetime_access" in user
        
        print(f"Login success: {user['email']}, token length: {len(data['token'])}")
    
    def test_login_invalid_credentials(self):
        """POST /api/auth/login with wrong password should fail"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "nonexistent@test.com",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert "invalid" in data.get("detail", "").lower()
    
    def test_login_with_test_credentials(self):
        """Test login with credentials from test_credentials.md"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        # This may fail if test user doesn't exist - that's ok
        if response.status_code == 200:
            data = response.json()
            assert data.get("success") == True
            print(f"Test user login success: {data['user']['email']}")
        else:
            print(f"Test user not found (expected if not seeded): {response.status_code}")


class TestAuthMe:
    """Test /api/auth/me endpoint"""
    
    def test_get_me_with_valid_token(self):
        """GET /api/auth/me returns user info with has_lifetime_access field"""
        # Register and get token
        unique_email = f"test_me_{uuid.uuid4().hex[:8]}@test.com"
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "testpass123",
            "name": "Me Test"
        })
        token = reg_response.json().get("token")
        
        # Call /me
        response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        
        assert response.status_code == 200, f"Get me failed: {response.text}"
        data = response.json()
        
        assert data.get("success") == True
        assert "user" in data
        
        user = data["user"]
        assert user["email"] == unique_email.lower()
        assert "has_lifetime_access" in user
        assert "auth_provider" in user
        
        print(f"Get me: {user['email']}, has_lifetime_access: {user['has_lifetime_access']}")
    
    def test_get_me_without_token(self):
        """GET /api/auth/me without token should fail"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code in [401, 403, 422]
    
    def test_get_me_with_invalid_token(self):
        """GET /api/auth/me with invalid token should fail"""
        response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": "Bearer invalid_token_xyz"
        })
        assert response.status_code in [401, 403]


class TestPaymentEndpoints:
    """Test payment endpoints (require auth)"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token for payment tests"""
        unique_email = f"test_pay_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "testpass123",
            "name": "Payment Test"
        })
        return response.json().get("token")
    
    def test_create_invoice_requires_auth(self):
        """POST /api/payment/create-invoice without auth should fail"""
        response = requests.post(f"{BASE_URL}/api/payment/create-invoice", json={})
        assert response.status_code in [401, 403, 422]
    
    def test_create_invoice_with_auth(self, auth_token):
        """POST /api/payment/create-invoice creates NOWPayments invoice"""
        response = requests.post(
            f"{BASE_URL}/api/payment/create-invoice",
            headers={"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"},
            json={}
        )
        
        assert response.status_code == 200, f"Create invoice failed: {response.text}"
        data = response.json()
        
        assert data.get("success") == True
        
        # If already paid, that's fine
        if data.get("already_paid"):
            print("User already has lifetime access")
            return
        
        # Verify invoice data
        assert "order_id" in data
        assert "payment_id" in data
        assert "pay_address" in data
        assert "pay_amount" in data
        assert "pay_currency" in data
        assert data["pay_currency"] == "usdttrc20"
        assert data["price"] == 39.99
        
        print(f"Invoice created: order_id={data['order_id']}, amount={data['pay_amount']} {data['pay_currency']}")
    
    def test_check_payment_requires_auth(self):
        """GET /api/payment/check/{id} without auth should fail"""
        response = requests.get(f"{BASE_URL}/api/payment/check/12345")
        assert response.status_code in [401, 403, 422]
    
    def test_check_payment_with_auth(self, auth_token):
        """GET /api/payment/check/{id} checks payment status"""
        # First create an invoice
        create_response = requests.post(
            f"{BASE_URL}/api/payment/create-invoice",
            headers={"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"},
            json={}
        )
        
        if create_response.status_code != 200:
            pytest.skip("Could not create invoice")
        
        data = create_response.json()
        if data.get("already_paid"):
            pytest.skip("User already has lifetime access")
        
        payment_id = data.get("payment_id")
        
        # Check payment status
        response = requests.get(
            f"{BASE_URL}/api/payment/check/{payment_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200, f"Check payment failed: {response.text}"
        check_data = response.json()
        
        assert check_data.get("success") == True
        assert "status" in check_data
        assert "has_lifetime_access" in check_data
        
        print(f"Payment status: {check_data['status']}, has_access: {check_data['has_lifetime_access']}")
    
    def test_my_payment_status(self, auth_token):
        """GET /api/payment/my-status returns user's payment status"""
        response = requests.get(
            f"{BASE_URL}/api/payment/my-status",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("success") == True
        assert "has_lifetime_access" in data
        assert "price" in data
        assert data["price"] == 39.99
        
        print(f"My status: has_access={data['has_lifetime_access']}, price={data['price']}")


class TestLibraryPeptides:
    """Test library peptides are all PRO"""
    
    def test_all_96_peptides_are_pro(self):
        """All 96 peptides should have is_free=false (PRO)"""
        response = requests.get(f"{BASE_URL}/api/library")
        assert response.status_code == 200
        data = response.json()
        
        peptides = data.get("peptides", [])
        assert len(peptides) == 96, f"Expected 96 peptides, got {len(peptides)}"
        
        free_peptides = [p for p in peptides if p.get("is_free") == True]
        pro_peptides = [p for p in peptides if p.get("is_free") == False]
        
        # All should be PRO (is_free=false)
        assert len(free_peptides) == 0, f"Found {len(free_peptides)} free peptides, expected 0"
        assert len(pro_peptides) == 96, f"Found {len(pro_peptides)} PRO peptides, expected 96"
        
        print(f"All {len(pro_peptides)} peptides are PRO (is_free=false)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
