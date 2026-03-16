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

## To deploy on Streamlit Cloud:
1. Push this code to GitHub
2. Go to share.streamlit.io
3. Connect your GitHub and select the repository
4. Done!

## Local Setup:
```
pip install -r requirements.txt
streamlit run app.py
```
