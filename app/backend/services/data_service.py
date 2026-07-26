"""
Data Service
Handles loading and caching CSV data files
"""

import logging
import pandas as pd
from typing import Optional, List, Dict, Any
from datetime import datetime
import os

from ..config import settings

logger = logging.getLogger(__name__)


class DataService:
    """Service for data management"""
    
    def __init__(self):
        """Initialize data service"""
        self.users_df: Optional[pd.DataFrame] = None
        self.devices_df: Optional[pd.DataFrame] = None
        self.profiles_df: Optional[pd.DataFrame] = None
        self.cybersecurity_df: Optional[pd.DataFrame] = None
        self.processed_logs_df: Optional[pd.DataFrame] = None
        
        self._load_data()
    
    def _load_data(self):
        """Load all data files"""
        try:
            if os.path.exists(settings.USERS_CSV):
                self.users_df = pd.read_csv(settings.USERS_CSV)
                logger.info(f"✅ Users data loaded ({len(self.users_df)} records)")
            
            if os.path.exists(settings.DEVICES_CSV):
                self.devices_df = pd.read_csv(settings.DEVICES_CSV)
                logger.info(f"✅ Devices data loaded ({len(self.devices_df)} records)")
            
            if os.path.exists(settings.PROFILES_CSV):
                self.profiles_df = pd.read_csv(settings.PROFILES_CSV)
                logger.info(f"✅ Profiles data loaded ({len(self.profiles_df)} records)")
            
            if os.path.exists(settings.CYBERSECURITY_CSV):
                self.cybersecurity_df = pd.read_csv(settings.CYBERSECURITY_CSV)
                logger.info(f"✅ Cybersecurity data loaded ({len(self.cybersecurity_df)} records)")
            
            if os.path.exists(settings.PROCESSED_LOGS_CSV):
                self.processed_logs_df = pd.read_csv(settings.PROCESSED_LOGS_CSV)
                logger.info(f"✅ Processed logs loaded ({len(self.processed_logs_df)} records)")
            
        except Exception as e:
            logger.error(f"❌ Error loading data: {e}")
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        if self.users_df is None:
            return None
        
        user_rows = self.users_df[self.users_df['user_id'] == user_id]
        if len(user_rows) > 0:
            return user_rows.iloc[0].to_dict()
        return None
    
    def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get device by ID"""
        if self.devices_df is None:
            return None
        
        device_rows = self.devices_df[self.devices_df['device_id'] == device_id]
        if len(device_rows) > 0:
            return device_rows.iloc[0].to_dict()
        return None
    
    def get_all_users(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all users"""
        if self.users_df is None:
            return []
        
        return self.users_df.head(limit).to_dict('records')
    
    def get_all_devices(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all devices"""
        if self.devices_df is None:
            return []
        
        return self.devices_df.head(limit).to_dict('records')
    
    def get_entity_events(self, entity_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent events for an entity"""
        if self.cybersecurity_df is None:
            return []

        try:
            entity_events = self.cybersecurity_df[self.cybersecurity_df['entity_id'] == entity_id]
            return entity_events.head(limit).to_dict('records')
        except Exception as e:
            logger.error(f"Error getting entity events: {e}")
            return []

    def get_user_events(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Deprecated alias for entity events using user identifier"""
        return self.get_entity_events(user_id, limit)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get data statistics"""
        stats = {
            "users_count": len(self.users_df) if self.users_df is not None else 0,
            "devices_count": len(self.devices_df) if self.devices_df is not None else 0,
            "events_count": len(self.cybersecurity_df) if self.cybersecurity_df is not None else 0,
            "processed_logs_count": len(self.processed_logs_df) if self.processed_logs_df is not None else 0,
        }
        
        # Calculate date range
        if self.cybersecurity_df is not None and 'timestamp' in self.cybersecurity_df.columns:
            try:
                stats["date_range"] = {
                    "start": self.cybersecurity_df['timestamp'].min(),
                    "end": self.cybersecurity_df['timestamp'].max()
                }
            except:
                pass
        
        return stats
    
    def search_events(
        self,
        entity_id: Optional[str] = None,
        resource: Optional[str] = None,
        location: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search events with filters"""
        if self.cybersecurity_df is None:
            return []
        
        try:
            df = self.cybersecurity_df.copy()
            
            if entity_id:
                df = df[df['entity_id'] == entity_id]
            
            if resource:
                df = df[df['resource_accessed'] == resource]
            
            if location:
                df = df[df['geo_location'] == location]
            
            return df.head(limit).to_dict('records')
            
        except Exception as e:
            logger.error(f"Error searching events: {e}")
            return []
    
    def get_time_series_data(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get time series data for analytics"""
        if self.cybersecurity_df is None or len(self.cybersecurity_df) == 0:
            return []
        
        try:
            df = self.cybersecurity_df.copy()
            
            # Convert timestamp to datetime
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                # Group by hour
                df['hour'] = df['timestamp'].dt.floor('h')
                
                time_series = df.groupby('hour').size().reset_index(name='count')
                time_series['risk_score'] = df.groupby('hour')['risk_score'].mean().values if 'risk_score' in df.columns else 0.5
                
                return time_series.to_dict('records')
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting time series data: {e}")
            return []
    
    def get_top_resources(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top accessed resources"""
        if self.cybersecurity_df is None:
            return []
        
        try:
            resource_counts = self.cybersecurity_df['resource_accessed'].value_counts().head(limit)
            return [
                {"resource": resource, "count": int(count)}
                for resource, count in resource_counts.items()
            ]
        except Exception as e:
            logger.error(f"Error getting top resources: {e}")
            return []
    
    def get_top_locations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top locations"""
        if self.cybersecurity_df is None:
            return []
        
        try:
            location_counts = self.cybersecurity_df['geo_location'].value_counts().head(limit)
            return [
                {"location": location, "count": int(count)}
                for location, count in location_counts.items()
            ]
        except Exception as e:
            logger.error(f"Error getting top locations: {e}")
            return []

    def get_top_risk_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Return the highest-risk events to seed the alert queue"""
        if self.cybersecurity_df is None or 'risk_score' not in self.cybersecurity_df.columns:
            return []

        try:
            df = self.cybersecurity_df.sort_values(by='risk_score', ascending=False).head(limit)
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"Error getting top risk events: {e}")
            return []
