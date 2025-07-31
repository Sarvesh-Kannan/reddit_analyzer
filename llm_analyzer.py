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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LLMFashionAnalyzer:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "deepseek-r1:8b"  # Using DeepSeek model
        self.cleaned_data = None
        self.analysis_results = {}
    
    def load_cleaned_data(self, filepath):
        """Load cleaned fashion data"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.cleaned_data = data['posts']
            logger.info(f"✅ Loaded {len(self.cleaned_data)} cleaned posts")
            return True
        except Exception as e:
            logger.error(f"❌ Error loading cleaned data: {str(e)}")
            return False
    
    def call_ollama(self, prompt, max_tokens=2048):
        """Call Ollama API"""
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
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
        """Analyze trending fashion keywords"""
        logger.info("🔍 Analyzing trending keywords...")
        
        # Get keyword statistics
        all_keywords = []
        for post in self.cleaned_data:
            all_keywords.extend(post['keywords'])
        
        keyword_counts = pd.Series(all_keywords).value_counts()
        top_keywords = keyword_counts.head(15).to_dict()
        
        # Create prompt for LLM analysis
        prompt = f"""
        Analyze the following Indian fashion keywords from Reddit data and provide insights:

        Top Keywords: {list(top_keywords.keys())}
        Keyword Counts: {top_keywords}

        Please provide:
        1. What are the most trending Indian fashion items/styles?
        2. Which traditional vs modern fashion elements are popular?
        3. What does this indicate about current Indian fashion preferences?
        4. Any regional or cultural patterns you notice?
        5. Recommendations for fashion retailers/buyers based on these trends.

        Provide detailed analysis with specific insights and actionable recommendations.
        """
        
        response = self.call_ollama(prompt)
        
        if response:
            self.analysis_results['trending_keywords'] = {
                'keywords': top_keywords,
                'analysis': response,
                'timestamp': datetime.now().isoformat()
            }
            logger.info("✅ Keyword analysis completed")
            return True
        else:
            logger.error("❌ Keyword analysis failed")
            return False
    
    def analyze_regional_trends(self):
        """Analyze regional fashion trends"""
        logger.info("🗺️ Analyzing regional trends...")
        
        # Get regional statistics
        df = pd.DataFrame(self.cleaned_data)
        regional_stats = df['region'].value_counts().to_dict()
        
        # Get keywords by region
        regional_keywords = {}
        for post in self.cleaned_data:
            region = post['region']
            if region not in regional_keywords:
                regional_keywords[region] = []
            regional_keywords[region].extend(post['keywords'])
        
        # Count keywords by region
        for region in regional_keywords:
            regional_keywords[region] = pd.Series(regional_keywords[region]).value_counts().head(10).to_dict()
        
        prompt = f"""
        Analyze Indian regional fashion trends from Reddit data:

        Regional Distribution: {regional_stats}
        Regional Keywords: {regional_keywords}

        Please provide:
        1. Which Indian regions show the most fashion engagement?
        2. What are the unique fashion preferences by region?
        3. How do traditional vs modern fashion vary across regions?
        4. What cultural factors influence these regional trends?
        5. Business opportunities for region-specific fashion marketing.

        Provide detailed analysis with cultural context and business insights.
        """
        
        response = self.call_ollama(prompt)
        
        if response:
            self.analysis_results['regional_trends'] = {
                'regional_stats': regional_stats,
                'regional_keywords': regional_keywords,
                'analysis': response,
                'timestamp': datetime.now().isoformat()
            }
            logger.info("✅ Regional analysis completed")
            return True
        else:
            logger.error("❌ Regional analysis failed")
            return False
    
    def analyze_sentiment_trends(self):
        """Analyze sentiment and engagement trends"""
        logger.info("📊 Analyzing sentiment and engagement...")
        
        # Calculate engagement metrics
        df = pd.DataFrame(self.cleaned_data)
        
        engagement_stats = {
            'avg_score': df['score'].mean(),
            'avg_comments': df['num_comments'].mean(),
            'avg_upvote_ratio': df['upvote_ratio'].mean(),
            'high_engagement_posts': len(df[df['score'] > df['score'].quantile(0.8)]),
            'top_subreddits': df['subreddit'].value_counts().head(5).to_dict()
        }
        
        # Get high engagement posts
        high_engagement = df[df['score'] > df['score'].quantile(0.8)].head(10)
        top_posts = []
        for _, post in high_engagement.iterrows():
            top_posts.append({
                'title': post['title'],
                'score': post['score'],
                'subreddit': post['subreddit'],
                'keywords': post['keywords']
            })
        
        prompt = f"""
        Analyze Indian fashion engagement and sentiment from Reddit data:

        Engagement Statistics: {engagement_stats}
        Top Performing Posts: {top_posts}

        Please provide:
        1. What types of fashion content get the most engagement?
        2. Which subreddits are most active for Indian fashion?
        3. What sentiment patterns do you observe?
        4. What makes certain fashion posts go viral?
        5. Recommendations for creating engaging Indian fashion content.

        Provide detailed analysis with engagement insights and content strategy recommendations.
        """
        
        response = self.call_ollama(prompt)
        
        if response:
            self.analysis_results['sentiment_trends'] = {
                'engagement_stats': engagement_stats,
                'top_posts': top_posts,
                'analysis': response,
                'timestamp': datetime.now().isoformat()
            }
            logger.info("✅ Sentiment analysis completed")
            return True
        else:
            logger.error("❌ Sentiment analysis failed")
            return False
    
    def generate_comprehensive_report(self):
        """Generate comprehensive fashion trend report"""
        logger.info("📋 Generating comprehensive report...")
        
        # Prepare summary statistics
        df = pd.DataFrame(self.cleaned_data)
        
        summary_stats = {
            'total_posts': len(self.cleaned_data),
            'subreddits_analyzed': df['subreddit'].nunique(),
            'regions_covered': df['region'].nunique(),
            'avg_score': df['score'].mean(),
            'total_keywords': sum(len(post['keywords']) for post in self.cleaned_data),
            'date_range': {
                'earliest': datetime.fromtimestamp(df['created'].min()).strftime('%Y-%m-%d'),
                'latest': datetime.fromtimestamp(df['created'].max()).strftime('%Y-%m-%d')
            }
        }
        
        prompt = f"""
        Generate a comprehensive Indian fashion trend analysis report based on Reddit data:

        Summary Statistics: {summary_stats}
        
        Previous Analysis Results:
        - Keyword Trends: {self.analysis_results.get('trending_keywords', {}).get('keywords', {})}
        - Regional Patterns: {self.analysis_results.get('regional_trends', {}).get('regional_stats', {})}
        - Engagement Metrics: {self.analysis_results.get('sentiment_trends', {}).get('engagement_stats', {})}

        Please provide:
        1. Executive Summary of Indian Fashion Trends
        2. Key Insights and Patterns
        3. Regional Fashion Preferences
        4. Engagement and Sentiment Analysis
        5. Business Recommendations for Fashion Retailers
        6. Future Trend Predictions
        7. Actionable Insights for Buyers and Sellers

        Format as a professional business report with clear sections and actionable recommendations.
        """
        
        response = self.call_ollama(prompt, max_tokens=4096)
        
        if response:
            self.analysis_results['comprehensive_report'] = {
                'summary_stats': summary_stats,
                'report': response,
                'timestamp': datetime.now().isoformat()
            }
            logger.info("✅ Comprehensive report generated")
            return True
        else:
            logger.error("❌ Comprehensive report generation failed")
            return False
    
    def run_full_analysis(self):
        """Run complete analysis pipeline"""
        logger.info("🚀 Starting comprehensive LLM analysis...")
        
        # Run all analyses
        analyses = [
            self.analyze_trending_keywords(),
            self.analyze_regional_trends(),
            self.analyze_sentiment_trends(),
            self.generate_comprehensive_report()
        ]
        
        success_count = sum(analyses)
        
        if success_count > 0:
            # Save analysis results
            self.save_analysis_results()
            
            logger.info(f"✅ Analysis completed! {success_count}/4 analyses successful")
            return True
        else:
            logger.error("❌ All analyses failed")
            return False
    
    def save_analysis_results(self, filepath=None):
        """Save analysis results"""
        if not filepath:
            filepath = f"{Config.OUTPUT_DIR}/llm_analysis_results.json"
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.analysis_results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Analysis results saved to: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving analysis results: {str(e)}")
            return False

def main():
    """Main function to run LLM analysis"""
    analyzer = LLMFashionAnalyzer()
    
    # Load cleaned data
    if not analyzer.load_cleaned_data(f"{Config.OUTPUT_DIR}/cleaned_fashion_data.json"):
        logger.error("❌ Could not load cleaned data. Run preprocessing first.")
        return
    
    # Run analysis
    if analyzer.run_full_analysis():
        print("\n" + "="*60)
        print("🎉 LLM FASHION ANALYSIS COMPLETED!")
        print("="*60)
        print("📊 Analysis Results:")
        for analysis_type in analyzer.analysis_results.keys():
            print(f"   ✅ {analysis_type.replace('_', ' ').title()}")
        print("="*60)
        print("📁 Results saved to: output/llm_analysis_results.json")
        print("="*60)
    else:
        print("\n❌ LLM analysis failed. Check Ollama is running.")

if __name__ == "__main__":
    main() 