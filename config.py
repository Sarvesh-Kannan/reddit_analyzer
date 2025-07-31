import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Reddit API Configuration
    REDDIT_CLIENT_ID = 'PBSIhI4MnvL2gTGjnGF5Rg'
    REDDIT_CLIENT_SECRET = '9vPsmX51DvXm0Lfz7eZ2KnkCEgR7WA'
    REDDIT_USERNAME = 'Mindless-Call8360'
    REDDIT_PASSWORD = 'NALAGOLDEN'
    REDDIT_USER_AGENT = 'fashion-trend-analyzer-india/1.0.0'
    
    # India-centric Fashion Subreddits
    FASHION_SUBREDDITS = [
        'IndianFashionAddicts',
        'IndianFashion',
        'DesiFashion',
        'IndianBeautyGossip',
        'TwoXIndia',
        'IndianSkincareAddicts',
        'IndianMakeupAddicts',
        'streetwear',  # Global but relevant for Indian streetwear
        'fashion',     # Global fashion trends
        'femalefashionadvice'  # Global but useful for Indian women
    ]
    
    # Indian Fashion Keywords and Categories
    INDIAN_FASHION_KEYWORDS = {
        'traditional': [
            'saree', 'salwar', 'kameez', 'lehenga', 'anarkali', 'kurta', 'dhoti', 'mundu',
            'ghagra', 'choli', 'dupatta', 'pallu', 'pallav', 'zari', 'zardosi', 'embroidery',
            'bandhani', 'ikat', 'block_print', 'ajrakh', 'kalamkari', 'phulkari', 'chikankari'
        ],
        'modern_indian': [
            'indian_western', 'fusion_wear', 'contemporary_indian', 'modern_saree',
            'indian_casual', 'ethnic_casual', 'indian_formal', 'indian_party_wear'
        ],
        'indian_brands': [
            'fabindia', 'anita_dongre', 'sabyasachi', 'manish_malhotra', 'tarun_tahiliani',
            'rohit_bal', 'satya_paul', 'w_for_woman', 'biba', 'global_desai',
            'masaba', 'payal_khandwala', 'ridhi_mehra', 'suket_dhir', 'abraham_thakore'
        ],
        'indian_styles': [
            'indian_streetwear', 'desi_aesthetic', 'indian_minimalist', 'indian_bohemian',
            'indian_preppy', 'indian_gothic', 'indian_vintage', 'indian_retro'
        ],
        'indian_accessories': [
            'jhumka', 'kundan', 'polki', 'meenakari', 'thewa', 'lac_bangles',
            'indian_jewelry', 'traditional_jewelry', 'indian_bags', 'indian_footwear',
            'kolhapuri', 'mojari', 'jutti', 'indian_scarves', 'indian_belts'
        ],
        'indian_colors': [
            'indian_red', 'saffron', 'turmeric_yellow', 'mehendi_green', 'indigo',
            'rose_pink', 'marigold', 'lotus_pink', 'peacock_blue', 'mango_yellow'
        ],
        'indian_fabrics': [
            'silk', 'cotton', 'khadi', 'linen', 'wool', 'jute', 'bamboo_fabric',
            'banana_fiber', 'lotus_fiber', 'organic_cotton', 'handloom', 'powerloom'
        ]
    }
    
    # Indian Regions for Analysis
    INDIAN_REGIONS = {
        'North_India': ['delhi', 'punjab', 'haryana', 'rajasthan', 'uttar_pradesh', 'himachal'],
        'South_India': ['karnataka', 'tamil_nadu', 'kerala', 'andhra_pradesh', 'telangana'],
        'East_India': ['west_bengal', 'bihar', 'odisha', 'jharkhand', 'assam'],
        'West_India': ['maharashtra', 'gujarat', 'goa', 'madhya_pradesh'],
        'Central_India': ['chhattisgarh', 'madhya_pradesh'],
        'Northeast_India': ['assam', 'manipur', 'meghalaya', 'nagaland', 'tripura']
    }
    
    # Analysis Settings
    MAX_POSTS_PER_SUBREDDIT = 100
    MAX_COMMENTS_PER_POST = 50
    SENTIMENT_THRESHOLD = 0.1
    KEYWORD_MIN_FREQUENCY = 3
    
    # Data Storage
    DATA_DIR = './data'
    OUTPUT_DIR = './output'
    CACHE_DIR = './cache'
    
    # LLM Settings (for local model integration)
    LLM_MODEL_PATH = './models/deepseek-r1-8b'
    LLM_MAX_TOKENS = 2048
    LLM_TEMPERATURE = 0.7
    
    # Dashboard Settings
    DASHBOARD_PORT = 8050
    DASHBOARD_HOST = 'localhost'
    
    # Scheduling
    SCRAPE_INTERVAL_HOURS = 6
    ANALYSIS_INTERVAL_HOURS = 12
    CLEANUP_INTERVAL_DAYS = 7
    
    # Indian Fashion Trends to Monitor
    INDIAN_TREND_CATEGORIES = [
        'Traditional Revival',
        'Fusion Fashion',
        'Sustainable Indian Fashion',
        'Indian Streetwear',
        'Wedding Fashion',
        'Festival Fashion',
        'Indian Workwear',
        'Indian Casual Wear',
        'Indian Luxury Fashion',
        'Indian Fast Fashion'
    ]
    
    # Indian Fashion Events and Seasons
    INDIAN_FASHION_SEASONS = {
        'Wedding_Season': ['October', 'November', 'December', 'January', 'February'],
        'Festival_Season': ['September', 'October', 'November'],
        'Summer_Fashion': ['March', 'April', 'May', 'June'],
        'Monsoon_Fashion': ['June', 'July', 'August', 'September'],
        'Winter_Fashion': ['December', 'January', 'February']
    }
    
    # Indian Fashion Price Points
    INDIAN_PRICE_CATEGORIES = {
        'Budget': 'Under ₹1000',
        'Mid_Range': '₹1000-₹5000',
        'Premium': '₹5000-₹20000',
        'Luxury': 'Above ₹20000'
    }
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories if they don't exist"""
        import os
        for directory in [cls.DATA_DIR, cls.OUTPUT_DIR, cls.CACHE_DIR]:
            os.makedirs(directory, exist_ok=True)
    
    @classmethod
    def get_reddit_config(cls):
        """Get Reddit configuration as dictionary"""
        return {
            'client_id': cls.REDDIT_CLIENT_ID,
            'client_secret': cls.REDDIT_CLIENT_SECRET,
            'username': cls.REDDIT_USERNAME,
            'password': cls.REDDIT_PASSWORD,
            'user_agent': cls.REDDIT_USER_AGENT
        } 