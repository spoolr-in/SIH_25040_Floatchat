"""
FloatChat - AI-Powered ARGO Data Explorer
Main Streamlit application for interactive oceanographic data exploration.
"""

import streamlit as st
import pandas as pd
import logging
import os
from pathlib import Path
import sys

# Add src to path for imports
sys.path.append(str(Path(__file__).parent))

from components.interpreter import create_interpreter
from components.query_engine import QueryEngine
from components.visualizer import DataVisualizer
from components.data_summarizer import DataSummarizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="FloatChat - ARGO Data Explorer",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 600;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stats-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.75rem;
        border: 2px solid #e9ecef;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        color: #212529;
    }
    .stats-title {
        color: #495057;
        font-weight: 600;
        margin-bottom: 1rem;
        font-size: 1.1rem;
    }
    .stats-item {
        color: #6c757d;
        margin: 0.5rem 0;
        font-size: 0.95rem;
    }
    .stats-value {
        color: #212529;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_components():
    """Initialize the application components"""
    try:
        # Get project root directory
        project_root = Path(__file__).parent.parent
        data_path = project_root / "processed_data" / "master_dataset.parquet"
        
        if not data_path.exists():
            st.error(f"Master dataset not found at {data_path}")
            st.info("Please run the data consolidation script first: `python src/data_consolidation.py`")
            st.stop()
        
        # Initialize components
        query_engine = QueryEngine(str(data_path))
        visualizer = DataVisualizer()
        interpreter = create_interpreter()
        
        return query_engine, visualizer, interpreter
        
    except Exception as e:
        st.error(f"Failed to initialize components: {str(e)}")
        st.stop()

def display_dataset_info(query_engine):
    """Display dataset information in the sidebar"""
    st.sidebar.header("📊 Dataset Information")
    
    summary = query_engine.get_dataset_summary()
    
    st.sidebar.markdown(f"""
    **Total Records:** {summary.get('total_records', 0):,}
    
    **Float Count:** {summary.get('float_count', 0)}
    
    **Date Range:**
    - Start: {summary.get('date_range', {}).get('start', 'N/A')[:10] if summary.get('date_range', {}).get('start') else 'N/A'}
    - End: {summary.get('date_range', {}).get('end', 'N/A')[:10] if summary.get('date_range', {}).get('end') else 'N/A'}
    
    **Parameter Coverage:**
    """)
    
    param_counts = summary.get('parameter_counts', {})
    for param, count in param_counts.items():
        st.sidebar.markdown(f"- {param.title()}: {count:,} measurements")

def display_example_queries():
    """Display example queries in the sidebar"""
    st.sidebar.header("💡 Example Queries")
    
    examples = [
        "Show me temperature data in the Indian Ocean",
        "What's the salinity around Madagascar?",
        "Display pressure measurements in the Arabian Sea",
        "Temperature data from 2010 to 2015",
        "Salinity between 100-500 meters depth",
        "Show all data near Sri Lanka"
    ]
    
    for i, example in enumerate(examples):
        st.sidebar.code(example, language=None)
    
    st.sidebar.info("💡 Copy any example above and paste it into the search box!")

def process_query(query, interpreter, query_engine, visualizer):
    """Process a user query and return results"""
    try:
        # Extract entities using LLM
        with st.spinner("🧠 Understanding your query..."):
            entities = interpreter.extract_entities(query)
            st.success(f"✅ Interpreted: Looking for {entities.parameter or 'all parameters'}" + 
                      (f" in {entities.location}" if entities.location else ""))
        
        # Execute query
        with st.spinner("🔍 Searching the data..."):
            results_df = query_engine.execute_query(entities)
            
            if results_df.empty:
                st.warning("No data found matching your query. Try a different location or parameter.")
                return None, None
        
        # Create visualization
        with st.spinner("📊 Creating visualization..."):
            fig = visualizer.create_map_visualization(
                results_df, 
                parameter=entities.parameter,
                title=f"Ocean Data: {query}"
            )
        
        return results_df, fig
        
    except Exception as e:
        st.error(f"Error processing query: {str(e)}")
        logger.error(f"Query processing error: {str(e)}")
        return None, None

def display_results(results_df, fig, entities, query_text):
    """Display query results"""
    # Get component instances for this display
    visualizer = DataVisualizer()
    
    # Initialize components (get interpreter for potential LLM use)
    query_engine, _, interpreter = initialize_components()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🗺️ Geographic Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 Summary Statistics")
        
        if entities.parameter and entities.parameter in results_df.columns:
            stats = visualizer.get_summary_stats(results_df, entities.parameter)
            if stats:
                st.markdown(f"""
                <div class="stats-box">
                    <div class="stats-title">{entities.parameter.title()} Statistics</div>
                    <div class="stats-item"><span class="stats-value">Count:</span> {stats['count']:,}</div>
                    <div class="stats-item"><span class="stats-value">Mean:</span> {stats['mean']:.2f} {stats['unit']}</div>
                    <div class="stats-item"><span class="stats-value">Std Dev:</span> {stats['std']:.2f} {stats['unit']}</div>
                    <div class="stats-item"><span class="stats-value">Range:</span> {stats['min']:.2f} - {stats['max']:.2f} {stats['unit']}</div>
                    <div class="stats-item"><span class="stats-value">Median:</span> {stats['median']:.2f} {stats['unit']}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="stats-box">
            <div class="stats-title">Query Results</div>
            <div class="stats-item"><span class="stats-value">Total Points:</span> {len(results_df):,}</div>
            <div class="stats-item"><span class="stats-value">Date Range:</span> {results_df['date'].min().strftime('%Y-%m-%d')} to {results_df['date'].max().strftime('%Y-%m-%d')}</div>
            <div class="stats-item"><span class="stats-value">Geographic Bounds:</span></div>
            <div class="stats-item">Lat: {results_df['latitude'].min():.2f}° to {results_df['latitude'].max():.2f}°</div>
            <div class="stats-item">Lon: {results_df['longitude'].min():.2f}° to {results_df['longitude'].max():.2f}°</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Additional visualizations
    if entities.parameter:
        col3, col4 = st.columns(2)
        
        with col3:
            st.subheader("📅 Time Series")
            time_fig = visualizer.create_time_series(results_df, entities.parameter)
            st.plotly_chart(time_fig, use_container_width=True)
        
        with col4:
            st.subheader("🌊 Depth Profile")
            depth_fig = visualizer.create_depth_profile(results_df, entities.parameter)
            st.plotly_chart(depth_fig, use_container_width=True)
    
    # Intelligent Data Summary Section
    st.subheader("🤖 Intelligent Summary")
    
    # Add option to disable LLM for faster performance
    use_llm = st.sidebar.checkbox("🚀 Use AI Enhancement (slower)", value=True, key="use_llm_summary")
    
    with st.spinner("🧠 Generating intelligent summary..."):
        # Get stats if parameter is available
        stats = None
        if entities.parameter and entities.parameter in results_df.columns:
            stats = visualizer.get_summary_stats(results_df, entities.parameter)
        
        # Use LLM only if enabled and create fast/slow options
        if use_llm:
            summarizer_with_llm = DataSummarizer(interpreter)
            summary_text = summarizer_with_llm.generate_summary(results_df, entities, query_text, stats)
        else:
            # Fast rule-based only
            summarizer_fast = DataSummarizer(None)  # No LLM
            summary_text = summarizer_fast.generate_summary(results_df, entities, query_text, stats)
        
        if summary_text:
            # Create a beautiful summary container
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 15px;
                border-radius: 10px;
                margin: 20px 0 10px 0;
                text-align: center;
            ">
                <h3 style="color: white; margin: 0; font-weight: 600;">
                    🤖 """ + f"""{'AI-Enhanced' if use_llm else 'Quick'}""" + """ Ocean Data Analysis
                </h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Display the summary with proper markdown rendering
            with st.container():
                st.markdown(summary_text, unsafe_allow_html=False)
        else:
            st.info("Summary generation is temporarily unavailable.")
    
    # Show data table (optional)
    if st.checkbox("Show Raw Data Table", key="show_data_table"):
        st.subheader("📋 Data Table")
        display_cols = ['date', 'latitude', 'longitude', 'float_id']
        if entities.parameter and entities.parameter in results_df.columns:
            display_cols.append(entities.parameter)
        
        # Show total count
        st.info(f"Showing first 1000 rows out of {len(results_df):,} total results")
        
        st.dataframe(
            results_df[display_cols].head(1000),
            use_container_width=True,
            height=400
        )

def main():
    """Main application function"""
    # Header
    st.markdown('<h1 class="main-header">🌊 FloatChat - ARGO Data Explorer</h1>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    Ask natural language questions about oceanographic data from ARGO floats. 
    Get instant visualizations and insights powered by AI.
    """)
    
    # Initialize components
    query_engine, visualizer, interpreter = initialize_components()
    
    # Sidebar
    display_dataset_info(query_engine)
    display_example_queries()
    
    # LLM Configuration (sidebar)
    st.sidebar.header("🤖 AI Configuration")
    
    # Test LLM connection with error handling
    try:
        import requests
        response = requests.get('http://localhost:11434/api/tags', timeout=2)
        if response.status_code == 200:
            models = response.json().get('models', [])
            if models:
                st.sidebar.success("✅ LLM Connected")
                st.sidebar.info(f"Model: {models[0].get('name', 'Unknown')}")
                llm_available = True
            else:
                st.sidebar.warning("⚠️ LLM Service Running (No Models)")
                llm_available = False
        else:
            st.sidebar.error("❌ LLM Not Available")
            llm_available = False
    except:
        st.sidebar.error("❌ LLM Not Available")
        st.sidebar.info("Using fallback keyword extraction")
        llm_available = False
    
    # Main chat interface
    st.header("💬 Ask Your Question")
    
    # Initialize session state for results
    if 'current_results' not in st.session_state:
        st.session_state.current_results = None
    if 'current_fig' not in st.session_state:
        st.session_state.current_fig = None
    if 'current_entities' not in st.session_state:
        st.session_state.current_entities = None
    if 'current_query' not in st.session_state:
        st.session_state.current_query = ""
    
    # Query input
    query = st.text_input(
        "What would you like to know about the ocean data?",
        placeholder="e.g., Show me temperature in the Arabian Sea",
        key="main_query_input"
    )
    
    # Process query
    if st.button("🔍 Search", type="primary") and query.strip():
        # Process the query
        results_df, fig = process_query(query, interpreter, query_engine, visualizer)
        
        if results_df is not None and fig is not None:
            # Get entities for display
            entities = interpreter.extract_entities(query)
            
            # Store results in session state
            st.session_state.current_results = results_df
            st.session_state.current_fig = fig
            st.session_state.current_entities = entities
            st.session_state.current_query = query
    
    # Display results from session state if available
    if (st.session_state.current_results is not None and 
        st.session_state.current_fig is not None and 
        st.session_state.current_entities is not None):
        
        # Results header with clear button
        col_header, col_clear = st.columns([4, 1])
        with col_header:
            st.markdown(f"**Results for:** *{st.session_state.current_query}*")
        with col_clear:
            if st.button("🗑️ Clear Results", key="clear_results"):
                st.session_state.current_results = None
                st.session_state.current_fig = None
                st.session_state.current_entities = None
                st.session_state.current_query = ""
                st.rerun()
        
        display_results(
            st.session_state.current_results, 
            st.session_state.current_fig, 
            st.session_state.current_entities,
            st.session_state.current_query
        )

if __name__ == "__main__":
    main()
