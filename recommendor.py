import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3
import re

class ProductRecommender:
    def __init__(self):
        """Initialize the recommender with product data from SQLite."""
        self.product_data = self._load_data()
        self.tfidf = None
        self.product_vectors = None
        self.build_cosine_model()

    def _load_data(self):
        """Load product data from SQLite database."""
        conn = sqlite3.connect("products.db")
        query = "SELECT asin, title, price, category, description FROM products"
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Handle missing values
        df['title'] = df['title'].fillna('')
        df['description'] = df['description'].fillna('')
        df['category'] = df['category'].fillna('Unknown')
        
        print(f"Loaded {len(df)} products from SQLite")
        return df

    def preprocess_text(self, text):
        """Clean and normalize text data."""
        if isinstance(text, str):
            text = re.sub(r'[^\w\s]', '', text.lower())
            return text
        return ""

    def build_cosine_model(self):
        """Build a cosine similarity model based on product text features."""
        # Combine title, category, and description
        self.product_data['combined_features'] = (
            self.product_data['title'] + " " +
            self.product_data['category'] + " " +
            self.product_data['description']
        ).apply(self.preprocess_text)

        # Create TF-IDF vectors
        self.tfidf = TfidfVectorizer(stop_words='english')
        self.product_vectors = self.tfidf.fit_transform(self.product_data['combined_features'])
        
        print(f"Cosine similarity model built with {self.product_vectors.shape[0]} products")
    
    def parse_query(self, query: str) -> tuple:
        """Extract key info from user query (e.g., price limit, category)."""
        query = query.lower().strip()
        max_price = float('inf')
        
        # Extract price (e.g., "under $100", "less than 50")
        price_match = re.search(r"(under|less than)\s*\$?(\d+\.?\d*)", query)
        if price_match:
            max_price = float(price_match.group(2))
            query = re.sub(r"(under|less than)\s*\$?\d+\.?\d*", "", query).strip()
        
        return query, max_price

    def get_recommendations(self, user_input: str, top_n: int = 3) -> list:
        """
        Get product recommendations based on user input using cosine similarity.
        
        Parameters:
        -----------
        user_input: str
            User query (e.g., "running shoes under $100")
        top_n: int
            Number of recommendations to return
            
        Returns:
        --------
        list
            List of recommended product ASINs (or names if ASIN not available)
        """
        # Parse query
        query_text, max_price = self.parse_query(user_input)
        
        # Vectorize query
        query_vector = self.tfidf.transform([self.preprocess_text(query_text)])
        
        # Compute cosine similarity
        similarities = cosine_similarity(query_vector, self.product_vectors).flatten()
        
        # Filter by price
        filtered_indices = [
            i for i in range(len(similarities))
            if self.product_data.iloc[i]['price'] <= max_price
        ]
        
        if not filtered_indices:
            return []
        
        # Sort by similarity within filtered indices
        filtered_similarities = [(i, similarities[i]) for i in filtered_indices]
        sorted_indices = [idx for idx, _ in sorted(filtered_similarities, key=lambda x: x[1], reverse=True)]
        
        # Get top N
        top_indices = sorted_indices[:top_n]
        recommendations = self.product_data.iloc[top_indices]
        
        # Return ASINs (or names if ASIN is missing)
        if 'asin' in recommendations.columns:
            return recommendations['asin'].tolist()
        return recommendations['title'].tolist()

# Singleton instance for backend integration
recommender = ProductRecommender()

def get_recommendations(user_input: str) -> list:
    """Wrapper function for backend compatibility."""
    return recommender.get_recommendations(user_input)

if __name__ == "__main__":
    # Test with sample queries
    test_queries = [
        "running shoes under $100",
        "stylish headphones",
        "cheap kitchen gadgets",
        "bestselling books under $20",
        "comfortable sneakers less than 50"
    ]
    for query in test_queries:
        print(f"Query: {query}")
        print(f"Recommendations: {get_recommendations(query)}")
        print("-" * 50)


   
  
     
