
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import re

class AmazonProductRecommender:
    def __init__(self, amazon_data):
        """
        Initialize the recommender with Amazon product data
        
        Parameters:
        -----------
        amazon_data: pandas DataFrame
            DataFrame containing Amazon product information with columns:
            - asin: Amazon Standard Identification Number (unique identifier)
            - title: product title
            - description: product description
            - category: product category/department
            - price: product price
            - rating: product rating (optional)
            - review_count: number of reviews (optional)
            - sales_rank: Amazon sales rank (optional)
        """
        self.product_data = amazon_data
        self.cosine_model = None
        self.cluster_model = None
        
    def preprocess_text(self, text):
        """Clean and normalize text data"""
        if isinstance(text, str):
            # Convert to lowercase and remove special characters
            text = re.sub(r'[^\w\s]', '', text.lower())
            return text
        return ""
        
    def build_cosine_model(self):
        """Build a cosine similarity model based on product descriptions and sales data"""
        # Combine title, category, description for better matching
        # Also include sales rank information if available
        text_features = []
        
        for _, row in self.product_data.iterrows():
            feature_text = f"{row.get('title', '')} {row.get('category', '')} {row.get('description', '')}"
            
            # Add sales information to enhance recommendations with popular items
            if 'sales_rank' in self.product_data.columns:
                # Convert sales rank to a descriptive term (better rank = more mentions)
                sales_rank = row.get('sales_rank', 0)
                if sales_rank > 0:  # Lower rank is better
                    popularity_level = min(10, max(1, int(1000000 / (sales_rank + 1000))))
                    popularity_text = ' '.join(['bestseller'] * popularity_level)
                    feature_text += f" {popularity_text}"
            
            # Add rating information if available
            if 'rating' in self.product_data.columns and 'review_count' in self.product_data.columns:
                rating = row.get('rating', 0)
                review_count = row.get('review_count', 0)
                
                if rating > 4.0 and review_count > 50:
                    # Highly rated products with many reviews get boosted
                    feature_text += " highly rated well reviewed popular recommended"
            
            text_features.append(feature_text)
        
        self.product_data['combined_features'] = text_features
        
        # Clean text
        self.product_data['combined_features'] = self.product_data['combined_features'].apply(self.preprocess_text)
        
        # Create TF-IDF vectors
        self.tfidf = TfidfVectorizer(stop_words='english')
        self.product_vectors = self.tfidf.fit_transform(self.product_data['combined_features'])
        
        print(f"Cosine similarity model built with {self.product_vectors.shape[0]} Amazon products")
        self.cosine_model = True
        
    def build_cluster_model(self, n_clusters=15):
        """Build a clustering model based on product features including sales data"""
        # Select numerical features
        numerical_features = ['price']
        
        # Add sales and review features if available
        if 'rating' in self.product_data.columns:
            numerical_features.append('rating')
        if 'review_count' in self.product_data.columns:
            numerical_features.append('review_count')
        if 'sales_rank' in self.product_data.columns:
            # Convert sales rank to a score (higher is better)
            self.product_data['sales_score'] = 1 / (self.product_data['sales_rank'] + 1)  # Avoid division by zero
            numerical_features.append('sales_score')
            
        # Select available numerical features
        available_features = [f for f in numerical_features if f in self.product_data.columns]
        features = self.product_data[available_features].copy()
        
        # One-hot encode categorical features
        if 'category' in self.product_data.columns:
            # Limit to top categories to avoid too many dimensions
            top_categories = self.product_data['category'].value_counts().head(20).index
            self.product_data['top_category'] = self.product_data['category'].apply(
                lambda x: x if x in top_categories else 'Other'
            )
            category_dummies = pd.get_dummies(self.product_data['top_category'], prefix='category')
            features = pd.concat([features, category_dummies], axis=1)
        
        # Handle missing values
        features = features.fillna(0)
        
        # Standardize features
        self.scaler = StandardScaler()
        scaled_features = self.scaler.fit_transform(features)
        
        # Train KMeans
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        self.product_data['cluster'] = self.kmeans.fit_predict(scaled_features)
        
        # Save feature columns for prediction
        self.feature_columns = features.columns
        
        print(f"Cluster model built with {n_clusters} clusters for Amazon products")
        self.cluster_model = True
    
    def get_recommendations_cosine(self, query, top_n=5):
        """
        Get recommendations using cosine similarity with Amazon data
        
        Parameters:
        -----------
        query: str
            User input query (e.g., "bestselling headphones under $100")
        top_n: int
            Number of recommendations to return
            
        Returns:
        --------
        list of dict
            List of recommended Amazon products
        """
        if not self.cosine_model:
            print("Cosine similarity model not built yet. Building now...")
            self.build_cosine_model()
            
        # Enhance query with Amazon-specific terms
        enhanced_query = query
        if 'bestseller' in query.lower() or 'best seller' in query.lower() or 'popular' in query.lower():
            enhanced_query += " bestseller popular top selling"
        if 'highly rated' in query.lower() or 'best rated' in query.lower() or 'top rated' in query.lower():
            enhanced_query += " highly rated recommended"
            
        # Transform query to TF-IDF vector
        query_vector = self.tfidf.transform([self.preprocess_text(enhanced_query)])
        
        # Calculate similarity
        similarities = cosine_similarity(query_vector, self.product_vectors).flatten()
        
        # Parse price filter from query
        max_price = float('inf')
        min_price = 0
        if 'under' in query.lower():
            match = re.search(r'under\s*\$?(\d+)', query.lower())
            if match:
                max_price = float(match.group(1))
        elif 'over' in query.lower():
            match = re.search(r'over\s*\$?(\d+)', query.lower())
            if match:
                min_price = float(match.group(1))
                
        # Apply price filter
        filtered_indices = [
            i for i, idx in enumerate(range(len(similarities)))
            if min_price <= self.product_data.iloc[idx]['price'] <= max_price
        ]
        
        # Apply sales filter if requested
        if 'bestseller' in query.lower() or 'best seller' in query.lower() or 'popular' in query.lower():
            if 'sales_rank' in self.product_data.columns:
                # Keep only top 20% products by sales rank
                sales_threshold = self.product_data['sales_rank'].quantile(0.2)
                filtered_indices = [
                    i for i in filtered_indices
                    if self.product_data.iloc[i]['sales_rank'] <= sales_threshold
                ]
        
        # Apply rating filter if requested
        if 'highly rated' in query.lower() or 'best rated' in query.lower() or 'top rated' in query.lower():
            if 'rating' in self.product_data.columns:
                # Keep only products with rating >= 4.0
                filtered_indices = [
                    i for i in filtered_indices
                    if self.product_data.iloc[i]['rating'] >= 4.0
                ]
        
        if filtered_indices:
            filtered_similarities = [(i, similarities[i]) for i in filtered_indices]
            # Sort by similarity
            sorted_indices = sorted(filtered_similarities, key=lambda x: x[1], reverse=True)
            
            # Get top N results
            top_indices = [idx for idx, _ in sorted_indices[:top_n]]
            recommendations = self.product_data.iloc[top_indices]
            
            # Format results
            result_fields = ['asin', 'title', 'category', 'price']
            # Add optional fields if available
            for field in ['rating', 'review_count', 'sales_rank']:
                if field in self.product_data.columns:
                    result_fields.append(field)
                    
            return recommendations[result_fields].to_dict('records')
        else:
            return []
    
    def get_recommendations_cluster(self, query, top_n=5):
        """
        Get recommendations using clustering with Amazon sales data
        
        Parameters:
        -----------
        query: str
            User input query (e.g., "bestselling headphones under $100")
        top_n: int
            Number of recommendations to return
            
        Returns:
        --------
        list of dict
            List of recommended Amazon products
        """
        if not self.cluster_model:
            print("Cluster model not built yet. Building now...")
            self.build_cluster_model()
            
        # Extract features from query
        category = None
        for cat in self.product_data['category'].unique():
            # Look for category mentions in the query
            if isinstance(cat, str) and cat.lower() in query.lower():
                category = cat
                break
                
        # Parse price constraints
        max_price = float('inf')
        if 'under' in query.lower():
            match = re.search(r'under\s*\$?(\d+)', query.lower())
            if match:
                max_price = float(match.group(1))
        
        # Create a feature vector for the query
        test_features = pd.DataFrame(columns=self.feature_columns)
        test_features.loc[0, 'price'] = max_price / 2  # Use half of max price as estimate
        
        # Add sales and rating preferences
        if 'sales_score' in self.feature_columns and ('bestseller' in query.lower() or 'popular' in query.lower()):
            # High sales score for popular items
            test_features.loc[0, 'sales_score'] = 0.9  # High value indicates popular item
            
        if 'rating' in self.feature_columns and ('highly rated' in query.lower() or 'top rated' in query.lower()):
            # High rating for well-rated items
            test_features.loc[0, 'rating'] = 4.5
            
        # Set category if mentioned
        if category:
            category_col = f'category_{category}'
            if category_col in self.feature_columns:
                test_features.loc[0, category_col] = 1
        
        # Fill NAs with 0
        test_features = test_features.fillna(0)
        
        # Ensure all feature columns exist
        for col in self.feature_columns:
            if col not in test_features.columns:
                test_features[col] = 0
                
        # Standardize the features
        scaled_test_features = self.scaler.transform(test_features[self.feature_columns])
        
        # Predict cluster
        cluster = self.kmeans.predict(scaled_test_features)[0]
        
        # Get products from the same cluster
        cluster_products = self.product_data[self.product_data['cluster'] == cluster].copy()
        
        # Apply price filter
        if max_price < float('inf'):
            cluster_products = cluster_products[cluster_products['price'] <= max_price]
            
        # Apply category filter if specified
        if category and 'category' in self.product_data.columns:
            category_products = cluster_products[cluster_products['category'] == category]
            if not category_products.empty:
                cluster_products = category_products
        
        # Apply sales filter if requested
        if 'bestseller' in query.lower() or 'best seller' in query.lower() or 'popular' in query.lower():
            if 'sales_rank' in cluster_products.columns:
                cluster_products = cluster_products.sort_values('sales_rank')
                
        # Apply rating filter if requested
        elif 'highly rated' in query.lower() or 'best rated' in query.lower():
            if 'rating' in cluster_products.columns:
                cluster_products = cluster_products.sort_values('rating', ascending=False)
        # Default sorting
        elif 'sales_rank' in cluster_products.columns:
            cluster_products = cluster_products.sort_values('sales_rank')
        
        # Get top recommendations
        recommendations = cluster_products.head(top_n)
        
        # Format results
        result_fields = ['asin', 'title', 'category', 'price']
        # Add optional fields if available
        for field in ['rating', 'review_count', 'sales_rank']:
            if field in recommendations.columns:
                result_fields.append(field)
                
        return recommendations[result_fields].to_dict('records')
    
    def get_recommendations(self, user_input, method='hybrid', top_n=5):
        """
        Get Amazon product recommendations based on user input
        
        Parameters:
        -----------
        user_input: str
            User query (e.g., "bestselling headphones under $100")
        method: str
            Recommendation method ('cosine', 'cluster', or 'hybrid')
        top_n: int
            Number of recommendations to return
            
        Returns:
        --------
        list of dict
            List of recommended Amazon products
        """
        if method == 'cosine':
            return self.get_recommendations_cosine(user_input, top_n)
        elif method == 'cluster':
            return self.get_recommendations_cluster(user_input, top_n)
        else:  # hybrid approach
            # Get recommendations from both methods
            cosine_recs = self.get_recommendations_cosine(user_input, top_n)
            cluster_recs = self.get_recommendations_cluster(user_input, top_n)
            
            # Combine and deduplicate
            all_recs = cosine_recs + cluster_recs
            unique_recs = []
            seen_ids = set()
            
            for rec in all_recs:
                if rec['asin'] not in seen_ids:
                    unique_recs.append(rec)
                    seen_ids.add(rec['asin'])
                    if len(unique_recs) >= top_n:
                        break
                        
            return unique_recs


# Example of how to load and prepare Amazon data
def load_amazon_data(file_path):
    """
    Load Amazon product data from CSV or JSON
    
    The expected format should include at minimum:
    - asin (Amazon Standard Identification Number)
    - title
    - price
    - category
    
    Optional but valuable fields:
    - description
    - rating
    - review_count
    - sales_rank
    """
    # Detect file type from extension
    if file_path.endswith('.csv'):
        data = pd.read_csv(file_path)
    elif file_path.endswith('.json'):
        data = pd.read_json(file_path, lines=True)  # For JSON Lines format
    else:
        raise ValueError("Unsupported file format. Use CSV or JSON.")
    
    # Ensure required columns exist
    required_cols = ['asin', 'title', 'price']
    for col in required_cols:
        if col not in data.columns:
            raise ValueError(f"Required column '{col}' not found in data")
    
    # Handle missing values
    data['title'] = data['title'].fillna('')
    data['description'] = data['description'].fillna('') if 'description' in data.columns else ''
    data['category'] = data['category'].fillna('Unknown') if 'category' in data.columns else 'Unknown'
    
    # Convert price to float if it's not already
    if data['price'].dtype == 'object':
        # Remove currency symbols and convert to float
        data['price'] = data['price'].astype(str).str.replace('[$,]', '', regex=True).astype(float)
    
    print(f"Loaded {len(data)} Amazon products")
    return data

# Example usage
if __name__ == "__main__":
    # Sample usage - replace with your actual data loading
    try:
        # Try to load the data from a file
        amazon_data = load_amazon_data('amazon_products.csv')
    except:
        # If file not found, create sample data for demonstration
        print("Sample file not found. Creating sample Amazon data for demonstration.")
        
        # Create sample data
        categories = ['Electronics', 'Books', 'Home & Kitchen', 'Clothing', 'Sports & Outdoors']
        n_samples = 1000
        
        amazon_data = pd.DataFrame({
            'asin': [f'B{i:09d}' for i in range(1, n_samples+1)],
            'title': [f"Amazon Product {i}" for i in range(1, n_samples+1)],
            'description': [f"This is a great product with many features." for _ in range(n_samples)],
            'category': np.random.choice(categories, n_samples),
            'price': np.random.uniform(10, 200, n_samples).round(2),
            'rating': np.random.uniform(1, 5, n_samples).round(1),
            'review_count': np.random.randint(0, 1000, n_samples),
            'sales_rank': np.random.randint(1, 100000, n_samples)
        })
    
    # Initialize recommender with Amazon data
    recommender = AmazonProductRecommender(amazon_data)
    
    # Build models
    recommender.build_cosine_model()
    recommender.build_cluster_model()
    
    # Test with sample queries
    test_queries = [
        "bestselling headphones under $100",
        "highly rated kitchen gadgets",
        "popular science fiction books",
        "running shoes under $80"
    ]
    
    # Demonstrate recommendations
    for query in test_queries:
        print(f"\nQuery: {query}")
        recommendations = recommender.get_recommendations(query, method='hybrid')
        
        print("\nRecommended Products:")
        for i, rec in enumerate(recommendations):
            print(f"{i+1}. {rec['title']} - ${rec['price']:.2f}")
            if 'rating' in rec:
                print(f"   Rating: {rec['rating']} ({rec.get('review_count', 0)} reviews)")
            if 'sales_rank' in rec:
                print(f"   Sales Rank: {rec['sales_rank']}")
            print(f"   Category: {rec['category']}")
            print(f"   ASIN: {rec['asin']}")
            print()