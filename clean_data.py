"""
Clean OpenFoodFacts TSV data to extract required columns per PRD.
Uses chunked reading to handle large files efficiently.

Required columns per PRD A.1 Data Schema:
- product_name
- ingredients_text
- energy_100g
- fat_100g
- saturated-fat_100g
- carbohydrates_100g
- sugars_100g
- fiber_100g
- proteins_100g
- sodium_100g
- cholesterol_100g
- additives_tags
- allergens_tags
"""

import pandas as pd
import gc

# Define columns we actually need from the raw file
# This dramatically reduces memory usage
COLUMNS_TO_KEEP = [
    # Basic product info
    'product_name',
    'ingredients_text',
    
    # Nutrition data
    'energy_100g',
    'fat_100g',
    'saturated-fat_100g',
    'carbohydrates_100g',
    'sugars_100g',
    'fiber_100g',
    'proteins_100g',
    'sodium_100g',
    'cholesterol_100g',
    
    # Additional nutrition (new)
    'salt_100g',
    'trans-fat_100g',
    
    # Additives & allergens
    'additives_tags',
    'allergens_en',  # Using allergens_en for cleaner data
    
    # Product metadata (new)
    'brands',
    'brands_tags',
    'labels_tags',
    'categories_tags',
    'main_category_en',
    
    # Nutri-Score (new) - nutrition_grade_fr is the standard Nutri-Score (A-E)
    'nutrition_grade_fr',
    'nutrition-score-fr_100g',
    
    # Palm oil info (new)
    'ingredients_from_palm_oil_n',
    'ingredients_that_may_be_from_palm_oil_n',
    
    # Image
    'image_url',
]

# Rename mapping for output
COLUMN_RENAME = {
    'allergens_en': 'allergens_tags'
}

def clean_openfoodfacts_data(input_file, output_file):
    """Clean OpenFoodFacts TSV data and save as CSV using chunked reading."""
    
    print(f"Reading raw data from: {input_file}")
    
    # First, read only the header to check available columns
    df_header = pd.read_csv(input_file, sep='\t', nrows=0, low_memory=False)
    available_cols = [c for c in COLUMNS_TO_KEEP if c in df_header.columns]
    print(f"Found {len(available_cols)} required columns in the file")
    
    # Read in chunks to avoid memory issues
    chunk_size = 50000
    chunks = []
    
    for i, chunk in enumerate(pd.read_csv(input_file, sep='\t', 
                                           usecols=available_cols,
                                           low_memory=False, 
                                           chunksize=chunk_size)):
        # Filter out rows without product_name
        chunk = chunk[chunk['product_name'].notna()]
        chunk = chunk[chunk['product_name'].str.strip() != '']
        
        if len(chunk) > 0:
            chunks.append(chunk)
        
        print(f"Processed chunk {i+1}: {len(chunk)} valid rows")
        gc.collect()
    
    print(f"\nCombining {len(chunks)} chunks...")
    df_cleaned = pd.concat(chunks, ignore_index=True)
    del chunks
    gc.collect()
    
    print(f"Total rows after filtering: {len(df_cleaned)}")
    
    # Rename columns
    df_cleaned = df_cleaned.rename(columns=COLUMN_RENAME)
    
    # Fill NaN values with empty strings for text columns
    text_columns = [
        'product_name', 'ingredients_text', 'additives_tags', 'allergens_tags',
        'brands', 'brands_tags', 'labels_tags', 'categories_tags', 'main_category_en',
        'nutrition_grade_fr', 'image_url'
    ]
    for col in text_columns:
        if col in df_cleaned.columns:
            df_cleaned[col] = df_cleaned[col].fillna('')
    
    # Fill NaN values with 0 for numeric columns
    numeric_columns = [
        'energy_100g', 'fat_100g', 'saturated-fat_100g', 'carbohydrates_100g',
        'sugars_100g', 'fiber_100g', 'proteins_100g', 'sodium_100g', 'cholesterol_100g',
        'salt_100g', 'trans-fat_100g', 'nutrition-score-fr_100g',
        'ingredients_from_palm_oil_n', 'ingredients_that_may_be_from_palm_oil_n'
    ]
    for col in numeric_columns:
        if col in df_cleaned.columns:
            df_cleaned[col] = pd.to_numeric(df_cleaned[col], errors='coerce').fillna(0)
    
    # Reset index
    df_cleaned = df_cleaned.reset_index(drop=True)
    
    # Save to CSV
    print(f"\nSaving cleaned data to: {output_file}")
    df_cleaned.to_csv(output_file, index=False)
    
    print(f"\nCleaning complete!")
    print(f"Final shape: {df_cleaned.shape}")
    print(f"\nColumn summary:")
    for col in df_cleaned.columns:
        if col in text_columns:
            non_empty = (df_cleaned[col] != '').sum()
        else:
            non_empty = (df_cleaned[col] != 0).sum()
        print(f"  {col}: {non_empty} non-empty values")
    
    return df_cleaned

if __name__ == "__main__":
    input_file = "en.openfoodfacts.org.products.tsv"
    output_file = "foods_cleaned.csv"
    
    df = clean_openfoodfacts_data(input_file, output_file)
    
    # Show sample data
    print("\n=== Sample Data (first 5 rows) ===")
    print(df.head().to_string())
