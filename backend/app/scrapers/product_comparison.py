"""
Advanced product comparison engine for matching products across retailers
"""
import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from difflib import SequenceMatcher
from collections import defaultdict
import json

logger = logging.getLogger(__name__)

class ProductComparison:
    """
    Advanced product comparison and matching engine
    """
    
    def __init__(self):
        # Brand variations and aliases
        self.brand_aliases = {
            'samsung': ['samsung', 'galaxy'],
            'apple': ['apple', 'iphone', 'ipad', 'macbook', 'mac'],
            'huawei': ['huawei', 'honor'],
            'xiaomi': ['xiaomi', 'mi', 'redmi', 'poco'],
            'oppo': ['oppo', 'oneplus'],
            'tecno': ['tecno', 'infinix', 'itel'],
            'hp': ['hp', 'hewlett packard'],
            'dell': ['dell'],
            'lenovo': ['lenovo', 'thinkpad'],
            'asus': ['asus'],
            'acer': ['acer'],
            'lg': ['lg'],
            'sony': ['sony', 'xperia'],
            'nokia': ['nokia', 'hmd']
        }
        
        # Common product categories and their keywords
        self.category_keywords = {
            'smartphone': ['phone', 'smartphone', 'mobile', 'cell', 'android', 'ios'],
            'laptop': ['laptop', 'notebook', 'ultrabook', 'macbook', 'chromebook'],
            'tablet': ['tablet', 'ipad', 'tab'],
            'headphones': ['headphones', 'earphones', 'earbuds', 'airpods'],
            'tv': ['tv', 'television', 'smart tv', 'led', 'oled', 'qled'],
            'appliance': ['fridge', 'refrigerator', 'washing machine', 'microwave', 'oven']
        }
        
        # Storage and memory patterns
        self.storage_patterns = [
            r'(\d+)\s*gb',
            r'(\d+)\s*tb',
            r'(\d+)\s*mb'
        ]
        
        self.memory_patterns = [
            r'(\d+)\s*gb\s*ram',
            r'(\d+)\s*gb\s*memory',
            r'(\d+)gb\s*ram'
        ]
    
    def normalize_product_name(self, name: str) -> str:
        """Normalize product name for better comparison"""
        if not name:
            return ""
        
        # Convert to lowercase
        normalized = name.lower()
        
        # Remove special characters but keep spaces and alphanumeric
        normalized = re.sub(r'[^\w\s]', ' ', normalized)
        
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        
        # Remove common filler words
        filler_words = ['new', 'original', 'genuine', 'brand', 'latest', 'hot', 'sale']
        words = normalized.split()
        words = [word for word in words if word not in filler_words]
        
        return ' '.join(words)
    
    def extract_brand(self, name: str) -> Optional[str]:
        """Extract brand from product name"""
        normalized_name = self.normalize_product_name(name)
        
        for brand, aliases in self.brand_aliases.items():
            for alias in aliases:
                if alias in normalized_name:
                    return brand
        
        return None
    
    def extract_category(self, name: str) -> Optional[str]:
        """Extract product category from name"""
        normalized_name = self.normalize_product_name(name)
        
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword in normalized_name:
                    return category
        
        return None
    
    def extract_specifications(self, name: str) -> Dict[str, Any]:
        """Extract technical specifications from product name"""
        specs = {}
        normalized_name = self.normalize_product_name(name)
        
        # Extract storage
        for pattern in self.storage_patterns:
            match = re.search(pattern, normalized_name)
            if match:
                storage_value = int(match.group(1))
                unit = pattern.split('\\s*')[1].replace(')', '')
                specs['storage'] = f"{storage_value}{unit.upper()}"
                break
        
        # Extract RAM
        for pattern in self.memory_patterns:
            match = re.search(pattern, normalized_name)
            if match:
                ram_value = int(match.group(1))
                specs['ram'] = f"{ram_value}GB"
                break
        
        # Extract screen size (for phones/laptops)
        screen_pattern = r'(\d+\.?\d*)\s*inch'
        screen_match = re.search(screen_pattern, normalized_name)
        if screen_match:
            specs['screen_size'] = f"{screen_match.group(1)} inch"
        
        # Extract model numbers
        model_pattern = r'[a-z]+\d+[a-z]*'
        model_matches = re.findall(model_pattern, normalized_name)
        if model_matches:
            specs['models'] = model_matches
        
        return specs
    
    def calculate_similarity_score(self, product1: Dict[str, Any], 
                                 product2: Dict[str, Any]) -> float:
        """Calculate similarity score between two products"""
        if not product1.get('name') or not product2.get('name'):
            return 0.0
        
        # Normalize names
        name1 = self.normalize_product_name(product1['name'])
        name2 = self.normalize_product_name(product2['name'])
        
        # Base name similarity
        name_similarity = SequenceMatcher(None, name1, name2).ratio()
        
        # Brand matching bonus
        brand1 = self.extract_brand(product1['name'])
        brand2 = self.extract_brand(product2['name'])
        brand_bonus = 0.2 if brand1 and brand2 and brand1 == brand2 else 0
        
        # Category matching bonus
        category1 = self.extract_category(product1['name'])
        category2 = self.extract_category(product2['name'])
        category_bonus = 0.1 if category1 and category2 and category1 == category2 else 0
        
        # Specifications matching
        specs1 = self.extract_specifications(product1['name'])
        specs2 = self.extract_specifications(product2['name'])
        specs_bonus = self._calculate_specs_similarity(specs1, specs2) * 0.15
        
        # Price similarity (products with very different prices are less likely to be the same)
        price_penalty = 0
        if product1.get('price') and product2.get('price'):
            price1, price2 = product1['price'], product2['price']
            price_diff_ratio = abs(price1 - price2) / max(price1, price2)
            if price_diff_ratio > 0.5:  # More than 50% price difference
                price_penalty = 0.1
        
        total_score = name_similarity + brand_bonus + category_bonus + specs_bonus - price_penalty
        return min(1.0, max(0.0, total_score))
    
    def _calculate_specs_similarity(self, specs1: Dict[str, Any], 
                                  specs2: Dict[str, Any]) -> float:
        """Calculate similarity between specifications"""
        if not specs1 or not specs2:
            return 0.0
        
        common_keys = set(specs1.keys()) & set(specs2.keys())
        if not common_keys:
            return 0.0
        
        matches = 0
        for key in common_keys:
            if specs1[key] == specs2[key]:
                matches += 1
        
        return matches / len(common_keys)
    
    def find_product_matches(self, products: List[Dict[str, Any]], 
                           similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Find matching products across different retailers"""
        matches = []
        processed_indices = set()
        
        for i, product1 in enumerate(products):
            if i in processed_indices:
                continue
            
            match_group = {
                'primary_product': product1,
                'similar_products': [],
                'retailers': [product1.get('retailer', 'Unknown')],
                'price_range': {
                    'min': product1.get('price'),
                    'max': product1.get('price'),
                    'avg': product1.get('price')
                },
                'similarity_scores': []
            }
            
            processed_indices.add(i)
            
            for j, product2 in enumerate(products[i+1:], i+1):
                if j in processed_indices:
                    continue
                
                similarity = self.calculate_similarity_score(product1, product2)
                
                if similarity >= similarity_threshold:
                    match_group['similar_products'].append(product2)
                    match_group['retailers'].append(product2.get('retailer', 'Unknown'))
                    match_group['similarity_scores'].append(similarity)
                    processed_indices.add(j)
                    
                    # Update price range
                    if product2.get('price'):
                        current_min = match_group['price_range']['min']
                        current_max = match_group['price_range']['max']
                        
                        if current_min is None or product2['price'] < current_min:
                            match_group['price_range']['min'] = product2['price']
                        if current_max is None or product2['price'] > current_max:
                            match_group['price_range']['max'] = product2['price']
            
            # Calculate average price
            all_prices = [p.get('price') for p in [product1] + match_group['similar_products'] if p.get('price')]
            if all_prices:
                match_group['price_range']['avg'] = sum(all_prices) / len(all_prices)
            
            # Only include groups with multiple retailers or high-confidence single matches
            if len(set(match_group['retailers'])) > 1 or (
                len(match_group['similar_products']) > 0 and 
                max(match_group['similarity_scores'], default=0) > 0.85
            ):
                matches.append(match_group)
        
        # Sort by number of retailers and average similarity
        matches.sort(key=lambda x: (
            len(set(x['retailers'])), 
            sum(x['similarity_scores']) / len(x['similarity_scores']) if x['similarity_scores'] else 0
        ), reverse=True)
        
        return matches
    
    def create_price_comparison(self, search_results: Dict[str, List[Dict[str, Any]]], 
                              similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Create a comprehensive price comparison from search results"""
        # Flatten all products
        all_products = []
        for retailer, products in search_results.items():
            for product in products:
                product['retailer'] = retailer
                all_products.append(product)
        
        # Find matches
        matches = self.find_product_matches(all_products, similarity_threshold)
        
        # Enhance matches with additional analysis
        enhanced_matches = []
        for match in matches:
            enhanced_match = self._enhance_match_data(match)
            enhanced_matches.append(enhanced_match)
        
        return enhanced_matches
    
    def _enhance_match_data(self, match: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance match data with additional analysis"""
        all_products = [match['primary_product']] + match['similar_products']
        
        # Extract common specifications
        common_specs = self._find_common_specifications(all_products)
        
        # Calculate savings
        prices = [p.get('price') for p in all_products if p.get('price')]
        if len(prices) > 1:
            min_price = min(prices)
            max_price = max(prices)
            savings = max_price - min_price
            savings_percent = (savings / max_price) * 100 if max_price > 0 else 0
        else:
            savings = 0
            savings_percent = 0
        
        # Find best deal
        best_deal = None
        if prices:
            min_price = min(prices)
            for product in all_products:
                if product.get('price') == min_price:
                    best_deal = product
                    break
        
        # Retailer analysis
        retailer_count = len(set(match['retailers']))
        retailer_distribution = {}
        for retailer in match['retailers']:
            retailer_distribution[retailer] = retailer_distribution.get(retailer, 0) + 1
        
        enhanced_match = {
            **match,
            'common_specifications': common_specs,
            'savings': {
                'amount': savings,
                'percentage': savings_percent
            },
            'best_deal': best_deal,
            'retailer_analysis': {
                'count': retailer_count,
                'distribution': retailer_distribution
            },
            'confidence_score': self._calculate_match_confidence(match)
        }
        
        return enhanced_match
    
    def _find_common_specifications(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find specifications common across all products in a match group"""
        if not products:
            return {}
        
        # Extract specs from all products
        all_specs = [self.extract_specifications(p.get('name', '')) for p in products]
        
        # Find common keys
        common_keys = set(all_specs[0].keys()) if all_specs else set()
        for specs in all_specs[1:]:
            common_keys &= set(specs.keys())
        
        # Get common values
        common_specs = {}
        for key in common_keys:
            values = [specs[key] for specs in all_specs]
            if len(set(values)) == 1:  # All values are the same
                common_specs[key] = values[0]
        
        return common_specs
    
    def _calculate_match_confidence(self, match: Dict[str, Any]) -> float:
        """Calculate confidence score for a match group"""
        factors = []
        
        # Number of retailers (more retailers = higher confidence)
        retailer_count = len(set(match['retailers']))
        factors.append(min(1.0, retailer_count / 3))  # Normalize to max 3 retailers
        
        # Average similarity score
        if match['similarity_scores']:
            avg_similarity = sum(match['similarity_scores']) / len(match['similarity_scores'])
            factors.append(avg_similarity)
        
        # Price consistency (less variation = higher confidence)
        if match['price_range']['min'] and match['price_range']['max']:
            price_variation = (match['price_range']['max'] - match['price_range']['min']) / match['price_range']['max']
            price_consistency = 1 - min(1.0, price_variation)
            factors.append(price_consistency)
        
        # Brand consistency
        all_products = [match['primary_product']] + match['similar_products']
        brands = [self.extract_brand(p.get('name', '')) for p in all_products]
        brands = [b for b in brands if b]
        brand_consistency = len(set(brands)) == 1 if brands else 0.5
        factors.append(brand_consistency)
        
        return sum(factors) / len(factors) if factors else 0.0
