# FloatChat Deployment Guide

## Quick Start

### 1. Automated Setup (Recommended)
```bash
# Clone or navigate to the project directory
cd /home/superblazer/Projects/Floatchat_POC

# Run the automated setup script
./setup.sh
```

### 2. Manual Setup

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Process Data
```bash
python3 src/data_consolidation.py
```

#### Configure LLM (Optional)
Choose one of the following options:

**Option A: Ollama (Local, Recommended)**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama
ollama serve &

# Pull Mistral model
ollama pull mistral

# Test the model
echo "Hello" | ollama run mistral
```

**Option B: Mistral API (Cloud)**
1. Get API key from https://console.mistral.ai
2. Edit `.env` file:
   ```
   LLM_PROVIDER=mistral
   MISTRAL_API_KEY=your_api_key_here
   ```

**Option C: Keyword Fallback (No Setup)**
- The application works without LLM setup using keyword matching

#### Start Application
```bash
streamlit run src/app.py
```

## Usage Guide

### 1. Basic Queries
- "Show me temperature data in the Indian Ocean"
- "What's the salinity around Madagascar?"
- "Display pressure measurements in the Arabian Sea"

### 2. Advanced Queries
- "Temperature data from 2010 to 2015"
- "Salinity between 100-500 meters depth"
- "Show all data near Sri Lanka"

### 3. Supported Parameters
- **Temperature**: Ocean temperature in °C
- **Salinity**: Salinity in PSU (Practical Salinity Units)
- **Pressure**: Water pressure in dbar (approximately depth in meters)

### 4. Supported Locations
**Predefined regions:**
- Arabian Sea
- Bay of Bengal
- Indian Ocean
- Equatorial Indian Ocean
- Southern Ocean
- Madagascar
- Maldives
- Sri Lanka

**Dynamic locations:**
- Any location that can be geocoded (uses Nominatim/OpenStreetMap)

## Architecture Overview

### Phase 1: Data Consolidation
- **Script**: `src/data_consolidation.py`
- **Purpose**: Merges all float data into `processed_data/master_dataset.parquet`
- **Output**: Unified dataset with 34,322+ records from ARGO floats

### Phase 2: Application Components

#### 1. Frontend (`src/app.py`)
- **Technology**: Streamlit
- **Features**: Chat interface, visualizations, history
- **URL**: http://localhost:8501

#### 2. AI Interpreter (`src/components/interpreter.py`)
- **Purpose**: Extracts entities from natural language
- **Providers**: Ollama, Mistral API, Keyword fallback
- **Output**: Structured JSON with parameter, location, date info

#### 3. Query Engine (`src/components/query_engine.py`)
- **Purpose**: Filters data based on extracted entities
- **Features**: Geocoding, location bounds, parameter filtering
- **Technology**: pandas, geopy

#### 4. Visualizer (`src/components/visualizer.py`)
- **Purpose**: Creates interactive visualizations
- **Features**: Maps, time series, depth profiles
- **Technology**: Plotly

## API Reference

### Environment Variables (.env)
```bash
# LLM Configuration
LLM_PROVIDER=ollama           # ollama, mistral, huggingface
LLM_MODEL=mistral            # Model name
LLM_API_URL=http://localhost:11434/api/generate

# API Keys (optional)
MISTRAL_API_KEY=your_key_here

# Application Settings
DATA_PATH=processed_data/master_dataset.parquet
LOG_LEVEL=INFO
```

### Query Entity Structure
```python
{
    "parameter": "temperature",    # temperature, salinity, pressure, null
    "location": "Arabian Sea",     # Geographic location or null
    "date": "2010-01-01",         # Specific date or null
    "date_range": {               # Date range or null
        "start": "2010-01-01",
        "end": "2015-12-31"
    },
    "depth_range": {              # Depth range or null
        "min": 100,
        "max": 500
    }
}
```

## Testing

### Run Component Tests
```bash
python3 test_components.py
```

### Manual Testing
1. Start the application: `streamlit run src/app.py`
2. Navigate to http://localhost:8501
3. Try example queries from the sidebar
4. Check visualizations and data tables

## Performance Considerations

### Data Limits
- Results limited to 10,000 records for performance
- Visualizations sample down to 5,000 points
- Time series and depth profiles use full filtered data

### Memory Usage
- Master dataset: ~0.5 MB (34K records)
- Application memory: ~100-200 MB
- LLM memory (Ollama): ~4-8 GB for Mistral model

### Response Times
- Keyword extraction: <100ms
- LLM extraction (local): 1-3 seconds
- LLM extraction (API): 0.5-2 seconds
- Data filtering: 100-500ms
- Visualization: 200-1000ms

## Troubleshooting

### Common Issues

**1. "Master dataset not found"**
```bash
python3 src/data_consolidation.py
```

**2. "LLM Not Available"**
- Check Ollama is running: `ollama serve`
- Or use keyword fallback (works without LLM)

**3. "Geocoding failed"**
- Internet connection required for unknown locations
- Use predefined regions for offline operation

**4. "No data found"**
- Try broader location terms
- Check spelling of locations
- Use example queries from sidebar

### Log Analysis
```bash
# Check application logs
tail -f ~/.streamlit/logs/streamlit.log

# Enable debug logging
export LOG_LEVEL=DEBUG
streamlit run src/app.py
```

## Deployment Options

### 1. Local Development
- Current setup (localhost:8501)
- Best for development and testing

### 2. Local Network
```bash
streamlit run src/app.py --server.address 0.0.0.0 --server.port 8501
```

### 3. Cloud Deployment
- **Streamlit Cloud**: Push to GitHub, deploy via share.streamlit.io
- **Docker**: Create container for consistent deployment
- **VPS/AWS**: Deploy on virtual private server

### 4. Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python3 src/data_consolidation.py

EXPOSE 8501
CMD ["streamlit", "run", "src/app.py", "--server.address", "0.0.0.0"]
```

## Future Enhancements (Phase 4)

### Planned Features
1. **FAISS Vector Database**: Replace simple filtering with semantic search
2. **Advanced RAG**: Full Retrieval-Augmented Generation system
3. **More LLM Providers**: Llama 3, QWEN integration
4. **Real-time Data**: Connect to live ARGO data feeds
5. **Advanced Analytics**: Statistical analysis, trend detection
6. **Export Features**: PDF reports, CSV downloads
7. **User Authentication**: Multi-user support
8. **Caching**: Redis for improved performance

### MVP to Full RAG Migration
The current MVP provides a solid foundation for migrating to a full RAG system:
- **Query Engine** → Vector database queries
- **Interpreter** → Complex query generation
- **Data Structure** → Vector embeddings
- **Visualization** → Enhanced with ML insights
