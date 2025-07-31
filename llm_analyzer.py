#!/usr/bin/env python3
"""
LLM Analyzer for Indian Fashion Trends
Uses Ollama with DeepSeek-R1:8B for analysis
"""

import json
import pandas as pd
import requests
import logging
from datetime import datetime
from config import Config
from web_search_analyzer import WebSearchAnalyzer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LLMFashionAnalyzer:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "deepseek-r1:8b"  # Using DeepSeek model
        self.cleaned_data = None
        self.web_trends = None
        self.analysis_results = {}
        self.web_analyzer = WebSearchAnalyzer()
    
    def load_cleaned_data(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.cleaned_data = data['posts']
            logger.info(f"✅ Loaded {len(self.cleaned_data)} cleaned posts")
            return True
        except Exception as e:
            logger.error(f"❌ Error loading cleaned data: {str(e)}")
            return False
    
    def load_web_trends(self, filepath):
        """Load web search trends data"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.web_trends = json.load(f)
            logger.info(f"✅ Loaded web trends data")
            return True
        except Exception as e:
            logger.error(f"❌ Error loading web trends: {str(e)}")
            return False
    
    def call_ollama(self, prompt, max_tokens=2048):
        """Call Ollama API with enhanced prompt"""
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": Config.LLM_TEMPERATURE,
                    "top_p": Config.LLM_TOP_P,
                    "max_tokens": max_tokens
                }
            }
            
            response = requests.post(self.ollama_url, json=payload, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
            else:
                logger.error(f"❌ Ollama API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error calling Ollama: {str(e)}")
            return None
    
    def analyze_trending_keywords(self):
        """Analyze trending keywords with web data integration"""
        if not self.cleaned_data:
            return None
        
        # Extract Reddit keywords
        all_keywords = []
        for post in self.cleaned_data:
            all_keywords.extend(post['keywords'])
        
        reddit_keyword_counts = pd.Series(all_keywords).value_counts()
        top_reddit_keywords = reddit_keyword_counts.head(15).to_dict()
        
        # Get web trends if available
        web_keywords = {}
        web_brands = {}
        web_regions = {}
        
        if self.web_trends and 'trending_summary' in self.web_trends:
            web_summary = self.web_trends['trending_summary']
            web_keywords = web_summary.get('top_keywords', {})
            web_brands = web_summary.get('top_brands', {})
            web_regions = web_summary.get('top_regions', {})
        
        # Create comprehensive prompt
        prompt = f"""
        Analyze Indian fashion trends using both Reddit community data and current web search results:

        REDDIT DATA (Community Trends):
        Top Keywords: {list(top_reddit_keywords.keys())}
        Keyword Counts: {top_reddit_keywords}

        WEB SEARCH DATA (Current Trends):
        Top Web Keywords: {list(web_keywords.keys())[:10] if web_keywords else 'No web data'}
        Top Brands Mentioned: {list(web_brands.keys())[:5] if web_brands else 'No brand data'}
        Top Regions: {list(web_regions.keys())[:5] if web_regions else 'No regional data'}

        Please provide a comprehensive analysis covering:

        1. **Trending Fashion Items**: What are the most popular Indian fashion items/styles currently?
        2. **Traditional vs Modern**: Which traditional and modern fashion elements are trending?
        3. **Regional Patterns**: What regional fashion preferences are emerging?
        4. **Brand Analysis**: Which Indian fashion brands are most popular?
        5. **Platform Comparison**: How do Reddit community trends compare to web search trends?
        6. **Cultural Insights**: What does this indicate about current Indian fashion culture?
        7. **Business Recommendations**: What should fashion retailers/buyers focus on?
        8. **Future Predictions**: What trends are likely to continue or emerge?

        Provide detailed insights with specific examples and actionable recommendations.
        """
        
        analysis = self.call_ollama(prompt)
        return {
            'analysis': analysis,
            'reddit_keywords': top_reddit_keywords,
            'web_keywords': web_keywords,
            'web_brands': web_brands,
            'web_regions': web_regions
        }
    
    def analyze_regional_trends(self):
        """Analyze regional trends with web data"""
        if not self.cleaned_data:
            return None
        
        df = pd.DataFrame(self.cleaned_data)
        regional_data = df['region'].value_counts().to_dict()
        
        # Get web regional data
        web_regional_data = {}
        if self.web_trends and 'trending_summary' in self.web_trends:
            web_regional_data = self.web_trends['trending_summary'].get('top_regions', {})
        
        prompt = f"""
        Analyze regional Indian fashion trends using both Reddit and web data:

        REDDIT REGIONAL DATA:
        {regional_data}

        WEB REGIONAL DATA:
        {web_regional_data}

        Please analyze:
        1. Which regions are most active in fashion discussions?
        2. What are the unique fashion preferences by region?
        3. How do regional trends compare between Reddit and web search?
        4. What cultural factors influence regional fashion choices?
        5. Which regions show the most fashion innovation?
        6. Recommendations for region-specific fashion marketing.

        Provide detailed regional insights with cultural context.
        """
        
        analysis = self.call_ollama(prompt)
        return {
            'analysis': analysis,
            'reddit_regions': regional_data,
            'web_regions': web_regional_data
        }
    
    def analyze_brand_trends(self):
        """Analyze brand trends with web data"""
        if not self.cleaned_data:
            return None
        
        # Extract brand mentions from Reddit data
        all_text = ' '.join([post['title'] + ' ' + post['content'] for post in self.cleaned_data])
        reddit_brands = {}
        
        for brand in Config.INDIAN_FASHION_KEYWORDS['indian_brands']:
            count = all_text.lower().count(brand.lower())
            if count > 0:
                reddit_brands[brand] = count
        
        # Get web brand data
        web_brands = {}
        if self.web_trends and 'trending_summary' in self.web_trends:
            web_brands = self.web_trends['trending_summary'].get('top_brands', {})
        
        prompt = f"""
        Analyze Indian fashion brand trends using Reddit and web data:

        REDDIT BRAND MENTIONS:
        {reddit_brands}

        WEB BRAND MENTIONS:
        {web_brands}

        Please analyze:
        1. Which Indian fashion brands are most popular?
        2. How do Reddit community preferences compare to web search trends?
        3. What factors make certain brands more popular?
        4. Which brands are trending upward/downward?
        5. Brand positioning and market analysis
        6. Recommendations for brand strategy and marketing.

        Provide detailed brand analysis with market insights.
        """
        
        analysis = self.call_ollama(prompt)
        return {
            'analysis': analysis,
            'reddit_brands': reddit_brands,
            'web_brands': web_brands
        }
    
    def generate_comprehensive_report(self):
        """Generate comprehensive analysis report with web data integration"""
        logger.info("🤖 Starting comprehensive LLM analysis with web data...")
        
        # Run all analyses
        keyword_analysis = self.analyze_trending_keywords()
        regional_analysis = self.analyze_regional_trends()
        brand_analysis = self.analyze_brand_trends()
        
        # Generate final comprehensive report
        prompt = f"""
        Create a comprehensive Indian Fashion Trend Analysis Report using all available data:

        KEYWORD ANALYSIS:
        {keyword_analysis['analysis'] if keyword_analysis else 'No keyword data'}

        REGIONAL ANALYSIS:
        {regional_analysis['analysis'] if regional_analysis else 'No regional data'}

        BRAND ANALYSIS:
        {brand_analysis['analysis'] if brand_analysis else 'No brand data'}

        Please create a comprehensive report covering:
        1. Executive Summary
        2. Current Fashion Trends
        3. Regional Insights
        4. Brand Analysis
        5. Platform Comparison (Reddit vs Web)
        6. Cultural Insights
        7. Business Recommendations
        8. Future Predictions
        9. Actionable Insights

        Format the report professionally with clear sections and bullet points.
        """
        
        comprehensive_report = self.call_ollama(prompt, max_tokens=4096)
        
        self.analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'keyword_analysis': keyword_analysis,
            'regional_analysis': regional_analysis,
            'brand_analysis': brand_analysis,
            'comprehensive_report': comprehensive_report
        }
        
        return self.analysis_results
    
    def save_analysis_results(self, filepath):
        """Save analysis results to file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.analysis_results, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Analysis results saved to: {filepath}")
            return True
        except Exception as e:
            logger.error(f"❌ Error saving analysis results: {str(e)}")
            return False
    
    def run_full_analysis(self, cleaned_data_path, web_trends_path=None):
        """Run complete analysis with web data integration"""
        logger.info("🚀 Starting full LLM analysis with web data integration...")
        
        # Load cleaned data
        if not self.load_cleaned_data(cleaned_data_path):
            logger.error("❌ Failed to load cleaned data")
            return False
        
        # Load web trends if available
        if web_trends_path:
            self.load_web_trends(web_trends_path)
            logger.info("✅ Web trends data loaded")
        else:
            logger.info("⚠️ No web trends data provided")
        
        # Run comprehensive analysis
        results = self.generate_comprehensive_report()
        
        if results:
            # Save results
            output_path = f"{Config.OUTPUT_DIR}/llm_analysis_results.json"
            self.save_analysis_results(output_path)
            
            logger.info("🎉 Comprehensive LLM analysis completed!")
            logger.info(f"📁 Results saved to: {output_path}")
            return True
        else:
            logger.error("❌ LLM analysis failed")
            return False

def main():
    """Main function to run LLM analysis"""
    analyzer = LLMFashionAnalyzer()
    
    # Run analysis with web data integration
    cleaned_data_path = f"{Config.OUTPUT_DIR}/cleaned_fashion_data.json"
    web_trends_path = f"{Config.OUTPUT_DIR}/web_trends.json"
    
    success = analyzer.run_full_analysis(cleaned_data_path, web_trends_path)
    
    if success:
        print("\n" + "="*60)
        print("🎉 COMPREHENSIVE LLM ANALYSIS COMPLETED!")
        print("="*60)
        print("📊 Analysis includes:")
        print("   - Reddit community trends")
        print("   - Web search current trends")
        print("   - Regional fashion patterns")
        print("   - Brand popularity analysis")
        print("   - Platform comparison insights")
        print("   - Business recommendations")
        print("="*60)
        print("📁 Results saved to: output/llm_analysis_results.json")
        print("="*60)
    else:
        print("❌ Analysis failed. Check logs for details.")

if __name__ == "__main__":
    main() 