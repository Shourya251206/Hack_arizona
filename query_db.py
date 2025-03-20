import sqlite3

def get_products(query_params):
    """
    Query the products database based on user preferences.
    
    Args:
        query_params (dict): Dictionary with keys like 'keywords', 'price', 'stars', 
                             'reviews', 'category_id', 'isBestSeller', 'boughtInLastMonth'.
                             Example: {"keywords": "running shoes", "price": 100.0, "stars": 4.0}
    
    Returns:
        list: List of tuples, each tuple representing a product row.
    """
    # Connect to the database
    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()

    # Build the SQL query dynamically
    sql = "SELECT * FROM products WHERE 1=1"  # Base query
    params = []

    # Keywords in title (partial match)
    if "keywords" in query_params:
        sql += " AND title LIKE ?"
        params.append(f"%{query_params['keywords']}%")  # Wildcards for partial match

    # Price (max)
    if "price" in query_params:
        sql += " AND price <= ?"
        params.append(query_params["price"])

    # Stars (min)
    if "stars" in query_params:
        sql += " AND stars >= ?"
        params.append(query_params["stars"])

    # Reviews (min)
    if "reviews" in query_params:
        sql += " AND reviews >= ?"
        params.append(query_params["reviews"])

    # Category ID
    if "category_id" in query_params:
        sql += " AND category_id = ?"
        params.append(query_params["category_id"])

    # Best Seller (True/False, stored as 1/0)
    if "isBestSeller" in query_params:
        sql += " AND isBestSeller = ?"
        params.append(1 if query_params["isBestSeller"] else 0)

    # Bought in Last Month (min)
    if "boughtInLastMonth" in query_params:
        sql += " AND boughtInLastMonth >= ?"
        params.append(query_params["boughtInLastMonth"])

    # Execute the query
    cursor.execute(sql, params)
    results = cursor.fetchall()

    # Close the connection
    conn.close()

    return results

# Test the function
if __name__ == "__main__":
    # Example test cases
    test_cases = [
        {"keywords": "running shoes", "price": 100.0, "stars": 4.0},  # Running shoes under $100, 4+ stars
        {"keywords": "jacket", "reviews": 50},                        # Jackets with 50+ reviews
        {"category_id": 5, "isBestSeller": True},                    # Best sellers in category 5
        {"boughtInLastMonth": 100}                                   # Products bought 100+ times last month
    ]

    for test in test_cases:
        print(f"\nQuerying with: {test}")
        products = get_products(test)
        if products:
            for product in products:
                print(product)
        else:
            print("No matching products found.")