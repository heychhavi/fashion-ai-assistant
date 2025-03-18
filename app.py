import streamlit as st
import os
import re
from dotenv import load_dotenv
import google.generativeai as genai
import PIL.Image
import pathlib
import json
import requests
from typing import Dict, List
from style_analyzer import StyleAnalyzer

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
SHOPIFY_STOREFRONT_TOKEN = os.getenv("SHOPIFY_STOREFRONT_TOKEN")

# Initialize session state for Twitter data
if 'twitter_data' not in st.session_state:
    st.session_state.twitter_data = None
if 'twitter_connected' not in st.session_state:
    st.session_state.twitter_connected = False

# Initialize models and style analyzer
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    # Set default parameters for the model
    generation_config = {
        "temperature": 0.9,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 2048,
    }
    
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]
    
    # Initialize models
    text_model = genai.GenerativeModel(
        model_name='gemini-1.5-pro',
        generation_config=generation_config,
        safety_settings=safety_settings
    )
    vision_model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        generation_config=generation_config,
        safety_settings=safety_settings
    )
    
    # Initialize style analyzer
    style_analyzer = StyleAnalyzer(vision_model)
else:
    st.error("GEMINI_API_KEY not found. Image analysis will be disabled.")

# Initialize Shopify client
shopify_client = None

# Load dummy products
try:
    with open(os.path.join(os.path.dirname(__file__), 'dummy_products.json'), 'r') as f:
        DUMMY_PRODUCTS = json.load(f)['products']
except Exception as e:
    print(f"Error loading dummy products: {str(e)}")
    DUMMY_PRODUCTS = []

# Shopify connector
class ShopifyConnector:
    def __init__(self, store_url: str, access_token: str = None, storefront_token: str = None):
        """Initialize Shopify connector with store credentials"""
        self.store_url = store_url
        self.access_token = access_token
        self.storefront_token = storefront_token
        self.base_url = f"https://{store_url}"
        self.products = DUMMY_PRODUCTS
    
    def search_products(self, query: str, limit: int = 3) -> List[Dict]:
        """Search for products in the local dummy products"""
        query_terms = query.lower().split()
        matching_products = []
        
        for product in self.products:
            # Convert product data to lowercase for comparison
            title_lower = product['title'].lower()
            desc_lower = product['description'].lower()
            tags_lower = [tag.lower() for tag in product['tags']]
            
            # Check if all query terms appear in either title, description, or tags
            if (all(term in title_lower for term in query_terms) or
                all(term in desc_lower for term in query_terms) or
                all(any(term in tag for tag in tags_lower) for term in query_terms)):
                
                matching_products.append({
                    "id": product['id'],
                    "title": product['title'],
                    "description": product['description'],
                    "handle": product['handle'],
                    "url": f"{self.base_url}/products/{product['handle']}",
                    "price": product['price'],
                    "image_url": product['image_url']
                })
                
                if len(matching_products) >= limit:
                    break
        
        return matching_products

    def get_product_recommendations(self, product_id: str, limit: int = 3) -> List[Dict]:
        """Get product recommendations based on a product ID"""
        try:
            # Find the source product
            source_product = next((p for p in self.products if p['id'] == product_id), None)
            if not source_product:
                return []
            
            # Get products with matching category or tags
            recommendations = []
            for product in self.products:
                if product['id'] == product_id:
                    continue
                
                # Check if categories match or if there are common tags
                if (product['category'] == source_product['category'] or 
                    any(tag in source_product['tags'] for tag in product['tags'])):
                    
                    recommendations.append({
                        "id": product['id'],
                        "title": product['title'],
                        "description": product['description'],
                        "handle": product['handle'],
                        "url": f"{self.base_url}/products/{product['handle']}",
                        "price": product['price'],
                        "image_url": product['image_url']
                    })
                    
                    if len(recommendations) >= limit:
                        break
            
            return recommendations
        except Exception as e:
            print(f"Error getting product recommendations: {str(e)}")
            return []

# Initialize Shopify client with dummy data
shopify_client = ShopifyConnector("example-store.myshopify.com")

def get_twitter_style_data(username):
    """Fetch user's fashion preferences and recent tweets from Twitter (simulated)"""
    try:
        simulated_data = {
            "user_info": {
                "username": username,
                "display_name": f"{username.capitalize()} Fashion",
                "bio": "Fashion enthusiast and style explorer"
            },
            "fashion_interests": ["casual", "streetwear", "vintage", "minimalist"],
            "color_preferences": ["black", "white", "earth tones", "pastels"],
            "recent_fashion_tweets": [
                {"text": "Loving the new sustainable fashion trends this season! #EcoFashion"},
                {"text": "Just picked up some amazing vintage pieces from the thrift store"},
                {"text": "Minimalist outfits are my go-to for busy days"}
            ]
        }
        
        return simulated_data
    except Exception as e:
        st.error(f"Error fetching Twitter data: {str(e)}")
        return None

def enhance_prompt_with_twitter_data(base_prompt, twitter_data):
    """Enhance the prompt with personalized information from Twitter"""
    if not twitter_data:
        return base_prompt
    
    fashion_interests = twitter_data.get("fashion_interests", [])
    color_preferences = twitter_data.get("color_preferences", [])
    recent_tweets = twitter_data.get("recent_fashion_tweets", [])
    
    twitter_context = []
    
    if fashion_interests:
        twitter_context.append(f"User is interested in these fashion styles: {', '.join(fashion_interests)}.")
    
    if color_preferences:
        twitter_context.append(f"User tends to prefer these colors: {', '.join(color_preferences)}.")
    
    if recent_tweets:
        tweet_texts = [tweet["text"] for tweet in recent_tweets[:3]]
        twitter_context.append("Based on recent Twitter activity, the user has mentioned: " + 
                             " | ".join(tweet_texts))
    
    if twitter_context:
        enhanced_prompt = f"{base_prompt}\n\nConsider the user's personal style preferences based on Twitter data: {' '.join(twitter_context)}"
        return enhanced_prompt
    
    return base_prompt

def extract_search_terms(recommendation_text):
    """Extract key fashion items from recommendation text"""
    # First try using regex pattern matching as a reliable fallback
    def extract_with_regex(text):
        patterns = [
            r'((?:black|white|navy|blue|red|gray|grey|brown)\s+(?:leather\s+)?(?:jacket|blazer|shirt|pants|trousers|dress|skirt|shoes|boots|heels|flats))',
            r'((?:oversized|fitted|tailored|classic|formal|casual)\s+(?:white|black|navy|blue)\s+(?:shirt|t-shirt|blouse|jacket|blazer|dress))',
            r'((?:leather|denim|wool|cotton)\s+(?:jacket|pants|shirt|dress|skirt))',
            r'([\w\s]+(?:jacket|shirt|pants|shoes|dress|hat|sweater|jeans|boots|sneakers|coat|blazer|flats|heels))'
        ]
        
        items = set()
        for pattern in patterns:
            matches = re.findall(pattern, recommendation_text.lower())
            items.update(match.strip() for match in matches if len(match.strip()) > 5)
        
        return list(items)
    
    # Try using Gemini API first
    try:
        prompt = f"""
        Extract only the main fashion items mentioned in this outfit recommendation. 
        Format as a comma-separated list of specific search terms. 
        Focus on individual items (like "black leather jacket" or "white sneakers"), 
        not styles or outfit concepts.
        
        RECOMMENDATION TEXT:
        {recommendation_text}
        
        ITEMS:
        """
        
        response = text_model.generate_content(prompt)
        response.resolve()
        
        search_terms = response.text.strip()
        terms = [term.strip() for term in search_terms.split(',') if term.strip()]
        
        # If Gemini returned valid terms, use them
        if terms:
            return terms
        
        # Otherwise fall back to regex
        return extract_with_regex(recommendation_text)
        
    except Exception as e:
        st.warning("Using fallback search term extraction due to API limits.")
        return extract_with_regex(recommendation_text)

def search_shopify_products(search_term, limit=3):
    """Search for products on Shopify"""
    if not shopify_client:
        return None
    
    try:
        products = shopify_client.search_products(search_term, limit)
        return products
    except Exception as e:
        st.error(f"Error searching Shopify: {str(e)}")
        return None

# Streamlit UI
st.title("Personalized Fashion Analysis & Recommendations")

# Sidebar for preferences and Twitter integration
with st.sidebar:
    # Style Preferences
    st.header("Style Preferences")
    
    # Occasion dropdown
    occasion = st.selectbox(
        "What's the occasion?",
        ["Business Meeting", "Casual Outing", "Date Night", "Formal Event", "Workout", "Other"]
    )
    st.session_state.occasion = occasion
    
    # Budget slider
    budget_range = st.slider(
        "Budget per outfit",
        min_value=50,
        max_value=1000,
        value=300,
        step=50,
        format="$%d"
    )
    st.session_state.budget = f"${budget_range}"
    
    # Color multiselect
    colors = st.multiselect(
        "Preferred colors",
        ["Black", "White", "Blue", "Red", "Green", "Yellow", "Purple", "Pink", "Brown", "Gray"],
        default=["Black", "Blue"]
    )
    st.session_state.colors = colors
    
    # Preferred brands
    brands = st.text_input(
        "Preferred brands (optional, comma-separated)",
        placeholder="e.g., Nike, Zara, H&M"
    )
    st.session_state.brands = brands
    
    # Special requirements
    requirements = st.text_area(
        "Any special requirements?",
        placeholder="e.g., comfortable shoes, weather-appropriate"
    )
    st.session_state.requirements = requirements
    
    st.divider()
    
    # Twitter Integration
    st.header("Twitter Integration")
    st.write("Connect your Twitter account for additional personalization")
    twitter_username = st.text_input("Twitter Username (without @)")
    
    if twitter_username and st.button("Connect Twitter"):
        twitter_data = get_twitter_style_data(twitter_username)
        if twitter_data:
            st.success(f"Connected to Twitter: @{twitter_username}")
            st.session_state.twitter_data = twitter_data
            st.session_state.twitter_connected = True
        else:
            st.error("Could not connect to Twitter. Please check your username.")
    
    if st.session_state.get("twitter_connected", False):
        st.info("Your recommendations will be personalized based on your Twitter activity.")

# Main content
st.header("Upload an Image for Analysis")
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Save uploaded file temporarily
    img_path = f"temp_{uploaded_file.name}"
    with open(img_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Display the uploaded image
    st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
    
    if st.button("Analyze Image"):
        with st.spinner("Analyzing image..."):
            try:
                # Get user preferences
                preferences = {
                    'occasion': st.session_state.get('occasion', ''),
                    'budget': st.session_state.get('budget', ''),
                    'colors': st.session_state.get('colors', []),
                    'brands': st.session_state.get('brands', ''),
                    'requirements': st.session_state.get('requirements', '')
                }
                
                # Get style analysis
                analysis_results = style_analyzer.analyze_image(
                    image_path=img_path,
                    preferences=preferences,
                    twitter_data=st.session_state.get("twitter_data")
                )
                
                # Display analysis results
                st.markdown("### Image Analysis")
                
                # Description
                st.markdown("#### Description")
                st.write(analysis_results['description'])
                
                # Style Category and Occasions
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### Style Category")
                    st.write(analysis_results['style_category'])
                with col2:
                    st.markdown("#### Suitable Occasions")
                    st.write(", ".join(analysis_results['suitable_occasions']))
                
                # Color Palette
                st.markdown("#### Color Palette")
                st.write(", ".join(analysis_results['color_palette']))
                
                # Identified Items
                st.markdown("#### Identified Items")
                for item in analysis_results['identified_items']:
                    st.write(f"- {item}")
                
                # Detailed Recommendations
                st.markdown("### Styling Recommendations")
                st.markdown(f"For a {st.session_state.get('occasion', '')} (Budget: {st.session_state.get('budget', '')})")
                
                # Outerwear
                if analysis_results['detailed_recommendations']['outerwear']['details']:
                    with st.expander("Outerwear", expanded=True):
                        st.markdown(f"**Budget: {analysis_results['detailed_recommendations']['outerwear']['budget']}**")
                        st.write(analysis_results['detailed_recommendations']['outerwear']['details'])
                
                # Top/Shirt
                if analysis_results['detailed_recommendations']['top']['details']:
                    with st.expander("Top/Shirt", expanded=True):
                        st.markdown(f"**Budget: {analysis_results['detailed_recommendations']['top']['budget']}**")
                        st.write(analysis_results['detailed_recommendations']['top']['details'])
                
                # Bottom
                if analysis_results['detailed_recommendations']['bottom']['details']:
                    with st.expander("Bottom", expanded=True):
                        st.markdown(f"**Budget: {analysis_results['detailed_recommendations']['bottom']['budget']}**")
                        st.write(analysis_results['detailed_recommendations']['bottom']['details'])
                
                # Shoes
                if analysis_results['detailed_recommendations']['shoes']['details']:
                    with st.expander("Shoes", expanded=True):
                        st.markdown(f"**Budget: {analysis_results['detailed_recommendations']['shoes']['budget']}**")
                        st.write(analysis_results['detailed_recommendations']['shoes']['details'])
                
                # Additional Recommendations
                if analysis_results['additional_recommendations']:
                    st.markdown("#### Additional Styling Tips")
                    for tip in analysis_results['additional_recommendations']:
                        st.write(f"- {tip}")
                
                # Product search section
                if shopify_client:
                    st.markdown("### Shop Similar Items")
                    
                    # Extract search terms from recommendations
                    search_terms = []
                    
                    # Process outerwear recommendations
                    if details := analysis_results['detailed_recommendations']['outerwear']['details']:
                        details_text = details.lower()
                        if 'navy' in details_text and 'blazer' in details_text:
                            search_terms.append('navy blue blazer')
                        elif 'black' in details_text and 'blazer' in details_text:
                            search_terms.append('classic black blazer')
                        elif 'blazer' in details_text:
                            search_terms.append('blazer')
                    
                    # Process top recommendations
                    if details := analysis_results['detailed_recommendations']['top']['details']:
                        details_text = details.lower()
                        if 'button-down' in details_text or ('white' in details_text and 'shirt' in details_text):
                            search_terms.append('white button-down shirt')
                        elif 'oversized' in details_text and 't-shirt' in details_text:
                            search_terms.append('oversized white t-shirt')
                    
                    # Process bottom recommendations
                    if details := analysis_results['detailed_recommendations']['bottom']['details']:
                        details_text = details.lower()
                        if 'navy' in details_text and 'trousers' in details_text:
                            search_terms.append('navy blue tailored trousers')
                        elif 'black' in details_text and 'leggings' in details_text:
                            search_terms.append('black leather leggings')
                    
                    # Process shoes recommendations
                    if details := analysis_results['detailed_recommendations']['shoes']['details']:
                        details_text = details.lower()
                        if 'flats' in details_text:
                            search_terms.append('black dress flats')
                        elif 'heels' in details_text:
                            search_terms.append('navy high heels')
                    
                    # If no specific matches found, add some default terms
                    if not search_terms:
                        search_terms = ['blazer', 'white button-down shirt', 'navy blue tailored trousers']
                    
                    with st.expander("View Search Terms"):
                        st.write(", ".join(search_terms))
                    
                    # Search for products
                    shown_products = set()  # Track shown products to avoid duplicates
                    for term in search_terms:
                        st.markdown(f"#### Products matching: {term}")
                        with st.spinner(f"Searching Shopify for {term}..."):
                            products = shopify_client.search_products(term)
                            
                            if products:
                                for product in products:
                                    # Skip if we've already shown this product
                                    if product['id'] in shown_products:
                                        continue
                                        
                                    shown_products.add(product['id'])
                                    col1, col2 = st.columns([1, 2])
                                    with col1:
                                        try:
                                            if product.get("image_url"):
                                                image_url = product["image_url"]
                                                if "unsplash.com" in image_url:
                                                    # Check if URL already has parameters
                                                    if "?" in image_url:
                                                        image_url = image_url.replace("auto=format&fit=crop&q=80", "w=300&h=400&fit=crop&q=80")
                                                    else:
                                                        image_url = f"{image_url}?w=300&h=400&fit=crop&q=80"
                                                try:
                                                    st.image(image_url, use_container_width=True)
                                                except:
                                                    st.info("Unable to load image")
                                            else:
                                                st.info("No image available")
                                        except Exception as e:
                                            st.info("Unable to load image")
                                            
                                    with col2:
                                        st.markdown(f"**{product['title']}**")
                                        if product.get("price"):
                                            st.write(f"Price: ${product['price']['amount']} {product['price']['currency']}")
                                        if product.get("url"):
                                            st.markdown(f"[View on Shopify]({product['url']})")
                            else:
                                st.info("No products found for this search term.")
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        # Remove temporary file after processing
        os.remove(img_path)