"""
Dataset Loader for Food Nutrition Intelligence RAG.
Loads cleaned CSV data into memory for fast search.
"""

import pandas as pd
import os

class FoodDatasetLoader:
    """Load and manage the food products dataset."""
    
    def __init__(self, csv_path: str = None):
        """
        Initialize the dataset loader.
        
        Args:
            csv_path: Path to the cleaned CSV file. If None, searches standard locations.
        """
        self.csv_path = self._resolve_csv_path(csv_path)
        self.df = None
        self._load_data()
    
    def _resolve_csv_path(self, csv_path: str = None) -> str:
        """
        Resolve the CSV file path, supporting both absolute and relative paths.
        
        Searches in this order:
        1. Provided path (if given)
        2. Same directory as this script
        3. Current working directory
        4. Environment variable CSV_PATH
        
        Args:
            csv_path: Optional path to use
            
        Returns:
            Resolved path to CSV file
            
        Raises:
            FileNotFoundError: If file cannot be found in any location
        """
        # If path provided, check it first
        if csv_path and os.path.exists(csv_path):
            return csv_path
        
        # Try relative to this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_csv = os.path.join(script_dir, "foods_cleaned.csv")
        if os.path.exists(script_csv):
            return script_csv
        
        # Try current working directory
        if os.path.exists("foods_cleaned.csv"):
            return "foods_cleaned.csv"
        
        # Try environment variable
        env_path = os.getenv("CSV_PATH")
        if env_path and os.path.exists(env_path):
            return env_path
        
        # File not found - raise informative error
        raise FileNotFoundError(
            f"Dataset file 'foods_cleaned.csv' not found in expected locations:\n"
            f"  - {script_csv}\n"
            f"  - {os.path.abspath('foods_cleaned.csv')}\n"
            f"\nTo fix this:\n"
            f"1. Ensure 'foods_cleaned.csv' is in the same directory as your app\n"
            f"2. Or set the CSV_PATH environment variable\n"
            f"3. For first-time setup, run: python clean_data.py\n"
        )
    
    def _load_data(self):
        """Load the CSV file into memory with optimized parameters."""
        if not self.csv_path or not os.path.exists(self.csv_path):
            raise FileNotFoundError(
                f"Dataset not found: {self.csv_path}\n"
                f"Please ensure 'foods_cleaned.csv' exists in your deployment."
            )
        
        print(f"Loading dataset from: {self.csv_path}")
        
        # Optimize CSV loading for large files
        self.df = pd.read_csv(
            self.csv_path,
            engine='python',
            encoding='utf-8',
            on_bad_lines='skip'
        )
        
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

def get_dataset_loader(csv_path: str = None) -> FoodDatasetLoader:
    """
    Get or create the dataset loader singleton.
    
    Args:
        csv_path: Optional path to CSV file. If not provided, searches standard locations.
        
    Returns:
        FoodDatasetLoader instance
    """
    global _dataset_loader
    if _dataset_loader is None:
        _dataset_loader = FoodDatasetLoader(csv_path)
    return _dataset_loader
