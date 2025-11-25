# ABA Security Oracle - Project Analysis & Configuration Guide

## Project Overview

**ABA Security Oracle** is an AI-powered security intelligence platform for Aba, Abia State, Nigeria. It combines:
- Real-time incident clustering and hotspot detection
- Police coverage gap analysis
- Safe route optimization
- AI-powered recommendations using GPT-OSS models
- External data integration via Model Context Protocol (MCP)

---

## Architecture Components

### 1. **Frontend (Streamlit UI)** - `Frontend/app.py`
**Purpose**: Interactive dashboard for security analysis visualization

**Dependencies**:
- `streamlit` - Web application framework
- `plotly` - Interactive visualizations
- `pandas` - Data manipulation
- `numpy` - Numerical operations

**Key Features**:
- Demo data generation for prototyping
- Incident clustering visualization
- Heatmaps and risk assessment dashboards
- AI-powered recommendations display
- Temporal pattern analysis
- Resource allocation suggestions

---

### 2. **Brain (AI Engine)** - `Brain/brain.py`
**Purpose**: AI analysis and decision support using GPT-OSS models

**Dependencies**:
- `anthropic` - Claude API (if configured)
- MCP server integration for context
- Python standard libraries for rule-based fallback

**Key Classes**:
- `SecurityOracle` - Main AI analysis engine
- Methods for:
  - Hotspot analysis with contextual enrichment
  - Overall risk assessment
  - Hotspot prioritization
  - Recommendation generation
  - Resource allocation suggestions
  - Natural language report generation

**Key Features**:
- System prompt for security analysis
- MCP tool integration (weather, social media, news)
- Risk scoring with multiple factors
- Evidence-based recommendations
- Natural language report generation

---

### 3. **Engine (Analysis Modules)** - `Engine/`

#### 3.1 **Clustering** - `clustering.py`
**Purpose**: Identify crime hotspots using DBSCAN clustering

**Dependencies**:
- `scikit-learn` - DBSCAN algorithm
- `pandas` - Data handling
- `numpy` - Numerical operations
- `scipy` - Kernel density estimation

**Key Classes**:
- `IncidentClusterer` - Main clustering engine

**Key Methods**:
- `cluster_incidents()` - Apply DBSCAN to identify hotspots
- `identify_hotspots()` - Rank hotspots by risk
- `compute_density_heatmap()` - KDE for visualization
- `analyze_temporal_patterns()` - Identify peak hours/days
- `get_summary_stats()` - Generate summary statistics

**Algorithm Details**:
- Converts eps parameter from km to degrees
- Weights clusters by recent incidents
- Calculates temporal patterns (hourly, daily, monthly)
- Returns enriched hotspot data with:
  - Centroid coordinates
  - Incident count
  - Risk score
  - Primary incident type
  - Peak hours/days
  - Cluster radius

---

#### 3.2 **Gaps** - `gaps.py`
**Purpose**: Analyze police coverage and identify underserved areas

**Dependencies**:
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `geopy` - Distance calculations

**Key Classes**:
- `CoverageAnalyzer` - Coverage gap detection

**Key Methods**:
- `find_coverage_gaps()` - Grid-based gap analysis
- `calculate_coverage_score()` - Score locations by coverage
- `recommend_station_placement()` - Suggest new station locations
- `generate_coverage_report()` - Comprehensive gap report

**Algorithm Details**:
- Creates analysis grid based on incident locations
- Calculates distance to nearest police station
- Counts nearby incidents within buffer radius
- Assigns severity scores (critical, high, medium, low)
- Recommends optimal station placements

---

#### 3.3 **Routes** - `routes.py`
**Purpose**: Analyze route safety for patrol planning

**Dependencies**:
- `networkx` - Graph/network operations
- `geopy` - Distance calculations
- `pandas` - Data handling

**Key Classes**:
- `RouteAnalyzer` - Route safety analysis

**Key Methods**:
- `analyze_route()` - Comprehensive route analysis
- `_weight_edges()` - Weight road network by incident density
- `_find_nearest_node()` - Map coordinates to road network
- `identify_risk_segments()` - Find dangerous route sections
- `compare_routes()` - Compare shortest vs safest routes

**Features**:
- Loads OpenStreetMap road networks (GraphML format)
- Weights edges based on nearby incidents
- Finds both shortest and safest paths
- Time-based risk adjustments (night = higher risk)
- Generates contextual safety recommendations

---

#### 3.4 **Simulator** - `simulator.py`
**Purpose**: Season/event-based scenario simulation

**Expected Dependencies**:
- `pandas` - Temporal data handling
- `numpy` - Statistical calculations

**Typical Use Cases**:
- Weather event impact modeling
- Holiday incident pattern forecasting
- Large event security planning
- Seasonal trend analysis

---

### 4. **MCP Server (External Data Integration)** - `MCP/server.py`
**Purpose**: Integrate external data sources via Model Context Protocol

**Dependencies**:
- `requests` - HTTP client
- `aiohttp` - Async HTTP
- `httpx` - Modern HTTP client

**Key Classes**:
- `EnhancedMCPServer` - Main MCP server
- `APIRateLimiter` - Rate limiting for API calls

**Available Tools**:

1. **Weather Integration** (`get_weather`)
   - Requires: `OPENWEATHER_API_KEY`
   - Returns: Current conditions, forecast, alerts
   - Cache: 10 minutes (600s)

2. **Social Media Monitoring** (`monitor_twitter`)
   - Requires: `TWITTER_BEARER_TOKEN`
   - Searches for security-related tweets
   - Returns: Tweets with sentiment analysis
   - Cache: 5 minutes (300s)

3. **News Monitoring** (`get_news`)
   - Requires: `NEWSAPI_KEY`
   - Fetches security-related news
   - Filters by relevance
   - Cache: 30 minutes (1800s)

4. **Web Search** (`web_search`)
   - Requires: `SERPAPI_KEY`
   - General web search integration
   - Cache: 1 hour (3600s)

5. **Geocoding** (`geocode_address`, `reverse_geocode`)
   - OpenStreetMap Nominatim API (free, no key needed)
   - Address → coordinates and vice versa

6. **Traffic Information** (`get_traffic`)
   - Mock implementation (real APIs require commercial licenses)

7. **Sentiment Analysis** (`analyze_sentiment`)
   - Rule-based sentiment classification
   - No API required

**Features**:
- Caching with TTL
- Rate limiting per endpoint
- Mock data fallback for missing API keys
- Fallback to mock data when USE_MOCK_DATA=true

---

## File Structure Summary

```
Security/
├── Frontend/
│   └── app.py                    # Streamlit dashboard
├── Brain/
│   └── brain.py                  # GPT-OSS AI engine (SecurityOracle)
├── Engine/
│   ├── __init__.py
│   ├── clustering.py             # Hotspot detection (IncidentClusterer)
│   ├── gaps.py                   # Coverage analysis (CoverageAnalyzer)
│   ├── routes.py                 # Route safety (RouteAnalyzer)
│   └── simulator.py              # Event simulation
├── MCP/
│   └── server.py                 # External API integration (EnhancedMCPServer)
├── data/
│   ├── incidents.csv             # Historical incident data
│   ├── police.csv                # Police station locations
│   ├── aba_roads.graphml         # Road network (OpenStreetMap)
│   └── aba_pois.geojson          # Points of interest
├── maps/
│   └── reports.html              # Generated map reports
├── reports/
│   └── (PDF/report outputs)
├── requirements.txt              # Python dependencies
├── .env                          # Local configuration (git-ignored)
├── .env.example                  # Configuration template
└── Project.txt                   # Project structure doc
```

---

## Dependencies Summary

### **Core Framework**
- `fastapi==0.109.0` - REST API
- `uvicorn==0.27.0` - ASGI server
- `streamlit==1.31.0` - Web dashboard

### **Data Science**
- `pandas==2.1.4` - Data manipulation
- `numpy==1.26.3` - Numerical computing
- `scikit-learn==1.4.0` - ML algorithms (DBSCAN)
- `scipy==1.12.0` - Scientific functions

### **Geospatial**
- `geopandas==0.14.2` - Geographic data
- `networkx==3.2.1` - Route optimization graphs
- `shapely==2.0.2` - Geometric operations
- `geopy==2.4.1` - Distance calculations
- `osmnx==1.9.0` - OpenStreetMap data

### **AI/ML**
- `transformers==4.37.0` - HuggingFace models
- `torch==2.2.0` - PyTorch
- `sentence-transformers==2.3.1` - Semantic embeddings
- `anthropic==0.18.0` - Claude API

### **APIs & External Data**
- `requests==2.31.0` - HTTP requests
- `httpx==0.26.0` - Modern HTTP client
- `aiohttp==3.9.3` - Async HTTP

### **Utilities**
- `pydantic==2.5.3` - Data validation
- `python-dotenv==1.0.0` - Environment variables
- `pyyaml==6.0.1` - Configuration files
- `Jinja2==3.1.3` - Template engine

### **Visualization**
- `plotly==5.18.0` - Interactive charts
- `matplotlib==3.8.2` - Static plots
- `seaborn==0.13.1` - Statistical visualization
- `folium==0.15.1` - Interactive maps

### **Reporting**
- `reportlab==4.0.9` - PDF generation
- `weasyprint==60.2` - HTML to PDF

---

## Environment Variables (.env)

### **Required for Full Functionality**

```env
# Weather data (https://openweathermap.org/api)
OPENWEATHER_API_KEY=your_key

# Social media monitoring (https://developer.twitter.com/)
TWITTER_BEARER_TOKEN=your_token

# News aggregation (https://newsapi.org/)
NEWSAPI_KEY=your_key

# Web search (https://serpapi.com/)
SERPAPI_KEY=your_key

# Optional: Anthropic Claude (https://console.anthropic.com/)
ANTHROPIC_API_KEY=your_key
```

### **Application Settings**

```env
# Enable mock data (true for testing without API keys)
USE_MOCK_DATA=true

# Environment type
APP_ENV=development

# Streamlit server config
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_HEADLESS=true

# API server (if running FastAPI separately)
API_SERVER_PORT=8000
API_SERVER_HOST=127.0.0.1
```

### **Location & Analysis Parameters**

```env
# Aba, Abia State coordinates
DEFAULT_LATITUDE=5.1065
DEFAULT_LONGITUDE=7.3667
DEFAULT_LOCATION_NAME=Aba, Abia State, Nigeria

# Police coverage radius (km)
POLICE_COVERAGE_RADIUS_KM=2.0

# Clustering parameters
HOTSPOT_CLUSTERING_EPS_KM=0.5      # Distance threshold for clustering
HOTSPOT_MIN_SAMPLES=3               # Minimum incidents per cluster
```

### **Data File Paths**

```env
INCIDENTS_DATA_PATH=data/incidents.csv
POLICE_STATIONS_PATH=data/police.csv
ROAD_NETWORK_PATH=data/aba_roads.graphml
POI_DATA_PATH=data/aba_pois.geojson
```

### **Security & Caching**

```env
# JWT secret (generate: openssl rand -hex 32)
JWT_SECRET_KEY=your_secret_key

# Rate limiting
API_RATE_LIMIT_PER_MINUTE=60
TWITTER_RATE_LIMIT_PER_MINUTE=15
NEWS_RATE_LIMIT_PER_MINUTE=100

# Cache TTL (Time To Live) in seconds
WEATHER_CACHE_TTL=600
NEWS_CACHE_TTL=1800
SOCIAL_CACHE_TTL=300
SEARCH_CACHE_TTL=3600
```

### **Optional Features**

```env
# MCP tool integration
ENABLE_MCP_TOOLS=true

# Real-time monitoring
ENABLE_REALTIME_MONITORING=false

# Email alerts (SMTP)
SMTP_SERVER=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
ALERT_EMAIL_RECIPIENTS=

# Slack/webhook notifications
INCIDENT_WEBHOOK_URL=
```

---

## Data Format Requirements

### **Incidents CSV** (`data/incidents.csv`)
```
latitude,longitude,incident_type,timestamp
5.1065,7.3667,robbery,2024-01-15 14:30:00
5.1089,7.3621,assault,2024-01-15 18:45:00
5.0995,7.3705,theft,2024-01-16 10:15:00
```

### **Police Stations CSV** (`data/police.csv`)
```
latitude,longitude,name,district,capacity
5.1100,7.3650,Central Station,Commercial,50
5.0950,7.3800,North Station,Residential,35
```

### **Road Network** (`data/aba_roads.graphml`)
- OpenStreetMap GraphML format
- Contains: nodes with lat/lon, edges with length

### **POIs GeoJSON** (`data/aba_pois.geojson`)
- GeoJSON format
- Features: schools, hospitals, markets, landmarks

---

## Getting Started

### 1. **Install Dependencies**
```bash
python -m pip install -r requirements.txt
```

### 2. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your API keys (or leave as mock for testing)
```

### 3. **Run Streamlit Dashboard**
```bash
streamlit run Frontend/app.py
```

### 4. **Run FastAPI Backend** (optional)
```bash
uvicorn MCP.server:app --host 0.0.0.0 --port 8000
```

---

## Key Insights from Code Analysis

### **Strengths**
1. **Modular Architecture**: Clean separation of concerns (Frontend, AI, Analysis, APIs)
2. **Extensible MCP Integration**: Easy to add new data sources
3. **Production-Ready**: Caching, rate limiting, error handling
4. **Comprehensive Analysis**: Multi-dimensional (spatial, temporal, risk)
5. **AI-Powered**: GPT-OSS integration with fallback to rule-based

### **API Keys Required for Full Functionality**
1. OpenWeather API (weather data)
2. Twitter/X Bearer Token (social monitoring)
3. NewsAPI (news aggregation)
4. SerpAPI (web search)
5. Anthropic API (optional, for Claude)

### **Performance Considerations**
- Caching with configurable TTL
- Rate limiting per API
- Grid-based analysis for coverage gaps
- Efficient distance calculations using GeoPy
- Mock data fallback for development

---

## Running the Application

### **Development (with mock data)**
```bash
# Set USE_MOCK_DATA=true in .env
streamlit run Frontend/app.py
```

### **Production (with real APIs)**
1. Set API keys in `.env`
2. Set `USE_MOCK_DATA=false`
3. Deploy with proper error handling
4. Monitor API quotas

---

## Next Steps for Full Deployment

1. ✅ Install Python dependencies (requirements.txt updated)
2. ✅ Configure environment variables (.env created)
3. ⏳ Populate data files (incidents.csv, police.csv, etc.)
4. ⏳ Set up API keys for external services
5. ⏳ Configure database (optional: PostgreSQL)
6. ⏳ Set up monitoring and logging
7. ⏳ Deploy to production server
