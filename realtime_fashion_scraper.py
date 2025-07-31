#!/usr/bin/env python3
"""
Real-time Indian Fashion Reddit Scraper
Saves data in specified JSON structure and updates file simultaneously for monitoring
"""

import praw
import json
import time
import logging
import os
from datetime import datetime
from config import Config

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealtimeFashionScraper:
    def __init__(self):
        self.reddit = None
        self.fashion_data = {}
        self.setup_reddit()
        self.load_existing_data()
    
    def setup_reddit(self):
        """Setup Reddit API connection"""
        try:
            self.reddit = praw.Reddit(
                client_id=Config.REDDIT_CLIENT_ID,
                client_secret=Config.REDDIT_CLIENT_SECRET,
                username=Config.REDDIT_USERNAME,
                password=Config.REDDIT_PASSWORD,
                user_agent=Config.REDDIT_USER_AGENT
            )
            logger.info("✅ Reddit API connection successful!")
        except Exception as e:
            logger.error(f"❌ Reddit API connection failed: {str(e)}")
            raise
    
    def load_existing_data(self):
        """Load existing data if available"""
        try:
            if os.path.exists(f"{Config.OUTPUT_DIR}/fashion_corpus.json"):
                with open(f"{Config.OUTPUT_DIR}/fashion_corpus.json", 'r', encoding='utf-8') as f:
                    self.fashion_data = json.load(f)
                logger.info("✅ Loaded existing fashion data")
            else:
                self.fashion_data = {
                    "scrape_info": {
                        "start_time": datetime.now().isoformat(),
                        "target_corpus_size": 50000,
                        "total_items": 0,
                        "subreddits_scraped": []
                    }
                }
                logger.info("🆕 Starting fresh fashion data collection")
        except Exception as e:
            logger.error(f"❌ Error loading existing data: {str(e)}")
            self.fashion_data = {
                "scrape_info": {
                    "start_time": datetime.now().isoformat(),
                    "target_corpus_size": 50000,
                    "total_items": 0,
                    "subreddits_scraped": []
                }
            }
    
    def extract_fashion_keywords(self, text):
        """Extract Indian fashion keywords from text"""
        if not text:
            return []
        
        text_lower = text.lower()
        keywords = []
        
        # Check all Indian fashion keywords
        for category, words in Config.INDIAN_FASHION_KEYWORDS.items():
            for word in words:
                if word in text_lower:
                    keywords.append(word)
        
        return list(set(keywords))
    
    def is_fashion_relevant(self, title, content):
        """Check if post is fashion relevant"""
        text = (title + ' ' + content).lower()
        
        # Check for fashion keywords
        fashion_keywords = self.extract_fashion_keywords(text)
        if len(fashion_keywords) > 0:
            return True
        
        # Check for fashion-related subreddits
        fashion_subreddits = ['fashion', 'style', 'outfits', 'streetwear', 'indian']
        for subreddit in fashion_subreddits:
            if subreddit in text:
                return True
        
        return False
    
    def scrape_subreddit_realtime(self, subreddit_name, max_posts=100):
        """Scrape posts from a subreddit in real-time"""
        logger.info(f"Scraping r/{subreddit_name}...")
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            posts_scraped = 0
            
            # Initialize subreddit category if not exists
            if subreddit_name not in self.fashion_data:
                self.fashion_data[subreddit_name] = []
            
            # Scrape hot posts
            for post in subreddit.hot(limit=max_posts):
                if posts_scraped >= max_posts:
                    break
                
                # Check if post is fashion relevant
                if self.is_fashion_relevant(post.title, post.selftext):
                    # Extract post data in specified format
                    post_data = {
                        "title": post.title,
                        "score": post.score,
                        "url": post.url,
                        "comments": [],  # Will be populated if needed
                        "created": post.created_utc,
                        "body": post.selftext,
                        "author": str(post.author) if post.author else "deleted",
                        "subreddit": subreddit_name,
                        "flair": post.link_flair_text if post.link_flair_text else "None",
                        "keywords": self.extract_fashion_keywords(post.title + ' ' + post.selftext),
                        "num_comments": post.num_comments,
                        "upvote_ratio": post.upvote_ratio
                    }
                    
                    # Add to fashion data
                    self.fashion_data[subreddit_name].append(post_data)
                    posts_scraped += 1
                    
                    # Update scrape info
                    self.fashion_data["scrape_info"]["total_items"] += 1
                    
                    # Save data immediately
                    self.save_data_realtime()
                    
                    # Log progress
                    if posts_scraped % 10 == 0:
                        logger.info(f"📊 Scraped {posts_scraped} fashion posts from r/{subreddit_name}")
                        logger.info(f"📈 Total items: {self.fashion_data['scrape_info']['total_items']}")
                
                # Rate limiting
                time.sleep(0.5)
            
            # Update subreddits scraped
            if subreddit_name not in self.fashion_data["scrape_info"]["subreddits_scraped"]:
                self.fashion_data["scrape_info"]["subreddits_scraped"].append(subreddit_name)
            
            logger.info(f"✅ Scraped {posts_scraped} fashion posts from r/{subreddit_name}")
            return posts_scraped
            
        except Exception as e:
            logger.error(f"❌ Failed to scrape r/{subreddit_name}: {str(e)}")
            return 0
    
    def save_data_realtime(self):
        """Save data to JSON file in real-time"""
        try:
            # Create output directory if it doesn't exist
            os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
            
            filename = f"{Config.OUTPUT_DIR}/fashion_corpus.json"
            
            # Update timestamp
            self.fashion_data["scrape_info"]["last_updated"] = datetime.now().isoformat()
            
            # Save to JSON file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.fashion_data, f, indent=2, ensure_ascii=False)
            
            # Log file size
            file_size = os.path.getsize(filename)
            logger.info(f"💾 Data saved: {file_size} bytes, {self.fashion_data['scrape_info']['total_items']} items")
            
        except Exception as e:
            logger.error(f"❌ Error saving data: {str(e)}")
    
    def scrape_all_fashion_subreddits(self):
        """Scrape all fashion subreddits in real-time"""
        logger.info("🚀 Starting Real-time Indian Fashion Reddit Scraper...")
        logger.info(f"📊 Target corpus size: 50,000 items")
        logger.info(f"📊 Monitoring {len(Config.FASHION_SUBREDDITS)} subreddits")
        
        total_posts = 0
        
        for subreddit in Config.FASHION_SUBREDDITS:
            try:
                posts = self.scrape_subreddit_realtime(subreddit, max_posts=500)
                total_posts += posts
                
                # Check if we have enough data
                if self.fashion_data["scrape_info"]["total_items"] >= 50000:
                    logger.info(f"🎯 Target corpus size reached: {self.fashion_data['scrape_info']['total_items']} items")
                    break
                
                # Rate limiting between subreddits
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ Failed to scrape r/{subreddit}: {str(e)}")
                continue
        
        # Final save
        self.save_data_realtime()
        
        logger.info("🎉 Real-time scraping completed!")
        logger.info(f"📈 Final Summary:")
        logger.info(f"   - Total fashion posts: {total_posts}")
        logger.info(f"   - Total items in corpus: {self.fashion_data['scrape_info']['total_items']}")
        logger.info(f"   - Subreddits processed: {len(self.fashion_data['scrape_info']['subreddits_scraped'])}")
        
        return total_posts

def main():
    """Main function to run the real-time scraper"""
    try:
        scraper = RealtimeFashionScraper()
        posts = scraper.scrape_all_fashion_subreddits()
        
        print("\n" + "="*60)
        print("🎉 REAL-TIME FASHION CORPUS SCRAPER COMPLETED!")
        print("="*60)
        print(f"📊 Total Fashion Posts Scraped: {posts}")
        print(f"📈 Total Items in Corpus: {scraper.fashion_data['scrape_info']['total_items']}")
        print(f"📁 Data saved to: {Config.OUTPUT_DIR}/fashion_corpus.json")
        print("="*60)
        print("📋 You can monitor the JSON file in real-time!")
        print("🔍 Check the file size and content as it updates.")
        print("="*60)
        
    except Exception as e:
        logger.error(f"❌ Scraper failed: {str(e)}")
        print(f"\n❌ Error: {str(e)}")
        print("🔧 Please check your Reddit credentials and internet connection.")

if __name__ == "__main__":
    main() 