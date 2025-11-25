"""
Police Coverage Gap Analysis Engine
Identifies areas with inadequate police coverage and recommends optimization
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
from geopy.distance import geodesic
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CoverageAnalyzer:
    """
    Analyze police coverage and identify gaps in service areas
    
    This class performs spatial analysis to:
    - Identify areas with inadequate police coverage
    - Calculate coverage scores for locations
    - Recommend optimal placement for new stations
    - Generate comprehensive coverage reports
    
    Attributes:
        police_df: DataFrame with police station locations
        incidents_df: DataFrame with incident records
        coverage_radius: Effective coverage radius per station (km)
    """
    
    def __init__(self, police_df: pd.DataFrame, 
                 incidents_df: pd.DataFrame,
                 coverage_radius_km: float = 2.0):
        """
        Initialize the CoverageAnalyzer
        
        Args:
            police_df: DataFrame with columns ['latitude', 'longitude', 'name']
            incidents_df: DataFrame with incident data
            coverage_radius_km: Effective coverage radius per station (default: 2.0 km)
        """
        self.police_df = police_df
        self.incidents_df = incidents_df
        self.coverage_radius = coverage_radius_km
        
        logger.info(f"CoverageAnalyzer initialized: {len(police_df)} stations, "
                   f"{len(incidents_df)} incidents, {coverage_radius_km}km radius")
    
    def find_coverage_gaps(self, grid_size_km: float = 0.5) -> List[Dict]:
        """
        Find areas with inadequate police coverage
        
        Creates a grid of analysis points and evaluates coverage at each point
        based on distance to nearest station and incident density.
        
        Args:
            grid_size_km: Size of analysis grid cells (default: 0.5 km)
            
        Returns:
            List of gap area dictionaries containing:
                - location: {lat, lon} coordinates
                - coverage_score: 0-100 score (lower = worse coverage)
                - nearest_station_km: Distance to nearest station
                - incident_count: Number of nearby incidents
                - severity: 'critical', 'high', 'medium', or 'low'
                - priority: Priority score for resource allocation
        """
        logger.info(f"Analyzing coverage gaps with {grid_size_km}km grid...")
        
        # Create analysis grid
        grid_points = self._create_analysis_grid(grid_size_km)
        logger.info(f"Created grid with {len(grid_points)} analysis points")
        
        gaps = []
        
        for lat, lon in grid_points:
            # Calculate distance to nearest station
            nearest_station_dist = self._distance_to_nearest_station(lat, lon)
            
            # Count nearby incidents
            nearby_incidents = self._count_nearby_incidents(lat, lon, radius_km=1.0)
            
            # Calculate coverage score (0-100, lower = worse)
            if nearest_station_dist > self.coverage_radius:
                # Outside effective coverage
                distance_penalty = (nearest_station_dist - self.coverage_radius) * 10
                coverage_score = max(0, 50 - distance_penalty)
            else:
                # Within coverage - score based on how central
                centrality = (self.coverage_radius - nearest_station_dist) / self.coverage_radius
                coverage_score = 50 + (centrality * 50)
            
            # Adjust for incident density (higher incidents = lower score)
            incident_penalty = min(50, nearby_incidents * 5)
            adjusted_score = max(0, coverage_score - incident_penalty)
            
            # Only include areas below threshold (gaps)
            if adjusted_score < 50:
                severity = self._classify_gap_severity(adjusted_score, nearby_incidents)
                priority = self._calculate_priority(adjusted_score, nearby_incidents)
                
                gaps.append({
                    'location': {
                        'lat': round(lat, 6),
                        'lon': round(lon, 6)
                    },
                    'coverage_score': round(adjusted_score, 1),
                    'nearest_station_km': round(nearest_station_dist, 2),
                    'incident_count': nearby_incidents,
                    'severity': severity,
                    'priority': priority
                })
        
        # Sort by priority (highest first)
        gaps.sort(key=lambda x: x['priority'], reverse=True)
        
        logger.info(f"Identified {len(gaps)} coverage gaps")
        return gaps
    
    def _create_analysis_grid(self, grid_size_km: float = 0.5) -> List[Tuple[float, float]]:
        """
        Create a grid of analysis points covering Aba
        
        Args:
            grid_size_km: Grid cell size in kilometers
            
        Returns:
            List of (latitude, longitude) tuples
        """
        # Aba city boundaries (approximate)
        lat_min, lat_max = 5.05, 5.15
        lon_min, lon_max = 7.33, 7.40
        
        # Convert km to approximate degrees
        # 1 degree latitude ≈ 111 km
        # 1 degree longitude ≈ 111 km * cos(latitude)
        avg_lat = (lat_min + lat_max) / 2
        
        lat_step = grid_size_km / 111
        lon_step = grid_size_km / (111 * np.cos(np.radians(avg_lat)))
        
        points = []
        lat = lat_min
        
        while lat <= lat_max:
            lon = lon_min
            while lon <= lon_max:
                points.append((lat, lon))
                lon += lon_step
            lat += lat_step
        
        return points
    
    def _distance_to_nearest_station(self, lat: float, lon: float) -> float:
        """
        Calculate distance to nearest police station
        
        Args:
            lat: Latitude of point
            lon: Longitude of point
            
        Returns:
            Distance in kilometers
        """
        min_dist = float('inf')
        
        for _, station in self.police_df.iterrows():
            try:
                station_lat = float(station['latitude'])
                station_lon = float(station['longitude'])
                
                dist = geodesic((lat, lon), (station_lat, station_lon)).km
                min_dist = min(min_dist, dist)
            except (KeyError, ValueError, TypeError):
                continue
        
        return min_dist
    
    def _count_nearby_incidents(self, lat: float, lon: float, 
                               radius_km: float = 1.0) -> int:
        """
        Count incidents within radius of location
        
        Args:
            lat: Latitude of point
            lon: Longitude of point
            radius_km: Search radius in kilometers
            
        Returns:
            Count of incidents
        """
        count = 0
        
        for _, incident in self.incidents_df.iterrows():
            try:
                inc_lat = float(incident['latitude'])
                inc_lon = float(incident['longitude'])
                
                dist = geodesic((lat, lon), (inc_lat, inc_lon)).km
                
                if dist <= radius_km:
                    count += 1
            except (KeyError, ValueError, TypeError):
                continue
        
        return count
    
    def _classify_gap_severity(self, score: float, incidents: int) -> str:
        """
        Classify gap severity based on coverage score and incidents
        
        Args:
            score: Coverage score (0-100)
            incidents: Incident count
            
        Returns:
            Severity classification: 'critical', 'high', 'medium', or 'low'
        """
        if score < 20 or incidents > 10:
            return 'critical'
        elif score < 35 or incidents > 5:
            return 'high'
        elif score < 50:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_priority(self, score: float, incidents: int) -> int:
        """
        Calculate priority score for resource allocation
        
        Lower coverage score + higher incidents = higher priority
        
        Args:
            score: Coverage score (0-100)
            incidents: Incident count
            
        Returns:
            Priority score (higher = more urgent)
        """
        # Invert score so lower coverage = higher priority
        coverage_priority = 100 - score
        
        # Weight incidents heavily
        incident_priority = incidents * 10
        
        return int(coverage_priority + incident_priority)
    
    def recommend_new_stations(self, num_stations: int = 3) -> List[Dict]:
        """
        Recommend optimal locations for new police stations
        
        Uses gap analysis and incident clustering to suggest locations
        that would maximize coverage improvement.
        
        Args:
            num_stations: Number of station recommendations (default: 3)
            
        Returns:
            List of recommendation dictionaries with:
                - rank: Recommendation priority rank
                - location: {lat, lon} coordinates
                - coverage_improvement: Expected improvement
                - incidents_covered: Number of incidents that would be covered
                - nearby_gaps_covered: Number of gap areas addressed
                - estimated_impact: Overall impact assessment
                - justification: Explanation for recommendation
        """
        logger.info(f"Generating {num_stations} station placement recommendations...")
        
        # Get coverage gaps
        gaps = self.find_coverage_gaps()
        
        # Filter for critical/high severity gaps
        priority_gaps = [g for g in gaps if g['severity'] in ['critical', 'high']]
        
        if not priority_gaps:
            logger.warning("No critical/high severity gaps found")
            priority_gaps = gaps[:num_stations] if gaps else []
        
        recommendations = []
        
        for i, gap in enumerate(priority_gaps[:num_stations]):
            # Find nearby gaps that would also benefit
            nearby_gaps = self._find_nearby_gaps(
                gap['location'], gaps, radius_km=2.0
            )
            
            # Calculate total incidents covered
            total_incidents = gap['incident_count']
            for nearby in nearby_gaps:
                total_incidents += nearby['incident_count']
            
            # Estimate coverage improvement
            coverage_improvement = self._estimate_coverage_improvement(
                gap['location']
            )
            
            # Assess overall impact
            impact = self._estimate_impact(gap, nearby_gaps)
            
            # Generate justification
            justification = self._generate_justification(gap, nearby_gaps)
            
            recommendation = {
                'rank': i + 1,
                'location': gap['location'],
                'coverage_improvement': coverage_improvement,
                'incidents_covered': total_incidents,
                'nearby_gaps_covered': len(nearby_gaps),
                'estimated_impact': impact,
                'justification': justification,
                'current_gap_severity': gap['severity'],
                'current_coverage_score': gap['coverage_score']
            }
            
            recommendations.append(recommendation)
        
        logger.info(f"Generated {len(recommendations)} recommendations")
        return recommendations
    
    def _find_nearby_gaps(self, location: Dict, all_gaps: List[Dict],
                         radius_km: float = 2.0) -> List[Dict]:
        """
        Find gap areas within radius of a location
        
        Args:
            location: {lat, lon} dictionary
            all_gaps: List of all gap dictionaries
            radius_km: Search radius
            
        Returns:
            List of nearby gap dictionaries
        """
        lat, lon = location['lat'], location['lon']
        nearby = []
        
        for gap in all_gaps:
            gap_lat = gap['location']['lat']
            gap_lon = gap['location']['lon']
            
            # Don't include the same location
            if gap_lat == lat and gap_lon == lon:
                continue
            
            dist = geodesic((lat, lon), (gap_lat, gap_lon)).km
            
            if dist <= radius_km:
                nearby.append(gap)
        
        return nearby
    
    def _estimate_coverage_improvement(self, location: Dict) -> str:
        """
        Estimate percentage improvement in coverage
        
        Args:
            location: Proposed station location
            
        Returns:
            Improvement estimate string
        """
        # Simplified calculation
        # In production, would calculate actual coverage change
        return "25-35%"
    
    def _estimate_impact(self, gap: Dict, nearby_gaps: List[Dict]) -> str:
        """
        Estimate overall impact of placing a station
        
        Args:
            gap: Primary gap being addressed
            nearby_gaps: Other gaps that would benefit
            
        Returns:
            Impact classification: 'Very High', 'High', 'Medium', 'Low'
        """
        total_incidents = gap['incident_count']
        for nearby in nearby_gaps:
            total_incidents += nearby['incident_count']
        
        total_gaps = 1 + len(nearby_gaps)
        
        if total_incidents > 20 or total_gaps > 5:
            return 'Very High'
        elif total_incidents > 10 or total_gaps > 3:
            return 'High'
        elif total_incidents > 5:
            return 'Medium'
        else:
            return 'Low'
    
    def _generate_justification(self, gap: Dict, nearby_gaps: List[Dict]) -> str:
        """
        Generate human-readable justification for recommendation
        
        Args:
            gap: Primary gap dictionary
            nearby_gaps: Nearby gap dictionaries
            
        Returns:
            Justification text
        """
        justification = f"This location addresses a {gap['severity']} coverage gap "
        justification += f"with {gap['incident_count']} recent incidents. "
        justification += f"The nearest existing station is {gap['nearest_station_km']} km away. "
        
        if len(nearby_gaps) > 0:
            justification += f"Placing a station here would also improve coverage for "
            justification += f"{len(nearby_gaps)} nearby gap area(s), "
            
            total_incidents = sum(g['incident_count'] for g in nearby_gaps)
            justification += f"addressing an additional {total_incidents} incidents."
        
        return justification
    
    def generate_coverage_report(self) -> Dict:
        """
        Generate comprehensive coverage analysis report
        
        Returns:
            Dictionary containing:
                - summary: Overall statistics
                - gaps: List of top coverage gaps
                - recommendations: Station placement recommendations
                - coverage_percentage: Percentage of area with adequate coverage
                - station_efficiency: Metrics on current station effectiveness
        """
        logger.info("Generating comprehensive coverage report...")
        
        # Find gaps
        gaps = self.find_coverage_gaps()
        
        # Generate recommendations
        recommendations = self.recommend_new_stations()
        
        # Calculate statistics
        total_area_km2 = 142  # Aba approximate area
        stations_count = len(self.police_df)
        coverage_per_station = total_area_km2 / stations_count if stations_count > 0 else 0
        
        # Count gaps by severity
        critical_gaps = len([g for g in gaps if g['severity'] == 'critical'])
        high_gaps = len([g for g in gaps if g['severity'] == 'high'])
        medium_gaps = len([g for g in gaps if g['severity'] == 'medium'])
        
        # Calculate coverage percentage
        coverage_pct = self._calculate_coverage_percentage()
        
        # Station efficiency metrics
        station_efficiency = self._calculate_station_efficiency()
        
        report = {
            'summary': {
                'total_stations': stations_count,
                'coverage_per_station_km2': round(coverage_per_station, 2),
                'coverage_percentage': coverage_pct,
                'critical_gaps': critical_gaps,
                'high_severity_gaps': high_gaps,
                'medium_severity_gaps': medium_gaps,
                'total_gaps': len(gaps),
                'report_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            'gaps': gaps[:20],  # Top 20 gaps
            'recommendations': recommendations,
            'station_efficiency': station_efficiency
        }
        
        logger.info("Coverage report generated successfully")
        return report
    
    def _calculate_coverage_percentage(self, grid_size_km: float = 0.5) -> float:
        """
        Calculate percentage of area with adequate police coverage
        
        Args:
            grid_size_km: Grid resolution for calculation
            
        Returns:
            Coverage percentage (0-100)
        """
        grid_points = self._create_analysis_grid(grid_size_km)
        covered_count = 0
        
        for lat, lon in grid_points:
            dist = self._distance_to_nearest_station(lat, lon)
            if dist <= self.coverage_radius:
                covered_count += 1
        
        coverage_pct = (covered_count / len(grid_points)) * 100 if grid_points else 0.0
        
        logger.debug(f"Coverage calculation: {covered_count}/{len(grid_points)} points covered")
        
        return round(coverage_pct, 1)
    
    def _calculate_station_efficiency(self) -> Dict:
        """
        Calculate efficiency metrics for existing stations
        
        Returns:
            Dictionary with efficiency metrics
        """
        total_incidents = len(self.incidents_df)
        stations_count = len(self.police_df)
        
        # Calculate average incidents per station coverage area
        incidents_per_station = total_incidents / stations_count if stations_count > 0 else 0
        
        # Calculate response coverage (simplified)
        # Percent of incidents within 2km of a station
        covered_incidents = 0
        for _, incident in self.incidents_df.iterrows():
            try:
                inc_lat = float(incident['latitude'])
                inc_lon = float(incident['longitude'])
                
                nearest_dist = self._distance_to_nearest_station(inc_lat, inc_lon)
                if nearest_dist <= self.coverage_radius:
                    covered_incidents += 1
            except (KeyError, ValueError, TypeError):
                continue
        
        response_coverage = (covered_incidents / total_incidents * 100) if total_incidents > 0 else 0
        
        return {
            'incidents_per_station': round(incidents_per_station, 1),
            'response_coverage_percent': round(response_coverage, 1),
            'avg_station_spacing_km': round(self._calculate_avg_spacing(), 2),
            'efficiency_rating': self._classify_efficiency(response_coverage)
        }
    
    def _calculate_avg_spacing(self) -> float:
        """Calculate average spacing between stations"""
        if len(self.police_df) < 2:
            return 0.0
        
        distances = []
        stations = self.police_df[['latitude', 'longitude']].values
        
        for i in range(len(stations)):
            for j in range(i + 1, len(stations)):
                try:
                    dist = geodesic(stations[i], stations[j]).km
                    distances.append(dist)
                except:
                    continue
        
        return np.mean(distances) if distances else 0.0
    
    def _classify_efficiency(self, coverage: float) -> str:
        """Classify efficiency based on coverage percentage"""
        if coverage >= 80:
            return 'Excellent'
        elif coverage >= 60:
            return 'Good'
        elif coverage >= 40:
            return 'Fair'
        else:
            return 'Needs Improvement'