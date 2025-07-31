import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Reddit API Configuration
    REDDIT_CLIENT_ID = 'PBSIhI4MnvL2gTGjnGF5Rg'
    REDDIT_CLIENT_SECRET = '9vPsmX51DvXm0Lfz7eZ2KnxCEgR7WA'
    REDDIT_USERNAME = 'Mindless-Call8360'
    REDDIT_PASSWORD = 'NALAGOLDEN'
    REDDIT_USER_AGENT = 'fashion-trend-analyzer-india/1.0.0'

    # Serper API Configuration
    SERPER_API_KEY = 'b50bc7b777affe50d513b469428bc84c78713408'
    SERPER_BASE_URL = 'https://google.serper.dev/search'

    # India-centric Fashion Subreddits
    FASHION_SUBREDDITS = [
        'IndianFashionAddicts',
        'IndianFashion',
        'DesiFashion',
        'IndianBeautyGossip',
        'TwoXIndia',
        'IndianSkincareAddicts',
        'IndianMakeupAddicts',
        'streetwear',
        'fashion',
        'femalefashionadvice'
    ]

    # India-centric Fashion Keywords
    INDIAN_FASHION_KEYWORDS = {
        'traditional_wear': [
            'saree', 'salwar kameez', 'lehenga', 'anarkali', 'kurti', 'dupatta',
            'ghagra', 'choli', 'dhoti', 'kurta', 'pajama', 'dhoti kurta',
            'bandhgala', 'sherwani', 'jodhpuri', 'achkan', 'angarkha'
        ],
        'modern_fusion': [
            'fusion wear', 'indian western', 'contemporary indian', 'modern indian',
            'ethnic fusion', 'indian streetwear', 'desi streetwear', 'indian casual',
            'modern traditional', 'indian contemporary'
        ],
        'indian_brands': [
            'fabindia', 'anita dongre', 'sabyasachi', 'manish malhotra', 'tarun tahiliani',
            'rohit bal', 'abujani sandeep khosla', 'masaba', 'payal singhal',
            'ridhi mehta', 'amit aggarwal', 'gaurav gupta', 'falguni shane peacock'
        ],
        'fabrics_materials': [
            'silk', 'cotton', 'linen', 'khadi', 'chanderi', 'maheshwari', 'banarasi',
            'kanjeevaram', 'mangalgiri', 'ikkat', 'bandhani', 'block print',
            'ajrakh', 'kalamkari', 'chikankari', 'zardozi', 'embroidery'
        ],
        'accessories': [
            'jewelry', 'earrings', 'necklace', 'bangles', 'anklets', 'nose ring',
            'mangalsutra', 'payal', 'jhumka', 'tikka', 'maang tikka', 'haar',
            'kamarband', 'baju band', 'choker', 'statement necklace'
        ],
        'regional_styles': [
            'punjabi suit', 'gujarati chaniya choli', 'bengali saree', 'tamil silk',
            'kerala mundu', 'kashmiri phiran', 'rajasthani ghagra', 'maharashtrian nauvari',
            'odisha ikat', 'assam mekhela', 'manipuri phanek', 'nagaland shawl'
        ],
        'occasions': [
            'wedding wear', 'festival wear', 'party wear', 'casual wear', 'office wear',
            'traditional wear', 'bridal wear', 'groom wear', 'reception wear',
            'mehendi wear', 'sangeet wear', 'haldi wear'
        ]
    }

    # Indian Regions for Regional Analysis
    INDIAN_REGIONS = {
        'North_India': ['punjab', 'haryana', 'delhi', 'uttar pradesh', 'rajasthan', 'himachal pradesh', 'jammu kashmir', 'uttarakhand', 'chandigarh'],
        'South_India': ['tamil nadu', 'karnataka', 'kerala', 'andhra pradesh', 'telangana', 'puducherry'],
        'West_India': ['maharashtra', 'gujarat', 'goa', 'dadra nagar haveli', 'daman diu'],
        'East_India': ['west bengal', 'bihar', 'jharkhand', 'odisha', 'sikkim'],
        'Central_India': ['madhya pradesh', 'chhattisgarh'],
        'Northeast_India': ['assam', 'arunachal pradesh', 'manipur', 'meghalaya', 'mizoram', 'nagaland', 'tripura']
    }

    # Data Storage
    DATA_DIR = './data'
    OUTPUT_DIR = './output'
    CACHE_DIR = './cache'

    # LLM Configuration
    LLM_MODEL_NAME = 'deepseek-r1:8b'
    LLM_MAX_TOKENS = 2048
    LLM_TEMPERATURE = 0.7
    LLM_TOP_P = 0.9

    # Web Search Configuration
    SEARCH_QUERIES = [
        'Indian fashion trends 2024',
        'trending Indian saree styles',
        'popular Indian ethnic wear',
        'Indian fusion fashion trends',
        'traditional Indian clothing trends',
        'Indian wedding fashion 2024',
        'Indian streetwear trends',
        'regional Indian fashion styles',
        'Indian fashion influencers',
        'Indian fashion brands trending'
    ]

    # Analysis Configuration
    MAX_POSTS_PER_SUBREDDIT = 500
    TARGET_CORPUS_SIZE = 50000
    SCRAPING_DELAY = 0.5
    MAX_RETRIES = 3

    @classmethod
    def create_directories(cls):
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
        os.makedirs(cls.CACHE_DIR, exist_ok=True) 