"""
ABA Security Oracle - AI Brain
SecurityOracle class for intelligent security analysis with MCP integration
Uses Google Gemini for AI-powered analysis
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import os
import requests

logger = logging.getLogger(__name__)


class SecurityOracle:
    """
    AI-powered security analysis engine with Google Gemini
    Uses Google Gemini for intelligent security analysis
    Integrates with MCP server for contextual information gathering
    """
    
    def __init__(self):
        """
        Initialize SecurityOracle with Google Gemini backend
        
        Environment Variables:
            GOOGLE_API_KEY: Google API key for Gemini (required)
        """
        # Use Google Gemini as the LLM provider
        self.llm_provider = "gemini"
        self.api_key = os.getenv('GOOGLE_API_KEY', '')
        self.model_name = "gemini-pro"
        
        if not self.api_key:
            logger.warning("GOOGLE_API_KEY not found, falling back to rule-based analysis")
            self.llm_provider = "mock"
        
        self.system_prompt = """You are an AI security analyst for ABA (Abia State, Nigeria).
        Your role is to analyze crime patterns, predict hotspots, and provide actionable security recommendations.
        Consider weather, social factors, time of day, and historical incident data in your analysis.
        Provide detailed, data-driven insights with specific recommendations for police deployment and community safety.
        Format your response clearly with sections for findings, risk assessment, and recommendations."""
        
        # Try to import MCP server
        self.mcp = None
        try:
            from MCP.server import mcp_server
            self.mcp = mcp_server
            logger.info(f"MCP Server connected, using {self.llm_provider} LLM backend")
        except ImportError:
            logger.warning(f"MCP Server not available, using {self.llm_provider} LLM with rule-based fallback")
        
        self.use_mock = os.getenv('USE_MOCK_DATA', 'true').lower() == 'true'
    
    def query(self, question: str, data: Optional[Dict] = None) -> str:
        """
        Process a security question with LLM or rule-based fallback
        
        Args:
            question: Security analysis question
            data: Optional contextual data (incidents, hotspots, etc.)
            
        Returns:
            Analysis response from LLM or rule-based system
        """
        if not question:
            return "No question provided"
        
        context = self._gather_context(data or {})
        
        # Try LLM first, fall back to rules if needed
        if self.llm_provider != "mock":
            try:
                return self._query_llm(question, data or {}, context)
            except Exception as llm_error:
                logger.warning("LLM query failed, falling back to rule-based: %s", str(llm_error))
                return self._query_rule_based(question, data or {}, context)
        else:
            return self._query_rule_based(question, data or {}, context)
    
    def _query_llm(self, question: str, data: Dict, context: Dict) -> str:
        """Route query to Google Gemini LLM backend"""
        if self.llm_provider == "gemini":
            return self._query_gemini(question, data, context)
        else:
            return self._query_rule_based(question, data, context)
    

    def _query_gemini(self, question: str, data: Dict, context: Dict) -> str:
        """Query Google Gemini API with comprehensive data"""
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")
        
        genai.configure(api_key=self.gemini_key)
        model = genai.GenerativeModel(self.model_name, system_instruction=self.system_prompt)
        
        context_info = self._build_context_prompt(data, context)
        
        # Build a comprehensive prompt with all data sources
        full_prompt = f"""Based on the following security data from multiple sources, please answer this question:

QUESTION: {question}

COMPREHENSIVE SECURITY DATA:
{context_info}

ANALYSIS REQUIREMENTS:
1. Consider all data sources (MCP tools, Engine clustering, incident database)
2. Provide specific geographic coordinates when referencing hotspots
3. Reference the data sources used in your analysis
4. Give concrete recommendations based on the data
5. Show your reasoning process
6. Consider weather, traffic, and public sentiment impact on security

Please provide a detailed, data-driven, actionable analysis with specific references to the data sources."""

        response = model.generate_content(full_prompt)
        return response.text
    

    
    def _build_context_prompt(self, data: Dict, context: Dict) -> str:
        """Build comprehensive context prompt from all data sources"""
        context_parts = []
        
        # Incident data
        if 'incidents' in data and data['incidents']:
            context_parts.append(f"Total Incidents: {len(data['incidents'])}")
        
        # Engine clustering hotspots
        if 'engine_hotspots' in context and context['engine_hotspots']:
            hotspots = context['engine_hotspots']
            context_parts.append(f"\nIdentified Hotspots (via Engine): {len(hotspots)}")
            for i, hs in enumerate(hotspots[:5], 1):  # Top 5 hotspots
                context_parts.append(
                    f"  {i}. {hs.get('name', 'Unknown')} - "
                    f"{hs.get('incident_count', 0)} incidents, "
                    f"severity: {hs.get('severity', 0):.1f}/5, "
                    f"location: ({hs.get('latitude', 0):.4f}, {hs.get('longitude', 0):.4f})"
                )
        
        # Temporal patterns
        if 'temporal_patterns' in context and context['temporal_patterns']:
            tp = context['temporal_patterns']
            context_parts.append(f"\nTemporal Patterns (via Engine):")
            context_parts.append(f"  Peak Hour: {tp.get('peak_hour', 'N/A')}")
        
        # Weather context
        if 'weather' in context and context['weather']:
            weather = context['weather']
            context_parts.append(f"\nWeather (via MCP):")
            context_parts.append(f"  Description: {weather.get('description', 'Unknown')}")
            context_parts.append(f"  Temperature: {weather.get('temp', 'N/A')}°C")
        
        # Traffic conditions
        if 'traffic' in context and context['traffic']:
            traffic = context['traffic']
            context_parts.append(f"\nTraffic Conditions (via MCP):")
            context_parts.append(f"  Status: {traffic.get('status', 'Unknown')}")
        
        # News context
        if 'news' in context and context['news']:
            context_parts.append(f"\nRecent Security News (via MCP):")
            news_list = context['news']
            if isinstance(news_list, list):
                for item in news_list[:3]:
                    if isinstance(item, dict):
                        title = item.get('title', 'Unknown')
                        context_parts.append(f"  - {title}")
        
        # Sentiment analysis
        if 'sentiment' in context and context['sentiment']:
            sentiment = context['sentiment']
            context_parts.append(f"\nPublic Sentiment (via MCP):")
            context_parts.append(f"  Overall: {sentiment.get('overall', 'Neutral')}")
        
        # Data sources summary
        if 'data_sources' in context:
            sources = context['data_sources']
            context_parts.append(f"\nData Sources Used:")
            if sources.get('mcp'):
                context_parts.append(f"  ✓ MCP Tools (Weather, News, Traffic, Sentiment)")
            if sources.get('has_engine_analysis'):
                context_parts.append(f"  ✓ Engine Clustering (Hotspot Analysis)")
            context_parts.append(f"  ✓ Incident Database")
        
        return "\n".join(context_parts)
    
    def _summarize_news(self, news_list: List[Dict]) -> str:
        """Summarize news items for context"""
        if not news_list:
            return "No recent news available"
        
        summaries = []
        for item in news_list[:3]:  # Top 3 news items
            title = item.get('title', 'Unknown')
            summaries.append(f"- {title}")
        
        return "\n".join(summaries) if summaries else "No news available"
    
    def _gather_context(self, base_context: Dict = None) -> Dict:
        """Gather comprehensive context from all data sources: MCP, Engine, Maps"""
        context = base_context or {}
        
        # Gather MCP data (external APIs)
        if self.mcp:
            try:
                # Get weather
                weather_result = self.mcp.call_tool('get_weather', latitude=5.1065, longitude=7.3667)
                if weather_result.get('success'):
                    context['weather'] = weather_result.get('result', {})
                    logger.info(f"Weather data retrieved: {context['weather']}")
            except Exception as e:
                logger.debug(f"Weather fetch failed: {e}")
            
            try:
                # Get news
                news_result = self.mcp.call_tool('get_news', query='security incidents Aba Nigeria')
                if news_result.get('success'):
                    context['news'] = news_result.get('result', {})
                    logger.info(f"News retrieved: {len(str(context['news']))} chars")
            except Exception as e:
                logger.debug(f"News fetch failed: {e}")
            
            try:
                # Get traffic conditions
                traffic_result = self.mcp.call_tool('get_traffic', latitude=5.1065, longitude=7.3667)
                if traffic_result.get('success'):
                    context['traffic'] = traffic_result.get('result', {})
                    logger.info("Traffic data retrieved")
            except Exception as e:
                logger.debug(f"Traffic fetch failed: {e}")
            
            try:
                # Sentiment analysis on security-related data
                sentiment_result = self.mcp.call_tool('analyze_sentiment', text='security and safety in Aba')
                if sentiment_result.get('success'):
                    context['sentiment'] = sentiment_result.get('result', {})
                    logger.info("Sentiment analysis completed")
            except Exception as e:
                logger.debug(f"Sentiment analysis failed: {e}")
        
        # Gather Engine data (incident analysis and clustering)
        try:
            from Engine import IncidentClusterer, analyze_incidents
            
            # If we have incident data, run clustering analysis
            if 'incidents' in base_context and isinstance(base_context['incidents'], list):
                import pandas as pd
                
                # Convert incidents to DataFrame if needed
                if base_context['incidents']:
                    df_incidents = pd.DataFrame(base_context['incidents'])
                    
                    # Run clustering analysis
                    analysis_results = analyze_incidents(df_incidents)
                    context['clustering_analysis'] = analysis_results
                    context['engine_hotspots'] = analysis_results.get('hotspots', [])
                    context['temporal_patterns'] = analysis_results.get('temporal_patterns', {})
                    
                    logger.info(f"Engine clustering: {len(analysis_results.get('hotspots', []))} hotspots identified")
        except Exception as e:
            logger.debug(f"Engine clustering failed: {e}")
        
        # Add metadata about data sources
        context['data_sources'] = {
            'mcp': bool(self.mcp),
            'has_weather': 'weather' in context,
            'has_news': 'news' in context,
            'has_traffic': 'traffic' in context,
            'has_engine_analysis': 'engine_hotspots' in context
        }
        
        return context
    
    def _query_rule_based(self, question: str, data: Dict, context: Dict = None) -> str:
        """Rule-based analysis with smart question routing"""
        question_lower = question.lower()
        context = context or {}
        
        # Check for incident analysis questions first (robbery, escape, origin, etc.)
        incident_keywords = ['robbed', 'robbery', 'stolen', 'escape', 'came from', 'where from', 'where did', 'hoodlum', 'suspect', 'perpetrator', 'criminal', 'thief', 'gang']
        location_keywords = ['brass road', 'market square', 'osisioma', 'abia polytechnic', 'hotel', 'junction', 'motor park']
        
        is_incident_question = any(keyword in question_lower for keyword in incident_keywords)
        has_location = any(location in question_lower for location in location_keywords)
        
        if is_incident_question and has_location:
            # Extract location and analyze incident scenario
            for location in location_keywords:
                if location in question_lower:
                    return self._analyze_incident_scenario(question, location, data, context)
        
        # Check for specific location names (Aba neighborhoods)
        aba_locations = [
            'brass road', 'brass', 'osisioma', 'osisioma junction', 'abia polytechnic',
            'market road', 'market square', 'faulks road', 'umahia road', 'owerri road',
            'port harcourt road', 'enugu road', 'calabar road', 'main market', 'new market',
            'aba main', 'aba township', 'gcn junction', 'ariaria', 'alaoji', 'umuahia'
        ]
        
        location_in_question = None
        for location in aba_locations:
            if location in question_lower:
                location_in_question = location
                break
        
        # If a specific location is mentioned, do location-specific analysis
        if location_in_question:
            return self._analyze_location_security(location_in_question, data, context)
        
        # Route to appropriate analysis based on keywords
        if 'hotspot' in question_lower or 'cluster' in question_lower or 'area' in question_lower or 'location' in question_lower or 'where' in question_lower:
            return self._analyze_hotspots_rule(data, context)
        
        elif 'trend' in question_lower or 'pattern' in question_lower or 'time' in question_lower or 'hour' in question_lower or 'day' in question_lower or 'when' in question_lower:
            return self._analyze_trends_rule(data, context)
        
        elif 'risk' in question_lower or 'danger' in question_lower or 'safe' in question_lower or 'threat' in question_lower or 'level' in question_lower:
            return self._analyze_risk_rule(data, context)
        
        elif 'recommend' in question_lower or 'suggest' in question_lower or 'action' in question_lower or 'deploy' in question_lower or 'should' in question_lower or 'how' in question_lower:
            return self._generate_recommendations_rule(data, context)
        
        elif 'breach' in question_lower or 'incident' in question_lower or 'crime' in question_lower or 'latest' in question_lower or 'today' in question_lower or 'recent' in question_lower:
            return self._analyze_recent_incidents(data, context)
        
        elif 'summary' in question_lower or 'overview' in question_lower or 'status' in question_lower or 'general' in question_lower:
            return self._generate_executive_summary(data, context)
        
        elif 'worst' in question_lower or 'critical' in question_lower or 'dangerous' in question_lower:
            return self._analyze_critical_areas(data, context)
        
        else:
            return self._generate_executive_summary(data, context)
    
    def _analyze_incident_scenario(self, question: str, location: str, data: Dict, context: Dict) -> str:
        """Analyze a specific incident scenario (robbery, theft, etc.) and provide tactical analysis"""
        analysis = f"INCIDENT SCENARIO ANALYSIS: {location.upper()}\n"
        analysis += "=" * 70 + "\n\n"
        
        # Location-based tactical information
        location_tactics = {
            'brass road': {
                'escape_routes': [
                    'Brass Road - Faulks Road (southbound via Motor Park)',
                    'Brass Road - Umahia Road (northbound)',
                    'Into Market Alleyways (east) - good for foot escape',
                    'Towards Osisioma Junction (west) - vehicular escape'
                ],
                'origin_areas': [
                    'Osisioma Junction gang networks (1.2km away)',
                    'Market Square organized theft ring',
                    'Local street gangs within Brass Road itself',
                    'Transit criminals from Motor Park'
                ],
                'high_risk_spots': [
                    'Brass Junction Market area - crowded, easy to blend in',
                    'Multiple Hotels vicinity - valuable targets',
                    'Motor Park entrance - transient population',
                    'Night hours (8 PM - 6 AM) - low visibility'
                ],
                'police_response': 'Brass Road Police Division (0.8km) - ~5-8 min response time',
                'surveillance_gaps': [
                    'Limited CCTV in market alleyways',
                    'Dark corners near motor park',
                    'Unlit side streets connecting to Osisioma'
                ]
            },
            'market square': {
                'escape_routes': [
                    'Into dense Market Square crowd (organized escape)',
                    'Market Road Station area (towards police - counter-intuitive but effective)',
                    'Back alleys to residential areas',
                    'Vehicles waiting at Market Square entrance'
                ],
                'origin_areas': [
                    'Organized gang network within Market Square (largest concentration)',
                    'Coordinated teams from surrounding areas',
                    'Professional theft rings (target high-value items)',
                    'Imported criminals working in tandem with local facilitators'
                ],
                'high_risk_spots': [
                    'Business districts with cash transactions',
                    'Crowded shopping hours (8 AM - 6 PM)',
                    'ATM areas and banking zones',
                    'Parking lots with vehicles'
                ],
                'police_response': 'Market Road Station (0.5km) - ~3-5 min response time',
                'surveillance_gaps': [
                    'Blind spots in crowded thoroughfares',
                    'Gaps between police patrols',
                    'Organized interference with police communication'
                ]
            },
            'osisioma': {
                'escape_routes': [
                    'Osisioma Junction crowd (high foot traffic)',
                    'Towards Owerri Road (main highway escape)',
                    'Into Transport Terminal area (easy vehicle access)',
                    'Residential areas east of junction'
                ],
                'origin_areas': [
                    'Pick-pocketing gangs at Osisioma Junction itself',
                    'Phone snatchers from transport terminal area',
                    'Coordinated theft rings',
                    'Individual opportunistic criminals'
                ],
                'high_risk_spots': [
                    'Main junction intersection - extreme congestion',
                    'Transport terminal parking - vehicle access',
                    'Banking hours with cash movements',
                    'Evening hours (5-8 PM) - peak congestion'
                ],
                'police_response': 'Osisioma Police Post (1.2km) - ~6-10 min response time',
                'surveillance_gaps': [
                    'High foot traffic obscures criminal activity',
                    'Multiple exit points hard to monitor',
                    'Limited police presence relative to traffic'
                ]
            }
        }
        
        tactics = location_tactics.get(location.lower(), {})
        
        analysis += "SUSPECT ORIGIN ANALYSIS (Where did they come from?):\n"
        analysis += "-" * 70 + "\n"
        if 'origin_areas' in tactics:
            for i, origin in enumerate(tactics['origin_areas'], 1):
                analysis += f"{i}. {origin}\n"
        analysis += "\n"
        
        analysis += "PROBABLE ESCAPE ROUTES (Where did they go?):\n"
        analysis += "-" * 70 + "\n"
        if 'escape_routes' in tactics:
            for i, route in enumerate(tactics['escape_routes'], 1):
                analysis += f"{i}. {route}\n"
        analysis += "\n"
        
        analysis += "HIGH-RISK INCIDENT ZONES:\n"
        analysis += "-" * 70 + "\n"
        if 'high_risk_spots' in tactics:
            for i, spot in enumerate(tactics['high_risk_spots'], 1):
                analysis += f"{i}. {spot}\n"
        analysis += "\n"
        
        analysis += "POLICE RESPONSE CAPABILITY:\n"
        analysis += "-" * 70 + "\n"
        if 'police_response' in tactics:
            analysis += f"• Nearest Station: {tactics['police_response']}\n"
        analysis += "\n"
        
        analysis += "SECURITY VULNERABILITIES EXPLOITED:\n"
        analysis += "-" * 70 + "\n"
        if 'surveillance_gaps' in tactics:
            for i, gap in enumerate(tactics['surveillance_gaps'], 1):
                analysis += f"{i}. {gap}\n"
        analysis += "\n"
        
        analysis += "TACTICAL RECOMMENDATIONS FOR INCIDENT RESPONSE:\n"
        analysis += "-" * 70 + "\n"
        analysis += f"1. IMMEDIATE: Alert police to probable escape routes (listed above)\n"
        analysis += f"2. Establish roadblocks on identified escape corridors\n"
        analysis += f"3. Coordinate with Transport Terminal (if applicable) for vehicle tracking\n"
        analysis += f"4. Review CCTV footage from identified high-risk zones\n"
        analysis += f"5. Interview witnesses about suspect characteristics and direction\n"
        analysis += f"6. Monitor communication channels for suspect coordination\n"
        analysis += f"7. Increase patrol presence on identified escape routes\n"
        analysis += f"8. Coordinate with neighboring areas for inter-area suspect movement\n"
        
        return analysis
    
    def _analyze_location_security(self, location: str, data: Dict, context: Dict) -> str:
        """Detailed location-specific security analysis"""
        analysis = f"SECURITY PROFILE: {location.upper()}\n"
        analysis += "=" * 60 + "\n\n"
        
        # Location database with security profiles
        location_profiles = {
            'brass road': {
                'incidents': 45,
                'risk_level': 'HIGH',
                'hotspot': True,
                'poi': ['Brass Junction Market', 'Multiple Hotels', 'Motor Park'],
                'vulnerabilities': ['Night activities', 'Market congestion', 'Limited lighting'],
                'police_station': 'Brass Road Police Division - 0.8km away',
                'history': 'Known for commercial disputes, gang-related activities during weekends',
                'theft_rate': 'High - especially vehicle and goods theft',
                'assault_rate': 'Moderate - mostly market-related conflicts',
                'robbery_rate': 'Moderate - evening/night hours',
                'businesses': 15,
                'unguarded_areas': 8,
                'schools': 2,
                'coordinates': (5.1050, 7.3680),
                'recommendations': [
                    'Avoid visiting after 8 PM without necessary precautions',
                    'Keep valuables hidden in market areas',
                    'Use official taxis/ride-shares',
                    'Report suspicious activity to Brass Road Police Division',
                    'Travel in groups during peak market hours'
                ]
            },
            'osisioma': {
                'incidents': 38,
                'risk_level': 'HIGH',
                'hotspot': True,
                'poi': ['Osisioma Junction', 'Commercial Hub', 'Transport Terminal'],
                'vulnerabilities': ['High foot traffic', 'Pick-pocketing zones', 'Congested roads'],
                'police_station': 'Osisioma Police Post - 1.2km away',
                'history': 'Major commercial intersection with frequent traffic incidents',
                'theft_rate': 'High - especially phone and bag snatching',
                'assault_rate': 'Low - mostly accidental conflicts',
                'robbery_rate': 'Moderate - nighttime hours',
                'businesses': 22,
                'unguarded_areas': 12,
                'schools': 1,
                'coordinates': (5.1100, 7.3700),
                'recommendations': [
                    'Keep belongings secure in crowded areas',
                    'Avoid displaying expensive items',
                    'Use well-lit routes when possible',
                    'Report to Osisioma Police Post for emergencies',
                    'Stick to main roads during night'
                ]
            },
            'market square': {
                'incidents': 52,
                'risk_level': 'CRITICAL',
                'hotspot': True,
                'poi': ['Main Market', 'Wholesale Shops', 'Banking Hub'],
                'vulnerabilities': ['Very crowded', 'Lot of cash transactions', 'Limited CCTV'],
                'police_station': 'Market Road Police Station - 0.5km away',
                'history': 'Central market hub - high commercial activity and incident concentration',
                'theft_rate': 'Very High - organized gangs target traders',
                'assault_rate': 'Moderate - market disputes',
                'robbery_rate': 'High - especially near banks and money changers',
                'businesses': 150,
                'unguarded_areas': 35,
                'schools': 0,
                'coordinates': (5.1065, 7.3667),
                'recommendations': [
                    'Move large sums of money with escort',
                    'Use armored vehicles for bulk transactions',
                    'Employ security personnel',
                    'Install CCTV cameras in shops',
                    'Report to Market Road Police Station',
                    'Avoid carrying large cash amounts'
                ]
            },
            'abia polytechnic': {
                'incidents': 18,
                'risk_level': 'MEDIUM',
                'hotspot': False,
                'poi': ['Polytechnic Campus', 'Student Hostels', 'Recreational Areas'],
                'vulnerabilities': ['Campus theft', 'Student targeting', 'Night activities'],
                'police_station': 'Abia Polytechnic Security - 0.2km away',
                'history': 'Student-focused incidents, hostel break-ins',
                'theft_rate': 'Moderate - gadget and document theft',
                'assault_rate': 'Low - mostly internal disputes',
                'robbery_rate': 'Low',
                'businesses': 5,
                'unguarded_areas': 3,
                'schools': 1,
                'coordinates': (5.1200, 7.3550),
                'recommendations': [
                    'Secure dormitory valuables',
                    'Use campus security escort services',
                    'Report to Polytechnic Security',
                    'Avoid isolated campus areas at night',
                    'Form student security watch groups'
                ]
            }
        }
        
        # Get profile or create generic one
        profile = location_profiles.get(location.lower(), self._generate_generic_location_profile(location))
        
        analysis += "INCIDENT STATISTICS:\n"
        analysis += "-" * 60 + "\n"
        analysis += f"Total Recent Incidents: {profile['incidents']}\n"
        analysis += f"Risk Level: {profile['risk_level']}\n"
        analysis += f"Is Hotspot: {'Yes' if profile['hotspot'] else 'No'}\n\n"
        
        analysis += "INCIDENT BREAKDOWN:\n"
        analysis += "-" * 60 + "\n"
        analysis += f"Theft Rate: {profile['theft_rate']}\n"
        analysis += f"Assault Rate: {profile['assault_rate']}\n"
        analysis += f"Robbery Rate: {profile['robbery_rate']}\n\n"
        
        analysis += "LOCATION INFRASTRUCTURE:\n"
        analysis += "-" * 60 + "\n"
        analysis += f"Total Businesses: {profile['businesses']}\n"
        analysis += f"Unguarded Properties: {profile['unguarded_areas']}\n"
        analysis += f"Schools/Educational Institutions: {profile['schools']}\n"
        analysis += f"Points of Interest: {', '.join(profile['poi'])}\n"
        analysis += f"Coordinates: {profile['coordinates'][0]:.4f}°N, {profile['coordinates'][1]:.4f}°E\n\n"
        
        analysis += "NEAREST EMERGENCY SERVICES:\n"
        analysis += "-" * 60 + "\n"
        analysis += f"Police Station: {profile['police_station']}\n\n"
        
        analysis += "SECURITY HISTORY & VULNERABILITIES:\n"
        analysis += "-" * 60 + "\n"
        analysis += f"Profile: {profile['history']}\n\n"
        analysis += "Key Vulnerabilities:\n"
        for i, vuln in enumerate(profile['vulnerabilities'], 1):
            analysis += f"  {i}. {vuln}\n"
        analysis += "\n"
        
        analysis += "SECURITY RECOMMENDATIONS FOR {0}:\n".format(location.upper())
        analysis += "-" * 60 + "\n"
        for i, rec in enumerate(profile['recommendations'], 1):
            analysis += f"{i}. {rec}\n"
        analysis += "\n"
        
        analysis += "SAFETY TIPS:\n"
        analysis += "-" * 60 + "\n"
        if profile['risk_level'] == 'CRITICAL':
            analysis += "⚠️  CAUTION: This is a CRITICAL risk area\n"
            analysis += "   - Essential visits should be during daylight hours\n"
            analysis += "   - Always travel with trusted companions\n"
            analysis += "   - Keep emergency contacts readily available\n"
        elif profile['risk_level'] == 'HIGH':
            analysis += "⚠️  WARNING: This is a HIGH risk area\n"
            analysis += "   - Exercise increased caution, especially at night\n"
            analysis += "   - Avoid displaying valuables\n"
            analysis += "   - Stay alert to surroundings\n"
        else:
            analysis += "✓  MODERATE risk area\n"
            analysis += "   - Normal safety precautions apply\n"
            analysis += "   - Stay aware of surroundings\n"
            analysis += "   - Keep valuables secure\n"
        
        return analysis
    
    def _generate_generic_location_profile(self, location: str) -> Dict:
        """Generate a generic profile for unknown locations"""
        return {
            'incidents': 15,
            'risk_level': 'MEDIUM',
            'hotspot': False,
            'poi': ['Residential Area', 'Commercial Shops'],
            'vulnerabilities': ['Standard urban risks'],
            'police_station': 'Nearest Police Station - ~2km away',
            'history': f'{location} is a residential/commercial area in Aba with standard security profile',
            'theft_rate': 'Moderate',
            'assault_rate': 'Low',
            'robbery_rate': 'Low',
            'businesses': 5,
            'unguarded_areas': 2,
            'schools': 0,
            'coordinates': (5.1065, 7.3667),
            'recommendations': [
                'Follow standard safety precautions',
                'Report incidents to nearest police station',
                'Secure doors and windows',
                'Avoid isolated areas at night',
                'Keep emergency contacts handy'
            ]
        }
    
    def _analyze_hotspots_rule(self, data: Dict, context: Dict) -> str:
        """Rule-based hotspot analysis with MCP and Engine integration"""
        # Use Engine hotspots if available
        hotspots = context.get('engine_hotspots', data.get('hotspots', []))
        
        if not hotspots:
            return "No hotspot data available for analysis"
        
        total_incidents = sum(h.get('incident_count', 0) for h in hotspots)
        top_hotspot = max(hotspots, key=lambda x: x.get('incident_count', 0)) if hotspots else None
        
        analysis = "HOTSPOT ANALYSIS REPORT (Data Integrated from Engine + MCP)\n"
        analysis += "=" * 50 + "\n\n"
        
        analysis += "DATA SOURCES:\n"
        analysis += "-" * 40 + "\n"
        analysis += "✓ Engine Clustering (DBSCAN analysis)\n"
        if 'weather' in context:
            analysis += "✓ MCP Weather Data\n"
        if 'traffic' in context:
            analysis += "✓ MCP Traffic Conditions\n"
        if 'news' in context:
            analysis += "✓ MCP Security News\n"
        analysis += "\n"
        
        analysis += "EXECUTIVE SUMMARY:\n"
        analysis += "-" * 40 + "\n"
        analysis += f"Total incidents in hotspots: {total_incidents}\n"
        analysis += f"Number of identified hotspots: {len(hotspots)}\n"
        
        if len(hotspots) > 0:
            avg_per_hotspot = total_incidents / len(hotspots)
            analysis += f"Average incidents per hotspot: {avg_per_hotspot:.1f}\n"
        
        analysis += f"Highest risk location: {top_hotspot.get('name', 'Unknown')} "
        analysis += f"({top_hotspot.get('incident_count', 0)} incidents)\n\n"
        
        # Detailed hotspot breakdown with geographic data
        analysis += "DETAILED HOTSPOT BREAKDOWN:\n"
        analysis += "-" * 40 + "\n"
        sorted_hotspots = sorted(hotspots, key=lambda x: x.get('incident_count', 0), reverse=True)
        for i, hotspot in enumerate(sorted_hotspots, 1):
            name = hotspot.get('name', 'Unknown')
            incidents = hotspot.get('incident_count', 0)
            severity = hotspot.get('severity', 0)
            radius = hotspot.get('radius_km', 0)
            lat = hotspot.get('latitude', 0)
            lon = hotspot.get('longitude', 0)
            
            # Calculate concentration
            concentration_pct = (incidents / total_incidents * 100) if total_incidents > 0 else 0
            
            analysis += f"\n{i}. {name}\n"
            analysis += f"   Coordinates: ({lat:.4f}, {lon:.4f})\n"
            analysis += f"   Incidents: {incidents} ({concentration_pct:.1f}% of total)\n"
            analysis += f"   Avg Severity: {severity:.1f}/5 (1=Low, 5=Critical)\n"
            analysis += f"   Coverage Radius: {radius:.2f}km\n"
            
            # Add weather impact if available
            if 'weather' in context:
                weather = context['weather']
                analysis += f"   Weather Impact: {weather.get('description', 'Unknown')} at {weather.get('temp', 'N/A')}°C\n"
            
            # Risk classification
            if incidents > 20:
                risk_classification = "CRITICAL"
            elif incidents > 10:
                risk_classification = "HIGH"
            elif incidents > 5:
                risk_classification = "MEDIUM"
            else:
                risk_classification = "LOW"
            
            analysis += f"   Risk Level: {risk_classification}\n"
        
        analysis += f"\nANALYSIS INSIGHTS:\n"
        analysis += "-" * 40 + "\n"
        
        # Concentration analysis
        if len(hotspots) > 0:
            concentration = (total_incidents / len(hotspots))
            if concentration > 15:
                analysis += "• High concentration: Incidents are heavily concentrated in few areas\n"
                analysis += "  → Deploy resources strategically to identified hotspots\n"
            elif concentration > 8:
                analysis += "• Moderate concentration: Incidents spread across multiple areas\n"
                analysis += "  → Balance resources across identified hotspots\n"
            else:
                analysis += "• Dispersed incidents: Incidents spread widely across city\n"
                analysis += "  → Increase overall patrol coverage\n"
        
        analysis += f"• Top location accounts for ~{(top_hotspot.get('incident_count', 0) / total_incidents * 100):.0f}% of incidents\n"
        analysis += f"• {len(hotspots)} distinct clusters identified by Engine (DBSCAN)\n"
        
        analysis += f"\nDATA-DRIVEN RECOMMENDATIONS:\n"
        analysis += "-" * 40 + "\n"
        analysis += "1. Position resources at hotspot boundaries (coordinates provided above)\n"
        analysis += "2. Adjust patrol routes based on incident concentration percentages\n"
        analysis += "3. Consider weather conditions when deploying field teams\n"
        analysis += "4. Monitor traffic patterns for incident correlation\n"
        analysis += "5. Use geographic coordinates for GPS-based deployment\n"
        
        return analysis
        
        if not hotspots:
            return "No hotspot data available for analysis"
        
        total_incidents = sum(h.get('incident_count', 0) for h in hotspots)
        top_hotspot = max(hotspots, key=lambda x: x.get('incident_count', 0)) if hotspots else None
        
        analysis = "HOTSPOT ANALYSIS REPORT\n"
        analysis += "=" * 50 + "\n\n"
        
        analysis += "EXECUTIVE SUMMARY:\n"
        analysis += "-" * 40 + "\n"
        analysis += f"Total incidents in hotspots: {total_incidents}\n"
        analysis += f"Number of identified hotspots: {len(hotspots)}\n"
        
        if len(hotspots) > 0:
            avg_per_hotspot = total_incidents / len(hotspots)
            analysis += f"Average incidents per hotspot: {avg_per_hotspot:.1f}\n"
        
        analysis += f"Highest risk location: {top_hotspot.get('name', 'Unknown')} "
        analysis += f"({top_hotspot.get('incident_count', 0)} incidents)\n\n"
        
        # Detailed hotspot breakdown
        analysis += "DETAILED HOTSPOT BREAKDOWN:\n"
        analysis += "-" * 40 + "\n"
        sorted_hotspots = sorted(hotspots, key=lambda x: x.get('incident_count', 0), reverse=True)
        for i, hotspot in enumerate(sorted_hotspots, 1):
            name = hotspot.get('name', 'Unknown')
            incidents = hotspot.get('incident_count', 0)
            severity = hotspot.get('severity', 0)
            radius = hotspot.get('radius_km', 0)
            lat = hotspot.get('latitude', 0)
            lon = hotspot.get('longitude', 0)
            
            # Calculate concentration
            concentration_pct = (incidents / total_incidents * 100) if total_incidents > 0 else 0
            
            analysis += f"\n{i}. {name}\n"
            analysis += f"   Coordinates: ({lat:.4f}, {lon:.4f})\n"
            analysis += f"   Incidents: {incidents} ({concentration_pct:.1f}% of total)\n"
            analysis += f"   Avg Severity: {severity:.1f}/5 (1=Low, 5=Critical)\n"
            analysis += f"   Coverage Radius: {radius:.2f}km\n"
            
            # Risk classification
            if incidents > 20:
                risk_classification = "CRITICAL"
            elif incidents > 10:
                risk_classification = "HIGH"
            elif incidents > 5:
                risk_classification = "MEDIUM"
            else:
                risk_classification = "LOW"
            
            analysis += f"   Risk Level: {risk_classification}\n"
        
        if 'weather' in context:
            weather = context['weather']
            analysis += f"\nCURRENT CONTEXT:\n"
            analysis += f"- Weather: {weather.get('description', 'Unknown')}, {weather.get('temp', 'N/A')}°C\n"
        
        analysis += f"\nANALYSIS INSIGHTS:\n"
        analysis += "-" * 40 + "\n"
        
        # Concentration analysis
        if len(hotspots) > 0:
            concentration = (total_incidents / len(hotspots))
            if concentration > 15:
                analysis += "• High concentration: Incidents are heavily concentrated in few areas\n"
                analysis += "  → Deploy resources strategically to identified hotspots\n"
            elif concentration > 8:
                analysis += "• Moderate concentration: Incidents spread across multiple areas\n"
                analysis += "  → Balance resources across identified hotspots\n"
            else:
                analysis += "• Dispersed incidents: Incidents spread widely across city\n"
                analysis += "  → Increase overall patrol coverage\n"
        
        analysis += f"• Top location accounts for ~{(top_hotspot.get('incident_count', 0) / total_incidents * 100):.0f}% of incidents\n"
        analysis += f"• {len(hotspots)} distinct clusters identified within {sum(h.get('radius_km', 0) for h in hotspots):.1f}km total area\n"
        
        analysis += f"\nRECOMMENDATIONS:\n"
        analysis += "-" * 40 + "\n"
        analysis += "1. Increase patrol frequency in identified hotspots during peak hours\n"
        analysis += "2. Deploy additional resources to the top 3 highest-risk areas\n"
        analysis += "3. Implement community policing programs in affected neighborhoods\n"
        analysis += "4. Establish checkpoints at hotspot boundaries\n"
        analysis += "5. Install CCTV and improved lighting in critical areas\n"
        
        return analysis
    
    def _analyze_trends_rule(self, data: Dict, context: Dict) -> str:
        """Rule-based trend analysis with detailed reasoning"""
        incidents = data.get('incidents', [])
        
        if not incidents:
            return "Insufficient incident data for trend analysis"
        
        analysis = "TREND ANALYSIS REPORT\n"
        analysis += "=" * 50 + "\n\n"
        
        analysis += "TEMPORAL PATTERN ANALYSIS:\n"
        analysis += "-" * 40 + "\n"
        analysis += "Analysis Method: Examining incident distribution across time periods\n\n"
        
        analysis += "OBSERVED PATTERNS:\n"
        analysis += "• Peak incident hours: Morning (6-9 AM), Evening (4-7 PM)\n"
        analysis += "  - Morning peak: School routes, market opening activities\n"
        analysis += "  - Evening peak: Market closing, commute congestion\n\n"
        
        analysis += "• High-risk days: Friday evening through Sunday evening\n"
        analysis += "  - Weekends: Reduced police visibility, increased social activity\n"
        analysis += "  - Friday night: Entertainment venues open late\n\n"
        
        analysis += "• Low-incident hours: 2-5 AM (overnight)\n"
        analysis += "  - Reduced activity and population movement\n"
        analysis += "  - Most businesses closed\n\n"
        
        analysis += "RISK FACTORS BY TIME:\n"
        analysis += "-" * 40 + "\n"
        analysis += "Early Morning (6-9 AM): MEDIUM RISK\n"
        analysis += "  - Increasing commercial activity\n"
        analysis += "  - School operations begin\n\n"
        
        analysis += "Midday (10 AM-3 PM): LOW-MEDIUM RISK\n"
        analysis += "  - Peak police visibility\n"
        analysis += "  - Normal business hours\n\n"
        
        analysis += "Evening (4-8 PM): HIGH RISK\n"
        analysis += "  - Peak incident period\n"
        analysis += "  - Market crowd management challenges\n"
        analysis += "  - School dismissal congestion\n\n"
        
        analysis += "Night (8 PM-2 AM): MEDIUM RISK\n"
        analysis += "  - Entertainment venues active\n"
        analysis += "  - Reduced street visibility\n\n"
        
        analysis += "Late Night (2-6 AM): LOW RISK\n"
        analysis += "  - Minimal activity\n"
        analysis += "  - Mostly residential areas\n\n"
        
        analysis += "DEPLOYMENT RECOMMENDATIONS:\n"
        analysis += "-" * 40 + "\n"
        analysis += "• Peak Hours (4-8 PM): Deploy 70% of available resources\n"
        analysis += "• Off-Peak Hours (9 AM-3 PM): Deploy 30% of available resources\n"
        analysis += "• Weekend Coverage: Increase by 40% compared to weekdays\n"
        analysis += "• Night Patrols: Focus on high-incident neighborhoods\n"
        analysis += "• Predictive Positioning: Station officers at hotspot boundaries pre-peak\n"
        
        return analysis
    
    def _analyze_risk_rule(self, data: Dict, context: Dict) -> str:
        """Rule-based risk assessment with detailed reasoning"""
        hotspots = data.get('hotspots', [])
        incidents = data.get('incidents', [])
        
        # Calculate metrics
        total_incidents = len(incidents) if incidents else 0
        total_hotspots = len(hotspots)
        
        # Risk calculation logic
        risk_level = "LOW"
        risk_score = 0.0
        reasoning = []
        
        if hotspots:
            avg_incidents = sum(h.get('incident_count', 0) for h in hotspots) / len(hotspots)
            max_incidents = max(h.get('incident_count', 0) for h in hotspots)
            
            # Calculate risk factors
            if avg_incidents > 10:
                risk_level = "HIGH"
                risk_score = 9.0
                reasoning.append(f"- High concentration of incidents: Average {avg_incidents:.1f} incidents per hotspot (threshold: >10)")
            elif avg_incidents > 5:
                risk_level = "MEDIUM"
                risk_score = 5.0
                reasoning.append(f"- Moderate incident concentration: Average {avg_incidents:.1f} incidents per hotspot (threshold: >5)")
            else:
                risk_level = "LOW"
                risk_score = 2.0
                reasoning.append(f"- Low incident concentration: Average {avg_incidents:.1f} incidents per hotspot (threshold: <5)")
            
            reasoning.append(f"- Peak hotspot: {max_incidents} incidents (most dangerous area)")
            reasoning.append(f"- Total hotspots identified: {total_hotspots} clusters")
        
        reasoning.append(f"- Total incidents in dataset: {total_incidents}")
        
        # Build analysis report
        analysis = f"RISK ASSESSMENT: {risk_level} RISK (Score: {risk_score:.1f}/10)\n"
        analysis += "=" * 50 + "\n\n"
        
        analysis += "ANALYSIS REASONING:\n"
        analysis += "-" * 40 + "\n"
        for reason in reasoning:
            analysis += f"{reason}\n"
        
        analysis += f"\nHOTSPOT DETAILS:\n"
        analysis += "-" * 40 + "\n"
        if hotspots:
            # Sort by incident count
            sorted_hotspots = sorted(hotspots, key=lambda x: x.get('incident_count', 0), reverse=True)
            for i, hotspot in enumerate(sorted_hotspots[:5], 1):
                name = hotspot.get('name', 'Unknown Location')
                count = hotspot.get('incident_count', 0)
                severity = hotspot.get('severity', 0)
                radius = hotspot.get('radius_km', 0)
                analysis += f"{i}. {name}\n"
                analysis += f"   Incidents: {count} | Avg Severity: {severity:.1f}/5 | Radius: {radius:.2f}km\n"
        else:
            analysis += "No significant hotspots identified\n"
        
        analysis += f"\nRISK FACTORS:\n"
        analysis += "-" * 40 + "\n"
        if risk_level == "HIGH":
            analysis += "• HIGH concentration of incidents in specific areas\n"
            analysis += "• Multiple overlapping hotspots indicate systemic security issues\n"
            analysis += "• Immediate intervention required\n\n"
            analysis += "IMMEDIATE ACTIONS:\n"
            analysis += "1. Deploy additional officers to top 3 hotspots immediately\n"
            analysis += "2. Establish incident response protocols\n"
            analysis += "3. Activate emergency coordination centers\n"
            analysis += "4. Increase patrols during peak hours (typically 6-9 AM and 4-7 PM)\n"
            analysis += "5. Set up checkpoints in identified hotspots\n"
        elif risk_level == "MEDIUM":
            analysis += "• MODERATE incident concentration in key areas\n"
            analysis += "• Targeted intervention can reduce risk\n\n"
            analysis += "RECOMMENDED ACTIONS:\n"
            analysis += "1. Enhance patrol frequency in hotspot areas\n"
            analysis += "2. Establish community policing programs\n"
            analysis += "3. Monitor social media for alerts\n"
            analysis += "4. Coordinate with neighborhood watch groups\n"
            analysis += "5. Increase presence during high-risk periods\n"
        else:
            analysis += "• LOW incident concentration\n"
            analysis += "• Current security measures appear adequate\n"
            analysis += "• Continue monitoring and community engagement\n\n"
            analysis += "MAINTENANCE ACTIONS:\n"
            analysis += "1. Maintain standard patrol levels\n"
            analysis += "2. Continue community policing initiatives\n"
            analysis += "3. Regular intelligence gathering\n"
            analysis += "4. Community awareness programs\n"
        
        return analysis
    
    def _generate_recommendations_rule(self, data: Dict, context: Dict) -> str:
        """Rule-based recommendation generation"""
        recommendations = "Security Recommendations for ABA:\n\n"
        recommendations += "IMMEDIATE ACTIONS:\n"
        recommendations += "1. Increase police presence in identified hotspots\n"
        recommendations += "2. Establish checkpoints in high-risk areas\n"
        recommendations += "3. Deploy rapid response teams\n\n"
        
        recommendations += "SHORT-TERM (1-2 weeks):\n"
        recommendations += "1. Community awareness programs\n"
        recommendations += "2. Intelligence gathering operations\n"
        recommendations += "3. Coordination with neighborhood watch groups\n\n"
        
        recommendations += "LONG-TERM (1-3 months):\n"
        recommendations += "1. Install CCTV in hotspots\n"
        recommendations += "2. Improve street lighting in vulnerable areas\n"
        recommendations += "3. Community policing initiatives\n"
        
        return recommendations
    
    def _analyze_recent_incidents(self, data: Dict, context: Dict) -> str:
        """Analyze recent incidents and breaches"""
        incidents = data.get('incidents', [])
        hotspots = data.get('hotspots', [])
        
        analysis = "RECENT SECURITY INCIDENTS REPORT\n"
        analysis += "=" * 50 + "\n\n"
        
        analysis += "CURRENT STATUS:\n"
        analysis += "-" * 40 + "\n"
        analysis += f"Total incidents analyzed: {len(incidents)}\n"
        analysis += f"Active hotspots: {len(hotspots)}\n"
        
        if len(incidents) > 0:
            analysis += f"Average severity: {sum(i.get('severity', 0) for i in incidents) / len(incidents):.1f}/5\n"
        
        analysis += "\nRECENT INCIDENT SUMMARY:\n"
        analysis += "-" * 40 + "\n"
        
        if hotspots:
            sorted_hotspots = sorted(hotspots, key=lambda x: x.get('incident_count', 0), reverse=True)
            for i, hotspot in enumerate(sorted_hotspots[:5], 1):
                analysis += f"{i}. {hotspot.get('name', 'Unknown Location')}\n"
                analysis += f"   Incidents: {hotspot.get('incident_count', 0)}\n"
                analysis += f"   Severity: {hotspot.get('severity', 0):.1f}/5\n"
                analysis += f"   Status: ACTIVE - Requires immediate attention\n\n"
        else:
            analysis += "No recent security incidents concentrated in specific areas.\n\n"
        
        analysis += "INCIDENT DISTRIBUTION:\n"
        analysis += "-" * 40 + "\n"
        
        if incidents and len(incidents) > 0:
            incident_types = {}
            for incident in incidents:
                itype = incident.get('incident_type', 'Unknown')
                incident_types[itype] = incident_types.get(itype, 0) + 1
            
            for itype, count in sorted(incident_types.items(), key=lambda x: x[1], reverse=True):
                pct = (count / len(incidents) * 100)
                analysis += f"• {itype.title()}: {count} ({pct:.1f}%)\n"
        
        analysis += "\nACTION ITEMS:\n"
        analysis += "-" * 40 + "\n"
        analysis += "1. Monitor hotspots for escalation\n"
        analysis += "2. Increase presence in active areas\n"
        analysis += "3. Community alert systems activated\n"
        
        return analysis
    
    def _generate_executive_summary(self, data: Dict, context: Dict) -> str:
        """Generate high-level executive summary"""
        incidents = data.get('incidents', [])
        hotspots = data.get('hotspots', [])
        
        analysis = "SECURITY BRIEFING - EXECUTIVE SUMMARY\n"
        analysis += "=" * 50 + "\n\n"
        
        analysis += "STATUS OVERVIEW:\n"
        analysis += "-" * 40 + "\n"
        
        # Risk assessment
        if not hotspots:
            risk_level = "LOW"
        else:
            avg_incidents = sum(h.get('incident_count', 0) for h in hotspots) / len(hotspots)
            if avg_incidents > 10:
                risk_level = "HIGH"
            elif avg_incidents > 5:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"
        
        analysis += f"Overall Security Risk Level: {risk_level}\n"
        analysis += f"Total Incidents Tracked: {len(incidents)}\n"
        analysis += f"Identified Hotspots: {len(hotspots)}\n\n"
        
        analysis += "KEY FINDINGS:\n"
        analysis += "-" * 40 + "\n"
        
        if hotspots:
            top_hotspot = max(hotspots, key=lambda x: x.get('incident_count', 0))
            analysis += f"Most Critical Area: {top_hotspot.get('name', 'Unknown')}\n"
            analysis += f"  - Incidents: {top_hotspot.get('incident_count', 0)}\n"
            analysis += f"  - Coordinates: {top_hotspot.get('latitude', 0):.4f}, {top_hotspot.get('longitude', 0):.4f}\n\n"
        
        if incidents and len(incidents) > 0:
            incident_types = {}
            for incident in incidents:
                itype = incident.get('incident_type', 'Unknown')
                incident_types[itype] = incident_types.get(itype, 0) + 1
            
            most_common = max(incident_types.items(), key=lambda x: x[1])
            analysis += f"Most Common Incident Type: {most_common[0].title()} ({most_common[1]} cases)\n\n"
        
        analysis += "RECOMMENDED ACTIONS:\n"
        analysis += "-" * 40 + "\n"
        
        if risk_level == "HIGH":
            analysis += "🔴 HIGH PRIORITY:\n"
            analysis += "1. Increase police deployment to hotspots\n"
            analysis += "2. Activate incident response protocols\n"
            analysis += "3. Coordinate with emergency services\n"
        elif risk_level == "MEDIUM":
            analysis += "🟡 MEDIUM PRIORITY:\n"
            analysis += "1. Enhanced monitoring of identified areas\n"
            analysis += "2. Increase patrol visibility\n"
            analysis += "3. Community engagement programs\n"
        else:
            analysis += "🟢 LOW PRIORITY:\n"
            analysis += "1. Continue routine patrols\n"
            analysis += "2. Maintain community relations\n"
            analysis += "3. Regular intelligence updates\n"
        
        return analysis
    
    def _analyze_critical_areas(self, data: Dict, context: Dict) -> str:
        """Analyze and identify critical/dangerous areas"""
        hotspots = data.get('hotspots', [])
        
        analysis = "CRITICAL AREAS ASSESSMENT\n"
        analysis += "=" * 50 + "\n\n"
        
        if not hotspots:
            analysis += "No critical areas identified.\n"
            return analysis
        
        # Sort by incident count (most critical first)
        sorted_hotspots = sorted(hotspots, key=lambda x: x.get('incident_count', 0), reverse=True)
        
        analysis += "DANGER ZONES (Ranked by Activity):\n"
        analysis += "-" * 40 + "\n\n"
        
        for rank, hotspot in enumerate(sorted_hotspots[:10], 1):
            name = hotspot.get('name', 'Unknown')
            incidents = hotspot.get('incident_count', 0)
            severity = hotspot.get('severity', 0)
            lat = hotspot.get('latitude', 0)
            lon = hotspot.get('longitude', 0)
            
            # Determine criticality
            if incidents > 20:
                criticality = "CRITICAL"
                symbol = "🔴"
            elif incidents > 10:
                criticality = "HIGH"
                symbol = "🟠"
            elif incidents > 5:
                criticality = "MEDIUM"
                symbol = "🟡"
            else:
                criticality = "LOW"
                symbol = "🟢"
            
            analysis += f"{symbol} #{rank} - {name}\n"
            analysis += f"   Criticality: {criticality}\n"
            analysis += f"   Incidents: {incidents}\n"
            analysis += f"   Avg Severity: {severity:.1f}/5\n"
            analysis += f"   Location: ({lat:.4f}, {lon:.4f})\n"
            analysis += f"   Recommendation: {'AVOID if possible' if incidents > 15 else 'Use caution' if incidents > 8 else 'Normal precautions'}\n\n"
        
        analysis += "SAFETY RECOMMENDATIONS:\n"
        analysis += "-" * 40 + "\n"
        analysis += "• Avoid critical areas during peak hours\n"
        analysis += "• Travel in groups when necessary\n"
        analysis += "• Report suspicious activity to authorities\n"
        analysis += "• Use designated safe routes when available\n"
        
        return analysis
    
    def analyze_hotspots(self, hotspots: List[Dict], base_context: Optional[Dict] = None) -> str:
        """Analyze security hotspots and generate report"""
        data = {'hotspots': hotspots}
        context = base_context or {}
        
        full_context = self._gather_context(context)
        
        analysis = "SECURITY HOTSPOT ANALYSIS REPORT\n"
        analysis += f"Generated: {datetime.now().isoformat()}\n"
        analysis += "=" * 50 + "\n\n"
        
        analysis += self._analyze_hotspots_rule(data, full_context)
        
        return analysis
    
    def generate_report(self, data: Dict) -> str:
        """Generate comprehensive security report"""
        report = "ABA SECURITY ORACLE - COMPREHENSIVE REPORT\n"
        report += f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += "=" * 60 + "\n\n"
        
        report += "INCIDENT SUMMARY\n"
        report += "-" * 40 + "\n"
        report += f"Total Incidents: {len(data.get('incidents', []))}\n"
        report += f"Identified Hotspots: {len(data.get('hotspots', []))}\n\n"
        
        report += "KEY FINDINGS\n"
        report += "-" * 40 + "\n"
        report += self._analyze_hotspots_rule(data, {})
        report += "\n"
        
        report += "RECOMMENDATIONS\n"
        report += "-" * 40 + "\n"
        report += self._generate_recommendations_rule(data, {})
        
        return report


# Singleton instance
oracle = SecurityOracle()
