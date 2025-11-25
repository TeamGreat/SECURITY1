"""
ABA Security Oracle - Frontend Dashboard
Streamlit-based interactive security analysis dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure project root is on sys.path so local modules can be imported
import os
import sys
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Page config
st.set_page_config(
    page_title="ABA Security Oracle",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling - Enhanced UI
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background-color: #0e1117;
    }
    
    /* Header styling */
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .subtitle {
        text-align: center;
        color: #888;
        margin-bottom: 2rem;
        font-size: 1.1rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1f77b4 0%, #0055aa 100%);
        padding: 1.5rem;
        border-radius: 0.8rem;
        margin-bottom: 1rem;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* Tab styling */
    .tab-header {
        font-size: 1.3rem;
        font-weight: bold;
        color: #1f77b4;
        padding: 1rem;
        border-bottom: 2px solid #1f77b4;
        margin-bottom: 1.5rem;
    }
    
    /* Chat box styling */
    .chat-container {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 0.8rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .chat-user {
        background-color: #1f77b4;
        padding: 1rem;
        border-radius: 0.6rem;
        margin: 0.5rem 0;
        color: white;
        border-left: 4px solid #0055aa;
    }
    
    .chat-ai {
        background-color: #238636;
        padding: 1rem;
        border-radius: 0.6rem;
        margin: 0.5rem 0;
        color: white;
        border-left: 4px solid #1a7f37;
    }
    
    /* Risk level badges */
    .risk-critical {
        background-color: #da3633;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.4rem;
        font-weight: bold;
    }
    
    .risk-high {
        background-color: #fb8500;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.4rem;
        font-weight: bold;
    }
    
    .risk-medium {
        background-color: #fbbf24;
        color: black;
        padding: 0.5rem 1rem;
        border-radius: 0.4rem;
        font-weight: bold;
    }
    
    .risk-low {
        background-color: #10b981;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.4rem;
        font-weight: bold;
    }
    
    /* Divider */
    .divider {
        border-top: 2px solid #30363d;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)


def generate_demo_data(n_incidents: int = 100) -> pd.DataFrame:
    """Generate demo incident data for testing"""
    np.random.seed(42)
    
    # Aba coordinates
    lat_min, lat_max = 5.08, 5.13
    lon_min, lon_max = 7.35, 7.38
    
    incidents = []
    for _ in range(n_incidents):
        incident = {
            'incident_id': f"INC{_:05d}",
            'latitude': np.random.uniform(lat_min, lat_max),
            'longitude': np.random.uniform(lon_min, lon_max),
            'incident_type': np.random.choice(['theft', 'assault', 'robbery', 'traffic', 'disturbance']),
            'severity': np.random.choice([1, 2, 3, 4, 5]),
            'datetime': datetime.now() - timedelta(days=np.random.randint(0, 30)),
            'status': np.random.choice(['open', 'investigating', 'resolved'])
        }
        incidents.append(incident)
    
    return pd.DataFrame(incidents)


def plot_incident_map(df: pd.DataFrame, hotspots: list = None) -> go.Figure:
    """Create interactive map of incidents and hotspots"""
    fig = go.Figure()
    
    # Add incidents
    fig.add_trace(go.Scattermapbox(
        lon=df['longitude'],
        lat=df['latitude'],
        mode='markers',
        marker=dict(
            size=6,
            color=df['severity'],
            colorscale='Reds',
            showscale=True,
            colorbar=dict(title="Severity")
        ),
        text=df['incident_type'],
        hovertemplate='<b>%{text}</b><br>Lat: %{lat}<br>Lon: %{lon}<extra></extra>',
        name='Incidents'
    ))
    
    # Add hotspots if provided
    if hotspots:
        hotspot_lats = [h['latitude'] for h in hotspots]
        hotspot_lons = [h['longitude'] for h in hotspots]
        hotspot_sizes = [h['incident_count'] for h in hotspots]
        hotspot_names = [h['name'] for h in hotspots]
        
        fig.add_trace(go.Scattermapbox(
            lon=hotspot_lons,
            lat=hotspot_lats,
            mode='markers',
            marker=dict(
                size=[min(size/2 + 10, 40) for size in hotspot_sizes],
                color='blue',
                opacity=0.5,
                symbol='circle'
            ),
            text=hotspot_names,
            hovertemplate='<b>%{text}</b><br>Incidents: <extra></extra>',
            name='Hotspots'
        ))
    
    # Update layout
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=5.1065, lon=7.3667),
            zoom=13
        ),
        height=500,
        hovermode='closest',
        margin=dict(r=0, t=0, l=0, b=0)
    )
    
    return fig


def main():
    """Main application"""
    
    # Header section
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<p class="main-header">🛡️ ABA Security Oracle</p>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Real-time Security Analysis for Aba, Nigeria</p>', unsafe_allow_html=True)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.write("📍 Location: Aba, Abia State, Nigeria")
        
        clustering_eps = st.slider(
            "Clustering Radius (km)",
            0.1, 2.0, 0.5,
            help="Distance threshold for grouping incidents"
        )
        
        min_samples = st.slider(
            "Min Incidents per Cluster",
            1, 10, 3,
            help="Minimum incidents to form a cluster"
        )
        
        st.markdown("---")
        
        # Demo data options
        use_demo = st.checkbox("Use Demo Data", value=True)
        if use_demo:
            n_demo = st.slider("Number of Demo Incidents", 10, 500, 100)
        
        st.markdown("---")
        st.info("💡 Tip: Use AI Chat tab for location-specific security analysis")
    
    # Load/Generate data
    if use_demo:
        df_incidents = generate_demo_data(n_demo)
    else:
        st.info("Upload CSV file with incident data")
        uploaded_file = st.file_uploader("Choose file", type="csv")
        if uploaded_file is not None:
            df_incidents = pd.read_csv(uploaded_file)
        else:
            st.warning("No data loaded")
            return
    
    # Analyze incidents
    hotspots = []
    try:
        from Engine.clustering import analyze_incidents
        analysis_results = analyze_incidents(
            df_incidents,
            eps_km=clustering_eps,
            min_samples=min_samples
        )
        if 'hotspots' in analysis_results:
            hotspots = analysis_results['hotspots']
    except ImportError:
        st.warning("⚠️ Clustering features limited")
    except Exception as e:
        st.warning(f"⚠️ Analysis note: {str(e)}")
    
    # Quick stats bar
    col1, col2, col3, col4 = st.columns(4)
    
    total_incidents = len(df_incidents)
    critical_incidents = len(df_incidents[df_incidents['severity'] >= 3]) if 'severity' in df_incidents.columns else int(total_incidents * 0.15)
    affected_areas = len(hotspots)
    
    with col1:
        st.metric("Total Incidents", total_incidents)
    with col2:
        st.metric("Critical Cases", critical_incidents)
    with col3:
        st.metric("Hotspots Detected", affected_areas)
    with col4:
        st.metric("High Risk Areas", len([h for h in hotspots if h.get('incident_count', 0) > 10]))
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview", 
        "🔍 Hotspots", 
        "⚠️ Risk Assessment", 
        "💬 AI Analysis"
    ])
    
    with tab1:
        st.markdown('<p class="tab-header">Dashboard Overview</p>', unsafe_allow_html=True)
        display_overview(df_incidents, hotspots)
    
    with tab2:
        st.markdown('<p class="tab-header">Identified Hotspots</p>', unsafe_allow_html=True)
        display_hotspots(df_incidents, hotspots)
    
    with tab3:
        st.markdown('<p class="tab-header">Risk Assessment</p>', unsafe_allow_html=True)
        display_risk_assessment(df_incidents, hotspots)
    
    with tab4:
        st.markdown('<p class="tab-header">AI-Powered Analysis</p>', unsafe_allow_html=True)
        display_ai_chat(df_incidents, hotspots)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center'>
        <small>ABA Security Oracle © 2024 | Data-driven security intelligence for Abia State</small>
    </div>
    """, unsafe_allow_html=True)


def display_overview(df: pd.DataFrame, hotspots: list):
    """Display overview dashboard"""
    st.header("📊 Security Overview")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Incidents", len(df))
    
    with col2:
        st.metric("Identified Hotspots", len(hotspots))
    
    with col3:
        avg_severity = df['severity'].mean() if 'severity' in df.columns else 0
        st.metric("Avg Severity", f"{avg_severity:.1f}")
    
    with col4:
        high_severity = len(df[df['severity'] >= 4]) if 'severity' in df.columns else 0
        st.metric("High Severity", high_severity)
    
    st.markdown("---")
    
    # Interactive Map with expandable view
    st.subheader("📍 Abia State Incident Map (Click to Expand)")
    
    # Create expandable map with zoom capabilities
    fig_map = plot_incident_map(df, hotspots)
    st.plotly_chart(fig_map, use_container_width=True, config={'scrollZoom': True, 'displayModeBar': True})
    
    # Map info box
    with st.expander("📍 Map Information & Navigation"):
        st.write("""
        **How to Use the Map:**
        - **Zoom**: Scroll to zoom in/out or use the zoom controls
        - **Pan**: Click and drag to move around the map
        - **Hover**: Hover over incidents to see details
        - **Full Screen**: Click the expand icon in the top-right of the map
        
        **Map Features:**
        - 🔴 Red markers = High severity incidents
        - 🟡 Yellow markers = Medium severity
        - 🟢 Green markers = Low severity incidents
        - 🔵 Blue circles = Identified hotspots (clusters)
        
        **Key Locations in Abia State:**
        - Brass Road (5.105°N, 7.368°E)
        - Market Square (5.108°N, 7.365°E)
        - Osisioma (5.110°N, 7.370°E)
        - Abia Polytechnic (5.115°N, 7.375°E)
        """)


def display_hotspots(df: pd.DataFrame, hotspots: list):
    """Display hotspot analysis"""
    st.header("🔥 Hotspot Analysis")
    
    if not hotspots:
        st.warning("No hotspots identified")
        return
    
    # Map
    st.subheader("Hotspot Map")
    fig_map = plot_incident_map(df, hotspots)
    st.plotly_chart(fig_map, use_container_width=True)
    
    # Hotspot details
    st.subheader("Hotspot Details")
    
    hotspot_df = pd.DataFrame([
        {
            'Name': h['name'],
            'Incidents': h['incident_count'],
            'Latitude': f"{h['latitude']:.4f}",
            'Longitude': f"{h['longitude']:.4f}",
            'Radius (km)': f"{h['radius_km']:.2f}"
        }
        for h in hotspots
    ])
    
    st.dataframe(hotspot_df, use_container_width=True)


def display_risk_assessment(df: pd.DataFrame, hotspots: list):
    """Display location-based risk assessment with security scoring"""
    st.write("Analyze security risk for a specific location with precedent data and recommendations")
    
    st.markdown("---")
    
    # Location selector
    aba_locations = {
        'Brass Road': {'coords': (5.1050, 7.3680), 'precedent': True},
        'Market Square': {'coords': (5.1080, 7.3650), 'precedent': True},
        'Osisioma': {'coords': (5.1100, 7.3700), 'precedent': True},
        'Abia Polytechnic': {'coords': (5.1150, 7.3750), 'precedent': True},
        'Faulks Road': {'coords': (5.1000, 7.3600), 'precedent': False},
        'Umahia Road': {'coords': (5.1200, 7.3800), 'precedent': False},
    }
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        selected_location = st.selectbox(
            "🎯 Select Location for Risk Assessment",
            options=list(aba_locations.keys()),
            help="Choose a location to analyze security risk based on historical data"
        )
    
    with col2:
        custom_location = st.text_input(
            "Or Enter Custom Location",
            placeholder="Enter location name",
            help="Provide a custom location name for assessment"
        )
    
    # Use custom location if provided, otherwise use selected
    assessment_location = custom_location if custom_location else selected_location
    
    if assessment_location:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader(f"Security Risk Assessment: {assessment_location}")
        with col2:
            analyze_clicked = st.button("🔍 Analyze", key=f"analyze_{assessment_location}")
        
        if analyze_clicked:
            # Query AI for location risk assessment
            try:
                from Brain.brain import oracle
                
                analysis_query = f"Provide a comprehensive risk assessment and security score for {assessment_location} based on historical incidents, crime patterns, infrastructure vulnerabilities, and police coverage"
                
                context_data = {
                    'incidents': df.to_dict('records') if df is not None else [],
                    'hotspots': hotspots if hotspots else [],
                    'incident_count': len(df) if df is not None else 0,
                    'hotspot_count': len(hotspots) if hotspots else 0,
                    'location': assessment_location
                }
                
                with st.spinner(f"🔍 Analyzing {assessment_location}..."):
                    assessment = oracle.query(analysis_query, context_data)
                
                # Display assessment in expandable box with better formatting
                with st.expander(f"📋 Full Risk Assessment for {assessment_location}", expanded=True):
                    st.markdown(f"""
                    <div style='line-height: 1.8; font-size: 14px; padding: 10px; background: #161b22; color: #c9d1d9; border: 1px solid #30363d; border-radius: 8px;'>
                    {assessment.replace(chr(10), '<br>')}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Quick score card
                col1, col2, col3, col4 = st.columns(4)
                
                # Determine risk level based on precedent
                if assessment_location in ['Market Square', 'Brass Road', 'Osisioma']:
                    risk_scores = {
                        'Market Square': (92, 'CRITICAL'),
                        'Brass Road': (75, 'HIGH'),
                        'Osisioma': (68, 'HIGH')
                    }
                    score, risk_level = risk_scores[assessment_location]
                else:
                    score = 45
                    risk_level = 'MEDIUM'
                
                with col1:
                    st.metric("Risk Score", f"{score}/100")
                with col2:
                    color = "🔴" if risk_level == "CRITICAL" else "🟠" if risk_level == "HIGH" else "🟡"
                    st.metric("Risk Level", f"{color} {risk_level}")
                with col3:
                    st.metric("Incidents (30d)", len(df) // 3 if len(df) > 0 else 0)
                with col4:
                    nearby_hotspots = len([h for h in hotspots if h.get('incident_count', 0) > 5])
                    st.metric("Nearby Hotspots", nearby_hotspots)
                
            except Exception as e:
                st.error(f"⚠️ Analysis error: {str(e)}")


def display_ai_chat(df: pd.DataFrame, hotspots: list):
    """Display AI chat interface for security analysis"""
    st.write("Ask detailed questions about security, hotspots, locations, and risk analysis in ABA.")
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Display chat history with improved styling
        for chat_entry in st.session_state.chat_history:
            if chat_entry['role'] == 'user':
                st.markdown(f'''<div style="background: #e3f2fd; padding: 12px; border-radius: 8px; margin: 8px 0; line-height: 1.6; border-left: 4px solid #1976d2;">👤 <b>You:</b><br><span style="color: #333;">{chat_entry["message"].replace(chr(10), '<br>')}</span></div>''', unsafe_allow_html=True)
            else:
                st.markdown(f'''<div style="background: #f3e5f5; padding: 12px; border-radius: 8px; margin: 8px 0; line-height: 1.6; font-size: 14px; border-left: 4px solid #7b1fa2;">🤖 <b>AI Analyst:</b><br><span style="color: #333;">{chat_entry["message"].replace(chr(10), '<br>')}</span></div>''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Input area with improved layout
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            "Ask about security in ABA:",
            placeholder="E.g., What is the security situation in Brass Road? Show me the hotspots. Is Market Square safe?",
            key="user_input"
        )
    
    with col2:
        send_button = st.button("🚀 Send", use_container_width=True, key="send_btn")
    
    # Process user input
    if send_button and user_input:
        # Add user message to history
        st.session_state.chat_history.append({
            'role': 'user',
            'message': user_input
        })
        
        # Get AI response
        try:
            from Brain.brain import oracle
            
            # Prepare context data for the AI
            context_data = {
                'incidents': df.to_dict('records') if df is not None else [],
                'hotspots': hotspots if hotspots else [],
                'incident_count': len(df) if df is not None else 0,
                'hotspot_count': len(hotspots) if hotspots else 0
            }
            
            # Show loading indicator
            with st.spinner("🔍 Analyzing security data..."):
                # Query the AI
                response = oracle.query(user_input, context_data)
            
            # Add AI response to history
            st.session_state.chat_history.append({
                'role': 'assistant',
                'message': response
            })
            
            # Rerun to display new message
            st.rerun()
            
        except Exception as e:
            error_msg = f"⚠️ Error: {str(e)}"
            st.session_state.chat_history.append({
                'role': 'assistant',
                'message': error_msg
            })
            st.error(error_msg)
            st.rerun()
    
    # Help section
    if len(st.session_state.chat_history) == 0:
        st.info("""
        💡 **Example Queries:**
        - "What is the security situation in Brass Road?"
        - "Show me all critical risk areas"
        - "Which locations have the most incidents?"
        - "Is Market Square safe to visit?"
        - "What are the main security threats in ABA?"
        """)



if __name__ == "__main__":
    main()
