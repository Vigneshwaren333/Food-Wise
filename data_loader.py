"""
Dataset Loader for Food Nutrition Intelligence RAG.
Loads cleaned CSV data into memory for fast search.
"""

import pandas as pd
import os

class FoodDatasetLoader:
    """Load and manage the food products dataset."""
    
    def __init__(self, csv_path: str = "foods_cleaned.csv"):
        """
        Initialize the dataset loader.
        
        Args:
            csv_path: Path to the cleaned CSV file
        """
        self.csv_path = csv_path
        self.df = None
        self._load_data()
    
    def _load_data(self):
        """Load the CSV file into memory."""
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"Dataset not found: {self.csv_path}")
        
        print(f"Loading dataset from: {self.csv_path}")
        self.df = pd.read_csv(self.csv_path)
        
        # Convert product names to lowercase for easier searching
        self.df['product_name_lower'] = self.df['product_name'].str.lower()
        
        # Fill NaN values
        self.df = self.df.fillna('')
        
        print(f"Loaded {len(self.df)} products")
        print(f"Columns: {list(self.df.columns)}")
    
    def get_product_by_index(self, index: int) -> dict:
        """Get product details by DataFrame index."""
        if index < 0 or index >= len(self.df):
            return None
        return self.df.iloc[index].to_dict()
    
    def get_product_by_name(self, name: str) -> dict:
        """Get exact product match by name."""
        result = self.df[self.df['product_name_lower'] == name.lower()]
        if len(result) > 0:
            return result.iloc[0].to_dict()
        return None
    
    def get_all_products(self) -> pd.DataFrame:
        """Get the entire dataset."""
        return self.df
    
    def search_by_ingredients(self, ingredient: str) -> pd.DataFrame:
        """Search products by ingredient."""
        ingredient_lower = ingredient.lower()
        mask = self.df['ingredients_text'].str.lower().str.contains(ingredient_lower, na=False)
        return self.df[mask]
    
    def get_total_count(self) -> int:
        """Get total number of products."""
        return len(self.df)


# Singleton instance
_dataset_loader = None

def get_dataset_loader(csv_path: str = "foods_cleaned.csv") -> FoodDatasetLoader:
    """Get or create the dataset loader singleton."""
    global _dataset_loader
    if _dataset_loader is None:
        _dataset_loader = FoodDatasetLoader(csv_path)
    return _dataset_loader
