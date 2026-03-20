# 🍎 Food Nutrition Intelligence - Streamlit Deployment

A RAG-based food nutrition analysis app powered by Groq LLM and OpenFoodFacts data.

## 🚀 Quick Deploy to Streamlit Cloud

**Status**: ✅ Ready for deployment! The `foods_cleaned.csv` is tracked with Git LFS and already in the repo.

1. Go to https://share.streamlit.io
2. Click "New app" → "From existing repo"
3. Enter: `https://github.com/Vigneshwaren333/Food-Wise.git`
4. Select branch: `main`
5. File path: `app.py`
6. Click Deploy!

**That's it!** Streamlit Cloud will handle everything, including downloading the LFS-tracked dataset.

## 📁 Key Files:
- **app.py** - Main Streamlit application
- **foods_cleaned.csv** - Dataset (tracked with Git LFS, 126 MB)
- **requirements.txt** - Python dependencies
- **data_loader.py** - Dataset loading with smart path resolution
- **DEPLOYMENT_GUIDE.md** - Detailed deployment troubleshooting

## 💻 Local Development Setup

```bash
# 1. Clone and navigate to project
git clone https://github.com/Vigneshwaren333/Food-Wise.git
cd Food-Wise/Deployment_Version

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
cp .env.example .env
# Add your Groq API key to .env

# 4. Run the app
streamlit run app.py
```

## 📋 Setup Details:

### Dataset (foods_cleaned.csv)
- ✅ Already included in the repository with Git LFS
- Size: 126 MB of food nutrition data
- Automatically loaded from the repo on deployment

### Environment Variables (.env)
```bash
GROQ_API_KEY=your_groq_api_key_here  # Get free key from https://console.groq.com/
GROQ_MODEL=llama-3.3-70b-versatile   # Latest Groq model
CSV_PATH=foods_cleaned.csv            # Optional (auto-detected if not set)
```

### Alternative Platforms
If you prefer other deployment options:
- **HuggingFace Spaces**: Upload files directly at huggingface.co/spaces
- **Railway/Render**: Docker-based deployment with Streamlit support
- **Local Server**: `streamlit run app.py` on your machine

## 🆘 Troubleshooting

### "Dataset not found" Error
- **On Streamlit Cloud**: Check app logs in the menu → Manage App → Logs
- **Locally**: Ensure `foods_cleaned.csv` exists in the same directory as `app.py`
- **Custom path**: Set `CSV_PATH` environment variable
- See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed solutions

### Groq API Issues
- Verify your API key in `.env` (free at https://console.groq.com/)
- Check API rate limits in Groq console
- The app has a fallback rule-based analyzer if API fails

### First Deployment Taking Long?
- First deployment with LFS can take 2-3 minutes
- Subsequent deployments are faster
- Check Streamlit Cloud deployment logs for progress

## 📖 More Information
- See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for advanced deployment options
- For dataset generation from raw data: `python clean_data.py`
- For API-specific questions: https://console.groq.com/docs
