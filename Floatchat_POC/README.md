# FloatChat - AI-Powered ARGO Data Explorer

An intelligent chatbot interface for exploring oceanic float data from ARGO datasets. Built with Streamlit and powered by open-source LLMs.

## Features

- Natural language queries for oceanic data
- Interactive map visualizations using Plotly
- Support for multiple parameters (temperature, salinity, pressure)
- Location-based filtering with geocoding
- Real-time data processing and visualization

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your LLM API credentials
   ```

4. Process the data:
   ```bash
   python src/data_consolidation.py
   ```

5. Run the application:
   ```bash
   streamlit run src/app.py
   ```

## Project Structure

- `src/` - Main application code
  - `app.py` - Streamlit main application
  - `components/` - Individual components
    - `interpreter.py` - LLM-based query interpreter
    - `query_engine.py` - Data filtering logic
    - `visualizer.py` - Plotly visualization
  - `data_consolidation.py` - Data preprocessing script
- `data/` - Raw ARGO float data
- `processed_data/` - Consolidated dataset
- `plan/` - Project documentation

## Usage

Ask natural language questions like:
- "Show me temperature data in the Arabian Sea"
- "What's the salinity near Madagascar in 2019?"
- "Display pressure measurements around the Indian Ocean"

## Technology Stack

- **Frontend**: Streamlit
- **Backend**: Python, pandas
- **AI**: Open-source LLMs (Mistral, Llama 3, QWEN)
- **Visualization**: Plotly
- **Data Processing**: pandas, pyarrow
- **Geocoding**: geopy
