# AI Wardrobe: A Smart Personal Styling Assistant

---

## Quick Start
##App https://fashion-ai-assistant-ky6fo9oczhxvjjxhtxbwur.streamlit.app/
## Demo [https://drive.google.com/file/d/1cYcfbcwhEsTfByFqsKM_VkmXiPVxR3-P/view?usp=drive_link](https://drive.google.com/file/d/1P9recn5rYcIR63vQE-092RcdltydAx4s/view?usp=drive_link)

### Local Development
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-wardrobe.git
   cd ai-wardrobe
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables in `.env` file:
   ```env
   GEMINI_API_KEY=your_gemini_api_key
   SHOPIFY_STORE_URL=your_shopify_store_url
   SHOPIFY_ACCESS_TOKEN=your_shopify_access_token
   SHOPIFY_STOREFRONT_TOKEN=your_shopify_storefront_token
   ```

4. Run the app:
   ```bash
   streamlit run app.py
   ```



## Introduction
AI Wardrobe is an innovative personal styling assistant that leverages artificial intelligence to provide personalized wardrobe recommendations. The system combines computer vision, natural language processing, and e-commerce integration to analyze users' style preferences and suggest curated outfit sets for various occasions. By understanding both visual style patterns from user-uploaded images and explicit preferences, the application creates a highly personalized shopping experience.

## Existing Solutions and Their Limitations

### Current Market Solutions:
1. **Traditional E-commerce Platforms**
   - Limited personalization
   - No visual style analysis
   - Manual browsing through vast catalogs

2. **Personal Styling Services (e.g., Stitch Fix)**
   - High cost
   - Long wait times
   - Limited to specific brands
   - Requires human stylists

3. **Fashion Apps**
   - Basic outfit recommendations
   - No real-time shopping integration
   - Limited understanding of personal style

### Limitations of Existing Solutions:
- Lack of AI-powered visual analysis
- No real-time recommendations
- Limited integration with e-commerce platforms
- High dependency on human intervention
- Inability to learn from user preferences

## Our Approach

### Key Features:
1. **Visual Style Analysis**
   - Uses Google's Gemini 1.5 Flash model for image analysis
   - Extracts style patterns, colors, and preferences
   - Understands outfit compositions and combinations

2. **Personalization Engine**
   - Considers occasion/event type
   - Accounts for budget constraints
   - Incorporates color and brand preferences
   - Adapts to special requirements

3. **E-commerce Integration**
   - Direct integration with Shopify stores
   - Real-time product search and recommendations
   - Price comparison and tracking
   - Quick purchase functionality

4. **Interactive User Interface**
   - Streamlit-based web application
   - Real-time feedback and updates
   - Easy image upload and preference setting
   - Saved wardrobe sets feature

## Data Sources Used

1. **User-Provided Data**
   - Style inspiration images
   - Event/occasion preferences
   - Budget constraints
   - Color and brand preferences
   - Special requirements

2. **Shopify Product Data**
   - Product catalogs
   - Pricing information
   - Availability status
   - Product images
   - Store information

3. **AI Model Data**
   - Gemini 1.5 Flash model for image analysis
   - Style pattern recognition
   - Fashion trend analysis
   - Color palette analysis

## System Design and Code Explanation

### Block Diagram

System Architecture:
- User Interface Layer
- Application Layer
- Service Layer
- Integration Layer
- External Services

### Key Components:

1. **User Interface (Streamlit)**
   - Image upload functionality
   - Preference selection
   - Results display
   - Shopping integration

2. **Application Logic**
   - Style analysis
   - Recommendation generation
   - Product matching
   - Cart management

3. **Service Integration**
   - Gemini API client
   - Shopify API client
   - Image processing
   - Data management

4. **External Services**
   - Google Gemini API
   - Shopify Storefront API
   - Image storage
   - Session management

## Sample Interactions

1. **Style Analysis**
   - Input: User uploads 3 style inspiration images
   - Process: System analyzes images using Gemini 1.5 Flash
   - Output: Detailed style analysis with patterns and preferences

2. **Outfit Recommendation**
   - Input: User selects "Business Meeting" and "$200-500" budget
   - Process: System generates 3 complete outfit sets
   - Output: Curated items with shopping links and costs

3. **Shopping Integration**
   - Input: User clicks "Quick Purchase" on a set
   - Process: System creates cart with selected items
   - Output: Ready-to-checkout Shopify cart

## Limitations

1. **Technical Limitations**
   - Dependency on external API availability
   - Image processing constraints
   - Limited to Shopify-integrated stores

2. **Functional Limitations**
   - No real-time try-on capability
   - Limited to available product inventory
   - No size recommendation system

3. **User Experience Limitations**
   - Requires good quality input images
   - Limited to predefined event types
   - No social sharing features

## Future Scope

1. **Technical Enhancements**
   - Virtual try-on integration
   - Size recommendation AI
   - Multi-platform e-commerce integration

2. **Feature Additions**
   - Wardrobe organization tools
   - Style history tracking
   - Social sharing capabilities
   - Seasonal trend analysis

3. **Business Expansion**
   - Multi-store integration
   - International market support
   - Mobile app development
   - Subscription-based premium features

4. **AI Improvements**
   - Enhanced style learning
   - Trend prediction
   - Personalized pricing alerts
   - Style evolution tracking
