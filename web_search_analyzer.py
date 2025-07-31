#!/usr/bin/env python3
"""
Web Search Analyzer for Indian Fashion Trends
Uses Serper API to gather current web data and enhance analysis
"""

import requests
import json
import time
import logging
from datetime import datetime
from config import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebSearchAnalyzer:
    def __init__(self):
        self.api_key = Config.SERPER_API_KEY
        self.base_url = Config.SERPER_BASE_URL
        self.search_results = {}
        self.trending_data = {}
    
    def search_web_trends(self, query, num_results=10):
        """Search web for current fashion trends"""
        try:
            headers = {
                'X-API-KEY': self.api_key,
                'Content-Type': 'application/json'
            }
            
            payload = {
                'q': query,
                'num': num_results,
                'gl': 'in',  # India
                'hl': 'en'
            }
            
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Web search successful for: {query}")
                return data
            else:
                logger.error(f"❌ Web search failed for {query}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error in web search for {query}: {str(e)}")
            return None
    
    def extract_trending_keywords(self, search_data):
        """Extract trending keywords from search results"""
        keywords = []
        
        if not search_data or 'organic' not in search_data:
            return keywords
        
        for result in search_data['organic']:
            title = result.get('title', '').lower()
            snippet = result.get('snippet', '').lower()
            
            # Extract fashion keywords from title and snippet
            text = title + ' ' + snippet
            
            for category, words in Config.INDIAN_FASHION_KEYWORDS.items():
                for word in words:
                    if word in text:
                        keywords.append(word)
        
        return list(set(keywords))  # Remove duplicates
    
    def analyze_search_trends(self, search_data):
        """Analyze search results for trend patterns"""
        if not search_data:
            return {}
        
        analysis = {
            'total_results': len(search_data.get('organic', [])),
            'trending_topics': [],
            'popular_sources': [],
            'regional_mentions': [],
            'brand_mentions': [],
            'fabric_mentions': [],
            'occasion_mentions': []
        }
        
        # Analyze organic results
        for result in search_data.get('organic', []):
            title = result.get('title', '').lower()
            snippet = result.get('snippet', '').lower()
            link = result.get('link', '')
            
            # Check for regional mentions
            for region, states in Config.INDIAN_REGIONS.items():
                for state in states:
                    if state in title or state in snippet:
                        analysis['regional_mentions'].append(region)
            
            # Check for brand mentions
            for brand in Config.INDIAN_FASHION_KEYWORDS['indian_brands']:
                if brand in title or brand in snippet:
                    analysis['brand_mentions'].append(brand)
            
            # Check for fabric mentions
            for fabric in Config.INDIAN_FASHION_KEYWORDS['fabrics_materials']:
                if fabric in title or fabric in snippet:
                    analysis['fabric_mentions'].append(fabric)
            
            # Check for occasion mentions
            for occasion in Config.INDIAN_FASHION_KEYWORDS['occasions']:
                if occasion in title or occasion in snippet:
                    analysis['occasion_mentions'].append(occasion)
            
            # Extract source domain
            if link:
                try:
                    domain = link.split('/')[2]
                    analysis['popular_sources'].append(domain)
                except:
                    pass
        
        # Remove duplicates
        for key in ['regional_mentions', 'brand_mentions', 'fabric_mentions', 'occasion_mentions', 'popular_sources']:
            analysis[key] = list(set(analysis[key]))
        
        return analysis
    
    def gather_comprehensive_trends(self):
        """Gather comprehensive fashion trends from web search"""
        logger.info("🔍 Starting comprehensive web trend analysis...")
        
        all_trends = {}
        total_searches = 0
        successful_searches = 0
        
        for query in Config.SEARCH_QUERIES:
            logger.info(f"Searching for: {query}")
            
            search_data = self.search_web_trends(query, num_results=15)
            total_searches += 1
            
            if search_data:
                successful_searches += 1
                
                # Extract keywords
                keywords = self.extract_trending_keywords(search_data)
                
                # Analyze trends
                trend_analysis = self.analyze_search_trends(search_data)
                
                all_trends[query] = {
                    'keywords': keywords,
                    'analysis': trend_analysis,
                    'raw_results': search_data.get('organic', [])[:5],  # Top 5 results
                    'search_time': datetime.now().isoformat()
                }
            
            # Rate limiting
            time.sleep(1)
        
        self.search_results = all_trends
        
        logger.info(f"✅ Web search completed!")
        logger.info(f"📊 Successful searches: {successful_searches}/{total_searches}")
        logger.info(f"📈 Total queries analyzed: {len(all_trends)}")
        
        return all_trends
    
    def get_trending_summary(self):
        """Get a summary of trending topics from web search"""
        if not self.search_results:
            return {}
        
        summary = {
            'top_keywords': {},
            'top_brands': {},
            'top_regions': {},
            'top_fabrics': {},
            'top_occasions': {},
            'popular_sources': {},
            'trending_topics': []
        }
        
        # Aggregate data across all searches
        for query, data in self.search_results.items():
            # Keywords
            for keyword in data['keywords']:
                summary['top_keywords'][keyword] = summary['top_keywords'].get(keyword, 0) + 1
            
            # Brands
            for brand in data['analysis']['brand_mentions']:
                summary['top_brands'][brand] = summary['top_brands'].get(brand, 0) + 1
            
            # Regions
            for region in data['analysis']['regional_mentions']:
                summary['top_regions'][region] = summary['top_regions'].get(region, 0) + 1
            
            # Fabrics
            for fabric in data['analysis']['fabric_mentions']:
                summary['top_fabrics'][fabric] = summary['top_fabrics'].get(fabric, 0) + 1
            
            # Occasions
            for occasion in data['analysis']['occasion_mentions']:
                summary['top_occasions'][occasion] = summary['top_occasions'].get(occasion, 0) + 1
            
            # Sources
            for source in data['analysis']['popular_sources']:
                summary['popular_sources'][source] = summary['popular_sources'].get(source, 0) + 1
        
        # Sort by frequency
        for key in summary:
            if isinstance(summary[key], dict):
                summary[key] = dict(sorted(summary[key].items(), key=lambda x: x[1], reverse=True))
        
        return summary
    
    def save_web_trends(self, filepath):
        """Save web search trends to file"""
        try:
            data = {
                'metadata': {
                    'search_time': datetime.now().isoformat(),
                    'total_queries': len(self.search_results),
                    'api_used': 'Serper API'
                },
                'search_results': self.search_results,
                'trending_summary': self.get_trending_summary()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Web trends saved to: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving web trends: {str(e)}")
            return False
    
    def get_regional_trends(self, region_name):
        """Get specific regional trends"""
        regional_trends = {}
        
        for query, data in self.search_results.items():
            if region_name.lower() in query.lower():
                regional_trends[query] = data
        
        return regional_trends
    
    def compare_reddit_web_trends(self, reddit_keywords):
        """Compare Reddit trends with web trends"""
        web_keywords = []
        
        for query, data in self.search_results.items():
            web_keywords.extend(data['keywords'])
        
        web_keywords = list(set(web_keywords))
        
        # Find common keywords
        common_keywords = set(reddit_keywords) & set(web_keywords)
        
        # Find unique to each platform
        reddit_only = set(reddit_keywords) - set(web_keywords)
        web_only = set(web_keywords) - set(reddit_keywords)
        
        comparison = {
            'common_keywords': list(common_keywords),
            'reddit_only': list(reddit_only),
            'web_only': list(web_only),
            'reddit_count': len(reddit_keywords),
            'web_count': len(web_keywords),
            'common_count': len(common_keywords)
        }
        
        return comparison

def main():
    """Test the web search analyzer"""
    analyzer = WebSearchAnalyzer()
    
    print("🔍 Testing Web Search Analyzer...")
    print("="*50)
    
    # Test single search
    test_query = "Indian fashion trends 2024"
    print(f"Searching for: {test_query}")
    
    result = analyzer.search_web_trends(test_query)
    if result:
        print("✅ Single search successful!")
        keywords = analyzer.extract_trending_keywords(result)
        print(f"📊 Extracted keywords: {keywords[:10]}")
    
    # Test comprehensive search
    print("\n🔍 Running comprehensive trend analysis...")
    trends = analyzer.gather_comprehensive_trends()
    
    if trends:
        summary = analyzer.get_trending_summary()
        
        print("\n" + "="*50)
        print("🎯 WEB TREND ANALYSIS RESULTS")
        print("="*50)
        print(f"📊 Total queries analyzed: {len(trends)}")
        print(f"🏆 Top keywords: {list(summary['top_keywords'].keys())[:10]}")
        print(f"🏢 Top brands: {list(summary['top_brands'].keys())[:5]}")
        print(f"🗺️ Top regions: {list(summary['top_regions'].keys())[:5]}")
        print(f"🧵 Top fabrics: {list(summary['top_fabrics'].keys())[:5]}")
        print("="*50)
        
        # Save results
        analyzer.save_web_trends(f"{Config.OUTPUT_DIR}/web_trends.json")
        
        print("✅ Web trend analysis completed!")
        print(f"📁 Results saved to: {Config.OUTPUT_DIR}/web_trends.json")
    else:
        print("❌ Web trend analysis failed!")

if __name__ == "__main__":
    main() 