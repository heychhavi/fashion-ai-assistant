# Fashion AI Assistant

An AI-powered fashion assistant that provides personalized style analysis and recommendations using computer vision and natural language processing.

## Features

- Image-based style analysis
- Personalized outfit recommendations
- Product matching with Shopify integration
- Budget-aware suggestions
- Twitter integration for enhanced personalization
- Detailed style breakdowns by category
- Smart product search and recommendations

## Requirements

- Python 3.8+
- Streamlit
- Google Generative AI (Gemini)
- PIL (Python Imaging Library)
- python-dotenv

## Setup

1. Clone the repository:
```bash
git clone https://github.com/heychhavi/fashion-ai-assistant.git
cd fashion-ai-assistant
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:
```
GEMINI_API_KEY=your_gemini_api_key
SHOPIFY_STORE_URL=your_shopify_store_url
SHOPIFY_ACCESS_TOKEN=your_shopify_access_token
SHOPIFY_STOREFRONT_TOKEN=your_shopify_storefront_token
```

4. Run the application:
```bash
streamlit run app.py
```

## Project Structure

- `app.py`: Main Streamlit application
- `style_analyzer.py`: Style analysis and recommendation engine
- `dummy_products.json`: Sample product database
- `requirements.txt`: Project dependencies

## Usage

1. Launch the application
2. Set your style preferences in the sidebar
3. Upload an image for analysis
4. Get personalized recommendations and product matches

## Contributing

Feel free to submit issues and enhancement requests! 