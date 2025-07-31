#!/usr/bin/env python3
"""
Data Preprocessor for Indian Fashion Analysis
Cleans and filters fashion data for analysis
"""

import json
import pandas as pd
import re
import logging
from datetime import datetime
from config import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FashionDataPreprocessor:
    def __init__(self):
        self.raw_data = None
        self.cleaned_data = None
        self.fashion_keywords = self._get_fashion_keywords()
    
    def _get_fashion_keywords(self):
        """Get all fashion keywords from config"""
        keywords = []
        for category, words in Config.INDIAN_FASHION_KEYWORDS.items():
            keywords.extend(words)
        return set(keywords)
    
    def load_raw_data(self, filepath):
        """Load raw fashion data"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.raw_data = json.load(f)
            logger.info(f"✅ Loaded {len(self.raw_data)} subreddits from {filepath}")
            return True
        except Exception as e:
            logger.error(f"❌ Error loading data: {str(e)}")
            return False
    
    def clean_text(self, text):
        """Clean text data"""
        if not text:
            return ""
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove Reddit formatting
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # Remove markdown links
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Remove bold
        text = re.sub(r'\*([^*]+)\*', r'\1', text)  # Remove italic
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def is_fashion_relevant(self, title, content):
        """Check if post is fashion relevant"""
        text = (title + ' ' + content).lower()
        
        # Check for fashion keywords
        for keyword in self.fashion_keywords:
            if keyword in text:
                return True
        
        # Check for fashion-related terms
        fashion_terms = ['fashion', 'style', 'outfit', 'clothing', 'dress', 'wear', 'look']
        for term in fashion_terms:
            if term in text:
                return True
        
        return False
    
    def extract_fashion_keywords(self, text):
        """Extract fashion keywords from text"""
        if not text:
            return []
        
        text_lower = text.lower()
        found_keywords = []
        
        for keyword in self.fashion_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def detect_region(self, text):
        """Detect Indian region from text"""
        if not text:
            return 'Unknown'
        
        text_lower = text.lower()
        
        for region, states in Config.INDIAN_REGIONS.items():
            for state in states:
                if state in text_lower:
                    return region
        
        return 'Unknown'
    
    def preprocess_data(self):
        """Preprocess and clean the fashion data"""
        logger.info("🔄 Starting data preprocessing...")
        
        cleaned_posts = []
        total_posts = 0
        fashion_posts = 0
        
        for subreddit_name, posts in self.raw_data.items():
            if subreddit_name == 'scrape_info':
                continue
            
            logger.info(f"Processing r/{subreddit_name}: {len(posts)} posts")
            
            for post in posts:
                total_posts += 1
                
                # Clean text
                clean_title = self.clean_text(post.get('title', ''))
                clean_content = self.clean_text(post.get('body', ''))
                
                # Check if fashion relevant
                if self.is_fashion_relevant(clean_title, clean_content):
                    fashion_posts += 1
                    
                    # Extract keywords
                    keywords = self.extract_fashion_keywords(clean_title + ' ' + clean_content)
                    
                    # Detect region
                    region = self.detect_region(clean_title + ' ' + clean_content)
                    
                    # Create cleaned post
                    cleaned_post = {
                        'id': post.get('id', ''),
                        'title': clean_title,
                        'content': clean_content,
                        'subreddit': subreddit_name,
                        'score': post.get('score', 0),
                        'upvote_ratio': post.get('upvote_ratio', 0),
                        'num_comments': post.get('num_comments', 0),
                        'created': post.get('created', 0),
                        'author': post.get('author', ''),
                        'flair': post.get('flair', ''),
                        'keywords': keywords,
                        'region': region,
                        'url': post.get('url', ''),
                        'permalink': post.get('permalink', ''),
                        'text_length': len(clean_title + ' ' + clean_content),
                        'keyword_count': len(keywords)
                    }
                    
                    cleaned_posts.append(cleaned_post)
        
        self.cleaned_data = cleaned_posts
        
        logger.info(f"✅ Preprocessing completed!")
        logger.info(f"📊 Total posts processed: {total_posts}")
        logger.info(f"🎯 Fashion relevant posts: {fashion_posts}")
        logger.info(f"📈 Filtered data size: {len(self.cleaned_data)}")
        
        return len(self.cleaned_data)
    
    def save_cleaned_data(self, filepath):
        """Save cleaned data"""
        try:
            cleaned_data = {
                'metadata': {
                    'processed_at': datetime.now().isoformat(),
                    'total_posts': len(self.cleaned_data),
                    'fashion_keywords_used': list(self.fashion_keywords)
                },
                'posts': self.cleaned_data
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Cleaned data saved to: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving cleaned data: {str(e)}")
            return False
    
    def get_statistics(self):
        """Get preprocessing statistics"""
        if not self.cleaned_data:
            return {}
        
        df = pd.DataFrame(self.cleaned_data)
        
        stats = {
            'total_posts': len(self.cleaned_data),
            'subreddits': df['subreddit'].nunique(),
            'regions': df['region'].value_counts().to_dict(),
            'keyword_distribution': {},
            'score_stats': {
                'mean': df['score'].mean(),
                'median': df['score'].median(),
                'max': df['score'].max(),
                'min': df['score'].min()
            },
            'top_keywords': self._get_top_keywords(),
            'top_subreddits': df['subreddit'].value_counts().head(10).to_dict()
        }
        
        return stats
    
    def _get_top_keywords(self):
        """Get top keywords from cleaned data"""
        all_keywords = []
        for post in self.cleaned_data:
            all_keywords.extend(post['keywords'])
        
        keyword_counts = pd.Series(all_keywords).value_counts()
        return keyword_counts.head(20).to_dict()

def main():
    """Main function to run preprocessing"""
    preprocessor = FashionDataPreprocessor()
    
    # Load raw data
    if not preprocessor.load_raw_data(f"{Config.OUTPUT_DIR}/fashion_corpus.json"):
        return
    
    # Preprocess data
    cleaned_count = preprocessor.preprocess_data()
    
    if cleaned_count > 0:
        # Save cleaned data
        preprocessor.save_cleaned_data(f"{Config.OUTPUT_DIR}/cleaned_fashion_data.json")
        
        # Get and display statistics
        stats = preprocessor.get_statistics()
        
        print("\n" + "="*60)
        print("🎯 FASHION DATA PREPROCESSING COMPLETED!")
        print("="*60)
        print(f"📊 Total Posts: {stats['total_posts']}")
        print(f"📁 Subreddits: {stats['subreddits']}")
        print(f"🏆 Top Keywords: {list(stats['top_keywords'].keys())[:10]}")
        print(f"📈 Score Stats: Mean={stats['score_stats']['mean']:.2f}, Max={stats['score_stats']['max']}")
        print("="*60)
        
        # Save statistics
        with open(f"{Config.OUTPUT_DIR}/preprocessing_stats.json", 'w') as f:
            json.dump(stats, f, indent=2)
        
        logger.info("✅ Preprocessing statistics saved")
    else:
        logger.error("❌ No fashion relevant data found")

if __name__ == "__main__":
    main() 