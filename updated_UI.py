import streamlit as st
import requests
from PIL import Image
import io
import pandas as pd

# Configure page layout and theme colors
st.set_page_config(page_title="Product Recommendations", layout="wide")

# Custom CSS for the blue, white, and red theme
st.markdown("""
<style>
    .main {
        background-color: #f0f2f6;
    }
    .stButton button {
        background-color: #1e3d59 !important;
        color: white !important;
    }
    .stTextInput > div > div > input {
        border: 2px solid #1e3d59;
    }
    h1, h2, h3 {
        color: #1e3d59;
    }
    .product-card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        border-top: 4px solid #1e3d59;
        border-bottom: 4px solid #ff6b6b;
    }
    .recommendation-header {
        background-color: #1e3d59;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.markdown("<h1 style='text-align: center; color: #1e3d59;'>Smart Product Recommendations</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #1e3d59;'>Find the perfect products based on your preferences</p>", unsafe_allow_html=True)

# Container for the main content
main_container = st.container()

with main_container:
    # First row: Input and button
    col1, col2 = st.columns([3, 1])
    
    with col1:
        user_query = st.text_input("What are you looking for?", 
                                  placeholder="E.g., running shoes under $100, wireless earbuds with noise cancellation...")
    
    with col2:
        search_button = st.button("Find Products", use_container_width=True)

    # Function to call the backend API
    def get_recommendations(query):
        # In a real app, this would call your backend API
        # For demo purposes, we'll generate mock data
        try:
            # Replace with actual API endpoint
            # response = requests.post("http://your-backend-api/recommendations", 
            #                        json={"query": query})
            # return response.json()
            
            # Mock data for demonstration
            return {
                "recommendations": [
                    {
                        "name": f"Product for {query} - Option 1",
                        "price": "$89.99",
                        "description": "High-quality product that matches your requirements perfectly with excellent customer reviews.",
                        "rating": 4.7,
                        "image_url": "https://via.placeholder.com/150",
                        "product_url": "https://example.com/product1"
                    },
                    {
                        "name": f"Product for {query} - Option 2",
                        "price": "$94.99",
                        "description": "Great value option with slightly different features but still meeting your core requirements.",
                        "rating": 4.5,
                        "image_url": "https://via.placeholder.com/150",
                        "product_url": "https://example.com/product2"
                    },
                    {
                        "name": f"Premium {query}",
                        "price": "$99.99",
                        "description": "Premium version with additional features and longer warranty, still within your budget.",
                        "rating": 4.8,
                        "image_url": "https://via.placeholder.com/150",
                        "product_url": "https://example.com/product3"
                    }
                ]
            }
        except Exception as e:
            st.error(f"Error fetching recommendations: {e}")
            return {"recommendations": []}

    # Display recommendations when the button is clicked
    if search_button and user_query:
        with st.spinner('Finding the best products for you...'):
            result = get_recommendations(user_query)
            
            if result["recommendations"]:
                st.markdown("<div class='recommendation-header'><h2 style='text-align: center; margin: 0;'>Recommended Products</h2></div>", unsafe_allow_html=True)
                
                # Display each recommendation in a card format
                for i, rec in enumerate(result["recommendations"]):
                    with st.container():
                        st.markdown(f"<div class='product-card'>", unsafe_allow_html=True)
                        cols = st.columns([1, 3])
                        
                        with cols[0]:
                            # Display image
                            st.image(rec["image_url"], width=150)
                            
                        with cols[1]:
                            # Product details
                            st.markdown(f"<h3>{rec['name']}</h3>", unsafe_allow_html=True)
                            st.markdown(f"<p><strong>Price:</strong> {rec['price']}</p>", unsafe_allow_html=True)
                            st.markdown(f"<p><strong>Rating:</strong> {'⭐' * int(rec['rating'])} ({rec['rating']})</p>", unsafe_allow_html=True)
                            st.markdown(f"<p>{rec['description']}</p>", unsafe_allow_html=True)
                            st.markdown(f"<a href='{rec['product_url']}' target='_blank'>View Product</a>", unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("No products found matching your query. Try a different search term.")
    
    # Show a hint when the app first loads
    if not search_button:
        st.info("Enter your product preferences above and click 'Find Products' to get personalized recommendations.")

# Footer
st.markdown("""
<div style='text-align: center; margin-top: 50px; padding: 20px; color: #666;'>
    <p>© 2025 Product Recommendation System | All Rights Reserved</p>
</div>
""", unsafe_allow_html=True)
