import requests
from typing import List, Dict, Optional

class ShopifyClient:
    def __init__(self, store_url: str, access_token: str):
        """Initialize the Shopify client with store URL and Admin API access token.
        
        Args:
            store_url (str): Your Shopify store URL (e.g., 'your-store.myshopify.com')
            access_token (str): Your Shopify Admin API access token
        
        Raises:
            ValueError: If store_url or access_token is invalid
        """
        # Validate inputs
        if not store_url:
            raise ValueError("store_url is required (e.g., 'your-store.myshopify.com')")
        if not access_token:
            raise ValueError("access_token is required. Get it from Shopify Admin > Apps > Develop apps")
            
        # Clean and validate store URL
        store_url = store_url.strip().lower()
        store_url = store_url.replace('https://', '').replace('http://', '').rstrip('/')
        
        # Ensure URL has myshopify.com domain
        if not store_url.endswith('myshopify.com'):
            raise ValueError(
                "Invalid store URL format. Must end with 'myshopify.com'. "
                "Example: 'your-store.myshopify.com'"
            )
            
        # Validate store name format
        store_name = store_url.replace('.myshopify.com', '')
        if not store_name or not store_name.replace('-', '').isalnum():
            raise ValueError(
                "Invalid store name in URL. Store name should only contain "
                "letters, numbers, and hyphens."
            )
            
        self.store_url = store_url
        self.access_token = access_token
        
        # Use the 2023-10 API version (confirmed working)
        self.graphql_url = f"https://{self.store_url}/api/2023-10/graphql.json"
        print(f"Initialized Shopify client with store URL: {self.store_url}")
        
    def search_products(self, query: str, limit: int = 3) -> List[Dict]:
        """Search for products using Shopify's Storefront API.
        
        Args:
            query (str): Search query. Use '*' to match all products.
            limit (int): Maximum number of products to return (default: 3)
            
        Returns:
            List[Dict]: List of matching products with their details
        """
        # Convert empty query to wildcard
        query = query.strip() or "*"
        print(f"Searching Shopify products with query: {query}, limit: {limit}")
        graphql_query = """
        query searchProducts($query: String!, $first: Int!) {
            products(first: $first, query: $query) {
                edges {
                    node {
                        id
                        title
                        handle
                        description
                        priceRangeV2 {
                            minVariantPrice {
                                amount
                                currencyCode
                            }
                        }
                        images(first: 1) {
                            edges {
                                node {
                                    originalSrc
                                }
                            }
                        }
                        variants(first: 1) {
                            edges {
                                node {
                                    id
                                    price
                                }
                            }
                        }
                        status
                    }
                }
            }
        }
        """
        
        # Prepare headers with the correct token format
        headers = {
            'Content-Type': 'application/json',
            'X-Shopify-Access-Token': self.access_token,
            'Accept': 'application/json'
        }
        
        # Prepare the GraphQL request
        request_data = {
            'query': graphql_query,
            'variables': {
                'query': query,
                'first': min(limit, 10)  # Limit to max 10 products per request
            }
        }
        
        try:
            # Make the API request
            response = requests.post(
                self.graphql_url,
                json=request_data,
                headers=headers,
                timeout=10  # Add timeout
            )
            
            # Print detailed response information for debugging
            print(f"Response status code: {response.status_code}")
            print(f"Response headers: {response.headers}")
            print(f"Response URL: {response.url}")
            
            try:
                data = response.json()
                print(f"Response data: {data}")
            except Exception as e:
                print(f"Failed to parse response as JSON: {str(e)}")
                print(f"Raw response text: {response.text}")
                raise
                
            response.raise_for_status()
            
            # Check for GraphQL-specific errors
            if 'errors' in data:
                error_msg = data['errors'][0]['message'] if data['errors'] else 'Unknown GraphQL error'
                raise Exception(f"GraphQL Error: {error_msg}")
                
            # Check if data and products exist
            if not data.get('data') or not data['data'].get('products'):
                raise Exception("No product data received from Shopify")
            
            # Process and format the products
            products = []
            for edge in data['data']['products']['edges']:
                node = edge['node']
                try:
                    product = {
                        'title': node['title'],
                        'url': f"https://{self.store_url}/products/{node['handle']}",
                        'price': {
                            'amount': node['priceRangeV2']['minVariantPrice']['amount'],
                            'currency': node['priceRangeV2']['minVariantPrice']['currencyCode']
                        },
                        'image': node['images']['edges'][0]['node']['originalSrc'] if node['images']['edges'] else None,
                        'variant_id': node['variants']['edges'][0]['node']['id'] if node['variants']['edges'] else None
                    }
                    products.append(product)
                except (KeyError, IndexError) as e:
                    print(f"Warning: Skipping malformed product data: {str(e)}")
                    continue
            
            return products
            
        except requests.exceptions.RequestException as e:
            print(f"Shopify API connection error: {str(e)}")
            raise Exception(f"Failed to connect to Shopify API: {str(e)}")
        except ValueError as e:
            print(f"Invalid data received from Shopify: {str(e)}")
            raise Exception(f"Invalid Shopify data: {str(e)}")
        except Exception as e:
            print(f"Unexpected error during Shopify search: {str(e)}")
            raise Exception(f"Failed to search Shopify products: {str(e)}")
