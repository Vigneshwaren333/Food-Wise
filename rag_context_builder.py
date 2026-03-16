"""
RAG Context Builder for Food Nutrition Intelligence RAG.
Formats product information into context strings for LLM consumption.
"""


class RAGContextBuilder:
    """Build context strings from product data for LLM processing."""
    
    # Daily Value percentages for health risk assessment
    DAILY_VALUES = {
        'energy': 2000,  # kcal
        'fat': 78,  # g
        'saturated-fat': 20,  # g
        'carbohydrates': 275,  # g
        'sugars': 50,  # g
        'fiber': 28,  # g
        'proteins': 50,  # g
        'sodium': 2300,  # mg
        'salt': 6,  # g (new)
        'cholesterol': 300,  # mg
    }
    
    def __init__(self):
        """Initialize the RAG context builder."""
        pass
    
    def build_product_context(self, product_data: dict) -> str:
        """
        Build a context string from product data.
        
        Args:
            product_data: Dictionary containing product information
            
        Returns:
            Formatted context string for LLM
        """
        context_parts = []
        
        # Product name
        product_name = product_data.get('product_name', 'Unknown')
        context_parts.append(f"Product Name: {product_name}")
        
        # Brand
        brands = product_data.get('brands', '')
        if brands:
            context_parts.append(f"Brand: {brands}")
        
        # Nutri-Score
        nutriscore = product_data.get('nutrition_grade_fr', '')
        if nutriscore:
            context_parts.append(f"Nutri-Score: {nutriscore.upper()}")
        
        # Ingredients
        ingredients = product_data.get('ingredients_text', '')
        if ingredients:
            context_parts.append(f"\nIngredients: {ingredients}")
        
        # Nutrition information
        context_parts.append("\n--- Nutrition per 100g ---")
        
        # Energy
        energy = product_data.get('energy_100g', 0)
        if energy:
            context_parts.append(f"- Energy: {energy} kcal")
        
        # Fat
        fat = product_data.get('fat_100g', 0)
        sat_fat = product_data.get('saturated-fat_100g', 0)
        if fat:
            fat_info = f"- Fat: {fat}g"
            if sat_fat:
                fat_info += f" (Saturated: {sat_fat}g)"
            context_parts.append(fat_info)
        
        # Trans Fat (new)
        trans_fat = product_data.get('trans-fat_100g', 0)
        if trans_fat:
            context_parts.append(f"- Trans Fat: {trans_fat}g")
        
        # Carbohydrates
        carbs = product_data.get('carbohydrates_100g', 0)
        sugars = product_data.get('sugars_100g', 0)
        if carbs:
            carbs_info = f"- Carbohydrates: {carbs}g"
            if sugars:
                carbs_info += f" (Sugars: {sugars}g)"
            context_parts.append(carbs_info)
        
        # Fiber
        fiber = product_data.get('fiber_100g', 0)
        if fiber:
            context_parts.append(f"- Fiber: {fiber}g")
        
        # Protein
        proteins = product_data.get('proteins_100g', 0)
        if proteins:
            context_parts.append(f"- Protein: {proteins}g")
        
        # Salt (new)
        salt = product_data.get('salt_100g', 0)
        if salt:
            context_parts.append(f"- Salt: {salt}g")
        
        # Sodium
        sodium = product_data.get('sodium_100g', 0)
        if sodium:
            context_parts.append(f"- Sodium: {sodium}mg")
        
        # Cholesterol
        cholesterol = product_data.get('cholesterol_100g', 0)
        if cholesterol:
            context_parts.append(f"- Cholesterol: {cholesterol}mg")
        
        # Labels/Tags (new)
        labels = product_data.get('labels_tags', '')
        if labels:
            context_parts.append(f"\n--- Labels ---")
            context_parts.append(str(labels).replace('en:', ''))
        
        # Additives
        additives = product_data.get('additives_tags', '')
        if additives:
            context_parts.append(f"\n--- Additives ---")
            context_parts.append(str(additives))
        
        # Allergens
        allergens = product_data.get('allergens_tags', '')
        if allergens:
            context_parts.append(f"\n--- Allergens ---")
            context_parts.append(str(allergens))
        
        # Palm Oil (new)
        palm_oil = product_data.get('ingredients_from_palm_oil_n', 0)
        may_be_palm = product_data.get('ingredients_that_may_be_from_palm_oil_n', 0)
        if palm_oil > 0 or may_be_palm > 0:
            context_parts.append(f"\n--- Palm Oil ---")
            if palm_oil > 0:
                context_parts.append(f"Contains {int(palm_oil)} ingredient(s) from palm oil")
            if may_be_palm > 0:
                context_parts.append(f"May contain {int(may_be_palm)} ingredient(s) that may be from palm oil")
        
        return "\n".join(context_parts)
    
    def calculate_daily_value_percentages(self, product_data: dict) -> dict:
        """
        Calculate daily value percentages for nutrients.
        
        Args:
            product_data: Dictionary containing product nutrition data
            
        Returns:
            Dictionary of nutrient percentages
        """
        percentages = {}
        
        for nutrient, daily_value in self.DAILY_VALUES.items():
            value = product_data.get(f'{nutrient}_100g', 0)
            if value and daily_value:
                pct = (value / daily_value) * 100
                percentages[nutrient] = round(pct, 1)
        
        return percentages
    
    def identify_high_risk_nutrients(self, percentages: dict, threshold: int = 20) -> list:
        """
        Identify high-risk nutrients based on daily value percentages.
        
        Args:
            percentages: Dictionary of nutrient percentages
            threshold: Percentage threshold for high risk
            
        Returns:
            List of high-risk nutrients
        """
        high_risk = []
        
        # Nutrients to check (excluding ones where high is good)
        check_nutrients = ['fat', 'saturated-fat', 'carbohydrates', 'sugars', 
                           'sodium', 'cholesterol']
        
        for nutrient in check_nutrients:
            if nutrient in percentages and percentages[nutrient] >= threshold:
                high_risk.append({
                    'nutrient': nutrient,
                    'percentage': percentages[nutrient],
                    'severity': 'high' if percentages[nutrient] >= 40 else 'moderate'
                })
        
        return high_risk
    
    def build_health_report_prompt(self, product_data: dict) -> str:
        """
        Build a prompt for generating health report.
        
        Args:
            product_data: Dictionary containing product information
            
        Returns:
            Formatted prompt for LLM
        """
        context = self.build_product_context(product_data)
        percentages = self.calculate_daily_value_percentages(product_data)
        
        prompt = f"""You are a nutrition expert AI assistant. Analyze the following food product and provide a health report.

{context}

Daily Value Percentages:
"""
        for nutrient, pct in percentages.items():
            prompt += f"- {nutrient}: {pct}%\n"
        
        prompt += """
Based on this information, please provide:
1. Key health risks (if any) based on the nutritional content
2. Consumption recommendations
3. Explanation of any concerning ingredients or additives

Format your response in a clear, easy-to-read manner.
"""
        return prompt
    
    def format_nutrition_display(self, product_data: dict) -> dict:
        """
        Format nutrition data for display in UI.
        
        Args:
            product_data: Dictionary containing product nutrition data
            
        Returns:
            Dictionary with formatted display values
        """
        display = {
            'product_name': product_data.get('product_name', 'Unknown'),
            'ingredients': product_data.get('ingredients_text', 'Not available'),
            'nutrition': {},
            'additives': product_data.get('additives_tags', 'None'),
            'allergens': product_data.get('allergens_tags', 'None')
        }
        
        # Format nutrition values
        nutrition_items = [
            ('energy', 'Energy', 'kcal'),
            ('fat_100g', 'Fat', 'g'),
            ('saturated-fat_100g', 'Saturated Fat', 'g'),
            ('carbohydrates_100g', 'Carbohydrates', 'g'),
            ('sugars_100g', 'Sugars', 'g'),
            ('fiber_100g', 'Fiber', 'g'),
            ('proteins_100g', 'Protein', 'g'),
            ('sodium_100g', 'Sodium', 'mg'),
            ('cholesterol_100g', 'Cholesterol', 'mg'),
        ]
        
        for key, label, unit in nutrition_items:
            value = product_data.get(key, 0)
            if value and value != '':
                display['nutrition'][label] = f"{value} {unit}"
        
        return display


# Singleton instance
_rag_context_builder = None

def get_rag_context_builder() -> RAGContextBuilder:
    """Get or create the RAG context builder singleton."""
    global _rag_context_builder
    if _rag_context_builder is None:
        _rag_context_builder = RAGContextBuilder()
    return _rag_context_builder
