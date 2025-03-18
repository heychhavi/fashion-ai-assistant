import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Shopify credentials
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")

if not SHOPIFY_STORE_URL or not SHOPIFY_ACCESS_TOKEN:
    print("Error: Please set SHOPIFY_STORE_URL and SHOPIFY_ACCESS_TOKEN in your .env file")
    exit(1)

# Clean up URL
shopify_domain = SHOPIFY_STORE_URL
if shopify_domain.startswith(("http://", "https://")):
    shopify_domain = shopify_domain.split("//", 1)[1]
shopify_domain = shopify_domain.rstrip("/")

# API endpoint
api_url = f"https://{shopify_domain}/admin/api/2023-10/products.json"

# Headers
headers = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN
}

# Dummy products data
dummy_products = [
    {
        "product": {
            "title": "Classic White Sneakers",
            "body_html": "<p>Comfortable and stylish white sneakers perfect for everyday wear.</p>",
            "vendor": "FashionAI",
            "product_type": "Shoes",
            "variants": [
                {
                    "price": "89.99",
                    "sku": "SNEAK-WHITE-001"
                }
            ],
            "images": [
                {
                    "src": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&h=800&fit=crop"
                }
            ]
        }
    },
    {
        "product": {
            "title": "Black Leather Jacket",
            "body_html": "<p>Classic black leather jacket with modern styling.</p>",
            "vendor": "FashionAI",
            "product_type": "Outerwear",
            "variants": [
                {
                    "price": "199.99",
                    "sku": "JACK-BLACK-001"
                }
            ],
            "images": [
                {
                    "src": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=800&h=800&fit=crop"
                }
            ]
        }
    },
    {
        "product": {
            "title": "Blue Denim Jeans",
            "body_html": "<p>Classic fit blue denim jeans with comfortable stretch fabric.</p>",
            "vendor": "FashionAI",
            "product_type": "Pants",
            "variants": [
                {
                    "price": "79.99",
                    "sku": "JEAN-BLUE-001"
                }
            ],
            "images": [
                {
                    "src": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=800&h=800&fit=crop"
                }
            ]
        }
    },
    {
        "product": {
            "title": "White T-Shirt",
            "body_html": "<p>Essential white t-shirt made from soft cotton.</p>",
            "vendor": "FashionAI",
            "product_type": "Tops",
            "variants": [
                {
                    "price": "29.99",
                    "sku": "TSHR-WHITE-001"
                }
            ],
            "images": [
                {
                    "src": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=800&h=800&fit=crop"
                }
            ]
        }
    },
    {
        "product": {
            "title": "Black Dress",
            "body_html": "<p>Elegant black dress perfect for special occasions.</p>",
            "vendor": "FashionAI",
            "product_type": "Dresses",
            "variants": [
                {
                    "price": "129.99",
                    "sku": "DRES-BLACK-001"
                }
            ],
            "images": [
                {
                    "src": "https://images.unsplash.com/photo-1591369822096-ffd140ec948f?w=800&h=800&fit=crop"
                }
            ]
        }
    }
]

def create_products():
    print("Starting to create dummy products...")
    
    for product_data in dummy_products:
        try:
            response = requests.post(api_url, headers=headers, json=product_data)
            response.raise_for_status()
            
            product = response.json()["product"]
            print(f"Successfully created product: {product['title']}")
            print(f"Product URL: https://{shopify_domain}/products/{product['handle']}")
            print("-" * 50)
            
        except requests.exceptions.RequestException as e:
            print(f"Error creating product {product_data['product']['title']}: {str(e)}")
            print("-" * 50)

if __name__ == "__main__":
    create_products() 