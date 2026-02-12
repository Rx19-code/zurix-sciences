"""
Zurix Sciences API Tests
Tests for products, categories, product-types, representatives, and verify-product endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAPIHealth:
    """API health and basic connectivity tests"""
    
    def test_api_root_endpoint(self):
        """Test API root returns correct response"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Zurix Sciences API"
        assert data["version"] == "1.0.0"
        print(f"✓ API root endpoint working: {data}")


class TestProductsAPI:
    """Products endpoint tests"""
    
    def test_get_all_products(self):
        """Test GET /api/products returns all products"""
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200
        products = response.json()
        assert isinstance(products, list)
        assert len(products) == 49, f"Expected 49 products, got {len(products)}"
        print(f"✓ Got {len(products)} products")
    
    def test_products_have_required_fields(self):
        """Test that products have all required fields"""
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200
        products = response.json()
        
        required_fields = ['id', 'name', 'category', 'product_type', 'purity', 'dosage', 
                          'description', 'price', 'verification_code', 'storage_info',
                          'batch_number', 'manufacturing_date', 'expiry_date', 'coa_url', 'featured']
        
        for product in products[:5]:  # Check first 5 products
            for field in required_fields:
                assert field in product, f"Missing field: {field} in product {product.get('name', 'unknown')}"
        print(f"✓ All required fields present in products")
    
    def test_get_featured_products(self):
        """Test GET /api/products?featured=true returns featured products"""
        response = requests.get(f"{BASE_URL}/api/products?featured=true")
        assert response.status_code == 200
        products = response.json()
        assert isinstance(products, list)
        assert len(products) >= 6, f"Expected at least 6 featured products, got {len(products)}"
        for product in products:
            assert product['featured'] == True
        print(f"✓ Got {len(products)} featured products")
    
    def test_filter_products_by_category(self):
        """Test filtering products by category"""
        response = requests.get(f"{BASE_URL}/api/products?category=GLP-1%20Analogs")
        assert response.status_code == 200
        products = response.json()
        assert isinstance(products, list)
        for product in products:
            assert product['category'] == 'GLP-1 Analogs'
        print(f"✓ Category filter works, got {len(products)} GLP-1 Analogs")
    
    def test_filter_products_by_product_type(self):
        """Test filtering products by product type"""
        response = requests.get(f"{BASE_URL}/api/products?product_type=Tirzepatide")
        assert response.status_code == 200
        products = response.json()
        assert isinstance(products, list)
        for product in products:
            assert product['product_type'] == 'Tirzepatide'
        print(f"✓ Product type filter works, got {len(products)} Tirzepatide products")
    
    def test_search_products(self):
        """Test searching products"""
        response = requests.get(f"{BASE_URL}/api/products?search=BPC")
        assert response.status_code == 200
        products = response.json()
        assert isinstance(products, list)
        assert len(products) > 0, "Search should return results for 'BPC'"
        print(f"✓ Search works, got {len(products)} results for 'BPC'")
    
    def test_get_single_product(self):
        """Test GET /api/products/{id} returns single product"""
        # First get all products to get a valid ID
        response = requests.get(f"{BASE_URL}/api/products")
        products = response.json()
        product_id = products[0]['id']
        
        # Now get single product
        response = requests.get(f"{BASE_URL}/api/products/{product_id}")
        assert response.status_code == 200
        product = response.json()
        assert product['id'] == product_id
        print(f"✓ Single product retrieval works: {product['name']}")
    
    def test_get_nonexistent_product(self):
        """Test GET /api/products/{id} returns 404 for nonexistent product"""
        response = requests.get(f"{BASE_URL}/api/products/nonexistent-id-12345")
        assert response.status_code == 404
        print("✓ 404 returned for nonexistent product")


class TestCategoriesAPI:
    """Categories endpoint tests"""
    
    def test_get_categories(self):
        """Test GET /api/categories returns categories"""
        response = requests.get(f"{BASE_URL}/api/categories")
        assert response.status_code == 200
        data = response.json()
        assert 'categories' in data
        categories = data['categories']
        assert isinstance(categories, list)
        assert len(categories) == 4, f"Expected 4 categories, got {len(categories)}"
        
        expected_categories = ['GLP-1 Analogs', 'Research Peptides', 'Cognitive Enhancers', 'Coenzymes']
        for cat in expected_categories:
            assert cat in categories, f"Missing category: {cat}"
        print(f"✓ Got categories: {categories}")


class TestProductTypesAPI:
    """Product types endpoint tests"""
    
    def test_get_product_types(self):
        """Test GET /api/product-types returns product types"""
        response = requests.get(f"{BASE_URL}/api/product-types")
        assert response.status_code == 200
        data = response.json()
        assert 'types' in data
        types = data['types']
        assert isinstance(types, list)
        assert len(types) > 0, "Should have at least 1 product type"
        print(f"✓ Got {len(types)} product types")


class TestRepresentativesAPI:
    """Representatives endpoint tests"""
    
    def test_get_representatives(self):
        """Test GET /api/representatives returns representatives"""
        response = requests.get(f"{BASE_URL}/api/representatives")
        assert response.status_code == 200
        reps = response.json()
        assert isinstance(reps, list)
        assert len(reps) == 3, f"Expected 3 representatives, got {len(reps)}"
        print(f"✓ Got {len(reps)} representatives")
    
    def test_representatives_have_required_fields(self):
        """Test that representatives have all required fields"""
        response = requests.get(f"{BASE_URL}/api/representatives")
        assert response.status_code == 200
        reps = response.json()
        
        required_fields = ['id', 'country', 'region', 'name', 'whatsapp', 'flag_emoji']
        
        for rep in reps:
            for field in required_fields:
                assert field in rep, f"Missing field: {field} in representative {rep.get('country', 'unknown')}"
        print("✓ All required fields present in representatives")


class TestVerifyProductAPI:
    """Verify product endpoint tests"""
    
    def test_verify_valid_product_code(self):
        """Test POST /api/verify-product with valid code ZX-ZE101208"""
        response = requests.post(f"{BASE_URL}/api/verify-product", json={"code": "ZX-ZE101208"})
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert data['message'] == "Product authenticated successfully!"
        assert data['product'] is not None
        assert data['product']['verification_code'] == 'ZX-ZE101208'
        print(f"✓ Valid code verification works: {data['product']['name']}")
    
    def test_verify_lowercase_code(self):
        """Test verification with lowercase code (should still work)"""
        response = requests.post(f"{BASE_URL}/api/verify-product", json={"code": "zx-ze101208"})
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        print("✓ Lowercase code verification works")
    
    def test_verify_invalid_product_code(self):
        """Test POST /api/verify-product with invalid code ZX-FAKE-0001"""
        response = requests.post(f"{BASE_URL}/api/verify-product", json={"code": "ZX-FAKE-0001"})
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == False
        assert "counterfeit" in data['message'].lower() or "not found" in data['message'].lower()
        print(f"✓ Invalid code verification works: {data['message']}")
    
    def test_verify_wrong_format_code(self):
        """Test POST /api/verify-product with wrong format (not starting with ZX-)"""
        response = requests.post(f"{BASE_URL}/api/verify-product", json={"code": "WRONG-FORMAT-123"})
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == False
        assert "ZX-" in data['message']
        print(f"✓ Wrong format code rejected: {data['message']}")


class TestProductVerificationByCode:
    """Product verification by code endpoint tests"""
    
    def test_get_product_by_verification_code(self):
        """Test GET /api/products/code/{verification_code}"""
        response = requests.get(f"{BASE_URL}/api/products/code/ZX-ZE101208")
        assert response.status_code == 200
        product = response.json()
        assert product['verification_code'] == 'ZX-ZE101208'
        print(f"✓ Get product by code works: {product['name']}")
    
    def test_get_product_by_invalid_code(self):
        """Test GET /api/products/code/{verification_code} with invalid code"""
        response = requests.get(f"{BASE_URL}/api/products/code/ZX-INVALID-CODE")
        assert response.status_code == 404
        print("✓ 404 returned for invalid verification code")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
