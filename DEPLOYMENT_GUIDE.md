# Deployment Guide for Food Nutrition Intelligence

## Prerequisites
The app requires `foods_cleaned.csv` to run. This file should be generated from raw OpenFoodFacts data.

## Option 1: Streamlit Cloud Deployment (Recommended)

### Step 1: Prepare the CSV File Locally
```bash
# If you have the raw OpenFoodFacts TSV file:
python clean_data.py

# This will create foods_cleaned.csv
```

### Step 2: Upload CSV to Streamlit Cloud

Since Streamlit doesn't support large file uploads via GitHub, use one of these approaches:

#### Option A: GitHub LFS (for files < 2GB)
```bash
# Install Git LFS
# macOS: brew install git-lfs
# Windows: Download from https://git-lfs.github.com/
# Linux: apt-get install git-lfs

# Track the CSV file
git lfs install
git lfs track "foods_cleaned.csv"

# Commit and push
git add .gitattributes foods_cleaned.csv
git commit -m "Add cleaned food dataset"
git push
```

#### Option B: Environment Variable with Download URL
1. Upload `foods_cleaned.csv` to a cloud storage (Google Drive, Dropbox, AWS S3, etc.)
2. Get a direct download link
3. Add to Streamlit secrets:
   - Go to https://share.streamlit.io → click your app → Settings → Secrets
   - Add: `CSV_DOWNLOAD_URL = "https://your-download-link"`

Then the app can auto-download it on first run.

### Step 3: Deploy to Streamlit Cloud
```bash
git push  # Push to your GitHub repo
```
Then in Streamlit Cloud:
1. Click "New app" → "From existing repo"
2. Select your repository, branch, and `app.py`
3. Click Deploy

## Option 2: Use Smaller Sample Dataset (Testing Only)
If you don't have the full CSV:
- Create a minimal `foods_cleaned.csv` with sample data for testing
- Example columns: product_name, ingredients_text, energy_100g, etc.

## Troubleshooting

### Error: "Dataset not found: foods_cleaned.csv"

**Local Fix:**
```bash
# Generate the CSV from source data
python clean_data.py

# Verify it exists
ls -la foods_cleaned.csv  # macOS/Linux
dir foods_cleaned.csv     # Windows
```

**Streamlit Cloud Fix:**
1. Check your GitHub repository contains `foods_cleaned.csv`
2. If using Git LFS, verify it's properly installed and tracked
3. Check Streamlit Cloud logs (App menu → Manage app → Logs)
4. Try redeploying by clicking the menu → Reboot app

### File Size Issues
If your CSV is > 50MB:
- Consider sampling the data
- Use CSV compression
- Stream data from a database instead

## Local Testing
```bash
streamlit run app.py
```

This will use the local `foods_cleaned.csv` file from the same directory.
