import streamlit as st
import requests

# FastAPI backend URL
API_URL = "http://127.0.0.1:8000/recommend"  # Update if deployed elsewhere

# Streamlit UI
def main():
    st.title("AI-Powered Product Recommendation Engine")
    st.write("Enter your preferences to get personalized product recommendations.")

    # User input
    user_query = st.text_input("Search for products (e.g., 'running shoes under $100'):")
    size = st.selectbox("Select size (optional):", ["Any", "7", "8", "9", "10", "11"])  # Example sizes

    # Submit button
    if st.button("Get Recommendations"):
        if user_query:
            payload = {"query": user_query, "size": size if size != "Any" else None}
            response = requests.post(API_URL, json=payload)
            
            if response.status_code == 200:
                recommendations = response.json().get("recommendations", [])
                
                if recommendations:
                    st.subheader("Recommended Products:")
                    for product in recommendations:
                        st.write(f"- **{product['name']}** (Category: {product['category']}, Price: ${product['price']})")
                else:
                    st.write("No recommendations found. Try a different query!")
            else:
                st.error("Error fetching recommendations. Please check backend connection.")
        else:
            st.warning("Please enter a search query.")

if __name__ == "__main__":
    main()
