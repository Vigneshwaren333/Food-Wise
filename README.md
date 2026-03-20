# Vercel Deployment for Streamlit

**⚠️ Important Note:** Vercel does not natively support Streamlit apps. For deployment, consider:

## Option 1: Streamlit Community Cloud (Recommended)
- Deploy to [Streamlit Cloud](https://streamlit.io/cloud) for free
- Simply connect your GitHub repository

## Option 2: HuggingFace Spaces (Free)
- Create a new Space at huggingface.co/spaces
- Upload your files there

## Option 3: Railway/Render (Alternative)
- These platforms support Streamlit directly

## Files in this folder:
- app.py - Main Streamlit application
- requirements.txt - Python dependencies
- .env.example - Environment variables template
- DEPLOYMENT_GUIDE.md - **Detailed deployment instructions (READ THIS!)**

## Local Setup:
```bash
# Install dependencies
pip install -r requirements.txt

# Generate the dataset (if you have raw OpenFoodFacts data)
python clean_data.py

# Run the app
streamlit run app.py
```

## ⚠️ IMPORTANT: Dataset Setup for Deployment

**This app requires the `foods_cleaned.csv` file to function.**

### Before Deploying:
You must prepare the `foods_cleaned.csv` file. Choose one option:

1. **Generate it locally** (if you have raw OpenFoodFacts data):
   ```bash
   python clean_data.py
   ```

2. **Use Git LFS** (for GitHub deployment):
   ```bash
   git lfs install
   git lfs track "foods_cleaned.csv"
   git add .gitattributes foods_cleaned.csv
   git push
   ```

3. **Upload to cloud storage** and use Streamlit Secrets to auto-download

👉 **See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for complete deployment instructions.**

## Troubleshooting

**Error: "Dataset not found: foods_cleaned.csv"**
- Ensure `foods_cleaned.csv` is in the same directory as `app.py`
- Or set the `CSV_PATH` environment variable to point to it
- See DEPLOYMENT_GUIDE.md for detailed troubleshooting
