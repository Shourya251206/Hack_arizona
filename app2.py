import streamlit as st
import requests

# Configure page
st.set_page_config(page_title="Product Recommendations", layout="wide")

# Custom CSS with added microphone button styling
st.markdown("""
<style>
    .main {
        background-color: #f0f2f6;
    }
    .stButton button {
        background-color: #1e3d59 !important;
        color: white !important;
    }
    .stTextInput > div > div > input,
    .stNumberInput > div > input {
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
    .mic-button {
        background-color: #1e3d59;
        color: white;
        border: none;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        margin-top: 22px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        transition: all 0.3s;
    }
    .mic-button:hover {
        background-color: #ff6b6b;
        transform: scale(1.05);
    }
    .mic-icon {
        width: 20px;
        height: 20px;
    }
    .filter-container {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Add JavaScript for speech recognition
st.markdown("""
<script>
    document.addEventListener('DOMContentLoaded', function() {
        // Add event listener to microphone button after page loads
        setTimeout(function() {
            const micButton = document.querySelector('.mic-button');
            if (micButton) {
                micButton.addEventListener('click', startSpeechRecognition);
            }
        }, 1000);

        function startSpeechRecognition() {
            if (window.hasOwnProperty('webkitSpeechRecognition') || window.hasOwnProperty('SpeechRecognition')) {
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                const recognition = new SpeechRecognition();
                
                recognition.continuous = false;
                recognition.interimResults = false;
                recognition.lang = 'en-US';
                
                // Visual feedback
                const micButton = document.querySelector('.mic-button');
                if (micButton) {
                    micButton.innerHTML = '<svg class="mic-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 15.5C14.21 15.5 16 13.71 16 11.5V6C16 3.79 14.21 2 12 2C9.79 2 8 3.79 8 6V11.5C8 13.71 9.79 15.5 12 15.5Z" fill="white"/><path d="M4.03 12.5C3.76 12.5 3.5 12.26 3.5 12C3.5 7.52 7.02 3.5 12 3.5C16.98 3.5 20.5 7.52 20.5 12C20.5 12.28 20.24 12.5 19.97 12.5C19.7 12.5 19.5 12.26 19.5 12C19.5 8.14 16.36 4.5 12 4.5C7.64 4.5 4.5 8.14 4.5 12C4.5 12.26 4.3 12.5 4.03 12.5Z" fill="white"/><path d="M12 21.5C11.17 21.5 10.5 20.83 10.5 20V17.5C10.5 16.67 11.17 16 12 16C12.83 16 13.5 16.67 13.5 17.5V20C13.5 20.83 12.83 21.5 12 21.5Z" fill="white"/><path d="M17 22H7C6.59 22 6.25 21.66 6.25 21.25C6.25 20.84 6.59 20.5 7 20.5H17C17.41 20.5 17.75 20.84 17.75 21.25C17.75 21.66 17.41 22 17 22Z" fill="white"/></svg>';
                    micButton.style.backgroundColor = '#ff6b6b';
                }
                
                recognition.start();
                
                recognition.onresult = function(event) {
                    const result = event.results[0][0].transcript;
                    
                    // Find the search input and update it
                    const inputFields = document.querySelectorAll('input[type="text"]');
                    if (inputFields.length > 0) {
                        const inputField = inputFields[0];
                        inputField.value = result;
                        
                        // Dispatch events to notify Streamlit
                        inputField.dispatchEvent(new Event('input', { bubbles: true }));
                        inputField.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                    
                    // Reset mic button
                    if (micButton) {
                        micButton.innerHTML = '<svg class="mic-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 16C14.2091 16 16 14.2091 16 12V6C16 3.79086 14.2091 2 12 2C9.79086 2 8 3.79086 8 6V12C8 14.2091 9.79086 16 12 16Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M19 10V12C19 15.866 15.866 19 12 19C8.13401 19 5 15.866 5 12V10" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M12 19V22" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M8 22H16" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
                        micButton.style.backgroundColor = '#1e3d59';
                    }
                };
                
                recognition.onerror = function(event) {
                    console.error('Speech recognition error:', event.error);
                    // Reset mic button
                    if (micButton) {
                        micButton.innerHTML = '<svg class="mic-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 16C14.2091 16 16 14.2091 16 12V6C16 3.79086 14.2091 2 12 2C9.79086 2 8 3.79086 8 6V12C8 14.2091 9.79086 16 12 16Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M19 10V12C19 15.866 15.866 19 12 19C8.13401 19 5 15.866 5 12V10" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M12 19V22" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M8 22H16" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
                        micButton.style.backgroundColor = '#1e3d59';
                    }
                };
                
                recognition.onend = function() {
                    // Reset mic button when recognition ends
                    if (micButton) {
                        micButton.innerHTML = '<svg class="mic-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 16C14.2091 16 16 14.2091 16 12V6C16 3.79086 14.2091 2 12 2C9.79086 2 8 3.79086 8 6V12C8 14.2091 9.79086 16 12 16Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M19 10V12C19 15.866 15.866 19 12 19C8.13401 19 5 15.866 5 12V10" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M12 19V22" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M8 22H16" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
                        micButton.style.backgroundColor = '#1e3d59';
                    }
                };
            } else {
                alert("Your browser doesn't support speech recognition. Please try using Chrome.");
            }
        }
    });
</script>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 style='text-align: center; color: #1e3d59;'>Smart Product Recommendations</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #1e3d59;'>Find the perfect products based on your preferences</p>", unsafe_allow_html=True)

# Inputs
col1, col2, col3 = st.columns([3, 1, 2])
with col1:
    keywords = st.text_input("Enter keywords (e.g., 'running shoes')")
with col2:
    # Add microphone button
    st.markdown('<button class="mic-button"><svg class="mic-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 16C14.2091 16 16 14.2091 16 12V6C16 3.79086 14.2091 2 12 2C9.79086 2 8 3.79086 8 6V12C8 14.2091 9.79086 16 12 16Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M19 10V12C19 15.866 15.866 19 12 19C8.13401 19 5 15.866 5 12V10" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M12 19V22" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M8 22H16" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></button>', unsafe_allow_html=True)
with col3:
    price = st.number_input("Maximum price", min_value=0.0, value=100.0, step=5.0)  # Default to 100.0 instead of 0.0

# Filter section
st.markdown("<div class='filter-container'>", unsafe_allow_html=True)
filter_col1, filter_col2, filter_col3 = st.columns([1, 1, 1])
with filter_col1:
    stars = st.slider("Minimum star rating", min_value=0.0, max_value=5.0, value=0.0, step=0.5)
with filter_col2:
    sort_order = st.selectbox("Sort by Price", ["None", "Low to High", "High to Low"])
with filter_col3:
    search_button = st.button("Get Recommendations", use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# Backend call with mock data for testing
def get_recommendations(query_params):
    try:
        # Try to call the real API
        response = requests.post("http://127.0.0.1:8000/recommend", json=query_params)
        return response.json()
    except Exception as e:
        st.warning(f"Could not connect to the real API: {e}. Using mock data instead.")
        
        # Mock data for testing (in case the API is not running)
        mock_data = {
            "recommendations": [
                {
                    "title": f"{query_params.get('keywords', 'Product')} - Premium Edition",
                    "price": 79.99,
                    "rating": 4.5,
                    "category": "Electronics"
                },
                {
                    "title": f"{query_params.get('keywords', 'Product')} - Standard Model",
                    "price": 49.99,
                    "rating": 4.2,
                    "category": "Electronics"
                },
                {
                    "title": f"{query_params.get('keywords', 'Product')} - Budget Version",
                    "price": 29.99,
                    "rating": 3.8,
                    "category": "Electronics"
                }
            ]
        }
        
        # Apply sorting if requested
        if "sort" in query_params:
            if query_params["sort"] == "asc":
                mock_data["recommendations"].sort(key=lambda x: x["price"])
            elif query_params["sort"] == "desc":
                mock_data["recommendations"].sort(key=lambda x: x["price"], reverse=True)
        
        return mock_data

# Display results - Modified to always work even when API is unavailable
if search_button and keywords:
    query_params = {"keywords": keywords}
    
    # Price filter
    if price > 0:
        query_params["price"] = price
    
    # Stars filter
    if stars > 0:
        query_params["stars"] = stars
    
    # Add sorting parameter
    if sort_order == "Low to High":
        query_params["sort"] = "asc"
    elif sort_order == "High to Low":
        query_params["sort"] = "desc"

    with st.spinner("Finding the best products for you..."):
        result = get_recommendations(query_params)

    if result.get("recommendations"):
        st.markdown("<div class='recommendation-header'><h2 style='text-align: center;'>Recommended Products</h2></div>", unsafe_allow_html=True)

        # Add sorting info if used
        if sort_order != "None":
            st.markdown(f"<p style='text-align: center; margin-bottom: 20px;'>Products sorted by price: <strong>{sort_order}</strong></p>", unsafe_allow_html=True)

        for product in result["recommendations"]:
            st.markdown("<div class='product-card'>", unsafe_allow_html=True)
            cols = st.columns([1, 3])

            with cols[0]:
                img_url = product.get("imgURL", "")
                try:
                    if img_url and img_url.startswith("http"):
                        st.image(img_url, width=140)
                    else:
                        raise Exception("Invalid or missing image URL")
                except:
                    st.image("https://via.placeholder.com/150?text=No+Image", width=140)

            with cols[1]:
                title = product.get("title", "Unnamed Product")
                product_url = f"https://www.amazon.com/s?k={title.replace(' ', '+')}"

                st.markdown(f"<h3><a href='{product_url}' target='_blank' style='text-decoration:none; color:#1e3d59;'>{title}</a></h3>", unsafe_allow_html=True)
                st.markdown(f"<p><strong>Price:</strong> ${product.get('price', 0.0):.2f}</p>", unsafe_allow_html=True)
                if "rating" in product:
                    st.markdown(f"<p><strong>Rating:</strong> {'⭐' * int(float(product['rating']))} ({float(product['rating']):.1f})</p>", unsafe_allow_html=True)
                if "category" in product:
                    st.markdown(f"<p><strong>Category:</strong> {product['category']}</p>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No recommendations found. Try different criteria.")
else:
    st.info("Enter product keywords and click 'Get Recommendations'.")

# Footer
st.markdown("""
<div style='text-align: center; margin-top: 50px; padding: 20px; color: #666;'>
    <p>© 2025 Product Recommendation System | All Rights Reserved</p>
</div>
""", unsafe_allow_html=True)
