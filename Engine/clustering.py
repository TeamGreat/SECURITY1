"""
Engine - Clustering Module
DBSCAN-based incident clustering for hotspot detection
"""

import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from scipy.spatial.distance import cdist
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class IncidentClusterer:
    """
    DBSCAN-based clustering of security incidents
    Identifies hotspots based on incident density and proximity
    """
    
    def __init__(self, eps_km: float = 0.5, min_samples: int = 3):
        """
        Initialize clusterer
        
        Args:
            eps_km: Maximum distance between incidents in kilometers (cluster radius)
            min_samples: Minimum incidents required to form a cluster
        """
        self.eps_km = eps_km
        self.eps_meters = eps_km * 1000
        self.min_samples = min_samples
        self.clusters = None
        self.df = None
    
    def cluster_incidents(self, df: pd.DataFrame) -> Dict:
        """
        Cluster incidents using DBSCAN
        
        Args:
            df: DataFrame with columns [latitude, longitude, incident_type, datetime, severity]
        
        Returns:
            Dictionary with cluster information and statistics
        """
        if df.empty:
            return {'clusters': [], 'n_clusters': 0, 'noise_points': 0}
        
        self.df = df.copy()
        
        # Extract coordinates
        coords = df[['latitude', 'longitude']].values
        
        # Convert to radians for haversine distance
        coords_rad = np.radians(coords)
        
        # Apply DBSCAN with haversine distance (in kilometers)
        clustering = DBSCAN(
            eps=self.eps_km / 6371,  # Convert km to radians
            min_samples=self.min_samples,
            metric='haversine'
        ).fit(coords_rad)
        
        labels = clustering.labels_
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        n_noise = list(labels).count(-1)
        
        self.clusters = labels
        
        return {
            'clusters': int(n_clusters),
            'noise_points': int(n_noise),
            'total_incidents': len(df),
            'cluster_labels': labels.tolist()
        }
    
    def identify_hotspots(self, df: pd.DataFrame) -> List[Dict]:
        """
        Identify and characterize hotspots from clustered incidents
        
        Args:
            df: DataFrame with incident data
        
        Returns:
            List of hotspot dictionaries with statistics
        """
        if df.empty:
            return []
        
        # Cluster first if not done
        if self.clusters is None:
            self.cluster_incidents(df)
        
        df_copy = df.copy()
        df_copy['cluster'] = self.clusters
        
        hotspots = []
        
        # Process each cluster (except noise: label -1)
        for cluster_id in set(self.clusters):
            if cluster_id == -1:
                continue  # Skip noise points
            
            cluster_incidents = df_copy[df_copy['cluster'] == cluster_id]
            
            if len(cluster_incidents) < self.min_samples:
                continue
            
            # Calculate center
            center_lat = cluster_incidents['latitude'].mean()
            center_lon = cluster_incidents['longitude'].mean()
            
            # Collect statistics
            hotspot = {
                'cluster_id': int(cluster_id),
                'latitude': float(center_lat),
                'longitude': float(center_lon),
                'incident_count': len(cluster_incidents),
                'incident_types': cluster_incidents['incident_type'].value_counts().to_dict() if 'incident_type' in cluster_incidents.columns else {},
                'severity': cluster_incidents['severity'].mean() if 'severity' in cluster_incidents.columns else 0,
                'radius_km': self._calculate_radius(cluster_incidents),
                'name': self._generate_name(center_lat, center_lon)
            }
            
            hotspots.append(hotspot)
        
        # Sort by incident count
        hotspots.sort(key=lambda x: x['incident_count'], reverse=True)
        
        return hotspots
    
    def _calculate_radius(self, cluster_df: pd.DataFrame) -> float:
        """Calculate average radius of cluster"""
        if len(cluster_df) < 2:
            return 0.0
        
        center_lat = cluster_df['latitude'].mean()
        center_lon = cluster_df['longitude'].mean()
        
        # Simple distance calculation (Haversine approximation)
        distances = []
        for _, row in cluster_df.iterrows():
            lat_diff = (row['latitude'] - center_lat) * 111.32  # km per degree
            lon_diff = (row['longitude'] - center_lon) * 111.32 * np.cos(np.radians(center_lat))
            dist = np.sqrt(lat_diff**2 + lon_diff**2)
            distances.append(dist)
        
        return float(np.mean(distances)) if distances else 0.0
    
    def _generate_name(self, lat: float, lon: float) -> str:
        """Generate descriptive name for hotspot based on coordinates"""
        # Simple grid-based naming for Aba, Nigeria
        if lat < 5.10 and lon < 7.35:
            return "South Aba"
        elif lat > 5.11 and lon < 7.35:
            return "North Aba"
        elif lat < 5.10 and lon > 7.37:
            return "East Aba"
        elif lat > 5.11 and lon > 7.37:
            return "Central Aba"
        else:
            return f"Hotspot ({lat:.2f}, {lon:.2f})"
    
    def analyze_temporal_patterns(self, df: pd.DataFrame) -> Dict:
        """
        Analyze temporal patterns in incidents
        
        Args:
            df: DataFrame with datetime column
        
        Returns:
            Dictionary with temporal analysis
        """
        if df.empty or 'datetime' not in df.columns:
            return {}
        
        # Convert to datetime if needed
        if not pd.api.types.is_datetime64_any_dtype(df['datetime']):
            df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
        
        df_valid = df[df['datetime'].notna()].copy()
        
        if df_valid.empty:
            return {}
        
        # Extract time components
        df_valid['hour'] = df_valid['datetime'].dt.hour
        df_valid['day_of_week'] = df_valid['datetime'].dt.dayofweek
        df_valid['month'] = df_valid['datetime'].dt.month
        
        # Analyze patterns
        patterns = {
            'incidents_by_hour': df_valid.groupby('hour').size().to_dict(),
            'incidents_by_day': df_valid.groupby('day_of_week').size().to_dict(),
            'incidents_by_month': df_valid.groupby('month').size().to_dict(),
            'peak_hour': int(df_valid['hour'].mode()[0]) if len(df_valid['hour'].mode()) > 0 else None,
            'peak_day': int(df_valid['day_of_week'].mode()[0]) if len(df_valid['day_of_week'].mode()) > 0 else None
        }
        
        return patterns


def analyze_incidents(df: pd.DataFrame, eps_km: float = 0.5, min_samples: int = 3) -> Dict:
    """
    Convenience function to analyze incidents and return hotspots
    
    Args:
        df: DataFrame with incident data
        eps_km: Cluster radius in kilometers
        min_samples: Minimum incidents per cluster
    
    Returns:
        Dictionary with analysis results
    """
    clusterer = IncidentClusterer(eps_km=eps_km, min_samples=min_samples)
    
    cluster_info = clusterer.cluster_incidents(df)
    hotspots = clusterer.identify_hotspots(df)
    temporal_patterns = clusterer.analyze_temporal_patterns(df)
    
    return {
        'cluster_info': cluster_info,
        'hotspots': hotspots,
        'temporal_patterns': temporal_patterns,
        'clusterer': clusterer
    }
