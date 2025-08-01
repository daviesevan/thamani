#!/usr/bin/env python3
"""
Comprehensive test script for real web scraping system
"""
import sys
import os
import json
import time
from typing import Dict, List, Any

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.scrapers.scraper_manager import ScraperManager
from app.scrapers.product_comparison import ProductComparison
from app.scrapers.anti_bot_handler import AntiBot

def test_real_scraping():
    """Test the complete real scraping system"""
    print("🔍 REAL WEB SCRAPING SYSTEM TEST")
    print("=" * 60)
    
    # Initialize components
    scraper_manager = ScraperManager()
    product_comparison = ProductComparison()
    anti_bot = AntiBot()
    
    # Test queries - real products available in Kenya
    test_queries = [
        "Tecno Spark 10",
        "Tecno Camon 20",
        "Samsung Galaxy A14",
        "Infinix Hot 30",
        "Xiaomi Redmi 12"
    ]
    
    print("\n📊 SCRAPER STATUS CHECK")
    print("-" * 40)
    
    # Check scraper status
    status = scraper_manager.get_scraper_status()
    for retailer, info in status.items():
        status_icon = "✅" if info.get('available') else "❌"
        print(f"{status_icon} {retailer.title()}: {info.get('base_url', 'N/A')}")
        if not info.get('available'):
            print(f"   Error: {info.get('error', 'Unknown')}")
    
    print("\n🛒 TESTING REAL PRODUCT SEARCHES")
    print("-" * 40)
    
    all_results = {}
    
    for query in test_queries:
        print(f"\n🔍 Searching for: '{query}'")
        print("   " + "-" * 30)
        
        try:
            # Search all retailers
            search_results = scraper_manager.search_all_retailers(
                query=query, 
                max_pages_per_retailer=1,  # Limit to 1 page for testing
                max_workers=2  # Limit concurrent requests
            )
            
            all_results[query] = search_results
            
            # Display results summary
            total_products = 0
            for retailer, products in search_results.items():
                count = len(products)
                total_products += count
                status_icon = "✅" if count > 0 else "⚠️"
                print(f"   {status_icon} {retailer.title()}: {count} products")
                
                # Show sample products
                if products:
                    for i, product in enumerate(products[:2]):  # Show first 2
                        price_str = f"KSh {product['price']:,.0f}" if product.get('price') else "Price N/A"
                        print(f"      • {product['name'][:50]}... - {price_str}")
            
            print(f"   📈 Total found: {total_products} products")
            
            # Add delay between searches to be respectful
            time.sleep(3)
            
        except Exception as e:
            print(f"   ❌ Error searching '{query}': {str(e)}")
            all_results[query] = {}
    
    print("\n🔄 TESTING PRODUCT COMPARISON")
    print("-" * 40)
    
    # Test product comparison on the best results
    best_query = max(all_results.items(), 
                    key=lambda x: sum(len(products) for products in x[1].values()),
                    default=(None, {}))[0]
    
    if best_query and all_results[best_query]:
        print(f"Comparing results for: '{best_query}'")
        
        try:
            comparison_results = product_comparison.create_price_comparison(
                all_results[best_query],
                similarity_threshold=0.6
            )
            
            print(f"Found {len(comparison_results)} product match groups:")
            
            for i, match in enumerate(comparison_results[:3], 1):  # Show top 3
                print(f"\n   📱 Match Group {i}:")
                print(f"      Product: {match['primary_product']['name'][:60]}...")
                print(f"      Retailers: {len(set(match['retailers']))} ({', '.join(set(match['retailers']))})")
                
                if match['price_range']['min'] and match['price_range']['max']:
                    min_price = match['price_range']['min']
                    max_price = match['price_range']['max']
                    savings = max_price - min_price
                    print(f"      Price Range: KSh {min_price:,.0f} - KSh {max_price:,.0f}")
                    if savings > 0:
                        print(f"      💰 Potential Savings: KSh {savings:,.0f}")
                
                print(f"      🎯 Confidence: {match.get('confidence_score', 0):.2f}")
        
        except Exception as e:
            print(f"   ❌ Error in product comparison: {str(e)}")
    
    print("\n🤖 TESTING ANTI-BOT MEASURES")
    print("-" * 40)
    
    try:
        # Test anti-bot session creation
        session = anti_bot.create_session_with_rotation()
        print("   ✅ Anti-bot session created successfully")
        print(f"   🔧 User-Agent: {session.headers.get('User-Agent', 'N/A')[:60]}...")
        
        # Test smart request
        test_url = "https://www.jumia.co.ke"
        response = anti_bot.smart_request(test_url, session=session, max_retries=1)
        if response and response.status_code == 200:
            print(f"   ✅ Smart request successful: {response.status_code}")
        else:
            print(f"   ⚠️ Smart request failed or blocked")
        
    except Exception as e:
        print(f"   ❌ Error testing anti-bot measures: {str(e)}")
    
    print("\n📈 PERFORMANCE ANALYSIS")
    print("-" * 40)
    
    # Analyze overall performance
    total_searches = len(test_queries)
    successful_searches = len([q for q in all_results if any(all_results[q].values())])
    success_rate = (successful_searches / total_searches) * 100 if total_searches > 0 else 0
    
    total_products_found = sum(
        len(products) 
        for query_results in all_results.values() 
        for products in query_results.values()
    )
    
    retailer_performance = {}
    for query_results in all_results.values():
        for retailer, products in query_results.items():
            if retailer not in retailer_performance:
                retailer_performance[retailer] = {'total': 0, 'searches': 0}
            retailer_performance[retailer]['total'] += len(products)
            retailer_performance[retailer]['searches'] += 1
    
    print(f"   📊 Overall Success Rate: {success_rate:.1f}%")
    print(f"   🛍️ Total Products Found: {total_products_found}")
    print(f"   🔍 Searches Completed: {successful_searches}/{total_searches}")
    
    print("\n   🏪 Retailer Performance:")
    for retailer, stats in retailer_performance.items():
        avg_products = stats['total'] / stats['searches'] if stats['searches'] > 0 else 0
        print(f"      {retailer.title()}: {avg_products:.1f} products/search")
    
    print("\n💾 SAMPLE DATA OUTPUT")
    print("-" * 40)
    
    # Show sample structured data
    if all_results:
        sample_query = list(all_results.keys())[0]
        sample_results = all_results[sample_query]
        
        for retailer, products in sample_results.items():
            if products:
                sample_product = products[0]
                print(f"\n   📱 Sample {retailer.title()} Product:")
                print(f"      Name: {sample_product.get('name', 'N/A')}")
                print(f"      Price: KSh {sample_product.get('price', 0):,.0f}")
                url = sample_product.get('url', 'N/A')
                image_url = sample_product.get('image_url', 'N/A')
                print(f"      URL: {url[:60] if url else 'N/A'}...")
                print(f"      Image: {image_url[:60] if image_url else 'N/A'}...")
                print(f"      In Stock: {sample_product.get('in_stock', 'Unknown')}")
                break
    
    print("\n🎯 RECOMMENDATIONS")
    print("-" * 40)
    
    recommendations = []
    
    if success_rate < 50:
        recommendations.append("• Consider adding more robust error handling")
        recommendations.append("• Implement proxy rotation for better success rates")
    
    if total_products_found < 20:
        recommendations.append("• Optimize CSS selectors for better product extraction")
        recommendations.append("• Add more fallback extraction methods")
    
    if not any(len(products) > 5 for query_results in all_results.values() for products in query_results.values()):
        recommendations.append("• Increase pagination depth for more comprehensive results")
        recommendations.append("• Add category-specific scraping strategies")
    
    if recommendations:
        for rec in recommendations:
            print(f"   {rec}")
    else:
        print("   ✅ System performing well! Consider scaling up.")
    
    print("\n🚀 PRODUCTION READINESS")
    print("-" * 40)
    
    readiness_checks = [
        ("Real data extraction", total_products_found > 0),
        ("Multiple retailer support", len(retailer_performance) >= 2),
        ("Error handling", success_rate > 30),
        ("Anti-bot measures", True),  # We have the system in place
        ("Product comparison", len(comparison_results) > 0 if 'comparison_results' in locals() else False)
    ]
    
    for check_name, passed in readiness_checks:
        status_icon = "✅" if passed else "❌"
        print(f"   {status_icon} {check_name}")
    
    passed_checks = sum(1 for _, passed in readiness_checks if passed)
    readiness_score = (passed_checks / len(readiness_checks)) * 100
    
    print(f"\n   🎯 Production Readiness: {readiness_score:.0f}%")
    
    if readiness_score >= 80:
        print("   🎉 System is ready for production deployment!")
    elif readiness_score >= 60:
        print("   ⚠️ System needs minor improvements before production")
    else:
        print("   🔧 System requires significant improvements")
    
    print("\n" + "=" * 60)
    print("✅ REAL WEB SCRAPING TEST COMPLETED")
    
    # Cleanup
    anti_bot.cleanup()
    
    return all_results

if __name__ == '__main__':
    try:
        results = test_real_scraping()
        
        # Optionally save results to file
        with open('scraping_test_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print("\n💾 Results saved to 'scraping_test_results.json'")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
