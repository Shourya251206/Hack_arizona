import streamlit as st
import requests

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
    if price > 0:  # Only include if user sets a value
        query_params["price"] = price
    if stars > 0:  # Only include if user sets a minimum
        query_params["stars"] = stars

    if query_params:
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
                        st.write(f"- **{product['title']}** - ${product['price']:.2f}")
                        if "rating" in product:
                            st.write(f"  Rating: {product['rating']} ★ ({product.get('review_count', 0)} reviews)")
                        if "category" in product:
                            st.write(f"  Category: {product['category']}")
                        st.write("---")
                else:
                    st.write("No recommendations found. Try adjusting your query.")
            else:
                st.error(f"Error fetching recommendations: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter at least one preference (keywords, price, or stars).")
