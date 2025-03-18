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

# Initialize Gemini API
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    st.error("GEMINI_API_KEY not found. Image analysis will be disabled.")

# Initialize Shopify client
shopify_client = None

# Shopify connector
class ShopifyConnector:
    def __init__(self, store_url: str, access_token: str = None, storefront_token: str = None):
        """
        Initialize the Shopify connector with store credentials
        
        Args:
            store_url (str): The Shopify store URL (e.g., your-store.myshopify.com)
            access_token (str, optional): The Shopify Admin API access token
            storefront_token (str, optional): The Shopify Storefront API access token
        """
        self.store_url = store_url
        self.access_token = access_token
        self.storefront_token = storefront_token
        self.base_url = f"https://{store_url}"
        
        # Set up API URLs
        self.admin_api_url = f"{self.base_url}/admin/api/2023-10"
        self.storefront_api_url = f"{self.base_url}/api/2023-10/graphql.json"
        
        # Set up headers for Admin API if token provided
        self.admin_headers = None
        if access_token:
            self.admin_headers = {
                "Content-Type": "application/json",
                "X-Shopify-Access-Token": access_token
            }
        
        # Set up headers for Storefront API if token provided
        self.storefront_headers = None
        if storefront_token:
            self.storefront_headers = {
                "Content-Type": "application/json",
                "X-Shopify-Storefront-Access-Token": storefront_token
            }
    
    def search_products(self, query: str, limit: int = 3) -> List[Dict]:
        """
        Search for products in the Shopify store based on a query
        
        Args:
            query (str): The search query
            limit (int): Maximum number of products to return
            
        Returns:
            List[Dict]: List of product information dictionaries
        """
        products = []
        
        # Try Admin API first if we have a token
        if self.admin_headers:
            try:
                # Use Admin API to search products
                endpoint = f"{self.admin_api_url}/products.json"
                params = {
                    "limit": limit,
                    "title": query  # Search by title
                }
                
                response = requests.get(endpoint, headers=self.admin_headers, params=params)
                
                # If successful, process the response
                if response.status_code == 200:
                    data = response.json()
                    
                    if "products" in data and data["products"]:
                        for product in data["products"]:
                            product_info = {
                                "id": product.get("id"),
                                "title": product.get("title", "No title"),
                                "description": product.get("body_html", "No description"),
                                "handle": product.get("handle", ""),
                                "url": f"{self.base_url}/products/{product.get('handle', '')}",
                                "price": None,
                                "image_url": None
                            }
                            
                            # Get price from variants
                            if "variants" in product and product["variants"]:
                                variant = product["variants"][0]
                                price = variant.get("price")
                                if price:
                                    product_info["price"] = {
                                        "amount": price,
                                        "currency": "USD"  # Default to USD
                                    }
                            
                            # Get image URL
                            if "images" in product and product["images"]:
                                image = product["images"][0]
                                product_info["image_url"] = image.get("src")
                            
                            products.append(product_info)
                        
                        return products
                    
                # If Admin API fails or returns no products, continue to try Storefront API
            except Exception as e:
                print(f"Admin API search failed: {str(e)}")
        
        # Try Storefront API if we have a token and Admin API didn't work
        if self.storefront_headers and not products:
            try:
                # Use Storefront API with GraphQL
                graphql_query = """
                query searchProducts($query: String!, $first: Int!) {
                  products(query: $query, first: $first) {
                    edges {
                      node {
                        id
                        title
                        description
                        handle
                        onlineStoreUrl
                        priceRange {
                          minVariantPrice {
                            amount
                            currencyCode
                          }
                        }
                        images(first: 1) {
                          edges {
                            node {
                              url
                              altText
                            }
                          }
                        }
                      }
                    }
                  }
                }
                """
                
                # Variables for the query
                variables = {
                    "query": query,
                    "first": limit
                }
                
                # Make the request
                response = requests.post(
                    self.storefront_api_url,
                    headers=self.storefront_headers,
                    json={"query": graphql_query, "variables": variables}
                )
                
                # Check if the request was successful
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract product information
                    if "data" in data and "products" in data["data"] and "edges" in data["data"]["products"]:
                        for edge in data["data"]["products"]["edges"]:
                            node = edge["node"]
                            
                            # Extract price
                            price_info = None
                            if "priceRange" in node and "minVariantPrice" in node["priceRange"]:
                                price_data = node["priceRange"]["minVariantPrice"]
                                price_info = {
                                    "amount": price_data.get("amount", ""),
                                    "currency": price_data.get("currencyCode", "USD")
                                }
                            
                            # Extract image
                            image_url = None
                            if "images" in node and "edges" in node["images"] and len(node["images"]["edges"]) > 0:
                                image_data = node["images"]["edges"][0]["node"]
                                image_url = image_data.get("url", "")
                            
                            # Create product object
                            product = {
                                "id": node.get("id", ""),
                                "title": node.get("title", "No title"),
                                "description": node.get("description", ""),
                                "url": node.get("onlineStoreUrl", f"{self.base_url}/products/{node.get('handle', '')}"),
                                "price": price_info,
                                "image_url": image_url
                            }
                            
                            products.append(product)
            except Exception as e:
                print(f"Storefront API search failed: {str(e)}")
        
        return products
    
    def get_product_recommendations(self, product_id: str, limit: int = 3) -> List[Dict]:
        """
        Get product recommendations based on a product ID
        
        Args:
            product_id (str): The product ID to get recommendations for
            limit (int): Maximum number of recommendations to return
            
        Returns:
            List[Dict]: List of recommended product information dictionaries
        """
        try:
            # Try to get recommendations using Admin API first
            if self.admin_headers:
                try:
                    # For simplicity, just return other products from the store
                    # In a real implementation, you would use a recommendation algorithm
                    endpoint = f"{self.admin_api_url}/products.json"
                    params = {"limit": limit}
                    
                    response = requests.get(endpoint, headers=self.admin_headers, params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        recommendations = []
                        
                        if "products" in data and data["products"]:
                            for product in data["products"]:
                                # Skip the original product
                                if str(product.get("id")) == str(product_id):
                                    continue
                                    
                                product_info = {
                                    "id": product.get("id"),
                                    "title": product.get("title", "No title"),
                                    "description": product.get("body_html", "No description"),
                                    "handle": product.get("handle", ""),
                                    "url": f"{self.base_url}/products/{product.get('handle', '')}",
                                    "price": None,
                                    "image_url": None
                                }
                                
                                # Get price from variants
                                if "variants" in product and product["variants"]:
                                    variant = product["variants"][0]
                                    price = variant.get("price")
                                    if price:
                                        product_info["price"] = {
                                            "amount": price,
                                            "currency": "USD"  # Default to USD
                                        }
                                
                                # Get image URL
                                if "images" in product and product["images"]:
                                    image = product["images"][0]
                                    product_info["image_url"] = image.get("src")
                                
                                recommendations.append(product_info)
                                
                                if len(recommendations) >= limit:
                                    break
                            
                            return recommendations
                except Exception as e:
                    print(f"Admin API recommendations failed: {str(e)}")
            
            # If Admin API didn't work or we only have Storefront API access
            if self.storefront_headers:
                # Use Storefront API to get other products
                return self.search_products("", limit)
            
            return []
        except Exception as e:
            print(f"Error getting product recommendations: {str(e)}")
            return []
    
    def search_with_pinai(self, query: str, limit: int = 3) -> List[Dict]:
        """
        Search for products using PinAI data connector
        
        Args:
            query (str): The search query
            limit (int): Maximum number of products to return
            
        Returns:
            List[Dict]: List of product information dictionaries
        """
        if not self.pinai_client:
            return self.search_products(query, limit)
        
        try:
            # In a real implementation, we would use the PinAI data connector to search Shopify
            # For now, we'll simulate this by adding a small delay and then using the direct API
            st.info(f"Using PinAI data connector to search Shopify for: {query}")
            time.sleep(1)  # Simulate PinAI processing
            
            # Use the regular search function for now
            return self.search_products(query, limit)
        
        except Exception as e:
            st.error(f"Error using PinAI to search Shopify: {str(e)}")
            return []

# Initialize Shopify client if credentials are available
if SHOPIFY_STORE_URL and (SHOPIFY_ACCESS_TOKEN or SHOPIFY_STOREFRONT_TOKEN):
    try:
        # Clean up URL to get just the domain
        shopify_domain = SHOPIFY_STORE_URL
        if shopify_domain.startswith(("http://", "https://")):
            shopify_domain = shopify_domain.split("//", 1)[1]
        shopify_domain = shopify_domain.rstrip("/")
        
        shopify_client = ShopifyConnector(shopify_domain, SHOPIFY_ACCESS_TOKEN, SHOPIFY_STOREFRONT_TOKEN)
    except Exception as e:
        st.warning(f"Failed to initialize Shopify API: {str(e)}")
else:
    st.warning("Shopify API credentials not found. Shopify product search will be disabled.")

def get_twitter_style_data(username):
    """Fetch user's fashion preferences and recent tweets from Twitter (simulated)"""
    try:
        # Simulated response for demonstration
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
    
    # Extract style preferences from Twitter data
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
    # Create a specific prompt to identify key items
    prompt = f"""
    Extract only the main fashion items mentioned in this outfit recommendation. 
    Format as a comma-separated list of specific search terms. 
    Focus on individual items (like "black leather jacket" or "white sneakers"), 
    not styles or outfit concepts.
    
    RECOMMENDATION TEXT:
    {recommendation_text}
    
    ITEMS:
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        response.resolve()
        
        search_terms = response.text.strip()
        # Split by commas and clean up
        return [term.strip() for term in search_terms.split(',') if term.strip()]
    except Exception as e:
        st.error(f"Error extracting search terms: {str(e)}")
        # Fallback: try basic extraction with regex
        items = re.findall(r'([\w\s]+(?:jacket|shirt|pants|shoes|dress|hat|sweater|jeans|boots|sneakers|coat))', recommendation_text.lower())
        return [item.strip() for item in items if len(item.strip()) > 5]

def search_shopify_products(search_term, limit=3):
    """Search for products on Shopify"""
    if not shopify_client:
        return None
    
    try:
        # Search for products using Shopify API
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
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

    if st.button("Analyze Image"):
        with st.spinner("Analyzing image..."):
            try:
                # Read the image file as bytes
                image_data = pathlib.Path(img_path).read_bytes()
                
                # Get user preferences
                occasion = st.session_state.get('occasion', '')
                budget = st.session_state.get('budget', '')
                colors = st.session_state.get('colors', [])
                brands = st.session_state.get('brands', '')
                requirements = st.session_state.get('requirements', '')
                
                # Create base prompt
                base_prompt = f"""
                Analyze this fashion image and provide recommendations considering these preferences:
                - Occasion: {occasion}
                - Budget range: {budget}
                - Preferred colors: {', '.join(colors) if colors else 'Any'}
                - Preferred brands: {brands if brands else 'Any'}
                - Special requirements: {requirements if requirements else 'None'}
                
                Please provide:
                1. A detailed description of the outfit
                2. Style analysis (occasion, style category)
                3. Specific fashion items identified
                4. Styling recommendations that match the preferences above
                """

                # Enhance prompt with Twitter data if available
                if st.session_state.get("twitter_data"):
                    base_prompt = enhance_prompt_with_twitter_data(base_prompt, st.session_state.twitter_data)

                # Get Gemini's analysis
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(
                    contents=[
                        base_prompt,
                        {"mime_type": "image/jpeg", "data": image_data}
                    ]
                )
                response.resolve()
                
                # Display analysis
                st.markdown("### Image Analysis")
                st.write(response.text)
                
                # Extract search terms for product search
                search_terms = extract_search_terms(response.text)
                
                # Product search section
                if shopify_client and search_terms:
                    st.subheader("Similar Products on Shopify")
                    
                    with st.expander("View Search Terms"):
                        st.write(", ".join(search_terms))
                    
                    for term in search_terms[:3]:
                        st.markdown(f"#### Products matching: {term}")
                        with st.spinner(f"Searching Shopify for {term}..."):
                            products = shopify_client.search_products(term)
                            
                            if products:
                                for product in products:
                                    col1, col2 = st.columns([1, 2])
                                    with col1:
                                        if product.get("image_url"):
                                            st.image(product["image_url"], width=150)
                                    with col2:
                                        st.markdown(f"**{product['title']}**")
                                        if product.get("price"):
                                            st.write(f"Price: ${product['price']['amount']} {product['price']['currency']}")
                                        if product.get("url"):
                                            st.markdown(f"[View on Shopify]({product['url']})")
                            else:
                                st.info("No products found for this search term.")
                    
                    # Manual search option
                    st.markdown("### Search for Specific Items")
                    search_query = st.text_input("Enter your search term:")
                    if search_query and st.button("Search"):
                        with st.spinner(f"Searching Shopify for {search_query}..."):
                            products = shopify_client.search_products(search_query)
                            
                            if products:
                                for product in products:
                                    col1, col2 = st.columns([1, 2])
                                    with col1:
                                        if product.get("image_url"):
                                            st.image(product["image_url"], width=150)
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