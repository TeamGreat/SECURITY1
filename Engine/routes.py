"""
Route Analysis and Safety Assessment Engine
Analyzes route safety using road networks and incident data
"""
import networkx as nx
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from geopy.distance import geodesic
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RouteAnalyzer:
    """
    Analyze route safety using road network graphs and incident data
    
    This class provides comprehensive route analysis including:
    - Shortest path calculation
    - Safest path calculation (weighted by incidents)
    - Risk assessment along routes
    - Alternative route suggestions
    - Time-based safety adjustments
    
    Attributes:
        G: NetworkX graph representing the road network
        incidents_df: DataFrame containing incident records
    """
    
    def __init__(self, graph_path: str, incidents_df: pd.DataFrame):
        """
        Initialize the RouteAnalyzer
        
        Args:
            graph_path: Path to the GraphML file containing the road network
            incidents_df: DataFrame with incident data (must have lat/lon columns)
        """
        logger.info(f"Initializing RouteAnalyzer with graph: {graph_path}")
        
        try:
            # Load the road network graph
            self.G = nx.read_graphml(graph_path)
            logger.info(f"Loaded graph with {self.G.number_of_nodes()} nodes and {self.G.number_of_edges()} edges")
        except Exception as e:
            logger.error(f"Failed to load graph: {e}")
            raise
        
        self.incidents_df = incidents_df
        
        # Weight edges based on nearby incidents
        self._weight_edges()
        
    def _weight_edges(self, radius_km: float = 0.2):
        """
        Add safety weights to graph edges based on nearby incidents
        
        Higher weights indicate more dangerous routes
        
        Args:
            radius_km: Distance threshold for considering incidents near an edge
        """
        logger.info("Weighting edges based on incident proximity...")
        
        weighted_count = 0
        
        for u, v, data in self.G.edges(data=True):
            # Get node coordinates
            node_u = self.G.nodes[u]
            node_v = self.G.nodes[v]
            
            # Check if coordinates exist
            if 'y' not in node_u or 'x' not in node_u or 'y' not in node_v or 'x' not in node_v:
                data['safety_weight'] = 1.0
                continue
            
            try:
                lat_u, lon_u = float(node_u['y']), float(node_u['x'])
                lat_v, lon_v = float(node_v['y']), float(node_v['x'])
            except (ValueError, TypeError):
                data['safety_weight'] = 1.0
                continue
            
            # Calculate edge midpoint
            mid_lat = (lat_u + lat_v) / 2
            mid_lon = (lon_u + lon_v) / 2
            
            # Count nearby incidents
            incident_count = 0
            for _, incident in self.incidents_df.iterrows():
                try:
                    inc_lat = float(incident['latitude'])
                    inc_lon = float(incident['longitude'])
                    
                    # Calculate distance to edge midpoint
                    dist = geodesic((mid_lat, mid_lon), (inc_lat, inc_lon)).km
                    
                    if dist <= radius_km:
                        incident_count += 1
                except (KeyError, ValueError, TypeError):
                    continue
            
            # Assign safety weight
            # Base weight: 1.0, +0.5 per incident within radius
            data['safety_weight'] = 1.0 + (incident_count * 0.5)
            
            if incident_count > 0:
                weighted_count += 1
        
        logger.info(f"Weighted {weighted_count} edges based on incident proximity")
    
    def _find_nearest_node(self, lat: float, lon: float) -> Optional[str]:
        """
        Find the nearest graph node to given coordinates
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Node ID of nearest node, or None if not found
        """
        min_dist = float('inf')
        nearest_node = None
        
        for node, data in self.G.nodes(data=True):
            if 'y' not in data or 'x' not in data:
                continue
            
            try:
                node_lat = float(data['y'])
                node_lon = float(data['x'])
                
                dist = geodesic((lat, lon), (node_lat, node_lon)).km
                
                if dist < min_dist:
                    min_dist = dist
                    nearest_node = node
            except (ValueError, TypeError):
                continue
        
        if nearest_node:
            logger.debug(f"Found nearest node at {min_dist:.3f} km away")
        
        return nearest_node
    
    def analyze_route(self, start: str, end: str, 
                     time_of_day: Optional[str] = None) -> Dict:
        """
        Perform comprehensive route safety analysis
        
        Args:
            start: Start location (format: "lat,lon" or address)
            end: End location (format: "lat,lon" or address)
            time_of_day: 'morning', 'afternoon', 'evening', 'night' (optional)
            
        Returns:
            Dictionary containing:
                - distance_km: Total route distance
                - safety_rating: Overall safety score (0-10)
                - incident_count: Number of incidents along route
                - high_risk_segments: List of dangerous route segments
                - route_coordinates: List of (lat, lon) tuples for visualization
                - alternative_route: Alternative safer route coordinates (if available)
                - recommendations: List of safety recommendations
        """
        logger.info(f"Analyzing route from {start} to {end}")
        
        try:
            # Parse coordinates
            start_coords = self._parse_location(start)
            end_coords = self._parse_location(end)
            
            # Find nearest nodes in graph
            start_node = self._find_nearest_node(*start_coords)
            end_node = self._find_nearest_node(*end_coords)
            
            if not start_node or not end_node:
                logger.error("Could not find route nodes in graph")
                return {
                    "error": "Could not map locations to road network",
                    "start": start,
                    "end": end
                }
            
            # Calculate shortest path by distance
            try:
                shortest_path = nx.shortest_path(
                    self.G, start_node, end_node, weight='length'
                )
                shortest_distance = nx.shortest_path_length(
                    self.G, start_node, end_node, weight='length'
                )
            except nx.NetworkXNoPath:
                logger.error("No path found between locations")
                return {
                    "error": "No route exists between these locations",
                    "start": start,
                    "end": end
                }
            
            # Calculate safest path (weighted by safety)
            try:
                safest_path = nx.shortest_path(
                    self.G, start_node, end_node, weight='safety_weight'
                )
                safety_cost = nx.shortest_path_length(
                    self.G, start_node, end_node, weight='safety_weight'
                )
            except nx.NetworkXNoPath:
                safest_path = shortest_path
                safety_cost = 0
            
            # Analyze incidents along route
            route_incidents = self._incidents_along_path(shortest_path)
            
            # Calculate base safety rating (0-10)
            # Start at 10, subtract for incidents
            base_rating = max(1, 10 - len(route_incidents))
            
            # Apply time-based adjustment
            time_risk_factor = self._get_time_risk_factor(time_of_day)
            adjusted_rating = max(1, base_rating - time_risk_factor)
            
            # Identify high-risk segments
            risk_segments = self._identify_risk_segments(shortest_path)
            
            # Generate route coordinates for visualization
            route_coords = self._path_to_coords(shortest_path)
            alternative_coords = None
            if safest_path != shortest_path:
                alternative_coords = self._path_to_coords(safest_path)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                adjusted_rating, route_incidents, time_of_day, len(risk_segments)
            )
            
            result = {
                "start": start,
                "end": end,
                "distance_km": round(shortest_distance / 1000, 2),
                "safety_rating": round(adjusted_rating, 1),
                "incident_count": len(route_incidents),
                "high_risk_segments": risk_segments,
                "route_coordinates": route_coords,
                "alternative_route": alternative_coords,
                "recommendations": recommendations,
                "time_of_day": time_of_day or "any"
            }
            
            logger.info(f"Route analysis complete: {result['safety_rating']}/10 safety rating")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing route: {e}")
            return {
                "error": str(e),
                "start": start,
                "end": end
            }
    
    def _parse_location(self, location: str) -> Tuple[float, float]:
        """
        Parse location string to coordinates
        
        Args:
            location: Location string (format: "lat,lon")
            
        Returns:
            Tuple of (latitude, longitude)
        """
        # Try to parse as "lat,lon"
        parts = location.strip().split(',')
        
        if len(parts) == 2:
            try:
                lat = float(parts[0].strip())
                lon = float(parts[1].strip())
                
                # Basic validation
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    return lat, lon
            except ValueError:
                pass
        
        # Default to Aba city center if parsing fails
        logger.warning(f"Could not parse location '{location}', using default coordinates")
        return 5.1066, 7.3667
    
    def _incidents_along_path(self, path: List[str], 
                              buffer_km: float = 0.3) -> List[Dict]:
        """
        Find incidents near the route path
        
        Args:
            path: List of node IDs forming the route
            buffer_km: Distance buffer around route to check for incidents
            
        Returns:
            List of incident dictionaries
        """
        incidents = []
        seen_incidents = set()
        
        for node in path:
            node_data = self.G.nodes[node]
            
            if 'y' not in node_data or 'x' not in node_data:
                continue
            
            try:
                node_lat = float(node_data['y'])
                node_lon = float(node_data['x'])
            except (ValueError, TypeError):
                continue
            
            # Check incidents within buffer
            for idx, incident in self.incidents_df.iterrows():
                try:
                    inc_lat = float(incident['latitude'])
                    inc_lon = float(incident['longitude'])
                    
                    dist = geodesic((node_lat, node_lon), (inc_lat, inc_lon)).km
                    
                    if dist <= buffer_km and idx not in seen_incidents:
                        incidents.append(incident.to_dict())
                        seen_incidents.add(idx)
                        
                except (KeyError, ValueError, TypeError):
                    continue
        
        return incidents
    
    def _identify_risk_segments(self, path: List[str]) -> List[Dict]:
        """
        Identify high-risk segments along the route
        
        Args:
            path: List of node IDs forming the route
            
        Returns:
            List of risk segment dictionaries
        """
        segments = []
        
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            
            if not self.G.has_edge(u, v):
                continue
            
            edge_data = self.G[u][v]
            safety_weight = edge_data.get('safety_weight', 1.0)
            
            # Consider segment high-risk if weight > 2.0
            if safety_weight > 2.0:
                risk_level = 'high' if safety_weight > 3.0 else 'medium'
                
                segments.append({
                    'segment': f"{u[:8]} → {v[:8]}",
                    'risk_level': risk_level,
                    'weight': round(safety_weight, 2),
                    'incident_density': int((safety_weight - 1.0) / 0.5)
                })
        
        return segments
    
    def _path_to_coords(self, path: List[str]) -> List[Tuple[float, float]]:
        """
        Convert path node IDs to coordinate list
        
        Args:
            path: List of node IDs
            
        Returns:
            List of (latitude, longitude) tuples
        """
        coords = []
        
        for node in path:
            node_data = self.G.nodes[node]
            
            if 'y' in node_data and 'x' in node_data:
                try:
                    lat = float(node_data['y'])
                    lon = float(node_data['x'])
                    coords.append((lat, lon))
                except (ValueError, TypeError):
                    continue
        
        return coords
    
    def _get_time_risk_factor(self, time_of_day: Optional[str]) -> int:
        """
        Get risk adjustment factor based on time of day
        
        Args:
            time_of_day: Time period string
            
        Returns:
            Risk factor to subtract from base safety rating
        """
        time_risk = {
            'morning': 0,
            'afternoon': 0,
            'evening': 1,
            'night': 2,
            None: 0
        }
        
        return time_risk.get(time_of_day, 0)
    
    def _generate_recommendations(self, safety_rating: float,
                                 incidents: List[Dict],
                                 time_of_day: Optional[str],
                                 risk_segment_count: int) -> List[str]:
        """
        Generate contextual safety recommendations
        
        Args:
            safety_rating: Overall safety score
            incidents: List of incidents along route
            time_of_day: Time of day
            risk_segment_count: Number of high-risk segments
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Rating-based recommendations
        if safety_rating < 5:
            recommendations.append("⚠️ HIGH RISK: This route has significant safety concerns")
            recommendations.append("🚗 Consider using an alternative route if possible")
            recommendations.append("👥 Travel in groups for added security")
        elif safety_rating < 7:
            recommendations.append("⚠️ MODERATE RISK: Exercise caution on this route")
            recommendations.append("📱 Keep emergency contacts readily available")
        else:
            recommendations.append("✅ Generally safe route under normal conditions")
        
        # Incident-based recommendations
        if len(incidents) > 5:
            recommendations.append(f"⚠️ {len(incidents)} recent incidents reported along this route")
            recommendations.append("🚨 Remain vigilant and avoid stopping unless necessary")
        
        if len(incidents) > 0:
            # Analyze incident types
            incident_types = [i.get('type', 'unknown') for i in incidents]
            common_type = max(set(incident_types), key=incident_types.count) if incident_types else None
            
            if common_type:
                recommendations.append(f"📊 Most common incident type: {common_type}")
        
        # Time-based recommendations
        if time_of_day == 'night':
            recommendations.append("🌙 Night travel significantly increases risk")
            recommendations.append("💡 Ensure vehicle lights are functioning properly")
            recommendations.append("⏰ Consider delaying travel until daylight if possible")
        elif time_of_day == 'evening':
            recommendations.append("🌆 Evening hours carry moderate risk")
            recommendations.append("⏰ Complete travel before dark if possible")
        
        # Risk segment recommendations
        if risk_segment_count > 0:
            recommendations.append(f"⚠️ {risk_segment_count} high-risk segment(s) identified")
            recommendations.append("🚗 Do not stop in these areas")
        
        # General safety recommendations
        recommendations.append("🔒 Keep valuables hidden from view")
        recommendations.append("📱 Share your route with someone you trust")
        recommendations.append("🚨 Have emergency numbers saved and accessible")
        
        return recommendations
    
    def compare_routes(self, start: str, end: str) -> Dict:
        """
        Compare multiple route options
        
        Args:
            start: Start location
            end: End location
            
        Returns:
            Dictionary comparing shortest vs safest routes
        """
        logger.info("Comparing route options...")
        
        # Analyze shortest route
        shortest_analysis = self.analyze_route(start, end)
        
        # Try to find alternative (safest) route
        # This is already included in analyze_route
        
        return {
            "primary_route": shortest_analysis,
            "comparison": {
                "has_alternative": shortest_analysis.get('alternative_route') is not None,
                "primary_safety": shortest_analysis.get('safety_rating', 0),
                "primary_distance": shortest_analysis.get('distance_km', 0)
            }
        }