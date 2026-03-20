"""
Food Nutrition Intelligence RAG - Streamlit UI
A RAG-powered application with clean, minimal UI for food product analysis.
"""

import streamlit as st
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

from data_loader import FoodDatasetLoader, get_dataset_loader
from search_engine import FoodSearchEngine, get_search_engine
from llm_generator import HealthReportGenerator, get_health_report_generator
import time

# Page configuration
st.set_page_config(
    page_title="Food Nutrition Intelligence",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clean, modern look - works in both light and dark mode
st.markdown("""
<style>
    /* Root variables for light mode */
    :root {
        --bg-primary: #FFFFFF;
        --bg-secondary: #F0F2F6;
        --text-primary: #262730;
        --text-secondary: #555555;
        --border-color: #ECECEC;
        --card-border: #E0E0E0;
        --hover-bg: #F8F9FA;
        --accent-color: #10A981;
        --text-muted: #888888;
        --input-bg: #FFFFFF;
        --input-text: #262730;
        --placeholder-text: #999999;
    }
    
    /* Dark mode variables */
    @media (prefers-color-scheme: dark) {
        :root {
            --bg-primary: #0E1117;
            --bg-secondary: #161B22;
            --text-primary: #E6EDF3;
            --text-secondary: #D0D4D9;
            --border-color: #30363D;
            --card-border: #444C56;
            --hover-bg: #161B22;
            --accent-color: #10A981;
            --text-muted: #B1BCC7;
            --input-bg: #0D1117;
            --input-text: #E6EDF3;
            --placeholder-text: #8B949E;
        }
    }
    
    /* Main app styling */
    .stApp {
        background-color: var(--bg-primary);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: var(--bg-primary);
        border-right: 1px solid var(--border-color);
    }
    
    /* Sidebar text - ensure visibility */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: var(--text-primary) !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] div {
        color: var(--text-primary) !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
        color: var(--text-primary) !important;
        font-weight: 600;
    }
    
    /* Sidebar captions and small text */
    [data-testid="stSidebar"] small,
    [data-testid="stSidebar"] [class*="small"] {
        color: var(--text-muted) !important;
    }
    
    /* Card containers */
    [data-testid="stMetric"] {
        background-color: var(--bg-secondary);
        padding: 16px;
        border-radius: 10px;
        border: 1px solid var(--card-border);
        color: var(--text-primary);
    }
    
    .metric-card {
        background-color: var(--bg-secondary);
        padding: 16px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid var(--card-border);
        color: var(--text-primary);
    }
    
    /* Main content text elements */
    [data-testid="stMarkdownContainer"] {
        color: var(--text-primary);
    }
    
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,
    [data-testid="stMarkdownContainer"] h4,
    [data-testid="stMarkdownContainer"] h5,
    [data-testid="stMarkdownContainer"] h6,
    [data-testid="stMarkdownContainer"] li {
        color: var(--text-primary) !important;
    }
    
    /* All text should inherit primary color */
    body, p, span, div, li, h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary);
    }
    
    /* Headers */
    .section-header {
        font-size: 12px;
        font-weight: 600;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    
    /* Input elements - improved styling */
    [data-testid="stTextInput"] input,
    [data-testid="stSelectbox"] select,
    [data-testid="stNumberInput"] input {
        background-color: var(--input-bg) !important;
        color: var(--input-text) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 6px !important;
    }
    
    /* Placeholder text styling */
    [data-testid="stTextInput"] input::placeholder,
    [data-testid="stSelectbox"] select::placeholder,
    [data-testid="stNumberInput"] input::placeholder,
    input::placeholder,
    textarea::placeholder {
        color: var(--placeholder-text) !important;
        opacity: 1 !important;
    }
    
    /* Firefox specific placeholder styling */
    input::-moz-placeholder,
    textarea::-moz-placeholder {
        color: var(--placeholder-text) !important;
        opacity: 1 !important;
    }
    
    /* Buttons */
    [data-testid="stButton"] > button {
        background-color: var(--accent-color);
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 500;
    }
    
    [data-testid="stButton"] > button:hover {
        background-color: #0C8965;
        opacity: 0.9;
    }
    
    /* Expanders - ensure proper contrast */
    [data-testid="stExpander"] {
        background-color: var(--bg-secondary);
        border: 1px solid var(--card-border);
        border-radius: 8px;
        color: var(--text-primary);
    }
    
    .streamlit-expanderHeader {
        background-color: var(--bg-secondary) !important;
        border-radius: 8px !important;
        border: 1px solid var(--card-border) !important;
        color: var(--text-primary) !important;
    }
    
    /* Expander header text and icon */
    .streamlit-expanderHeader p,
    .streamlit-expanderHeader span,
    .streamlit-expanderHeader div {
        color: var(--text-primary) !important;
    }
    
    /* Expander content */
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] {
        color: var(--text-primary) !important;
    }
    
    /* Dividers */
    hr {
        background-color: var(--border-color);
        border: none;
        height: 1px;
    }
    
    /* Columns and containers */
    [data-testid="column"] {
        background-color: transparent;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--card-border);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-secondary);
    }
    
    /* Code blocks */
    code {
        background-color: var(--bg-secondary);
        color: var(--text-primary);
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.9em;
    }
    
    /* Tables */
    table {
        background-color: var(--bg-secondary);
        color: var(--text-primary);
    }
    
    th {
        background-color: var(--bg-secondary);
        color: var(--text-primary);
        border-color: var(--card-border);
    }
    
    td {
        border-color: var(--card-border);
        color: var(--text-primary);
    }
    
    /* Captions and muted text */
    [class*="caption"], 
    [class*="small-text"],
    .stCaption {
        color: var(--text-muted) !important;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'dataset_loader' not in st.session_state:
        with st.spinner("Loading dataset..."):
            st.session_state.dataset_loader = get_dataset_loader()
    
    if 'search_engine' not in st.session_state:
        st.session_state.search_engine = get_search_engine(st.session_state.dataset_loader)
    
    if 'health_generator' not in st.session_state:
        st.session_state.health_generator = get_health_report_generator()
    
    if 'selected_product' not in st.session_state:
        st.session_state.selected_product = None
    
    if 'search_results' not in st.session_state:
        st.session_state.search_results = []


def display_product_card(product_data: dict):
    """Display a single product's information in a clean card layout."""
    
    # Header with product name and brand
    st.markdown(f"### {product_data.get('product_name', 'Unknown Product')}")
    brands = product_data.get('brands', '')
    if brands:
        st.caption(f"🏷️ {brands}")
    
    # Quick stats row
    nutriscore = product_data.get('nutrition_grade_fr', '')
    nutriscore_num = product_data.get('nutrition-score-fr_100g', 0)
    energy = product_data.get('energy_100g', 0)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if nutriscore:
            st.metric("Nutri-Score", nutriscore.upper())
    
    with col2:
        if energy:
            st.metric("Energy", f"{energy:.0f} kcal")
    
    with col3:
        if nutriscore_num and nutriscore_num != 0:
            st.metric("Score", f"{nutriscore_num:.0f}")
    
    st.markdown("---")
    
    # Nutrition facts in grid
    st.subheader("Nutrition (per 100g)")
    
    nutrition_items = [
        ('energy_100g', 'Energy', 'kcal'),
        ('fat_100g', 'Fat', 'g'),
        ('saturated-fat_100g', 'Sat. Fat', 'g'),
        ('carbohydrates_100g', 'Carbs', 'g'),
        ('sugars_100g', 'Sugars', 'g'),
        ('fiber_100g', 'Fiber', 'g'),
        ('proteins_100g', 'Protein', 'g'),
        ('salt_100g', 'Salt', 'g'),
        ('sodium_100g', 'Sodium', 'mg'),
    ]
    
    # Display in 3-column grid
    for i in range(0, len(nutrition_items), 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            if i + j < len(nutrition_items):
                key, label, unit = nutrition_items[i + j]
                value = product_data.get(key, 0)
                if value and value != '' and value != 0:
                    with col:
                        st.metric(label, f"{value:.1f} {unit}")
    
    # Expandable sections
    with st.expander("📝 Ingredients", expanded=True):
        ingredients = product_data.get('ingredients_text', '')
        if ingredients:
            st.text(ingredients[:1000] + "..." if len(str(ingredients)) > 1000 else ingredients)
        else:
            st.caption("No ingredients information available")
    
    # Labels
    labels = product_data.get('labels_tags', '')
    with st.expander("🏷️ Labels & Certifications"):
        if labels:
            labels_list = str(labels).replace('en:', '').split(',')
            for label in labels_list[:8]:
                if label.strip():
                    st.success(f"✓ {label.strip().title()}")
        else:
            st.caption("No labels")
    
    # Allergens
    allergens = product_data.get('allergens_tags', '')
    with st.expander("🚨 Allergens"):
        if allergens:
            st.markdown(f"**Contains:** {allergens}")
        else:
            st.caption("No allergens listed")
    
    # Additives
    additives = product_data.get('additives_tags', '')
    with st.expander("🧪 Additives"):
        if additives:
            st.text(str(additives)[:800])
        else:
            st.caption("No additives listed")
    
    # Palm oil
    palm = product_data.get('ingredients_from_palm_oil_n', 0)
    may_palm = product_data.get('ingredients_that_may_be_from_palm_oil_n', 0)
    if palm > 0 or may_palm > 0:
        with st.expander("⚠️ Palm Oil"):
            if palm > 0:
                st.warning(f"Contains {int(palm)} ingredient(s) from palm oil")
            if may_palm > 0:
                st.warning(f"May contain {int(may_palm)} ingredient(s) from palm oil")


def display_health_report(product_data: dict):
    """Display health report with clean, structured layout."""
    with st.spinner("Analyzing product..."):
        report = st.session_state.health_generator.generate_report(product_data)
    
    score = report['health_score']
    nutriscore = report.get('nutriscore', '')
    
    # Header
    st.markdown(f"### {report['product_name']}")
    if report.get('brands'):
        st.caption(f"🏷️ {report['brands']}")
    
    # Score cards - using pure Streamlit
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Health Score", f"{score}/100")
        if score >= 70:
            st.success("Good")
        elif score >= 50:
            st.warning("Moderate")
        else:
            st.error("Poor")
    
    with col2:
        if nutriscore:
            st.metric("Nutri-Score", nutriscore.upper())
        else:
            st.metric("Nutri-Score", "N/A")
    
    with col3:
        labels = report.get('labels', '')
        if labels:
            labels_list = str(labels).replace('en:', '').split(',')
            st.metric("Labels", f"{len(labels_list[:3])}")
        else:
            st.metric("Labels", "0")
    
    st.markdown("---")
    
    # LLM Report (if available)
    llm_report = report.get('llm_report')
    if llm_report:
        st.subheader("🤖 AI Analysis")
        st.markdown(llm_report)
        st.markdown("---")
    
    # Key metrics in columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚠️ Risk Assessment")
        st.markdown(report['risk_assessment'])
        
        st.subheader("💡 Recommendations")
        st.markdown(report['recommendations'])
    
    with col2:
        st.subheader("🧪 Additives")
        st.markdown(report['additive_info'])
        
        st.subheader("🦠 Palm Oil")
        st.markdown(report['palm_oil_info'])
    
    # Allergens
    st.subheader("🚨 Allergens")
    st.markdown(report['allergen_info'])
    
    # Daily Values
    with st.expander("📊 Daily Value Percentages"):
        for nutrient, pct in report['daily_value_percentages'].items():
            bar_color = "red" if pct >= 40 else "orange" if pct >= 20 else "green"
            st.markdown(f"**{nutrient.replace('-', ' ').title()}**: {pct:.1f}%")
            st.progress(min(pct / 100, 1.0))


def main():
    """Main application entry point."""
    initialize_session_state()
    
    # Header
    st.title("🍎 Food Nutrition Intelligence")
    st.markdown("Search for food products to get AI-powered health insights")
    
    # Search bar
    col1, col2 = st.columns([4, 1])
    
    with col1:
        search_query = st.text_input(
            "Search products",
            placeholder="e.g., Chocolate, Chips, Rice...",
            label_visibility="collapsed"
        )
    
    with col2:
        search_type = st.selectbox("Search by", ["Product Name", "Ingredient"], label_visibility="collapsed")
    
    # Search button
    if st.button("🔍 Search", use_container_width=True):
        if search_query.strip():
            with st.spinner("Searching..."):
                start_time = time.time()
                
                if search_type == "Product Name":
                    results = st.session_state.search_engine.search(search_query, top_n=5)
                else:
                    results = st.session_state.search_engine.search_by_ingredient(search_query, top_n=10)
                
                elapsed = time.time() - start_time
                st.session_state.search_results = results
                st.session_state.selected_product = None
                
                if results:
                    st.success(f"Found {len(results)} results in {elapsed:.2f}s")
                else:
                    st.warning("No products found")
    
    # Search Results
    if st.session_state.search_results:
        st.divider()
        
        for i, result in enumerate(st.session_state.search_results):
            result_col1, result_col2 = st.columns([5, 1])
            
            with result_col1:
                # Get data for display
                data = result['data']
                name = data.get('product_name', 'Unknown')
                brand = data.get('brands', '')
                ns = data.get('nutrition_grade_fr', '')
                
                display_name = f"**{i+1}. {name}**"
                if brand:
                    display_name += f"  \n_{brand}_"
                if ns:
                    display_name += f"  \nNutri-Score: {ns.upper()}"
                
                st.markdown(display_name)
            
            with result_col2:
                if st.button("View →", key=f"select_{result['index']}", use_container_width=True):
                    st.session_state.selected_product = result['data']
                    st.rerun()
    
    # Product Details
    if st.session_state.selected_product:
        st.divider()
        
        # Tabs
        tab1, tab2 = st.tabs(["📦 Product", "💚 Health"])
        
        with tab1:
            display_product_card(st.session_state.selected_product)
        
        with tab2:
            display_health_report(st.session_state.selected_product)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📊 Dataset")
        total = st.session_state.dataset_loader.get_total_count()
        st.metric("Products", f"{total:,}")
        
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.caption("""
        Food Nutrition Intelligence uses AI to analyze food products and provide health insights based on nutritional data.
        
        **Powered by:** OpenFoodFacts + Groq LLM
        """)
        
        st.markdown("---")
        st.markdown("### ✨ Features")
        st.caption("""
        • Smart product search
        • AI health analysis
        • Nutri-Score ratings
        • Additive warnings
        • Allergen alerts
        • Palm oil detection
        """)


if __name__ == "__main__":
    main()
