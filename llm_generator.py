"""
LLM Health Report Generator for Food Nutrition Intelligence RAG.

This module provides health report generation using Groq Cloud LLM API.
It can also fall back to rule-based analysis if API is not available.
"""

from rag_context_builder import RAGContextBuilder, get_rag_context_builder
from typing import Dict, List
import os

# Try to import groq, install if not available
try:
    from groq import Groq
except ImportError:
    Groq = None


class LLMHealthReportGenerator:
    """Generate health reports using Groq LLM API."""
    
    def __init__(self):
        """Initialize the LLM client."""
        self.client = None
        self.model = os.getenv('GROQ_MODEL', 'llama-3.1-70b-versatile')
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Groq client from environment."""
        api_key = os.getenv('GROQ_API_KEY')
        if api_key and api_key != 'your_groq_api_key_here':
            if Groq:
                try:
                    self.client = Groq(api_key=api_key)
                    print(f"Groq LLM initialized with model: {self.model}")
                except Exception as e:
                    print(f"Failed to initialize Groq client: {e}")
                    self.client = None
        else:
            print("GROQ_API_KEY not found in environment. Using rule-based fallback.")
    
    def generate_health_report(self, product_data: dict) -> str:
        """
        Generate a health report using Groq LLM.
        
        Args:
            product_data: Dictionary containing product information
            
        Returns:
            Generated health report text
        """
        if not self.client:
            return None  # Fall back to rule-based
        
        # Build context using RAG context builder
        context_builder = get_rag_context_builder()
        prompt = context_builder.build_health_report_prompt(product_data)
        
        # Add specific instructions for health report
        full_prompt = f"""{prompt}

Please provide a comprehensive health report with the following sections:
1. **Health Score** (0-100) - Calculate based on nutritional values
2. **Key Health Risks** - What nutrients are concerning and why
3. **Consumption Recommendations** - Who should avoid, how often to consume
4. **Additive Concerns** - Explain any concerning additives
5. **Allergen Information** - List any allergens

Format the response in a clear, easy-to-read manner with emojis.

Provide your response in English."""
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a nutrition expert AI assistant specializing in food health analysis. Provide accurate, evidence-based health information."
                    },
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=2000
            )
            
            return chat_completion.choices[0].message.content
        
        except Exception as e:
            print(f"Error generating LLM response: {e}")
            return None


# Singleton for LLM generator
_llm_health_report_generator = None

def get_llm_health_report_generator() -> LLMHealthReportGenerator:
    """Get or create the LLM health report generator singleton."""
    global _llm_health_report_generator
    if _llm_health_report_generator is None:
        _llm_health_report_generator = LLMHealthReportGenerator()
    return _llm_health_report_generator


class HealthReportGenerator:
    """Generate health reports based on nutritional data."""
    
    # Common additive explanations
    ADDITIVE_EXPLANATIONS = {
        'e621': 'Monosodium Glutamate (MSG) - Flavor enhancer, generally considered safe but may cause headaches in sensitive individuals.',
        'e621': 'MSG - May cause headaches, flushing, and sweating in some people (Chinese Restaurant Syndrome).',
        'e250': 'Sodium nitrite - Preservative and color fixer, linked to increased cancer risk when consumed in large amounts.',
        'e251': 'Sodium nitrate - Preservative that can form carcinogenic compounds.',
        'e150': 'Caramel coloring - Generally safe, but some types may contain carcinogens.',
        'e150a': 'Plain caramel - Generally recognized as safe.',
        'e150c': 'Ammonia caramel - May contain carcinogens, banned in some countries.',
        'e160': 'Carotenoids - Natural colorings derived from plants, generally safe.',
        'e171': 'Titanium dioxide - Banned in EU due to potential DNA damage.',
        'e330': 'Citric acid - Natural preservative, generally safe.',
        'e331': 'Sodium citrate - Buffering agent, generally safe.',
        'e332': 'Potassium citrate - Generally safe.',
        'e338': 'Phosphoric acid - May affect calcium absorption, commonly found in colas.',
        'e339': 'Sodium phosphate - Generally safe but may affect calcium metabolism.',
        'e440': 'Pectin - Natural gelling agent, generally safe.',
        'e471': 'Mono- and diglycerides - Emulsifiers derived from fats, generally safe.',
        'e472': 'Esters of mono/diglycerides - Emulsifiers, generally safe.',
        'e500': 'Sodium carbonates - Baking soda related, generally safe.',
        'e501': 'Potassium carbonates - Generally safe.',
        'e503': 'Ammonium carbonates - Leavening agent, generally safe.',
        'e621': 'MSG - Flavor enhancer, may cause adverse reactions in sensitive individuals.',
    }
    
    # Allergen descriptions
    ALLERGEN_INFO = {
        'gluten': 'Gluten - Found in wheat, barley, rye. Problematic for celiac disease patients.',
        'wheat': 'Wheat - Contains gluten, common allergen.',
        'milk': 'Milk/Dairy - Lactose intolerance and milk allergy.',
        'eggs': 'Eggs - Common allergen, especially in children.',
        'soy': 'Soy - Legume allergen, common in processed foods.',
        'nuts': 'Tree Nuts - Includes almonds, walnuts, cashews, etc.',
        'peanuts': 'Peanuts - Legume allergen, can cause severe reactions.',
        'fish': 'Fish - Seafood allergen.',
        'shellfish': 'Shellfish - Crustacean allergen.',
        'sesame': 'Sesame - Increasing common allergen.',
    }
    
    def __init__(self):
        """Initialize the health report generator."""
        self.context_builder = get_rag_context_builder()
        self.llm_generator = get_llm_health_report_generator()
        self.use_llm = True  # Set to False to force rule-based
    
    def generate_report(self, product_data: dict) -> Dict:
        """
        Generate a comprehensive health report for a product.
        
        Args:
            product_data: Dictionary containing product information
            
        Returns:
            Dictionary containing the health report
        """
        # Try LLM first, fall back to rule-based
        llm_report = None
        if self.use_llm:
            llm_report = self.llm_generator.generate_health_report(product_data)
        
        # Always calculate rule-based metrics for structured data
        # Calculate daily value percentages
        percentages = self.context_builder.calculate_daily_value_percentages(product_data)
        
        # Identify high-risk nutrients
        high_risk = self.context_builder.identify_high_risk_nutrients(percentages)
        
        # Generate components
        risk_assessment = self._assess_risks(percentages, high_risk)
        recommendations = self._generate_recommendations(percentages, high_risk)
        additive_info = self._explain_additives(product_data.get('additives_tags', ''))
        allergen_info = self._explain_allergens(product_data.get('allergens_tags', ''))
        palm_oil_info = self._explain_palm_oil(product_data)
        
        # Calculate health score
        health_score = self._calculate_health_score(percentages)
        
        return {
            'product_name': product_data.get('product_name', 'Unknown'),
            'brands': product_data.get('brands', ''),
            'nutriscore': product_data.get('nutrition_grade_fr', ''),
            'health_score': health_score,
            'llm_report': llm_report,  # Full LLM-generated report
            'risk_assessment': risk_assessment,
            'recommendations': recommendations,
            'additive_info': additive_info,
            'allergen_info': allergen_info,
            'palm_oil_info': palm_oil_info,
            'labels': product_data.get('labels_tags', ''),
            'daily_value_percentages': percentages,
            'high_risk_nutrients': high_risk
        }
    
    def _assess_risks(self, percentages: dict, high_risk: List[Dict]) -> str:
        """Generate risk assessment text."""
        if not high_risk:
            return "✓ This product has reasonable nutritional values for occasional consumption."
        
        assessment_parts = []
        
        for item in high_risk:
            nutrient = item['nutrient']
            pct = item['percentage']
            severity = item['severity']
            
            if severity == 'high':
                assessment_parts.append(
                    f"⚠️ High {nutrient.replace('-', ' ')}: {pct}% of daily value per serving"
                )
            else:
                assessment_parts.append(
                    f"⚡ Moderate {nutrient.replace('-', ' ')}: {pct}% of daily value per serving"
                )
        
        return "\n".join(assessment_parts)
    
    def _generate_recommendations(self, percentages: dict, high_risk: List[Dict]) -> str:
        """Generate consumption recommendations."""
        recommendations = []
        
        if not high_risk:
            recommendations.append("✓ This product can be consumed as part of a balanced diet.")
            recommendations.append("✓ No significant nutritional concerns identified.")
            return "\n".join(recommendations)
        
        # Check for specific high-risk nutrients
        high_sodium = percentages.get('sodium', 0) >= 40
        high_salt = percentages.get('salt', 0) >= 40
        high_sugar = percentages.get('sugars', 0) >= 40
        high_fat = percentages.get('fat', 0) >= 40
        high_sat_fat = percentages.get('saturated-fat', 0) >= 40
        high_trans_fat = percentages.get('trans-fat', 0) > 0
        
        if high_sodium:
            recommendations.append("⚠️ High sodium content - limit consumption, especially if you have hypertension.")
        
        if high_salt:
            recommendations.append("⚠️ High salt content - may contribute to high blood pressure.")
        
        if high_sugar:
            recommendations.append("⚠️ High sugar content - not recommended for diabetics or those watching sugar intake.")
        
        if high_fat:
            recommendations.append("⚠️ High fat content - consume in moderation as part of a balanced diet.")
        
        if high_sat_fat:
            recommendations.append("⚠️ High saturated fat - limit for heart health.")
        
        if high_trans_fat:
            recommendations.append("⚠️ Contains trans fats - should be avoided completely for heart health.")
        
        # General recommendation based on number of high-risk items
        if len(high_risk) >= 3:
            recommendations.append("📋 Recommendation: Occasional consumption only (1-2 times per week maximum).")
        elif len(high_risk) >= 1:
            recommendations.append("📋 Recommendation: Moderate consumption (3-4 times per week maximum).")
        
        return "\n".join(recommendations)
    
    def _explain_additives(self, additives_str: str) -> str:
        """Generate additive explanations."""
        if not additives_str or additives_str == '':
            return "No additives listed or information available."
        
        explanations = []
        
        # Parse additives (format varies, try to extract E-numbers)
        additives_lower = additives_str.lower()
        
        # Check for common concerning additives
        concerning = ['e621', 'e250', 'e251', 'e150c', 'e171', 'e338']
        
        for additive in concerning:
            if additive in additives_lower or additive.upper() in additives_str:
                if additive in self.ADDITIVE_EXPLANATIONS:
                    explanations.append(f"• {additive.upper()}: {self.ADDITIVE_EXPLANATIONS[additive]}")
        
        if not explanations:
            return "Additives present but no specific concerns identified. Always check for personal sensitivities."
        
        return "\n".join(explanations)
    
    def _explain_allergens(self, allergens_str: str) -> str:
        """Generate allergen information."""
        if not allergens_str or allergens_str == '':
            return "No common allergens identified in this product."
        
        allergen_list = []
        allergens_lower = allergens_str.lower()
        
        for allergen, description in self.ALLERGEN_INFO.items():
            if allergen in allergens_lower:
                allergen_list.append(f"• {allergen.title()}: {description}")
        
        if not allergen_list:
            return f"Allergens may be present: {allergens_str}"
        
        return "\n".join(allergen_list)
    
    def _explain_palm_oil(self, product_data: dict) -> str:
        """Generate palm oil information."""
        palm_oil = product_data.get('ingredients_from_palm_oil_n', 0)
        may_be_palm = product_data.get('ingredients_that_may_be_from_palm_oil_n', 0)
        
        if palm_oil > 0 and may_be_palm > 0:
            return f"⚠️ Contains {int(palm_oil)} ingredient(s) from palm oil and {int(may_be_palm)} that may be from palm oil.\n\nPalm oil is high in saturated fats and often linked to environmental concerns."
        elif palm_oil > 0:
            return f"⚠️ Contains {int(palm_oil)} ingredient(s) from palm oil.\n\nPalm oil is high in saturated fats and often linked to environmental concerns."
        elif may_be_palm > 0:
            return f"⚠️ May contain {int(may_be_palm)} ingredient(s) that may be from palm oil.\n\nCheck with manufacturer for specific details."
        else:
            return "✓ No palm oil ingredients detected."
    
    def _calculate_health_score(self, percentages: dict) -> int:
        """
        Calculate a health score from 0-100.
        
        Higher is better. Starts at 100 and subtracts based on:
        - High sodium, sugar, fat, saturated fat, cholesterol, salt, trans-fat
        """
        score = 100
        
        # Penalties for high-risk nutrients
        penalty_rules = [
            ('sodium', 30, 20),  # Over 30% DV: -20 points
            ('salt', 30, 15),    # Over 30% DV: -15 points (new)
            ('sugars', 25, 15),  # Over 25% DV: -15 points
            ('fat', 30, 15),     # Over 30% DV: -15 points
            ('saturated-fat', 20, 20),  # Over 20% DV: -20 points
            ('trans-fat', 0, 25),  # Any trans fat: -25 points (new)
            ('cholesterol', 15, 10),    # Over 15% DV: -10 points
        ]
        
        for nutrient, threshold, penalty in penalty_rules:
            value = percentages.get(nutrient, 0)
            if value > threshold:
                score -= penalty
        
        # Bonus for high fiber and protein
        if percentages.get('fiber', 0) > 20:
            score += 5
        if percentages.get('proteins', 0) > 20:
            score += 5
        
        # Clamp score between 0 and 100
        return max(0, min(100, score))
    
    def format_report_display(self, report: Dict) -> str:
        """
        Format the health report for display.
        
        Args:
            report: The generated health report
            
        Returns:
            Formatted text for display
        """
        lines = []
        
        # Header with score
        score = report['health_score']
        score_color = "🟢" if score >= 70 else "🟡" if score >= 50 else "🔴"
        lines.append(f"## {score_color} Health Score: {score}/100")
        
        lines.append(f"\n### 📊 Product: {report['product_name']}")
        
        # Risk Assessment
        lines.append("\n### ⚠️ Health Risk Assessment")
        lines.append(report['risk_assessment'])
        
        # Recommendations
        lines.append("\n### 💡 Recommendations")
        lines.append(report['recommendations'])
        
        # Additives
        lines.append("\n### 🧪 Additive Information")
        lines.append(report['additive_info'])
        
        # Allergens
        lines.append("\n### 🚨 Allergen Information")
        lines.append(report['allergen_info'])
        
        # Daily Values
        lines.append("\n### 📈 Daily Value Percentages")
        for nutrient, pct in report['daily_value_percentages'].items():
            status = "⚠️ HIGH" if pct >= 40 else "⚡ Moderate" if pct >= 20 else "✓ Low"
            lines.append(f"- {nutrient.replace('-', ' ').title()}: {pct}% {status}")
        
        return "\n".join(lines)


# Singleton instance
_health_report_generator = None

def get_health_report_generator() -> HealthReportGenerator:
    """Get or create the health report generator singleton."""
    global _health_report_generator
    if _health_report_generator is None:
        _health_report_generator = HealthReportGenerator()
    return _health_report_generator
