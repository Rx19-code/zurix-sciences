"""
Test suite for Peptide Library Data Quality
Tests: Portuguese content removal, competitor URL removal, dosage fixes, category mapping
"""
import pytest
import requests
import os
import re

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://peptide-catalog-3.preview.emergentagent.com').rstrip('/')

# Portuguese words that should NOT appear in English content
# Uses word-boundary matching to avoid false positives (e.g. 'eliminates' matching 'elimina')
PORTUGUESE_WORDS = [
    'semana', 'semanal', 'diário', 'diária', 'peptídeo', 'peptídico', 
    'aminoácidos', 'análogo', 'sintético', 'heptapeptídeo',
    'Emagrecimento', 'Biorregulador', 'Antioxidante', 'mg/semana', 'mcg/semana',
    'neurotrófica', 'derivada', 'suínos', 'Tripeptídeo',
    'propriedades', 'senolítico',
    'seletivamente', 'células', 'senescentes', 'angiotensina',
    'potentes', 'nootrópicos', 'Formulação', 'injetável',
    'neurotróficos', 'cartilagem', 'articulações', 'organismo'
]

# Competitor terms that should NOT appear
COMPETITOR_TERMS = ['peptideoshealth', '.com.br']

# Expected English categories (11 total)
EXPECTED_CATEGORIES = [
    'Aesthetics / Skin', 'Anti-aging', 'Bioregulators', 'Diluents',
    'GH / Secretagogues', 'Hormonal / Sexual Health', 'Immunity',
    'Metabolism', 'Nootropic / Cognitive', 'Recovery', 'Weight Loss / GLP-1'
]

# Portuguese categories that should NOT exist
PORTUGUESE_CATEGORIES = ['Emagrecimento', 'Biorregulador', 'Antioxidante', 'Cardiovascular']


class TestLibraryEndpoint:
    """Tests for GET /api/library endpoint"""
    
    def test_library_returns_96_peptides(self):
        """Verify library returns expected 96 peptides"""
        response = requests.get(f"{BASE_URL}/api/library")
        assert response.status_code == 200
        data = response.json()
        peptides = data.get('peptides', [])
        assert len(peptides) == 96, f"Expected 96 peptides, got {len(peptides)}"
    
    def test_library_returns_11_english_categories(self):
        """Verify library returns exactly 11 English categories"""
        response = requests.get(f"{BASE_URL}/api/library")
        assert response.status_code == 200
        data = response.json()
        categories = data.get('categories', [])
        assert len(categories) == 11, f"Expected 11 categories, got {len(categories)}: {categories}"
        
        # Verify all expected categories are present
        for cat in EXPECTED_CATEGORIES:
            assert cat in categories, f"Missing expected category: {cat}"
    
    def test_no_portuguese_categories(self):
        """Verify no Portuguese category names exist"""
        response = requests.get(f"{BASE_URL}/api/library")
        assert response.status_code == 200
        data = response.json()
        categories = data.get('categories', [])
        
        for pt_cat in PORTUGUESE_CATEGORIES:
            assert pt_cat not in categories, f"Portuguese category found: {pt_cat}"
    
    def test_no_competitor_urls_in_list(self):
        """Verify no competitor URLs in peptide list fields"""
        response = requests.get(f"{BASE_URL}/api/library")
        assert response.status_code == 200
        data = response.json()
        peptides = data.get('peptides', [])
        
        issues = []
        for p in peptides:
            for key, val in p.items():
                if isinstance(val, str):
                    for term in COMPETITOR_TERMS:
                        if term.lower() in val.lower():
                            issues.append(f"{p['slug']}.{key}: contains '{term}'")
                elif isinstance(val, list):
                    for item in val:
                        if isinstance(item, str):
                            for term in COMPETITOR_TERMS:
                                if term.lower() in item.lower():
                                    issues.append(f"{p['slug']}.{key}: contains '{term}'")
        
        assert len(issues) == 0, f"Competitor URLs found: {issues}"


class TestSemaglutideDetail:
    """Tests for GET /api/library/semaglutide"""
    
    def test_semaglutide_category_is_english(self):
        """Verify semaglutide has English category"""
        response = requests.get(f"{BASE_URL}/api/library/semaglutide")
        assert response.status_code == 200
        data = response.json()
        assert data.get('category') == 'Weight Loss / GLP-1', f"Wrong category: {data.get('category')}"
    
    def test_semaglutide_classification_is_english(self):
        """Verify semaglutide classification is in English (not 'Agonista do receptor GLP-1')"""
        response = requests.get(f"{BASE_URL}/api/library/semaglutide")
        assert response.status_code == 200
        data = response.json()
        classification = data.get('classification', '')
        
        # Should NOT contain Portuguese
        assert 'Agonista' not in classification, f"Portuguese classification: {classification}"
        assert 'receptor GLP-1' not in classification or 'Receptor' in classification, f"Portuguese classification: {classification}"
        
        # Should be in English
        assert 'GLP-1' in classification, f"Missing GLP-1 in classification: {classification}"
    
    def test_semaglutide_dosages_not_zero_mg(self):
        """Verify semaglutide dosages have proper mg values (not '0 mg')"""
        response = requests.get(f"{BASE_URL}/api/library/semaglutide")
        assert response.status_code == 200
        data = response.json()
        
        protocols = data.get('protocols', {})
        dosages = protocols.get('dosages', [])
        
        assert len(dosages) > 0, "No dosages found"
        
        for d in dosages:
            dose = d.get('dose', '')
            # Check for broken "0 mg" pattern (but allow valid doses like "0.25 mg")
            if re.match(r'^0\s*mg', dose) and not re.match(r'^0\.\d+', dose):
                pytest.fail(f"Broken dosage found: {d.get('indication')}: {dose}")
            
            # Verify dose contains mg or mcg
            assert 'mg' in dose.lower() or 'mcg' in dose.lower(), f"Invalid dose format: {dose}"
    
    def test_semaglutide_text_is_english(self):
        """Verify semaglutide overview/protocols text is in English"""
        response = requests.get(f"{BASE_URL}/api/library/semaglutide")
        assert response.status_code == 200
        data = response.json()
        
        # Check overview
        overview = data.get('overview', {})
        what_is = overview.get('what_is', '')
        
        # Should NOT contain Portuguese words
        for pt_word in ['semana', 'semanal', 'peptídeo']:
            assert pt_word.lower() not in what_is.lower(), f"Portuguese word '{pt_word}' found in overview"
        
        # Should contain English words
        assert 'GLP-1' in what_is or 'receptor' in what_is.lower(), "Overview doesn't appear to be in English"


class TestRetatrutideDetail:
    """Tests for GET /api/library/retatrutide"""
    
    def test_retatrutide_category_not_competitor_url(self):
        """Verify retatrutide category is 'Weight Loss / GLP-1' not a competitor URL"""
        response = requests.get(f"{BASE_URL}/api/library/retatrutide")
        assert response.status_code == 200
        data = response.json()
        
        category = data.get('category', '')
        assert category == 'Weight Loss / GLP-1', f"Wrong category: {category}"
        
        # Verify no competitor URL
        for term in COMPETITOR_TERMS:
            assert term.lower() not in category.lower(), f"Competitor URL in category: {category}"
    
    def test_retatrutide_text_is_english(self):
        """Verify retatrutide overview is in English"""
        response = requests.get(f"{BASE_URL}/api/library/retatrutide")
        assert response.status_code == 200
        data = response.json()
        
        overview = data.get('overview', {})
        what_is = overview.get('what_is', '')
        
        # Should be in English
        assert 'triple' in what_is.lower() or 'receptor' in what_is.lower() or 'agonist' in what_is.lower(), \
            f"Overview doesn't appear to be in English: {what_is[:200]}"
        
        # Should NOT contain Portuguese
        for pt_word in ['triplo', 'agonista', 'receptores']:
            assert pt_word.lower() not in what_is.lower(), f"Portuguese word '{pt_word}' found in overview"


class TestPortugueseContentRemoval:
    """Tests to verify Portuguese content has been translated"""
    
    @pytest.mark.parametrize("slug", [
        "aod-9604", "cartalax", "cerebrolysin", "dihexa", 
        "epithalon", "foxo4-dri", "glutathione"
    ])
    def test_peptide_description_is_english(self, slug):
        """Verify peptide descriptions are in English"""
        response = requests.get(f"{BASE_URL}/api/library/{slug}")
        assert response.status_code == 200
        data = response.json()
        
        description = data.get('description', '')
        
        # Check for Portuguese words
        pt_found = []
        for pt_word in PORTUGUESE_WORDS:
            if pt_word.lower() in description.lower():
                pt_found.append(pt_word)
        
        assert len(pt_found) == 0, f"{slug} description contains Portuguese: {pt_found} -> '{description}'"
    
    @pytest.mark.parametrize("slug", [
        "aod-9604", "cerebrolysin"
    ])
    def test_peptide_classification_is_english(self, slug):
        """Verify peptide classifications are in English"""
        response = requests.get(f"{BASE_URL}/api/library/{slug}")
        assert response.status_code == 200
        data = response.json()
        
        classification = data.get('classification', '')
        
        # Check for Portuguese words
        pt_found = []
        for pt_word in PORTUGUESE_WORDS:
            if pt_word.lower() in classification.lower():
                pt_found.append(pt_word)
        
        assert len(pt_found) == 0, f"{slug} classification contains Portuguese: {pt_found} -> '{classification}'"


class TestNoCompetitorURLs:
    """Tests to verify competitor URLs have been removed from all peptides"""
    
    def test_no_competitor_urls_in_any_peptide(self):
        """Comprehensive check for competitor URLs in all peptide details"""
        response = requests.get(f"{BASE_URL}/api/library")
        assert response.status_code == 200
        data = response.json()
        slugs = [p['slug'] for p in data.get('peptides', [])]
        
        issues = []
        # Check first 20 peptides for performance
        for slug in slugs[:20]:
            detail_response = requests.get(f"{BASE_URL}/api/library/{slug}")
            if detail_response.status_code == 200:
                detail = detail_response.json()
                self._check_dict_for_competitors(detail, slug, issues)
        
        assert len(issues) == 0, f"Competitor URLs found: {issues}"
    
    def _check_dict_for_competitors(self, obj, slug, issues, path=""):
        """Recursively check dict for competitor terms"""
        if isinstance(obj, dict):
            for key, val in obj.items():
                self._check_dict_for_competitors(val, slug, issues, f"{path}.{key}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                self._check_dict_for_competitors(item, slug, issues, f"{path}[{i}]")
        elif isinstance(obj, str):
            for term in COMPETITOR_TERMS:
                if term.lower() in obj.lower():
                    issues.append(f"{slug}{path}: contains '{term}'")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
