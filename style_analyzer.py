from typing import Dict, List, Optional
import google.generativeai as genai
import PIL.Image
from pathlib import Path

class StyleAnalyzer:
    def __init__(self, vision_model):
        """Initialize the style analyzer with a vision model"""
        self.vision_model = vision_model
        
    def analyze_image(self, 
                     image_path: str, 
                     preferences: Dict[str, any],
                     twitter_data: Optional[Dict] = None) -> Dict:
        """
        Analyze a fashion image and provide detailed style analysis
        
        Args:
            image_path: Path to the image file
            preferences: Dictionary containing user preferences
            twitter_data: Optional dictionary containing Twitter style data
            
        Returns:
            Dictionary containing analysis results
        """
        # Read image data
        image_data = Path(image_path).read_bytes()
        
        # Create base prompt
        base_prompt = self._create_analysis_prompt(preferences)
        
        # Enhance with Twitter data if available
        if twitter_data:
            base_prompt = self._enhance_prompt_with_twitter(base_prompt, twitter_data)
            
        try:
            # Get vision model's analysis
            response = self.vision_model.generate_content(
                contents=[
                    base_prompt,
                    {"mime_type": "image/jpeg", "data": image_data}
                ]
            )
            response.resolve()
            
            # Parse the response into structured data
            return self._parse_analysis_response(response.text)
            
        except Exception as e:
            raise Exception(f"Error analyzing image: {str(e)}")
    
    def _create_analysis_prompt(self, preferences: Dict) -> str:
        """Create the base analysis prompt from user preferences"""
        return f"""
        Analyze this fashion image and provide recommendations considering these preferences:
        - Occasion: {preferences.get('occasion', 'Any')}
        - Budget range: {preferences.get('budget', 'Any')}
        - Preferred colors: {', '.join(preferences.get('colors', [])) if preferences.get('colors') else 'Any'}
        - Preferred brands: {preferences.get('brands', 'Any')}
        - Special requirements: {preferences.get('requirements', 'None')}
        
        Please provide a detailed analysis in the following format:
        
        DESCRIPTION: [Detailed outfit description]
        
        STYLE_CATEGORY: [Formal/Casual/Business/etc.]
        
        SUITABLE_OCCASIONS: [Comma-separated list]
        
        IDENTIFIED_ITEMS: [Comma-separated list of specific items]
        
        COLOR_PALETTE: [Main colors used]
        
        DETAILED_RECOMMENDATIONS:
        To achieve a look suitable for {preferences.get('occasion', 'the occasion')}, within {preferences.get('budget', 'the')} budget, here's a complete outfit breakdown:

        1. Outerwear (Budget: $[range]):
        - Specific type (e.g., blazer, jacket)
        - Recommended colors and materials
        - Suggested brands and styles
        
        2. Top/Shirt (Budget: $[range]):
        - Specific type (e.g., button-down, blouse)
        - Recommended colors and materials
        - Suggested brands and styles
        
        3. Bottom (Budget: $[range]):
        - Specific type (e.g., trousers, skirt)
        - Recommended colors and materials
        - Suggested brands and styles
        
        4. Shoes (Budget: $[range]):
        - Specific type (e.g., heels, flats)
        - Recommended colors and materials
        - Suggested brands and styles
        
        ADDITIONAL_RECOMMENDATIONS:
        - Accessories suggestions
        - Styling tips
        - Additional considerations
        
        Format each section clearly and provide specific, actionable recommendations that match the preferences and budget constraints.
        """
    
    def _enhance_prompt_with_twitter(self, base_prompt: str, twitter_data: Dict) -> str:
        """Enhance the analysis prompt with Twitter data"""
        twitter_context = []
        
        if fashion_interests := twitter_data.get("fashion_interests"):
            twitter_context.append(f"User is interested in these fashion styles: {', '.join(fashion_interests)}.")
        
        if color_preferences := twitter_data.get("color_preferences"):
            twitter_context.append(f"User tends to prefer these colors: {', '.join(color_preferences)}.")
        
        if recent_tweets := twitter_data.get("recent_fashion_tweets"):
            tweet_texts = [tweet["text"] for tweet in recent_tweets[:3]]
            twitter_context.append("Based on recent Twitter activity, the user has mentioned: " + 
                                 " | ".join(tweet_texts))
        
        if twitter_context:
            return f"{base_prompt}\n\nConsider the user's personal style preferences based on Twitter data: {' '.join(twitter_context)}"
        
        return base_prompt
    
    def _parse_analysis_response(self, response_text: str) -> Dict:
        """Parse the vision model's response into structured data"""
        sections = {
            'description': '',
            'style_category': '',
            'suitable_occasions': [],
            'identified_items': [],
            'color_palette': [],
            'detailed_recommendations': {
                'outerwear': {'type': '', 'budget': '', 'details': ''},
                'top': {'type': '', 'budget': '', 'details': ''},
                'bottom': {'type': '', 'budget': '', 'details': ''},
                'shoes': {'type': '', 'budget': '', 'details': ''}
            },
            'additional_recommendations': []
        }
        
        current_section = None
        current_item = None
        
        for line in response_text.split('\n'):
            line = line.strip()
            
            # Main sections
            if line.startswith('DESCRIPTION:'):
                current_section = 'description'
                sections[current_section] = line.replace('DESCRIPTION:', '').strip()
            elif line.startswith('STYLE_CATEGORY:'):
                current_section = 'style_category'
                sections[current_section] = line.replace('STYLE_CATEGORY:', '').strip()
            elif line.startswith('SUITABLE_OCCASIONS:'):
                current_section = 'suitable_occasions'
                occasions = line.replace('SUITABLE_OCCASIONS:', '').strip()
                sections[current_section] = [occ.strip() for occ in occasions.split(',')]
            elif line.startswith('IDENTIFIED_ITEMS:'):
                current_section = 'identified_items'
                items = line.replace('IDENTIFIED_ITEMS:', '').strip()
                sections[current_section] = [item.strip() for item in items.split(',')]
            elif line.startswith('COLOR_PALETTE:'):
                current_section = 'color_palette'
                colors = line.replace('COLOR_PALETTE:', '').strip()
                sections[current_section] = [color.strip() for color in colors.split(',')]
            elif line.startswith('DETAILED_RECOMMENDATIONS:'):
                current_section = 'detailed_recommendations'
            elif line.startswith('ADDITIONAL_RECOMMENDATIONS:'):
                current_section = 'additional_recommendations'
            
            # Process detailed recommendations
            elif current_section == 'detailed_recommendations':
                if line.startswith('1. Outerwear'):
                    current_item = 'outerwear'
                elif line.startswith('2. Top/Shirt'):
                    current_item = 'top'
                elif line.startswith('3. Bottom'):
                    current_item = 'bottom'
                elif line.startswith('4. Shoes'):
                    current_item = 'shoes'
                elif current_item and line.startswith('- '):
                    sections['detailed_recommendations'][current_item]['details'] += line + '\n'
                elif 'Budget:' in line and current_item:
                    sections['detailed_recommendations'][current_item]['budget'] = line.split('Budget:')[1].strip()
            
            # Process additional recommendations
            elif current_section == 'additional_recommendations' and line.startswith('- '):
                sections['additional_recommendations'].append(line.replace('- ', '').strip())
            
            # Append to current section if it's description or style_category
            elif current_section and line and current_section in ['description', 'style_category']:
                sections[current_section] += ' ' + line
        
        return sections 