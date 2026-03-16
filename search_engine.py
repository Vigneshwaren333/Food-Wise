"""
Search Engine for Food Nutrition Intelligence RAG.
Provides fuzzy/partial matching on product names using RapidFuzz.
"""

from rapidfuzz import fuzz, process
import pandas as pd
from typing import List, Tuple, Dict
from data_loader import FoodDatasetLoader


class FoodSearchEngine:
    """Fuzzy search engine for food products."""
    
    def __init__(self, dataset_loader: FoodDatasetLoader, min_score: int = 50):
        """
        Initialize the search engine.
        
        Args:
            dataset_loader: The dataset loader instance
            min_score: Minimum fuzzy match score (0-100) to include in results
        """
        self.loader = dataset_loader
        self.df = dataset_loader.get_all_products()
        self.min_score = min_score
        
        # Extract product names as list for fuzzy matching
        self.product_names = self.df['product_name'].tolist()
        self.product_names_lower = self.df['product_name_lower'].tolist()
        
        print(f"Search engine initialized with {len(self.product_names)} products")
    
    def search(self, query: str, top_n: int = 5) -> List[Dict]:
        """
        Search for products matching the query.
        
        Args:
            query: Search query (product name or partial name)
            top_n: Number of results to return
            
        Returns:
            List of matching products with scores
        """
        if not query or not query.strip():
            return []
        
        query_lower = query.lower().strip()
        
        # First try exact substring match
        exact_matches = self.df[
            self.df['product_name_lower'].str.contains(query_lower, na=False)
        ]
        
        if len(exact_matches) > 0:
            results = []
            for idx, row in exact_matches.head(top_n).iterrows():
                results.append({
                    'index': idx,
                    'product_name': row['product_name'],
                    'score': 100,  # Exact substring match gets max score
                    'data': row.to_dict()
                })
            return results
        
        # If no substring match, use fuzzy matching
        # Use rapidfuzz process.extract for efficient fuzzy matching
        choices = self.product_names
        
        # Extract with scoring
        results = process.extract(
            query, 
            choices, 
            scorer=fuzz.WRatio,  # Weighted ratio for better partial matching
            limit=top_n * 2  # Get more results to filter
        )
        
        # Filter by minimum score and format results
        matched_results = []
        for match in results:
            product_name, score, idx = match
            
            if score >= self.min_score:
                # Get the full product data
                product_data = self.df.iloc[idx].to_dict()
                
                matched_results.append({
                    'index': idx,
                    'product_name': product_name,
                    'score': round(score, 2),
                    'data': product_data
                })
                
                if len(matched_results) >= top_n:
                    break
        
        return matched_results
    
    def search_by_ingredient(self, ingredient: str, top_n: int = 10) -> List[Dict]:
        """
        Search products by ingredient.
        
        Args:
            ingredient: Ingredient to search for
            top_n: Number of results to return
            
        Returns:
            List of products containing the ingredient
        """
        if not ingredient or not ingredient.strip():
            return []
        
        ingredient_lower = ingredient.lower().strip()
        
        # Search in ingredients text
        mask = self.df['ingredients_text'].str.lower().str.contains(
            ingredient_lower, na=False
        )
        
        matching_df = self.df[mask].head(top_n)
        
        results = []
        for idx, row in matching_df.iterrows():
            results.append({
                'index': idx,
                'product_name': row['product_name'],
                'score': 100,  # Ingredient match
                'data': row.to_dict()
            })
        
        return results


# Singleton instance
_search_engine = None

def get_search_engine(dataset_loader: FoodDatasetLoader = None) -> FoodSearchEngine:
    """Get or create the search engine singleton."""
    global _search_engine
    if _search_engine is None:
        if dataset_loader is None:
            dataset_loader = FoodDatasetLoader()
        _search_engine = FoodSearchEngine(dataset_loader)
    return _search_engine
