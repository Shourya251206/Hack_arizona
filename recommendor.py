import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import re
import random
import time
from collections import defaultdict

class QueryGenerator:
    """Generate realistic product search queries for testing recommendation systems"""
    
    def __init__(self, product_data):
        """
        Initialize with product data to extract realistic terms
        
        Parameters:
        -----------
        product_data: pandas DataFrame
            DataFrame containing product information
        """
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
        
    def extract_categories(self):
        """Extract unique product categories from data"""
        if 'category' in self.product_data.columns:
            # Get all unique categories
            all_categories = self.product_data['category'].dropna().unique().tolist()
            # Filter out overly long or complex categories
            categories = [cat for cat in all_categories if isinstance(cat, str) and len(cat.split()) < 4]
            return categories if categories else ["Electronics", "Books", "Home & Kitchen", "Clothing", "Sports"]
        return ["Electronics", "Books", "Home & Kitchen", "Clothing", "Sports"]
    
    def extract_brands(self):
        """Extract brand names from product titles"""
        common_brands = ["Amazon", "Apple", "Samsung", "Sony", "LG", "Bose", "Nike", "Adidas",
                         "Logitech", "Microsoft", "Dell", "HP", "Anker", "JBL", "Canon", "Nikon"]
        
        if 'title' in self.product_data.columns:
            # Try to extract brands from titles
            title_words = []
            for title in self.product_data['title'].dropna():
                if isinstance(title, str):
                    # Extract first word, which is often a brand
                    words = title.split()
                    if words and len(words[0]) > 2:
                        title_words.append(words[0])
            
            # Count word frequencies
            word_counts = defaultdict(int)
            for word in title_words:
                word_counts[word] += 1
            
            # Extract most common words as potential brands
            potential_brands = [word for word, count in word_counts.items() 
                              if count > 5 and word.isalpha()]
            
            return list(set(common_brands + potential_brands[:20]))
        return common_brands
    
    def generate_price_points(self):
        """Generate realistic price points based on data or defaults"""
        if 'price' in self.product_data.columns:
            prices = self.product_data['price'].dropna()
            if len(prices) > 0:
                # Generate price points based on actual data
                min_price = max(1, int(prices.min()))
                max_price = min(1000, int(prices.max()))
                
                # Create price brackets
                price_points = [
                    # Low price points
                    *range(min_price, min(50, max_price), 5),
                    # Medium price points
                    *range(50, min(200, max_price), 25),
                    # High price points
                    *range(200, min(max_price, 1000), 100)
                ]
                return sorted(list(set(price_points)))
        
        # Default price points if data unavailable
        return [10, 20, 25, 30, 50, 75, 100, 150, 200, 300, 500, 750, 1000]
    
    def build_product_mapping(self):
        """Build mapping of categories to products for more specific queries"""
        mapping = defaultdict(list)
        
        if 'category' in self.product_data.columns and 'asin' in self.product_data.columns:
            for _, row in self.product_data.iterrows():
                category = row.get('category')
                asin = row.get('asin')
                if category and asin:
                    mapping[category].append(asin)
                    
        return mapping
    
    def generate_query(self):
        """Generate a random realistic product search query"""
        template = random.choice(self.query_templates)
        
        # Category replacement
        if "{category}" in template:
            category = random.choice(self.categories)
            template = template.replace("{category}", category)
        
        # Price replacement
        if "{price}" in template:
            price = random.choice(self.price_points)
            template = template.replace("{price}", str(price))
            
        # Price range replacement
        if "{price_min}" in template and "{price_max}" in template:
            prices = sorted(random.sample(self.price_points, 2))
            template = template.replace("{price_min}", str(prices[0]))
            template = template.replace("{price_max}", str(prices[1]))
            
        # Adjective replacement
        if "{adjective}" in template:
            adjective = random.choice(self.adjectives)
            template = template.replace("{adjective}", adjective)
            
        # Color replacement
        if "{color}" in template:
            color = random.choice(self.colors)
            template = template.replace("{color}", color)
            
        # Usage replacement
        if "{usage}" in template:
            usage = random.choice(self.usages)
            template = template.replace("{usage}", usage)
            
        # Brand replacement
        if "{brand}" in template:
            brand = random.choice(self.brands)
            template = template.replace("{brand}", brand)
            
        # ASIN replacement (for product similarity queries)
        if "{asin}" in template:
            category = next((c for c in self.categories if c in template), random.choice(self.categories))
            asins = self.product_mapping.get(category, [])
            
            if asins:
                asin = random.choice(asins)
            else:
                # Fallback if no ASINs available for the category
                asin = f"B{random.randint(10000000, 99999999)}"
                
            template = template.replace("{asin}", asin)
            
        return template
    
    def generate_queries(self, n=100):
        """Generate multiple unique queries"""
        queries = set()
        while len(queries) < n:
            queries.add(self.generate_query())
        return list(queries)


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
        self.query_generator = QueryGenerator(amazon_data)
        
    # [Rest of the AmazonProductRecommender class stays the same]
    # ... [Include all previous methods from AmazonProductRecommender]
    
    def evaluate_model(self, n_queries=100, methods=['cosine', 'cluster', 'hybrid']):
        """
        Evaluate model performance across multiple random queries
        
        Parameters:
        -----------
        n_queries: int
            Number of random queries to generate and test
        methods: list
            List of recommendation methods to evaluate
            
        Returns:
        --------
        dict:
            Evaluation results
        """
        print(f"Evaluating recommendation model on {n_queries} random queries...")
        
        # Generate test queries
        test_queries = self.query_generator.generate_queries(n_queries)
        
        results = {
            'queries': test_queries,
            'recommendations': {},
            'stats': {}
        }
        
        # Track statistics
        for method in methods:
            results['recommendations'][method] = []
            results['stats'][method] = {
                'avg_recommendations': 0,
                'query_success_rate': 0,
                'avg_time': 0
            }
        
        # Run evaluation
        for method in methods:
            total_recs = 0
            successful_queries = 0
            total_time = 0
            
            for query in test_queries:
                start_time = time.time()
                recs = self.get_recommendations(query, method=method)
                elapsed_time = time.time() - start_time
                
                results['recommendations'][method].append({
                    'query': query,
                    'results': recs,
                    'time': elapsed_time
                })
                
                # Update statistics
                total_time += elapsed_time
                if recs:
                    successful_queries += 1
                    total_recs += len(recs)
            
            # Calculate averages
            results['stats'][method]['avg_recommendations'] = total_recs / n_queries
            results['stats'][method]['query_success_rate'] = successful_queries / n_queries
            results['stats'][method]['avg_time'] = total_time / n_queries
            
        return results
    
    def run_comprehensive_tests(self, queries_per_type=10):
        """
        Run comprehensive tests on different query types
        
        Parameters:
        -----------
        queries_per_type: int
            Number of queries to test per query type
            
        Returns:
        --------
        dict:
            Test results by query type
        """
        # Define query types to test
        query_types = {
            'basic': ["{category}"],
            'price_filtered': ["{category} under ${price}", "affordable {category}"],
            'bestseller': ["bestselling {category}", "popular {category}"],
            'rating': ["top rated {category}", "highly rated {category}", "{category} with good reviews"],
            'specific_features': ["{adjective} {category}", "{color} {category}"],
            'brand_specific': ["{brand} {category}", "alternatives to {brand} {category}"],
            'complex': ["bestselling {category} under ${price}", "{category} between ${price_min} and ${price_max}"]
        }
        
        results = {}
        
        # Override query templates temporarily for targeted testing
        original_templates = self.query_generator.query_templates
        
        for query_type, templates in query_types.items():
            print(f"Testing {query_type} queries...")
            
            # Set specific templates for this type
            self.query_generator.query_templates = templates
            
            # Generate and test queries
            type_queries = self.query_generator.generate_queries(queries_per_type)
            
            type_results = {
                'queries': type_queries,
                'cosine': [],
                'cluster': [],
                'hybrid': []
            }
            
            for query in type_queries:
                for method in ['cosine', 'cluster', 'hybrid']:
                    recs = self.get_recommendations(query, method=method)
                    type_results[method].append({
                        'query': query,
                        'count': len(recs),
                        'results': recs
                    })
            
            results[query_type] = type_results
            
        # Restore original templates
        self.query_generator.query_templates = original_templates
        
        return results
    
    def batch_test_and_save(self, output_file='recommendation_test_results.csv', n_queries=500):
        """
        Run batch tests on a large number of queries and save results to CSV
        
        Parameters:
        -----------
        output_file: str
            Path to save the results
        n_queries: int
            Number of queries to test
            
        Returns:
        --------
        DataFrame:
            Test results
        """
        print(f"Running batch test on {n_queries} queries...")
        
        # Generate queries
        test_queries = self.query_generator.generate_queries(n_queries)
        
        results = []
        
        for i, query in enumerate(test_queries):
            if i % 50 == 0:
                print(f"Processing query {i+1}/{n_queries}...")
                
            for method in ['cosine', 'cluster', 'hybrid']:
                start_time = time.time()
                recs = self.get_recommendations(query, method=method)
                elapsed_time = time.time() - start_time
                
                results.append({
                    'query': query,
                    'method': method,
                    'num_results': len(recs),
                    'processing_time': elapsed_time,
                    'success': len(recs) > 0
                })
                
                # Save detailed results for first recommendation
                if recs:
                    results[-1]['first_result_asin'] = recs[0].get('asin', '')
                    results[-1]['first_result_title'] = recs[0].get('title', '')
                    results[-1]['first_result_price'] = recs[0].get('price', 0)
                else:
                    results[-1]['first_result_asin'] = ''
                    results[-1]['first_result_title'] = ''
                    results[-1]['first_result_price'] = 0
        
        # Convert to DataFrame
        results_df = pd.DataFrame(results)
        
        # Save to CSV
        results_df.to_csv(output_file, index=False)
        print(f"Results saved to {output_file}")
        
        return results_df


# Example usage with extended testing
if __name__ == "__main__":
    # Try to load data or create sample data
    try:
        # Try to load the data from a file
        amazon_data = load_amazon_data('amazon_products.csv')
    except:
        # If file not found, create sample data for demonstration
        print("Sample file not found. Creating sample Amazon data for demonstration.")
        
        # Create more diverse sample data
        categories = ['Electronics', 'Books', 'Home & Kitchen', 'Clothing', 'Sports & Outdoors', 
                     'Beauty', 'Toys & Games', 'Grocery', 'Pet Supplies', 'Automotive']
        brands = ['Amazon', 'Apple', 'Samsung', 'Sony', 'LG', 'Bose', 'Nike', 'Adidas', 
                 'Logitech', 'Microsoft', 'Dell', 'HP', 'Anker', 'JBL', 'Canon', 'Nikon']
        
        n_samples = 2000
        
        # Create product names that include brands
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
    
    # Initialize recommender with Amazon data
    recommender = AmazonProductRecommender(amazon_data)
    
    # Build models
    print("Building recommendation models...")
    recommender.build_cosine_model()
    recommender.build_cluster_model()
    
    # Option 1: Generate and test a small set of queries
    print("\nTesting with generated queries:")
    generated_queries = recommender.query_generator.generate_queries(5)
    for query in generated_queries:
        print(f"\nQuery: {query}")
        recommendations = recommender.get_recommendations(query, method='hybrid')
        
        print("Recommendations:")
        for i, rec in enumerate(recommendations[:3]):  # Show only top 3 to save space
            print(f"{i+1}. {rec['title']} - ${rec['price']:.2f}")
    
    # Option 2: Run a comprehensive evaluation
    print("\nRunning comprehensive evaluation...")
    eval_results = recommender.evaluate_model(n_queries=20)
    
    # Print summary statistics
    print("\nModel Evaluation Summary:")
    for method, stats in eval_results['stats'].items():
        print(f"\nMethod: {method.upper()}")
        print(f"Average recommendations per query: {stats['avg_recommendations']:.2f}")
        print(f"Query success rate: {stats['query_success_rate']*100:.1f}%")
        print(f"Average processing time: {stats['avg_time']*1000:.2f}ms")
    
    # Option 3: Run query type tests
    print("\nRunning targeted query tests...")
    type_results = recommender.run_comprehensive_tests(queries_per_type=3)
    
    # Print query type success rates
    print("\nSuccess Rates by Query Type:")
    for query_type, results in type_results.items():
        success_rates = {}
        for method in ['cosine', 'cluster', 'hybrid']:
            successful = sum(1 for item in results[method] if item['count'] > 0)
            success_rates[method] = successful / len(results[method]) * 100
            
        print(f"{query_type.capitalize()} Queries:")
        for method, rate in success_rates.items():
            print(f"  - {method.capitalize()}: {rate:.1f}%")
    
    # Option 4: Run a large batch test and save results
    print("\nRunning large batch test...")
    batch_results = recommender.batch_test_and_save(n_queries=50)
    
    # Print batch test summary
    print("\nBatch Test Summary:")
    method_stats = batch_results.groupby('method').agg({
        'num_results': 'mean',
        'processing_time': 'mean',
        'success': 'mean'
    })
    print(method_stats)
