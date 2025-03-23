import streamlit as st
import requests
from ml_module import get_recommendations

# Custom CSS for Styling
st.markdown(
    """
    <style>
    .stApp {
        background-color: #ffffff;
        color: #0d47a1;
    }
    .stTextInput, .stNumberInput, .stSlider {
        background-color: #f5f5f5;
        border-radius: 5px;
    }
    .stButton>button {
        background-color: #d32f2f;
        color: white;
        border-radius: 5px;
        font-weight: bold;
        padding: 8px 15px;
    }
    .stButton>button:hover {
        background-color: #b71c1c;
    }
    .product-card {
        background-color: #ffffff;
        padding: 15px;
        margin: 10px 0;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 255, 0.2);
        border: 2px solid #d32f2f;
    }
    .product-image {
        width: 120px;
        height: auto;
        border-radius: 5px;
        border: 2px solid #0d47a1;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Title
st.title("Product Recommendation System")

# User Input Fields
keywords = st.text_input("Enter keywords (e.g., 'running shoes')", "")
price = st.number_input("Maximum price (optional)", min_value=0.0, value=0.0, step=10.0)
stars = st.slider("Minimum star rating (optional)", min_value=0.0, max_value=5.0, value=0.0, step=0.5)

# Submit Button
if st.button("Get Recommendations"):
    # Prepare query parameters (only include non-default values)
    query_params = {}
    if keywords:
        query_params["keywords"] = keywords
    if price > 0:  # Only include if user sets a value greater than 0
        query_params["price"] = price
    if stars > 0:  # Only include if user sets a minimum
        query_params["stars"] = stars

    # Check if price is 0 before proceeding
    if price == 0:
        st.warning("You can't buy products for free! Please set a maximum price greater than 0.")
    elif query_params:  # Proceed only if there are valid parameters and price > 0
        try:
            # Send POST request to backend
            response = requests.post(
                "http://127.0.0.1:8000/recommend",
                json=query_params
            )
            if response.status_code == 200:
                data = response.json()
                if data["recommendations"]:
                    st.write("### Recommended Products:")
                    for product in data["recommendations"]:
                        st.markdown("----")
                        cols = st.columns([1, 3])  # Left for image, right for details

                        with cols[0]:
                            if product.get("imgURL"):
                                st.image(product["imgURL"], width=120, caption="", use_column_width=False, output_format='auto',)

                        with cols[1]:
                            title = product.get("title", "Unnamed Product")
                            product_url = f"https://www.amazon.com/s?k={title.replace(' ', '+')}"

                            if product_url and product_url.startswith("http"):
                                st.markdown(f'<a href="{product_url}" target="_blank" style="color: #d32f2f;"><strong>{title}</strong></a>', unsafe_allow_html=True)
                            else:
                                st.markdown(f"**{title}**")

                            st.write(f"<span style='color: #d32f2f; font-weight: bold;'>${product['price']:.2f}</span>", unsafe_allow_html=True)
                            if "rating" in product:
                                st.write(f"Rating: <span style='color: #0d47a1;'>{product['rating']} ★</span> ({product.get('review_count', 0)} reviews)", unsafe_allow_html=True)
                            if "category" in product:
                                st.write(f"Category: {product['category']}")
                else:
                    st.write("No recommendations found. Try adjusting your query.")
            else:
                st.error(f"Error fetching recommendations: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter at least one preference (keywords, price, or stars).")
