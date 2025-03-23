import streamlit as st
import requests

# Configure page
st.set_page_config(page_title="Product Recommendations", layout="wide")

# Custom CSS with enhanced microphone button styling
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
    .voice-container {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        text-align: center;
    }
    .transcript {
        margin-top: 10px;
        padding: 10px;
        background-color: #f8f9fa;
        border-radius: 5px;
        min-height: 30px;
    }
    .listening {
        color: #ff6b6b;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 style='text-align: center; color: #1e3d59;'>Smart Product Recommendations</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #1e3d59;'>Find the perfect products based on your preferences</p>", unsafe_allow_html=True)

# Initialize session state for voice input
if "voice_transcript" not in st.session_state:
    st.session_state.voice_transcript = ""

# Voice Input Component
st.markdown("<div class='voice-container'>", unsafe_allow_html=True)
st.subheader("Voice Search")

# Create a more sophisticated voice input component
voice_html = """
<div id="voiceSearchContainer">
    <button id="voiceButton" class="mic-button" style="margin: 0 auto; display: block;">
        <svg class="mic-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 16C14.2091 16 16 14.2091 16 12V6C16 3.79086 14.2091 2 12 2C9.79086 2 8 3.79086 8 6V12C8 14.2091 9.79086 16 12 16Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M19 10V12C19 15.866 15.866 19 12 19C8.13401 19 5 15.866 5 12V10" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 19V22" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M8 22H16" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
    </button>
    <p id="statusText" style="text-align: center; margin-top: 10px;">Click to speak</p>
    <div id="transcript" class="transcript">Your spoken words will appear here</div>
</div>

<script>
    // Set up speech recognition
    document.addEventListener('DOMContentLoaded', function() {
        const voiceButton = document.getElementById('voiceButton');
        const statusText = document.getElementById('statusText');
        const transcriptDiv = document.getElementById('transcript');
        let recognition;
        
        if (window.SpeechRecognition || window.webkitSpeechRecognition) {
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = 'en-US';
            recognition.interimResults = false;
            recognition.continuous = false;
            
            recognition.onstart = function() {
                statusText.innerHTML = "<span class='listening'>Listening...</span>";
                voiceButton.style.backgroundColor = '#ff6b6b';
            };
            
            recognition.onresult = function(event) {
                const transcript = event.results[0][0].transcript;
                transcriptDiv.textContent = transcript;
                
                // Send to Streamlit via session state
                window.parent.postMessage({
                    type: "streamlit:setComponentValue",
                    value: transcript
                }, "*");
            };
            
            recognition.onerror = function(event) {
                statusText.textContent = "Error: " + event.error;
                voiceButton.style.backgroundColor = '#1e3d59';
            };
            
            recognition.onend = function() {
                statusText.textContent = "Click to speak";
                voiceButton.style.backgroundColor = '#1e3d59';
            };
            
            voiceButton.addEventListener('click', function() {
                recognition.start();
            });
        } else {
            statusText.textContent = "Speech recognition not supported in this browser";
            voiceButton.disabled = true;
            voiceButton.style.backgroundColor = '#cccccc';
        }
    });
</script>
"""

import streamlit.components.v1 as components
voice_component = components.html(voice_html, height=150)

# Apply the voice result to the search field if available
if st.session_state.voice_transcript:
    st.markdown(f"<p>Recognized: <strong>{st.session_state.voice_transcript}</strong></p>", unsafe_allow_html=True)

# Button to use voice input
if st.button("Use Voice Input", key="use_voice"):
    if st.session_state.voice_transcript:
        keywords = st.session_state.voice_transcript
        st.session_state.keywords = keywords
    else:
        st.warning("Please speak something first")

st.markdown("</div>", unsafe_allow_html=True)

# Regular search inputs
st.subheader("Search Criteria")
col1, col2 = st.columns([3, 1])
with col1:
    # Use the voice transcript if available, otherwise empty
    default_keywords = st.session_state.get("keywords", "")
    keywords = st.text_input("Enter keywords (e.g., 'running shoes')", value=default_keywords)
with col2:
    price = st.number_input("Maximum price", min_value=0.0, value=100.0, step=5.0)

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

# Handle Streamlit component communication
from streamlit.components.v1.components import _Component
import json

class StreamlitComponentCallback:
    def __init__(self):
        self._component_callback = None
    
    def __call__(self, callback):
        self._component_callback = callback

# Process voice input and update session state
if voice_component:
    try:
        # This part will capture the result from the voice recognition
        transcript = voice_component
        if isinstance(transcript, str) and transcript:
            st.session_state.voice_transcript = transcript
    except:
        pass

# Display results
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
    st.info("Enter product keywords or use voice input and click 'Get Recommendations'.")

# Footer
st.markdown("""
<div style='text-align: center; margin-top: 50px; padding: 20px; color: #666;'>
    <p>© 2025 Product Recommendation System | All Rights Reserved</p>
</div>
""", unsafe_allow_html=True)
