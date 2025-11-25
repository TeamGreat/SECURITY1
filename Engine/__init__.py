"""
ABA Security Oracle Engine
Main analysis and simulation components

NOTE: Fixed imports on 2024-11-24
- Changed HotspotDetector → IncidentClusterer (actual class name)
- Added analyze_incidents function export
"""
# Clustering module
try:
    from .clustering import IncidentClusterer, analyze_incidents
except ImportError as e:
    print(f"Warning: Could not import clustering module: {e}")

# Routing module
try:
    from .routes import RouteAnalyzer
except ImportError as e:
    print(f"Warning: Could not import routes module: {e}")

# Simulation modules
try:
    from .simulator import SeasonSimulator, EventImpactAnalyzer
except ImportError as e:
    print(f"Warning: Could not import simulator module: {e}")

# Coverage analysis module
try:
    from .gaps import CoverageAnalyzer
except ImportError as e:
    print(f"Warning: Could not import gaps module: {e}")

__version__ = "1.0.0"
__author__ = "ABA Security Oracle Team"

__all__ = [
    'IncidentClusterer',          # Main clustering class (was: HotspotDetector)
    'analyze_incidents',          # Convenience function
    'RouteAnalyzer',              # Route safety analysis
    'SeasonSimulator',            # Seasonal pattern simulation
    'EventImpactAnalyzer',        # Event impact analysis
    'CoverageAnalyzer'            # Coverage gap detection
]