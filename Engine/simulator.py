"""
Season and Event Simulator
Simulates how seasons, events, and temporal patterns affect crime
"""
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SeasonSimulator:
    """
    Simulate seasonal and event-based crime risk patterns
    
    This class models how various temporal factors affect security:
    - Seasonal variations (dry/rainy season)
    - Cultural and religious events (Christmas, Sallah, etc.)
    - Economic cycles (month-end, market days)
    - Day of week patterns
    
    Attributes:
        EVENTS: Dictionary of events and their risk multipliers
        SEASONS: Dictionary of seasons and their characteristics
        current_date: Reference date for simulations
    """
    
    # Nigerian festive and cultural calendar
    EVENTS = {
        'christmas': {
            'month': 12,
            'days': [20, 31],
            'risk_multiplier': 1.5,
            'description': 'Christmas season (Dec 20-31)'
        },
        'new_year': {
            'month': 1,
            'days': [1, 7],
            'risk_multiplier': 1.4,
            'description': 'New Year period (Jan 1-7)'
        },
        'easter': {
            'variable': True,
            'risk_multiplier': 1.3,
            'description': 'Easter period (variable dates)'
        },
        'sallah': {
            'variable': True,
            'risk_multiplier': 1.3,
            'description': 'Eid celebration (variable dates)'
        },
        'market_days': {
            'weekdays': [3, 5],  # Thursday=3, Saturday=5
            'risk_multiplier': 1.2,
            'description': 'Major market days (Thu, Sat)'
        },
        'month_end': {
            'days': [28, 31],
            'risk_multiplier': 1.3,
            'description': 'Month-end period (28th-31st)'
        }
    }
    
    # Seasonal patterns
    SEASONS = {
        'dry_season': {
            'months': [11, 12, 1, 2, 3],
            'risk_multiplier': 1.1,
            'description': 'Dry season (Nov-Mar)',
            'characteristics': ['Higher mobility', 'More outdoor activity']
        },
        'rainy_season': {
            'months': [4, 5, 6, 7, 8, 9, 10],
            'risk_multiplier': 0.9,
            'description': 'Rainy season (Apr-Oct)',
            'characteristics': ['Reduced mobility', 'Indoor activity']
        }
    }
    
    def __init__(self, reference_date: Optional[datetime] = None):
        """
        Initialize the SeasonSimulator
        
        Args:
            reference_date: Date to use as reference (default: current date)
        """
        self.current_date = reference_date or datetime.now()
        logger.info(f"SeasonSimulator initialized for date: {self.current_date.strftime('%Y-%m-%d')}")
    
    def get_current_context(self) -> Dict:
        """
        Get current temporal context including season and active events
        
        Returns:
            Dictionary containing:
                - date: Current date string
                - season: Current season name
                - events: List of active events
                - risk_multiplier: Combined risk factor
                - day_of_week: Day name
                - month: Month name
        """
        month = self.current_date.month
        day = self.current_date.day
        weekday = self.current_date.weekday()
        
        # Determine season
        season = 'dry_season' if month in self.SEASONS['dry_season']['months'] else 'rainy_season'
        
        # Initialize context
        active_events = []
        total_multiplier = 1.0
        
        # Check for festive periods
        if month == 12 and 20 <= day <= 31:
            active_events.append('Christmas Season')
            total_multiplier *= self.EVENTS['christmas']['risk_multiplier']
        
        if month == 1 and day <= 7:
            active_events.append('New Year Period')
            total_multiplier *= self.EVENTS['new_year']['risk_multiplier']
        
        # Check for market days (Thursday=3, Saturday=5)
        if weekday in [3, 5]:
            active_events.append('Market Day')
            total_multiplier *= self.EVENTS['market_days']['risk_multiplier']
        
        # Check for month-end
        if day >= 28:
            active_events.append('Month End')
            total_multiplier *= self.EVENTS['month_end']['risk_multiplier']
        
        # Apply seasonal multiplier
        total_multiplier *= self.SEASONS[season]['risk_multiplier']
        
        context = {
            'date': self.current_date.strftime('%Y-%m-%d'),
            'season': self.SEASONS[season]['description'],
            'season_key': season,
            'events': active_events,
            'risk_multiplier': round(total_multiplier, 2),
            'day_of_week': self.current_date.strftime('%A'),
            'month': self.current_date.strftime('%B'),
            'is_weekend': weekday >= 5,
            'is_month_end': day >= 28
        }
        
        logger.debug(f"Context: {context['season']}, Events: {len(active_events)}, Multiplier: {context['risk_multiplier']}")
        
        return context
    
    def simulate_future_risk(self, days_ahead: int = 30) -> List[Dict]:
        """
        Simulate risk levels for upcoming days
        
        Args:
            days_ahead: Number of days to forecast (default: 30)
            
        Returns:
            List of daily forecast dictionaries
        """
        logger.info(f"Simulating risk for next {days_ahead} days...")
        
        forecasts = []
        original_date = self.current_date
        
        for i in range(days_ahead):
            future_date = self.current_date + timedelta(days=i)
            
            # Temporarily set date for simulation
            self.current_date = future_date
            
            # Get context for this date
            context = self.get_current_context()
            context['days_from_now'] = i
            
            # Classify risk level
            multiplier = context['risk_multiplier']
            if multiplier >= 1.4:
                risk_level = 'high'
                risk_color = '🔴'
            elif multiplier >= 1.2:
                risk_level = 'medium'
                risk_color = '🟡'
            else:
                risk_level = 'low'
                risk_color = '🟢'
            
            context['risk_level'] = risk_level
            context['risk_color'] = risk_color
            
            forecasts.append(context)
        
        # Restore original date
        self.current_date = original_date
        
        logger.info(f"Generated {len(forecasts)} daily forecasts")
        return forecasts
    
    def adjust_incident_probability(self, base_probability: float,
                                   location_type: str = 'urban') -> float:
        """
        Adjust incident probability based on current temporal context
        
        Args:
            base_probability: Base probability (0-1)
            location_type: 'urban', 'suburban', 'market', 'residential'
            
        Returns:
            Adjusted probability (0-1)
        """
        context = self.get_current_context()
        adjusted = base_probability * context['risk_multiplier']
        
        # Location-specific adjustments
        location_factors = {
            'urban': 1.0,
            'market': 1.3 if 'Market Day' in context['events'] else 1.0,
            'suburban': 0.8,
            'residential': 0.7,
            'commercial': 1.2
        }
        
        adjusted *= location_factors.get(location_type, 1.0)
        
        # Ensure probability stays within bounds
        return min(1.0, max(0.0, adjusted))
    
    def get_high_risk_periods(self, days_ahead: int = 90) -> List[Dict]:
        """
        Identify high-risk periods in the future
        
        Args:
            days_ahead: Number of days to analyze (default: 90)
            
        Returns:
            List of high-risk period dictionaries with:
                - start: Start date
                - end: End date
                - risk_level: Risk classification
                - events: Active events during period
                - duration_days: Length of period
        """
        logger.info(f"Identifying high-risk periods for next {days_ahead} days...")
        
        forecasts = self.simulate_future_risk(days_ahead)
        
        # Filter for high and medium risk days
        high_risk_days = [
            f for f in forecasts 
            if f['risk_level'] in ['high', 'medium']
        ]
        
        if not high_risk_days:
            logger.info("No high-risk periods identified")
            return []
        
        # Group consecutive days into periods
        periods = []
        current_period = {
            'start': high_risk_days[0]['date'],
            'end': high_risk_days[0]['date'],
            'risk_level': high_risk_days[0]['risk_level'],
            'events': set(high_risk_days[0]['events']),
            'max_multiplier': high_risk_days[0]['risk_multiplier']
        }
        
        for i in range(1, len(high_risk_days)):
            forecast = high_risk_days[i]
            prev_date = datetime.strptime(current_period['end'], '%Y-%m-%d')
            curr_date = datetime.strptime(forecast['date'], '%Y-%m-%d')
            
            # Check if consecutive
            if (curr_date - prev_date).days == 1:
                # Extend current period
                current_period['end'] = forecast['date']
                current_period['events'].update(forecast['events'])
                current_period['max_multiplier'] = max(
                    current_period['max_multiplier'],
                    forecast['risk_multiplier']
                )
                # Upgrade risk level if needed
                if forecast['risk_level'] == 'high':
                    current_period['risk_level'] = 'high'
            else:
                # Save current period and start new one
                periods.append(self._finalize_period(current_period))
                current_period = {
                    'start': forecast['date'],
                    'end': forecast['date'],
                    'risk_level': forecast['risk_level'],
                    'events': set(forecast['events']),
                    'max_multiplier': forecast['risk_multiplier']
                }
        
        # Add the last period
        periods.append(self._finalize_period(current_period))
        
        logger.info(f"Identified {len(periods)} high-risk periods")
        return periods
    
    def _finalize_period(self, period: Dict) -> Dict:
        """
        Finalize a risk period by calculating additional metrics
        
        Args:
            period: Partial period dictionary
            
        Returns:
            Complete period dictionary
        """
        start_date = datetime.strptime(period['start'], '%Y-%m-%d')
        end_date = datetime.strptime(period['end'], '%Y-%m-%d')
        duration = (end_date - start_date).days + 1
        
        return {
            'start': period['start'],
            'end': period['end'],
            'risk_level': period['risk_level'],
            'events': list(period['events']),
            'duration_days': duration,
            'max_multiplier': round(period['max_multiplier'], 2),
            'period_type': self._classify_period_type(period['events'])
        }
    
    def _classify_period_type(self, events: set) -> str:
        """Classify the type of risk period based on events"""
        events_list = list(events)
        
        if not events_list:
            return 'General'
        
        if 'Christmas Season' in events_list or 'New Year Period' in events_list:
            return 'Festive Season'
        elif 'Market Day' in events_list:
            return 'Market Activity'
        elif 'Month End' in events_list:
            return 'Economic Cycle'
        else:
            return 'Multiple Factors'
    
    def get_risk_explanation(self) -> str:
        """
        Get human-readable explanation of current risk factors
        
        Returns:
            Formatted explanation string
        """
        context = self.get_current_context()
        
        explanation = f"**Current Risk Assessment for {context['date']}**\n\n"
        explanation += f"Season: {context['season']}\n"
        explanation += f"Overall Risk Multiplier: {context['risk_multiplier']}x\n\n"
        
        if context['events']:
            explanation += "**Active Factors:**\n"
            for event in context['events']:
                explanation += f"• {event}\n"
        else:
            explanation += "No special events or high-risk factors today.\n"
        
        # Add recommendations
        if context['risk_multiplier'] >= 1.4:
            explanation += "\n⚠️ **HIGH RISK**: Exercise extra caution today."
        elif context['risk_multiplier'] >= 1.2:
            explanation += "\n⚠️ **MODERATE RISK**: Remain vigilant."
        else:
            explanation += "\n✅ **NORMAL RISK**: Standard security precautions apply."
        
        return explanation


class EventImpactAnalyzer:
    """
    Analyze how specific events impact security incidents
    
    This class provides detailed analysis of event-incident correlations
    and helps predict event-related security challenges.
    """
    
    def __init__(self, incidents_df: pd.DataFrame):
        """
        Initialize the EventImpactAnalyzer
        
        Args:
            incidents_df: DataFrame with incident records
        """
        self.incidents_df = incidents_df
        self.simulator = SeasonSimulator()
        logger.info(f"EventImpactAnalyzer initialized with {len(incidents_df)} incidents")
    
    def analyze_event_correlation(self, event_name: str) -> Dict:
        """
        Analyze correlation between an event and incident patterns
        
        Args:
            event_name: Name of event to analyze
            
        Returns:
            Dictionary with correlation analysis
        """
        logger.info(f"Analyzing correlation for event: {event_name}")
        
        context = self.simulator.get_current_context()
        
        # Get event multiplier
        if event_name in context['events']:
            multiplier = context['risk_multiplier']
        else:
            multiplier = 1.0
        
        # Calculate risk increase percentage
        risk_increase = (multiplier - 1.0) * 100
        
        return {
            'event': event_name,
            'risk_increase_percent': round(risk_increase, 1),
            'risk_multiplier': multiplier,
            'affected_areas': self._get_most_affected_areas(),
            'common_incident_types': self._get_common_types_during_event(event_name),
            'recommendations': self._generate_event_recommendations(event_name, multiplier)
        }
    
    def _get_most_affected_areas(self, top_n: int = 5) -> List[str]:
        """
        Get areas most affected by incidents
        
        Args:
            top_n: Number of top areas to return
            
        Returns:
            List of area names
        """
        if 'location' in self.incidents_df.columns:
            top_areas = self.incidents_df['location'].value_counts().head(top_n)
            return top_areas.index.tolist()
        
        # Default areas if no location data
        return [
            'Ariaria Market',
            'City Center',
            'Aba North',
            'Commercial Districts',
            'Transport Hubs'
        ]
    
    def _get_common_types_during_event(self, event_name: str) -> List[str]:
        """
        Get common incident types during specific events
        
        Args:
            event_name: Event name
            
        Returns:
            List of incident types
        """
        # Event-type mapping based on typical patterns
        event_incident_mapping = {
            'Christmas Season': ['theft', 'robbery', 'burglary', 'pickpocketing'],
            'New Year Period': ['theft', 'assault', 'vandalism', 'robbery'],
            'Market Day': ['pickpocketing', 'theft', 'fraud', 'assault'],
            'Month End': ['robbery', 'theft', 'fraud', 'burglary'],
            'Easter': ['theft', 'robbery', 'traffic incidents'],
            'Sallah': ['theft', 'traffic incidents', 'petty crime']
        }
        
        return event_incident_mapping.get(event_name, ['theft', 'assault', 'robbery'])
    
    def _generate_event_recommendations(self, event_name: str, 
                                       multiplier: float) -> List[str]:
        """
        Generate event-specific security recommendations
        
        Args:
            event_name: Event name
            multiplier: Risk multiplier
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        if 'Christmas' in event_name or 'New Year' in event_name:
            recommendations.extend([
                "🛍️ Avoid carrying large amounts of cash while shopping",
                "🏬 Stay in well-populated areas, especially at night",
                "🚗 Park in well-lit, secure areas",
                "📱 Keep valuables secure and out of sight"
            ])
        
        elif 'Market' in event_name:
            recommendations.extend([
                "👥 Stay alert in crowded areas - pickpockets are active",
                "💰 Keep money in secure, front pockets",
                "👜 Carry bags in front of your body",
                "🤝 Shop with a companion when possible"
            ])
        
        elif 'Month End' in event_name:
            recommendations.extend([
                "🏧 Use ATMs during daylight in populated areas",
                "🚶 Avoid walking alone with cash",
                "🚗 Be vigilant when leaving banks",
                "📱 Stay aware of your surroundings"
            ])
        
        # General high-risk recommendations
        if multiplier >= 1.4:
            recommendations.extend([
                "⚠️ Risk level is HIGH during this period",
                "🕐 Minimize travel during late hours",
                "📞 Keep emergency contacts readily available"
            ])
        
        return recommendations
    
    def generate_event_calendar(self, days_ahead: int = 90) -> pd.DataFrame:
        """
        Generate a calendar of upcoming events and their risk levels
        
        Args:
            days_ahead: Number of days to include
            
        Returns:
            DataFrame with event calendar
        """
        forecasts = self.simulator.simulate_future_risk(days_ahead)
        
        calendar_data = []
        for forecast in forecasts:
            calendar_data.append({
                'Date': forecast['date'],
                'Day': forecast['day_of_week'],
                'Risk Level': forecast['risk_level'],
                'Risk Multiplier': forecast['risk_multiplier'],
                'Events': ', '.join(forecast['events']) if forecast['events'] else 'None',
                'Season': forecast['season']
            })
        
        df = pd.DataFrame(calendar_data)
        logger.info(f"Generated event calendar for {days_ahead} days")
        
        return df