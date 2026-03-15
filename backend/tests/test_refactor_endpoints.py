"""
Test all endpoints after server.py refactoring to modular files.
Tests: health, products, categories, protocols, admin, verification endpoints.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
ADMIN_PASSWORD = "Rx050217!"
TEST_VERIFICATION_CODE = "ZX-260312-GHK50-1-TEST01"


class TestHealthEndpoint:
    """Test /api/health returns ok status with database connected"""
    
    def test_health_check(self):
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.text}"
        
        data = response.json()
        assert data.get("status") == "ok", f"Expected status 'ok', got {data.get('status')}"
        assert data.get("database") == "connected", f"Database not connected: {data.get('database')}"
        assert "timestamp" in data, "Missing timestamp in health response"


class TestProductsEndpoints:
    """Test product-related endpoints"""
    
    def test_get_all_products_returns_32(self):
        """GET /api/products returns 32 products"""
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200, f"Products fetch failed: {response.text}"
        
        products = response.json()
        assert isinstance(products, list), "Products should be a list"
        assert len(products) == 32, f"Expected 32 products, got {len(products)}"
    
    def test_all_products_have_image_url(self):
        """All products should have image_url field"""
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200
        
        products = response.json()
        products_without_image = [p.get("name") for p in products if not p.get("image_url")]
        assert len(products_without_image) == 0, f"Products without image_url: {products_without_image}"
    
    def test_get_single_product(self):
        """GET /api/products/{id} returns a single product"""
        # First get list to get a valid product ID
        list_response = requests.get(f"{BASE_URL}/api/products")
        products = list_response.json()
        product_id = products[0]["id"]
        
        # Get single product
        response = requests.get(f"{BASE_URL}/api/products/{product_id}")
        assert response.status_code == 200, f"Single product fetch failed: {response.text}"
        
        product = response.json()
        assert product.get("id") == product_id
        assert "name" in product
        assert "category" in product
        assert "price" in product
    
    def test_get_product_not_found(self):
        """GET /api/products/{invalid_id} returns 404"""
        response = requests.get(f"{BASE_URL}/api/products/invalid-id-12345")
        assert response.status_code == 404


class TestCategoriesEndpoint:
    """Test categories endpoint"""
    
    def test_get_categories(self):
        """GET /api/categories returns categories list"""
        response = requests.get(f"{BASE_URL}/api/categories")
        assert response.status_code == 200, f"Categories fetch failed: {response.text}"
        
        data = response.json()
        assert "categories" in data, "Missing 'categories' key in response"
        categories = data["categories"]
        assert isinstance(categories, list), "Categories should be a list"
        assert len(categories) > 0, "Categories list should not be empty"


class TestProductImagesEndpoint:
    """Test product image serving endpoint"""
    
    def test_product_image_returns_200(self):
        """GET /api/images/products/{filename} returns 200 for product images"""
        # First get a product with image_url
        response = requests.get(f"{BASE_URL}/api/products")
        products = response.json()
        
        # Find a product with image_url
        product_with_image = next((p for p in products if p.get("image_url")), None)
        assert product_with_image is not None, "No products with image_url found"
        
        # Extract filename from image_url
        image_url = product_with_image["image_url"]
        # image_url is like /api/images/products/xxx.png
        
        # Make request to image endpoint
        image_response = requests.get(f"{BASE_URL}{image_url}")
        assert image_response.status_code == 200, f"Image fetch failed for {image_url}: {image_response.status_code}"
    
    def test_missing_image_returns_404(self):
        """Non-existent image should return 404"""
        response = requests.get(f"{BASE_URL}/api/images/products/nonexistent-image-12345.png")
        assert response.status_code == 404


class TestProtocolsV2Endpoints:
    """Test protocols-v2 endpoints"""
    
    def test_get_protocols_returns_11(self):
        """GET /api/protocols-v2 returns 11 protocols"""
        response = requests.get(f"{BASE_URL}/api/protocols-v2")
        assert response.status_code == 200, f"Protocols fetch failed: {response.text}"
        
        data = response.json()
        assert data.get("success") is True
        protocols = data.get("protocols", [])
        assert len(protocols) == 11, f"Expected 11 protocols, got {len(protocols)}"
    
    def test_validate_code_valid(self):
        """POST /api/protocols-v2/validate-code validates correctly"""
        response = requests.post(
            f"{BASE_URL}/api/protocols-v2/validate-code",
            json={"code": TEST_VERIFICATION_CODE}
        )
        assert response.status_code == 200, f"Validate code failed: {response.text}"
        
        data = response.json()
        assert data.get("success") is True
        assert data.get("valid") is True
        assert "protocol_id" in data
        assert "protocol_title" in data
    
    def test_validate_code_invalid(self):
        """POST /api/protocols-v2/validate-code with invalid code"""
        response = requests.post(
            f"{BASE_URL}/api/protocols-v2/validate-code",
            json={"code": "INVALID-CODE-12345"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") is True
        assert data.get("valid") is False


class TestAdminEndpoints:
    """Test admin endpoints"""
    
    def test_admin_login_success(self):
        """POST /api/admin/login with correct password returns success"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            json={"password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        
        data = response.json()
        assert data.get("success") is True
        assert data.get("message") == "Login successful"
    
    def test_admin_login_failure(self):
        """POST /api/admin/login with wrong password returns 401"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            json={"password": "wrongpassword123"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    def test_admin_codes_with_password(self):
        """GET /api/admin/codes with admin password returns codes"""
        response = requests.get(
            f"{BASE_URL}/api/admin/codes",
            headers={"X-Admin-Password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200, f"Admin codes fetch failed: {response.text}"
        
        data = response.json()
        assert "codes" in data
        assert "total" in data
    
    def test_admin_codes_without_password(self):
        """GET /api/admin/codes without password returns 401"""
        response = requests.get(f"{BASE_URL}/api/admin/codes")
        assert response.status_code == 401
    
    def test_admin_batches_with_password(self):
        """GET /api/admin/batches with admin password returns batches"""
        response = requests.get(
            f"{BASE_URL}/api/admin/batches",
            headers={"X-Admin-Password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200, f"Admin batches fetch failed: {response.text}"
        
        data = response.json()
        assert "batches" in data
        assert isinstance(data["batches"], list)
    
    def test_admin_batches_without_password(self):
        """GET /api/admin/batches without password returns 401"""
        response = requests.get(f"{BASE_URL}/api/admin/batches")
        assert response.status_code == 401


class TestVerificationEndpoint:
    """Test product verification endpoint"""
    
    def test_verify_product_with_valid_code(self):
        """POST /api/verify-product with test code returns verification"""
        response = requests.post(
            f"{BASE_URL}/api/verify-product",
            json={"code": TEST_VERIFICATION_CODE}
        )
        assert response.status_code == 200, f"Verify product failed: {response.text}"
        
        data = response.json()
        assert data.get("success") is True
        assert "message" in data
        assert "verification_count" in data
    
    def test_verify_product_invalid_format(self):
        """POST /api/verify-product with non-ZX code returns error"""
        response = requests.post(
            f"{BASE_URL}/api/verify-product",
            json={"code": "INVALID-FORMAT"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") is False
        assert "ZX-" in data.get("message", "")
    
    def test_verify_product_not_found(self):
        """POST /api/verify-product with unknown ZX code returns not found"""
        response = requests.post(
            f"{BASE_URL}/api/verify-product",
            json={"code": "ZX-UNKNOWN-CODE-12345"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") is False
        assert "warning_level" in data


class TestRootEndpoint:
    """Test root API endpoint"""
    
    def test_root_endpoint(self):
        """GET /api/ returns API info"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data or "version" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
