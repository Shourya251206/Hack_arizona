import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import speech_recognition as sr
import nltk
from nltk.tokenize import word_tokenize
import time
import sqlite3
from collections import defaultdict

# Download NLTK data if needed
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class VoiceQueryHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        
    def listen_for_query(self):
        """Record audio from microphone and convert to text"""
        with sr.Microphone() as source:
            print("Listening for your query... Speak now")
            # Adjust for ambient noise
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            # Record audio
            audio = self.recognizer.listen(source)
            
        try:
            # Recognize speech using Google Speech Recognition
            query = self.recognizer.recognize_google(audio)
            print(f"You said: {query}")
            return query
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand your query. Please try again.")
            return None
        except sr.RequestError as e:
            print(f"Could not request results from speech recognition service; {e}")
            return None

class QueryGenerator:
    def __init__(self, product_data):
        self.product_data = product_data
        self.categories = self.extract_categories()
        self.price_points = self.generate_price_points()
        self.query_templates = [
            "{category}",
            "{category} under ${price}",
            "best {category}",
            "bestselling {category}",
            "popular {category}",
            "top rated {category}",
            "highly rated {category}",
            "{category} between ${price_min} and ${price_max}",
            "affordable {category}",
            "premium {category}",
            "{category} with good reviews",
            "{adjective} {category}",
            "{brand} {category}",
            "{color} {category}",
            "{category} for {usage}",
            "{category} similar to {asin}",
            "alternatives to {brand} {category}",
            "{category} under ${price} with good reviews",
            "bestselling {category} under ${price}",
            "highly rated {category} under ${price}"
        ]
        self.adjectives = [
            "comfortable", "durable", "lightweight", "waterproof", "wireless", 
            "portable", "smart", "budget", "professional", "compact", "foldable",
            "noise-cancelling", "ergonomic", "adjustable", "fast", "powerful"
        ]
        self.colors = [
            "black", "white", "red", "blue", "green", "gray", "silver", "gold",
            "pink", "purple", "brown", "orange", "yellow"
        ]
        self.usages = [
            "home", "office", "travel", "gaming", "sports", "outdoors", "kids",
            "beginners", "professionals", "everyday use", "streaming", "work",
            "school", "exercise", "hiking", "camping", "cooking", "cleaning"
        ]
        self.brands = self.extract_brands()
        self.product_mapping = self.build_product_mapping()
        
    # Other methods remain the same as in your original code
    def extract_categories(self):
        if 'category' in self.product_data.columns:
            all_categories = self.product_data['category'].dropna().unique().tolist()
            categories = [cat for cat in all_categories if isinstance(cat, str) and len(cat.split()) < 4]
            return categories if categories else ["Electronics", "Books", "Home & Kitchen", "Clothing", "Sports"]
        return ["Electronics", "Books", "Home & Kitchen", "Clothing", "Sports"]
    
    def extract_brands(self):
        common_brands = ["Amazon", "Apple", "Samsung", "Sony", "LG", "Bose", "Nike", "Adidas",
                         "Logitech", "Microsoft", "Dell", "HP", "Anker", "JBL", "Canon", "Nikon"]
        if 'title' in self.product_data.columns:
            title_words = []
            for title in self.product_data['title'].dropna():
                if isinstance(title, str):
                    words = title.split()
                    if words and len(words[0]) > 2:
                        title_words.append(words[0])
            word_counts = defaultdict(int)
            for word in title_words:
                word_counts[word] += 1
            potential_brands = [word for word, count in word_counts.items() 
                              if count > 5 and word.isalpha()]
            return list(set(common_brands + potential_brands[:20]))
        return common_brands
    
    def generate_price_points(self):
        if 'price' in self.product_data.columns:
            prices = self.product_data['price'].dropna()
            if len(prices) > 0:
                min_price = max(1, int(prices.min()))
                max_price = min(1000, int(prices.max()))
                price_points = [
                    *range(min_price, min(50, max_price), 5),
                    *range(50, min(200, max_price), 25),
                    *range(200, min(max_price, 1000), 100)
                ]
                return sorted(list(set(price_points)))
        return [10, 20, 25, 30, 50, 75, 100, 150, 200, 300, 500, 750, 1000]
    
    def build_product_mapping(self):
        mapping = defaultdict(list)
        if 'category' in self.product_data.columns and 'asin' in self.product_data.columns:
            for _, row in self.product_data.iterrows():
                category = row.get('category')
                asin = row.get('asin')
                if category and asin:
                    mapping[category].append(asin)
        return mapping
    
    def generate_query(self):
        # Implementation unchanged from original code
        template = random.choice(self.query_templates)
        if "{category}" in template:
            category = random.choice(self.categories)
            template = template.replace("{category}", category)
        if "{price}" in template:
            price = random.choice(self.price_points)
            template = template.replace("{price}", str(price))
        if "{price_min}" in template and "{price_max}" in template:
            prices = sorted(random.sample(self.price_points, 2))
            template = template.replace("{price_min}", str(prices[0]))
            template = template.replace("{price_max}", str(prices[1]))
        if "{adjective}" in template:
            adjective = random.choice(self.adjectives)
            template = template.replace("{adjective}", adjective)
        if "{color}" in template:
            color = random.choice(self.colors)
            template = template.replace("{color}", color)
        if "{usage}" in template:
            usage = random.choice(self.usages)
            template = template.replace("{usage}", usage)
        if "{brand}" in template:
            brand = random.choice(self.brands)
            template = template.replace("{brand}", brand)
        if "{asin}" in template:
            category = next((c for c in self.categories if c in template), random.choice(self.categories))
            asins = self.product_mapping.get(category, [])
            if asins:
                asin = random.choice(asins)
            else:
                asin = f"B{random.randint(10000000, 99999999)}"
            template = template.replace("{asin}", asin)
        return template
    
    def generate_queries(self, n=100):
        queries = set()
        while len(queries) < n:
            queries.add(self.generate_query())
        return list(queries)

class AmazonProductRecommender:
    def __init__(self, amazon_data, use_db=False, db_path=None):
        self.use_db = use_db
        self.db_path = db_path
        if use_db and db_path:
            self.product_data = self.load_from_db()
        else:
            self.product_data = amazon_data
        self.voice_handler = VoiceQueryHandler()
        self.cosine_model = None
        self.cluster_model = None
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.query_generator = QueryGenerator(self.product_data)
    
    def load_from_db(self):
        """Load product data from SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query("SELECT * FROM products", conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Database error: {e}")
            return pd.DataFrame()
    
    def preprocess_query(self, query):
        """Tokenize and normalize user query"""
        if not query:
            return ""
        tokens = word_tokenize(query.lower())
        return " ".join(tokens)

    def build_cosine_model(self):
        print("Building cosine similarity model...")
        if 'title' not in self.product_data.columns:
            raise ValueError("Product data must contain a 'title' column")

        # Combine title and description
        if 'description' in self.product_data.columns:
            self.product_data['text'] = (
                self.product_data['title'].fillna('') + " " +
                self.product_data['description'].fillna('')
            )
        else:
            self.product_data['text'] = self.product_data['title'].fillna('')

        # Create and store TF-IDF matrix
        self.tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.product_data['text'])
        self.cosine_model = cosine_similarity(self.tfidf_matrix)

    def build_cluster_model(self):
        print("Building cluster model...")
        if self.tfidf_matrix is None:
            self.build_cosine_model()
        
        # Standardize features
        scaler = StandardScaler(with_mean=False)
        scaled_features = scaler.fit_transform(self.tfidf_matrix)
        
        # Fit K-means
        self.cluster_model = KMeans(n_clusters=10, random_state=42)
        self.cluster_model.fit(scaled_features)
        self.product_data['cluster'] = self.cluster_model.labels_

    def get_recommendations(self, query, method='cosine', n=5):
        """Get product recommendations for a given query"""
        # Preprocess query
        processed_query = self.preprocess_query(query)
        
        if not processed_query:
            return []
            
        if method == 'cosine' and self.cosine_model is None:
            self.build_cosine_model()
        if method == 'cluster' and self.cluster_model is None:
            self.build_cluster_model()

        if method == 'cosine' or method == 'hybrid':
            # Transform query to TF-IDF space
            query_vec = self.tfidf_vectorizer.transform([processed_query])
            similarities = cosine_similarity(query_vec, self.tfidf_matrix)[0]
            
            # Get top similar products
            top_indices = similarities.argsort()[-n:][::-1]
            recommendations = []
            
            for idx in top_indices:
                if similarities[idx] > 0:  # Only include if there's some similarity
                    rec = {
                        'asin': self.product_data.iloc[idx]['asin'],
                        'title': self.product_data.iloc[idx]['title'],
                        'price': float(self.product_data.iloc[idx]['price'])
                    }
                    # Add image if available
                    if 'product_image' in self.product_data.columns:
                        rec['image'] = self.product_data.iloc[idx]['product_image']
                    recommendations.append(rec)
            
            if method == 'hybrid' and self.cluster_model is not None:
                # Add cluster-based filtering
                cluster_recs = self.get_recommendations(query, method='cluster', n=n)
                recommendations.extend(cluster_recs)
                # Remove duplicates and sort by relevance
                recommendations = sorted(list({r['asin']: r for r in recommendations}.values()),
                                      key=lambda x: similarities[self.product_data.index[self.product_data['asin'] == x['asin']].tolist()[0]], 
                                      reverse=True)[:n]
            
            return recommendations

        elif method == 'cluster':
            if self.cluster_model is None:
                return []
            
            # Transform query to TF-IDF space
            query_vec = self.tfidf_vectorizer.transform([processed_query])
            cluster_pred = self.cluster_model.predict(query_vec)[0]
            
            # Get products from the same cluster
            cluster_products = self.product_data[self.product_data['cluster'] == cluster_pred]
            return [{'asin': row['asin'], 'title': row['title'], 'price': float(row['price'])} 
                    for _, row in cluster_products.sample(min(n, len(cluster_products))).iterrows()]

        return []
    
    def get_voice_recommendations(self, method='hybrid', n=5):
        """Listen for voice query and return recommendations"""
        query = self.voice_handler.listen_for_query()
        if query:
            return self.get_recommendations(query, method=method, n=n)
        return []
    
    def interactive_voice_mode(self):
        """Run an interactive session with voice input"""
        print("=== Voice Recommendation Mode ===")
        print("Say 'exit' or 'quit' to end the session")
        
        while True:
            print("\nListening for your query...")
            query = self.voice_handler.listen_for_query()
            
            if not query:
                print("I didn't catch that. Please try again.")
                continue
                
            if query.lower() in ['exit', 'quit', 'stop', 'end']:
                print("Ending voice session. Goodbye!")
                break
                
            print(f"Finding recommendations for: '{query}'")
            recommendations = self.get_recommendations(query, method='hybrid')
            
            if recommendations:
                print(f"\nHere are {len(recommendations)} recommendations for you:")
                for i, rec in enumerate(recommendations):
                    print(f"{i+1}. {rec['title']} - ${rec['price']:.2f}")
            else:
                print("Sorry, I couldn't find any relevant products. Please try a different query.")
                
            time.sleep(1)  # Brief pause before listening again

# Example usage
if __name__ == "__main__":
    # Option 1: Use the sample data generation from your original code
    print("Creating sample Amazon data for demonstration.")
    categories = ['Electronics', 'Books', 'Home & Kitchen', 'Clothing', 'Sports & Outdoors', 
                  'Beauty', 'Toys & Games', 'Grocery', 'Pet Supplies', 'Automotive']
    brands = ['Amazon', 'Apple', 'Samsung', 'Sony', 'LG', 'Bose', 'Nike', 'Adidas', 
              'Logitech', 'Microsoft', 'Dell', 'HP', 'Anker', 'JBL', 'Canon', 'Nikon']
    
    n_samples = 2000
    import random
    
    titles = []
    for _ in range(n_samples):
        brand = random.choice(brands)
        category = random.choice(categories)
        product_type = random.choice(['Pro', 'Ultra', 'Max', 'Premium', 'Basic', 'Plus', 'Lite', ''])
        model = random.choice(['X', 'S', 'A', 'Z', 'M', 'Q', 'V']) + str(random.randint(1, 100))
        titles.append(f"{brand} {category.split()[0]} {product_type} {model}".strip())
    
    amazon_data = pd.DataFrame({
        'asin': [f'B{i:09d}' for i in range(1, n_samples+1)],
        'title': titles,
        'description': [f"This is a great product with many features." for _ in range(n_samples)],
        'category': np.random.choice(categories, n_samples),
        'price': np.random.uniform(10, 500, n_samples).round(2),
        'rating': np.random.uniform(1, 5, n_samples).round(1),
        'review_count': np.random.randint(0, 2000, n_samples),
        'sales_rank': np.random.randint(1, 500000, n_samples)
    })
    
    # Option 2: Use database
    # recommender = AmazonProductRecommender(None, use_db=True, db_path="products.db")
    
    # Use generated data
    recommender = AmazonProductRecommender(amazon_data)
    
    # Build models
    recommender.build_cosine_model()
    recommender.build_cluster_model()
    
    # Test with text query
    test_query = "wireless headphones under $100"
    print(f"\nTesting with text query: '{test_query}'")
    recs = recommender.get_recommendations(test_query, method='hybrid')
    print(f"Found {len(recs)} recommendations")
    for i, rec in enumerate(recs[:3]):
        print(f"{i+1}. {rec['title']} - ${rec['price']:.2f}")
    
    # Try voice mode (uncomment to test with a microphone)
    print("\nWould you like to try voice mode? (y/n)")
    response = input()
    if response.lower() == 'y':
        recommender.interactive_voice_mode()
    else:
        print("Voice mode skipped. Exiting.")
