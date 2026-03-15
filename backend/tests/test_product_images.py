"""
Tests for Product Images - Verifying all 32 products have images that load correctly
Focus: image_url presence in API responses and image serving endpoint functionality
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Products that previously had missing images - need special attention
PREVIOUSLY_MISSING_IMAGE_PRODUCTS = [
    "Tirzepatide 10mg",
    "Tirzepatide 15mg", 
    "Tirzepatide 20mg",
    "Semax 10mg",
    "Selank 10mg",
    "TB-500/thymosin beta 20mg",
    "BPC-157 10mg",
    "BPC157/TB4 Blend",
    "HGH 10iu",
    "HGH 176-191 5mg",
    "IGF-1 LR3 1mg",
    "CJC1295 DAC 5mg",
    "Tesamorelin+Ipamorelin Blend",
    "Ipamorelin 10mg",
    "Tesamorelin 20mg",
    "Glow Blend 70mg"
]


class TestProductImagesAPI:
    """Tests for /api/products endpoint - verifying image_url presence"""
    
    def test_api_products_returns_success(self):
        """Test that the products API returns 200 OK"""
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200, f"Products API returned {response.status_code}"
        print(f"PASS: /api/products returned status 200")
        
    def test_all_products_have_image_url(self):
        """Test that ALL 32 products have non-empty image_url"""
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200
        
        products = response.json()
        print(f"Total products returned: {len(products)}")
        
        products_without_images = []
        products_with_images = []
        
        for product in products:
            product_name = product.get('name', 'Unknown')
            image_url = product.get('image_url')
            
            if image_url and image_url.strip():
                products_with_images.append(product_name)
            else:
                products_without_images.append(product_name)
        
        print(f"Products with images: {len(products_with_images)}")
        print(f"Products without images: {len(products_without_images)}")
        
        if products_without_images:
            print(f"FAIL: Products missing image_url: {products_without_images}")
        
        assert len(products_without_images) == 0, f"Products missing image_url: {products_without_images}"
        print(f"PASS: All {len(products_with_images)} products have image_url")
    
    def test_previously_missing_images_now_have_urls(self):
        """Test that the 16 products that previously had no images now have image_url"""
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200
        
        products = response.json()
        product_map = {p['name']: p for p in products}
        
        missing_now = []
        fixed = []
        
        for product_name in PREVIOUSLY_MISSING_IMAGE_PRODUCTS:
            # Check for partial name match since names might differ slightly
            matching_product = None
            for p_name, p_data in product_map.items():
                if product_name.lower() in p_name.lower() or p_name.lower() in product_name.lower():
                    matching_product = p_data
                    break
            
            if matching_product:
                if matching_product.get('image_url') and matching_product['image_url'].strip():
                    fixed.append(matching_product['name'])
                else:
                    missing_now.append(matching_product['name'])
            else:
                print(f"WARNING: Could not find product matching '{product_name}'")
        
        print(f"Previously missing - now fixed: {len(fixed)}")
        print(f"Fixed products: {fixed}")
        
        if missing_now:
            print(f"FAIL: Still missing images: {missing_now}")
        
        assert len(missing_now) == 0, f"Products still missing images: {missing_now}"
        print(f"PASS: All {len(fixed)} previously missing products now have image_url")


class TestImageServingEndpoint:
    """Tests for /api/images/products/{filename} endpoint"""
    
    def test_image_endpoint_exists(self):
        """Test that the image serving endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/api/products")
        products = response.json()
        
        # Get first product with image
        for product in products:
            image_url = product.get('image_url', '')
            if image_url and '/api/images/products/' in image_url:
                # Extract filename from URL
                filename = image_url.split('/api/images/products/')[-1]
                
                # Try to fetch the image
                img_response = requests.get(f"{BASE_URL}/api/images/products/{filename}")
                assert img_response.status_code == 200, f"Image endpoint returned {img_response.status_code} for {filename}"
                
                # Check content type
                content_type = img_response.headers.get('content-type', '')
                assert 'image' in content_type.lower(), f"Content-type is not image: {content_type}"
                
                print(f"PASS: Image endpoint working for {filename}")
                return
        
        pytest.fail("No product with local image URL found")
    
    def test_multiple_product_images_load(self):
        """Test that images load for multiple products (sample of 5)"""
        response = requests.get(f"{BASE_URL}/api/products")
        products = response.json()
        
        tested_count = 0
        failed_images = []
        
        for product in products[:10]:  # Test first 10 products
            image_url = product.get('image_url', '')
            product_name = product.get('name', 'Unknown')
            
            if not image_url:
                failed_images.append(f"{product_name}: No image_url")
                continue
            
            if '/api/images/products/' in image_url:
                filename = image_url.split('/api/images/products/')[-1]
                full_url = f"{BASE_URL}/api/images/products/{filename}"
            else:
                full_url = image_url
            
            try:
                img_response = requests.get(full_url, timeout=10)
                if img_response.status_code == 200:
                    tested_count += 1
                    print(f"PASS: Image loads for '{product_name}'")
                else:
                    failed_images.append(f"{product_name}: HTTP {img_response.status_code}")
            except Exception as e:
                failed_images.append(f"{product_name}: {str(e)}")
        
        print(f"Successfully tested {tested_count} images")
        
        if failed_images:
            print(f"Failed images: {failed_images}")
        
        assert len(failed_images) == 0, f"Some images failed to load: {failed_images}"
    
    def test_previously_missing_images_actually_load(self):
        """Test that images for previously missing products actually load (HTTP 200)"""
        response = requests.get(f"{BASE_URL}/api/products")
        products = response.json()
        
        product_map = {p['name'].lower(): p for p in products}
        
        tested = 0
        failed = []
        
        for product_name in PREVIOUSLY_MISSING_IMAGE_PRODUCTS[:5]:  # Test 5 of the previously missing
            # Find matching product
            matching_product = None
            for p_name, p_data in product_map.items():
                if product_name.lower() in p_name or p_name in product_name.lower():
                    matching_product = p_data
                    break
            
            if not matching_product:
                print(f"WARNING: Product '{product_name}' not found")
                continue
            
            image_url = matching_product.get('image_url', '')
            if not image_url:
                failed.append(f"{matching_product['name']}: No image_url")
                continue
            
            # Fetch the image
            if '/api/images/products/' in image_url:
                filename = image_url.split('/api/images/products/')[-1]
                full_url = f"{BASE_URL}/api/images/products/{filename}"
            else:
                full_url = image_url
            
            try:
                img_response = requests.get(full_url, timeout=10)
                if img_response.status_code == 200:
                    tested += 1
                    print(f"PASS: Image loads for previously missing '{matching_product['name']}'")
                else:
                    failed.append(f"{matching_product['name']}: HTTP {img_response.status_code}")
            except Exception as e:
                failed.append(f"{matching_product['name']}: {str(e)}")
        
        print(f"Successfully tested {tested} previously missing images")
        
        if failed:
            print(f"FAIL: Failed images: {failed}")
        
        assert len(failed) == 0, f"Some previously missing images failed to load: {failed}"


class TestFeaturedProducts:
    """Tests for featured products section (homepage)"""
    
    def test_featured_products_have_images(self):
        """Test that featured products have image_url"""
        response = requests.get(f"{BASE_URL}/api/products?featured=true")
        assert response.status_code == 200
        
        featured = response.json()
        print(f"Featured products count: {len(featured)}")
        
        missing_images = []
        for product in featured:
            if not product.get('image_url'):
                missing_images.append(product.get('name', 'Unknown'))
        
        if missing_images:
            print(f"FAIL: Featured products without images: {missing_images}")
        
        assert len(missing_images) == 0, f"Featured products missing images: {missing_images}"
        print(f"PASS: All {len(featured)} featured products have images")
    
    def test_featured_products_images_load(self):
        """Test that featured product images actually load"""
        response = requests.get(f"{BASE_URL}/api/products?featured=true")
        featured = response.json()
        
        failed = []
        for product in featured[:6]:  # Test first 6 featured
            image_url = product.get('image_url', '')
            if not image_url:
                failed.append(f"{product['name']}: No image_url")
                continue
            
            if '/api/images/products/' in image_url:
                filename = image_url.split('/api/images/products/')[-1]
                full_url = f"{BASE_URL}/api/images/products/{filename}"
            else:
                full_url = image_url
            
            try:
                img_response = requests.get(full_url, timeout=10)
                if img_response.status_code != 200:
                    failed.append(f"{product['name']}: HTTP {img_response.status_code}")
                else:
                    print(f"PASS: Featured image loads for '{product['name']}'")
            except Exception as e:
                failed.append(f"{product['name']}: {str(e)}")
        
        assert len(failed) == 0, f"Featured images failed: {failed}"


class TestSingleProductDetail:
    """Tests for single product detail page API"""
    
    def test_product_detail_has_image(self):
        """Test that individual product detail includes image_url"""
        # First get list of products
        response = requests.get(f"{BASE_URL}/api/products")
        products = response.json()
        
        if not products:
            pytest.skip("No products available")
        
        # Test 3 products that previously had missing images
        test_names = ["Tirzepatide", "Semax", "BPC-157"]
        tested = 0
        
        for product in products:
            product_name = product.get('name', '')
            for test_name in test_names:
                if test_name.lower() in product_name.lower():
                    product_id = product.get('id')
                    
                    # Fetch single product detail
                    detail_response = requests.get(f"{BASE_URL}/api/products/{product_id}")
                    assert detail_response.status_code == 200
                    
                    detail = detail_response.json()
                    assert detail.get('image_url'), f"Product detail for {product_name} missing image_url"
                    
                    print(f"PASS: Product detail for '{product_name}' has image_url")
                    tested += 1
                    break
            
            if tested >= 3:
                break
        
        assert tested > 0, "Could not find any target products to test"
        print(f"PASS: Tested {tested} product details with images")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
