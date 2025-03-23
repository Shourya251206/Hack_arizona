import streamlit as st
import requests
from PIL import Image
import io
import pandas as pd
import base64

# FastAPI backend URL - Update if deployed elsewhere
API_URL = "http://127.0.0.1:8000/recommend"

# Configure page layout and theme colors
st.set_page_config(page_title="AI-Powered Product Recommendations", layout="wide")

# Custom CSS with cardinal red (#C41E3A) and navy blue (#003366) color scheme
st.markdown("""
<style>
    .main {
        background-color: #f0f2f6;
    }
    .stButton button {
        background-color: #003366 !important;
        color: white !important;
    }
    .stTextInput > div > div > input, .stSelectbox > div > div > div {
        border: 2px solid #003366;
    }
    h1, h2, h3 {
        color: white;
    }
    .product-card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        border-top: 4px solid #003366;
        border-bottom: 4px solid #C41E3A;
    }
    .product-card h3, .product-card p, .product-card strong {
        color: #003366;
    }
    .recommendation-header {
        background-color: #003366;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .filters {
        background-color: #003366;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .filters label {
        color: white !important;
    }
    .app-header {
        background-color: #003366;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border-bottom: 4px solid #C41E3A;
    }
    .stInfo {
        background-color: #003366;
    }
    .stInfo > div {
        color: white !important;
    }
    .footer {
        background-color: #003366;
        padding: 15px;
        border-radius: 10px;
        margin-top: 30px;
        color: white !important;
        border-top: 4px solid #C41E3A;
    }
    .notice-box {
        background-color: #003366;
        padding: 15px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
    }
    .mic-button {
        color: white;
        background-color: #C41E3A;
        border: none;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        font-size: 20px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-top: 4px;
    }
    .mic-button:hover {
        background-color: #A01A30;
    }
    .sorting-controls {
        background-color: white;
        padding: 10px 15px;
        border-radius: 5px;
        margin-bottom: 15px;
        border-left: 4px solid #C41E3A;
    }
</style>
""", unsafe_allow_html=True)

# JavaScript for speech recognition
speech_recognition_js = """
<script>
function toggleSpeechRecognition() {
    const micIcon = document.getElementById('mic-icon');
    const textInput = document.querySelector('.stTextInput input');
    
    if (!window.SpeechRecognition && !window.webkitSpeechRecognition) {
        alert('Speech recognition is not supported in your browser. Try Chrome or Edge.');
        return;
    }
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.continuous = false;
    recognition.interimResults = false;
    
    recognition.onstart = function() {
        micIcon.textContent = '⏹️';
        micIcon.style.backgroundColor = '#A01A30';
    };
    
    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        textInput.value = transcript;
        
        // Trigger an input event to update Streamlit
        const inputEvent = new Event('input', { bubbles: true });
        textInput.dispatchEvent(inputEvent);
    };
    
    recognition.onend = function() {
        micIcon.textContent = '🎤';
        micIcon.style.backgroundColor = '#C41E3A';
    };
    
    recognition.onerror = function(event) {
        console.error('Speech recognition error', event.error);
        micIcon.textContent = '🎤';
        micIcon.style.backgroundColor = '#C41E3A';
    };
    
    recognition.start();
}
</script>
"""

# App title and description in a custom header container
st.markdown("<div class='app-header'>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: white;'>AI-Powered Product Recommendation Engine</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: white;'>Enter your preferences to get personalized product recommendations</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# Add the speech recognition JavaScript to the page
st.markdown(speech_recognition_js, unsafe_allow_html=True)

# Container for the main content
main_container = st.container()

with main_container:
    # First row: Input and button
    st.markdown("<div class='filters'>", unsafe_allow_html=True)
    
    # Demo mode notice
    st.markdown("<div style='background-color: rgba(196, 30, 58, 0.2); padding: 10px; border-radius: 5px; margin-bottom: 15px;'><p style='color: white; margin: 0;'>⚠️ Running in demo mode with sample data</p></div>", unsafe_allow_html=True)
    
    # First row: Main query with microphone button
    col1, col2 = st.columns([3, 0.2])
    
    with col1:
        user_query = st.text_input("What are you looking for?", 
                                  placeholder="E.g., running shoes under $100, wireless earbuds with noise cancellation...")
    
    with col2:
        st.markdown("""
        <button id="mic-icon" class="mic-button" onclick="toggleSpeechRecognition()">🎤</button>
        """, unsafe_allow_html=True)
    
    # Second row: Additional filters
    col_size, col_price, col_brand = st.columns(3)
    
    with col_size:
        size = st.selectbox("Select size (optional):", 
                           ["Any", "XS", "S", "M", "L", "XL", "7", "8", "9", "10", "11"])
    
    with col_price:
        price_range = st.select_slider("Price range:", 
                                     options=["Any", "$0-$50", "$50-$100", "$100-$200", "$200+"])
    
    with col_brand:
        brand = st.selectbox("Brand preference (optional):", 
                           ["Any", "Nike", "Adidas", "Apple", "Samsung", "Sony", "Other"])
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Search button
    search_button = st.button("Get Recommendations", use_container_width=True)

    # Function to generate mock data based on user query and filters
    def generate_mock_data(query, size=None, price_range=None, brand=None):
        # Determine category based on query
        category = "Footwear"
        if any(term in query.lower() for term in ["electronics", "phone", "laptop", "computer", "headphone", "earbuds"]):
            category = "Electronics"
        elif any(term in query.lower() for term in ["shirt", "pants", "dress", "jacket", "clothing"]):
            category = "Clothing"
        
        # Adjust price based on filter
        price_map = {
            "Any": ["$89.99", "$94.99", "$99.99"],
            "$0-$50": ["$29.99", "$39.99", "$49.99"],
            "$50-$100": ["$59.99", "$79.99", "$99.99"],
            "$100-$200": ["$119.99", "$149.99", "$199.99"],
            "$200+": ["$229.99", "$299.99", "$349.99"]
        }
        prices = price_map.get(price_range, ["$89.99", "$94.99", "$99.99"])
        
        # Filter by brand if specified
        if brand != "Any" and brand != "Other":
            brands = [brand, brand, brand]
        else:
            if category == "Footwear":
                brands = ["Nike", "Adidas", "New Balance"]
            elif category == "Electronics":
                brands = ["Apple", "Samsung", "Sony"]
            else:
                brands = ["Gap", "H&M", "Zara"]
        
        # Generate descriptions
        descriptions = [
            f"High-quality {category.lower()} that matches your requirements perfectly with excellent customer reviews.",
            f"Great value option with slightly different features but still meeting your core requirements.",
            f"Premium version with additional features and longer warranty, still within your budget."
        ]
        
        # Generate product names
        product_names = [
            f"{brands[0]} {query.capitalize()} - Standard Model",
            f"{brands[1]} {query.capitalize()} - Value Model",
            f"{brands[2]} Premium {query.capitalize()}"
        ]
        
        # Generate mock data
        recommendations = []
        for i in range(3):
            # Convert price string to float for sorting
            price_value = float(prices[i].replace('$', ''))
            
            recommendations.append({
                "name": product_names[i],
                "price": prices[i],
                "price_value": price_value,  # Add numeric value for sorting
                "description": descriptions[i],
                "rating": 4.5 + (i * 0.2),  # 4.5, 4.7, 4.9
                "category": category,
                "image_url": "https://via.placeholder.com/150",
                "product_url": f"https://example.com/product{i+1}",
                "brand": brands[i]
            })
        
        return {"recommendations": recommendations}

    # Function to call the backend API with fallback to mock data
    def get_recommendations(query, size=None, price_range=None, brand=None):
        # Skip API call attempt and use mock data directly
        return generate_mock_data(query, size, price_range, brand)

    # Display recommendations when the button is clicked
    if search_button and user_query:
        with st.spinner('Finding the best products for you...'):
            result = get_recommendations(user_query, size, price_range, brand)
            
            if result.get("recommendations", []):
                st.markdown("<div class='recommendation-header'><h2 style='text-align: center; margin: 0;'>Recommended Products</h2></div>", unsafe_allow_html=True)
                
                # Add sorting options
                st.markdown("<div class='sorting-controls'>", unsafe_allow_html=True)
                col_sort_label, col_sort_option = st.columns([1, 3])
                
                with col_sort_label:
                    st.markdown("<p style='margin-top: 10px; font-weight: bold; color: #003366;'>Sort by:</p>", unsafe_allow_html=True)
                
                with col_sort_option:
                    sort_option = st.radio(
                        "",
                        options=["Recommended", "Price: Low to High", "Price: High to Low"],
                        horizontal=True,
                        label_visibility="collapsed"
                    )
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Sort the recommendations based on user selection
                recommendations = result["recommendations"]
                if sort_option == "Price: Low to High":
                    recommendations = sorted(recommendations, key=lambda x: x["price_value"])
                elif sort_option == "Price: High to Low":
                    recommendations = sorted(recommendations, key=lambda x: x["price_value"], reverse=True)
                
                # Display each recommendation in a card format
                for i, rec in enumerate(recommendations):
                    with st.container():
                        st.markdown(f"<div class='product-card'>", unsafe_allow_html=True)
                        cols = st.columns([1, 3])
                        
                        with cols[0]:
                            # Display image
                            st.image(rec["image_url"], width=150)
                            
                        with cols[1]:
                            # Product details
                            st.markdown(f"<h3 style='color: #003366;'>{rec['name']}</h3>", unsafe_allow_html=True)
                            st.markdown(f"<p><strong>Brand:</strong> {rec.get('brand', 'N/A')} | <strong>Category:</strong> {rec.get('category', 'N/A')}</p>", unsafe_allow_html=True)
                            st.markdown(f"<p><strong>Price:</strong> {rec['price']}</p>", unsafe_allow_html=True)
                            st.markdown(f"<p><strong>Rating:</strong> {'⭐' * int(rec['rating'])} ({rec['rating']})</p>", unsafe_allow_html=True)
                            st.markdown(f"<p>{rec['description']}</p>", unsafe_allow_html=True)
                            st.markdown(f"<a href='{rec['product_url']}' target='_blank' style='color: #003366; font-weight: bold;'>View Product</a>", unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='notice-box'>No products found matching your query. Try different search terms or filters.</div>", unsafe_allow_html=True)
    
    # Show a hint when the app first loads
    if not search_button:
        st.markdown("<div class='notice-box'>Enter your product preferences and use the filters above to get personalized recommendations. Click the microphone icon 🎤 to use speech input.</div>", unsafe_allow_html=True)

# Footer
st.markdown("""
<div class='footer'>
    <p style='text-align: center;'>© 2025 AI-Powered Product Recommendation System | All Rights Reserved</p>
</div>
""", unsafe_allow_html=True)
