import streamlit as st
import requests

# Title
st.title("Product Recommendation System")

# User Input Field
query = st.text_input("Enter your preference (e.g., 'running shoes under $100'): ")

# Submit Button
if st.button("Get Recommendations"):
    if query:
        try:
            # Replace 'http://127.0.0.1:5000/recommend' with the actual API endpoint from the Backend Developer
            response = requests.get(f"http://127.0.0.1:8000/recommend?query={query}")
            if response.status_code == 200:
                data = response.json()
                if data["recommendations"]:
                    st.write("### Recommended Products:")
                    for product in data["recommendations"]:
                        st.write(f"- **{product['name']}** - ${product['price']}")
                else:
                    st.write("No recommendations found. Try another query.")
            else:
                st.error("Error fetching recommendations from the backend.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a query before submitting.")
