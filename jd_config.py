
TIER_A = {
    'embeddings', 'vector search', 'semantic search',
    'information retrieval', 'sentence transformers',
    'faiss', 'pinecone', 'milvus', 'weaviate', 'qdrant',
    'pgvector', 'opensearch', 'elasticsearch', 'bm25',
    'learning to rank', 'rag', 'recommendation systems',
    'haystack', 'llamaindex'
}

TIER_B = {
    'llms', 'fine-tuning llms', 'nlp', 'pytorch', 'tensorflow',
    'python', 'langchain', 'prompt engineering', 'lora', 'qlora',
    'peft', 'hugging face transformers', 'machine learning',
    'deep learning', 'scikit-learn', 'mlops', 'mlflow',
    'weights & biases'
}

TIER_C = {
    'feature engineering', 'data science', 'statistical modeling',
    'kubeflow', 'bentoml', 'time series', 'forecasting'
}

CV_SPEECH = {
    'computer vision', 'opencv', 'yolo', 'object detection',
    'image classification', 'cnn', 'gans', 'diffusion models',
    'speech recognition', 'tts', 'asr', 'reinforcement learning'
}

TIER_WEIGHT = {
    'tier_a':     1.0,
    'tier_b':     0.6,
    'tier_c':     0.3,
    'cv_speech':  0.0,
    'irrelevant': 0.0
}

SKILL_NORMALIZATION = {
    'natural language processing':   'nlp',
    'information retrieval systems': 'information retrieval',
    'vector representations':        'vector search',
    'ranking systems':               'learning to rank',
    'search infrastructure':         'elasticsearch',
    'search backend':                'semantic search',
    'text encoders':                 'sentence transformers',
    'content matching':              'semantic search',
    'model adaptation':              'fine-tuning llms',
    'search & discovery':            'information retrieval',
    'workflow orchestration':        'mlops',
    'open-source ml libraries':      'machine learning',
    'indexing algorithms':           'faiss',
    'document processing':           'information retrieval'
}

# ── CAREER HISTORY CONSTANTS ──────────────────────────────────────
# Source: JD "do NOT want" section + "how to read between the lines"

COMPANY_CLASSIFICATION = {
    # FICTIONAL
    'Pied Piper':        ('fictional',   0.50),
    'Initech':           ('fictional',   0.50),
    'Wayne Enterprises': ('fictional',   0.50),
    'Acme Corp':         ('fictional',   0.50),
    'Stark Industries':  ('fictional',   0.50),
    'Hooli':             ('fictional',   0.50),
    'Globex Inc':        ('fictional',   0.50),
    'Dunder Mifflin':    ('fictional',   0.50),
    # CONSULTING 
    'Infosys':           ('consulting',  0.20),
    'Wipro':             ('consulting',  0.20),
    'TCS':               ('consulting',  0.20),
    'Capgemini':         ('consulting',  0.20),
    'HCL':               ('consulting',  0.20),
    'Accenture':         ('consulting',  0.20),
    'Cognizant':         ('consulting',  0.20),
    'Tech Mahindra':     ('consulting',  0.20),
    'Mindtree':          ('consulting',  0.20),
    'Mphasis':           ('consulting',  0.20),
    'Genpact AI':        ('consulting',  0.25),
    # PRODUCT 
    'Swiggy':            ('product',     0.75),
    'Razorpay':          ('product',     0.75),
    'CRED':              ('product',     0.75),
    'Zomato':            ('product',     0.75),
    'Flipkart':          ('product',     0.75),
    'PhonePe':           ('product',     0.75),
    'Meesho':            ('product',     0.70),
    'Nykaa':             ('product',     0.70),
    'InMobi':            ('product',     0.70),
    'PolicyBazaar':      ('product',     0.70),
    'Ola':               ('product',     0.70),
    'Zoho':              ('product',     0.70),
    'Dream11':           ('product',     0.70),
    'Paytm':             ('product',     0.70),
    'Freshworks':        ('product',     0.70),
    'upGrad':            ('product',     0.65),
    'Unacademy':         ('product',     0.65),
    "BYJU'S":            ('product',     0.65),
    'Vedantu':           ('product',     0.65),
    'PharmEasy':         ('product',     0.65),
    # AI STARTUPS
    'Yellow.ai':         ('ai_startup',  0.90),
    'Rephrase.ai':       ('ai_startup',  0.90),
    'Saarthi.ai':        ('ai_startup',  0.90),
    'Haptik':            ('ai_startup',  0.90),
    'Observe.AI':        ('ai_startup',  0.90),
    'Mad Street Den':    ('ai_startup',  0.90),
    'Krutrim':           ('ai_startup',  0.90),
    'Sarvam AI':         ('ai_startup',  0.90),
    'Aganitha':          ('ai_startup',  0.90),
    'Wysa':              ('ai_startup',  0.85),
    'Glance':            ('ai_startup',  0.85),
    'Niramai':           ('ai_startup',  0.85),
    'Locobuzz':          ('ai_startup',  0.85),
    'Verloop.io':        ('ai_startup',  0.85),
    # TOP GLOBAL TECH
    'Google':            ('top_tech',    1.00),
    'Meta':              ('top_tech',    1.00),
    'Amazon':            ('top_tech',    1.00),
    'Netflix':           ('top_tech',    1.00),
    'Apple':             ('top_tech',    0.95),
    'Microsoft':         ('top_tech',    0.95),
    'LinkedIn':          ('top_tech',    0.95),
    'Salesforce':        ('top_tech',    0.90),
    'Adobe':             ('top_tech',    0.90),
    'Uber':              ('top_tech',    0.90),
}

HIGH_FIT_TITLES = {
    'senior ai engineer', 'lead ai engineer',
    'staff machine learning engineer',
    'senior machine learning engineer',
    'senior nlp engineer', 'senior applied scientist',
    'senior ml engineer — search & ranking',
    'search engineer', 'applied ml engineer',
    'nlp engineer', 'machine learning engineer',
    'ai engineer', 'recommendation systems engineer',
    'senior data scientist'
}

GOOD_FIT_TITLES = {
    'ml engineer', 'ai research engineer', 'data scientist',
    'junior ml engineer', 'computer vision engineer',
    'ai specialist', 'senior software engineer (ml)'
}

ADJACENT_TITLES = {
    'analytics engineer', 'backend engineer', 'data engineer',
    'senior data engineer', 'data analyst',
    'senior software engineer', 'software engineer',
    'full stack developer', 'cloud engineer'
}

OWNERSHIP_VERBS = {
    'built', 'shipped', 'designed', 'developed', 'architected',
    'led', 'owned', 'created', 'deployed', 'launched',
    'implemented', 'engineered', 'delivered', 'wrote'
}

SYSTEM_TYPES_SAFE = {
    'recommendation', 'retrieval', 'embedding', 'embeddings',
    'vector', 'semantic', 'rerank', 're-rank', 'reranking',
    'recommender', 'retriever', 'indexing', 'similarity'
}

SYSTEM_PHRASES_AMBIGUOUS = {
    'search engine', 'search system', 'search infrastructure',
    'search index', 'search backend', 'search algorithm',
    'search functionality', 'vector search', 'semantic search',
    'hybrid search', 'search and discovery', 'search relevance',
    'ranking system', 'ranking algorithm', 'ranking model',
    'learning to rank', 'matching engine', 'matching algorithm',
    'index refresh', 'indexed documents', 'relevance score',
    'relevance ranking'
}

PRODUCTION_SIGNALS = {
    'production', 'users', 'scale', 'deployed', 'launched',
    'real', 'live', 'serving', 'million', 'billion',
    'latency', 'throughput', 'online', 'api', 'inference'
}

EVALUATION_SIGNALS = {
    'ndcg', 'mrr', 'map', 'precision', 'recall',
    'benchmark', 'evaluation', 'metric', 'experiment',
    'offline', 'feedback', 'quality'
}


WEIGHTS = {
    'career':       0.35,
    'skill':        0.25,
    'experience':   0.15,
    'availability': 0.15,
    'trust':        0.10
}

PEAK_LOW    = 4.3
PEAK_HIGH   = 8.0
BUFFER_LOW  = 4.3
BUFFER_HIGH = 4.88

TENURE_MIDPOINT  = 18.0
TENURE_STEEPNESS = 0.16


