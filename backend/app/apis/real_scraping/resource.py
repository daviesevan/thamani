"""
Real web scraping API endpoints for live product data
"""
import logging
from flask import jsonify, request, Blueprint
from app.scrapers.scraper_manager import ScraperManager
from app.scrapers.product_comparison import ProductComparison
from app.scrapers.anti_bot_handler import AntiBot
from app.utils.request_utils import get_request_data

# Set up logger
logger = logging.getLogger(__name__)

# Create blueprint
real_scraping = Blueprint('real_scraping', __name__)

# Initialize scraping components
scraper_manager = ScraperManager()
product_comparison = ProductComparison()
anti_bot = AntiBot()

@real_scraping.route('/search', methods=['POST'])
def search_products():
    """
    Search for real products across all retailers
    """
    try:
        data = get_request_data(request)
        query = data.get('query')
        max_pages = data.get('max_pages', 2)
        max_workers = data.get('max_workers', 3)
        
        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400
        
        logger.info(f"Searching for products: {query}")
        
        # Search all retailers
        search_results = scraper_manager.search_all_retailers(
            query=query,
            max_pages_per_retailer=max_pages,
            max_workers=max_workers
        )
        
        # Calculate totals
        total_products = sum(len(products) for products in search_results.values())
        retailer_summary = {}
        
        for retailer, products in search_results.items():
            retailer_summary[retailer] = {
                'count': len(products),
                'has_results': len(products) > 0,
                'sample_products': products[:3] if products else []  # First 3 products
            }
        
        return jsonify({
            'success': True,
            'query': query,
            'total_products': total_products,
            'retailers': retailer_summary,
            'full_results': search_results
        }), 200
        
    except Exception as e:
        logger.error(f"Error in product search: {str(e)}")
        return jsonify({'error': str(e)}), 500

@real_scraping.route('/compare', methods=['POST'])
def compare_products():
    """
    Compare products across retailers and find matches
    """
    try:
        data = get_request_data(request)
        query = data.get('query')
        similarity_threshold = data.get('similarity_threshold', 0.7)
        max_pages = data.get('max_pages', 1)
        
        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400
        
        logger.info(f"Comparing products for: {query}")
        
        # Search all retailers
        search_results = scraper_manager.search_all_retailers(
            query=query,
            max_pages_per_retailer=max_pages,
            max_workers=2
        )
        
        # Create price comparison
        comparison_results = product_comparison.create_price_comparison(
            search_results,
            similarity_threshold=similarity_threshold
        )
        
        # Format results for API response
        formatted_results = []
        for match in comparison_results:
            formatted_match = {
                'product_name': match['primary_product']['name'],
                'retailers_count': len(set(match['retailers'])),
                'retailers': list(set(match['retailers'])),
                'price_range': match['price_range'],
                'confidence_score': match.get('confidence_score', 0),
                'savings': match.get('savings', {}),
                'best_deal': match.get('best_deal'),
                'all_products': [match['primary_product']] + match['similar_products']
            }
            formatted_results.append(formatted_match)
        
        return jsonify({
            'success': True,
            'query': query,
            'matches_found': len(formatted_results),
            'comparison_results': formatted_results,
            'search_summary': {
                retailer: len(products) for retailer, products in search_results.items()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in product comparison: {str(e)}")
        return jsonify({'error': str(e)}), 500

@real_scraping.route('/retailers/<retailer_name>/search', methods=['POST'])
def search_specific_retailer(retailer_name):
    """
    Search a specific retailer only
    """
    try:
        data = get_request_data(request)
        query = data.get('query')
        max_pages = data.get('max_pages', 2)
        
        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400
        
        logger.info(f"Searching {retailer_name} for: {query}")
        
        # Search specific retailer
        search_results = scraper_manager.search_specific_retailers(
            query=query,
            retailer_names=[retailer_name],
            max_pages=max_pages
        )
        
        retailer_results = search_results.get(retailer_name, [])
        
        return jsonify({
            'success': True,
            'retailer': retailer_name,
            'query': query,
            'products_found': len(retailer_results),
            'products': retailer_results
        }), 200
        
    except Exception as e:
        logger.error(f"Error searching {retailer_name}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@real_scraping.route('/product/details', methods=['POST'])
def get_product_details():
    """
    Get detailed information for a specific product
    """
    try:
        data = get_request_data(request)
        product_url = data.get('url')
        retailer_name = data.get('retailer')
        
        if not product_url or not retailer_name:
            return jsonify({'error': 'URL and retailer parameters are required'}), 400
        
        logger.info(f"Getting product details from {retailer_name}: {product_url}")
        
        # Get product details
        details = scraper_manager.get_product_details(product_url, retailer_name)
        
        if details:
            return jsonify({
                'success': True,
                'product_details': details
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Could not retrieve product details'
            }), 404
        
    except Exception as e:
        logger.error(f"Error getting product details: {str(e)}")
        return jsonify({'error': str(e)}), 500

@real_scraping.route('/status', methods=['GET'])
def get_scraper_status():
    """
    Get status of all scrapers
    """
    try:
        status = scraper_manager.get_scraper_status()
        
        # Add summary
        total_scrapers = len(status)
        available_scrapers = sum(1 for s in status.values() if s.get('available'))
        
        return jsonify({
            'success': True,
            'summary': {
                'total_scrapers': total_scrapers,
                'available_scrapers': available_scrapers,
                'availability_rate': (available_scrapers / total_scrapers) * 100 if total_scrapers > 0 else 0
            },
            'scrapers': status
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting scraper status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@real_scraping.route('/demo', methods=['GET'])
def demo_scraping():
    """
    Demo endpoint showing real scraping capabilities
    """
    try:
        # Demo queries
        demo_queries = ['Samsung Galaxy', 'iPhone', 'MacBook']
        demo_results = {}
        
        for query in demo_queries:
            try:
                logger.info(f"Demo scraping: {query}")
                
                # Quick search with limited results
                search_results = scraper_manager.search_all_retailers(
                    query=query,
                    max_pages_per_retailer=1,
                    max_workers=2
                )
                
                # Summarize results
                summary = {}
                total_found = 0
                
                for retailer, products in search_results.items():
                    count = len(products)
                    total_found += count
                    
                    summary[retailer] = {
                        'products_found': count,
                        'sample_product': products[0] if products else None
                    }
                
                demo_results[query] = {
                    'total_products': total_found,
                    'retailers': summary
                }
                
            except Exception as e:
                logger.error(f"Error in demo for {query}: {str(e)}")
                demo_results[query] = {'error': str(e)}
        
        return jsonify({
            'success': True,
            'message': 'Real web scraping demo - live data from Kenyan retailers',
            'demo_results': demo_results,
            'capabilities': [
                'Real-time product data extraction',
                'Multi-retailer price comparison',
                'Anti-bot detection handling',
                'Product matching across retailers',
                'Structured data output'
            ]
        }), 200
        
    except Exception as e:
        logger.error(f"Error in demo: {str(e)}")
        return jsonify({'error': str(e)}), 500

@real_scraping.route('/test/anti-bot', methods=['POST'])
def test_anti_bot():
    """
    Test anti-bot detection capabilities
    """
    try:
        data = get_request_data(request)
        test_url = data.get('url', 'https://www.jumia.co.ke')
        
        logger.info(f"Testing anti-bot measures for: {test_url}")
        
        # Test session creation
        session = anti_bot.create_session_with_rotation()
        user_agent = session.headers.get('User-Agent', 'N/A')
        
        # Test smart request
        response = anti_bot.smart_request(test_url, session=session, max_retries=1)
        
        success = response is not None and response.status_code == 200
        
        return jsonify({
            'success': True,
            'anti_bot_test': {
                'url_tested': test_url,
                'request_successful': success,
                'status_code': response.status_code if response else None,
                'user_agent': user_agent[:100] + '...' if len(user_agent) > 100 else user_agent,
                'has_proxy_support': len(anti_bot.proxies) > 0,
                'selenium_available': True  # We have it installed
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error testing anti-bot: {str(e)}")
        return jsonify({'error': str(e)}), 500

@real_scraping.route('/categories', methods=['POST'])
def scrape_categories():
    """
    Scrape specific product categories
    """
    try:
        data = get_request_data(request)
        categories = data.get('categories', {})
        max_pages = data.get('max_pages', 2)
        
        if not categories:
            return jsonify({'error': 'Categories parameter is required'}), 400
        
        logger.info(f"Scraping categories: {list(categories.keys())}")
        
        # Scrape categories
        results = scraper_manager.scrape_categories(categories, max_pages)
        
        # Format results
        formatted_results = {}
        total_products = 0
        
        for retailer, products in results.items():
            count = len(products)
            total_products += count
            
            formatted_results[retailer] = {
                'products_found': count,
                'products': products[:10] if products else []  # Limit to first 10
            }
        
        return jsonify({
            'success': True,
            'total_products': total_products,
            'categories_scraped': list(categories.keys()),
            'results': formatted_results
        }), 200
        
    except Exception as e:
        logger.error(f"Error scraping categories: {str(e)}")
        return jsonify({'error': str(e)}), 500
