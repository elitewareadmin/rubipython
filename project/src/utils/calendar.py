"""
Calendar integration module
Provides calendar management functionality
"""
from datetime import datetime, timedelta
from src.utils.logger import get_logger

class CalendarManager:
    """Calendar Manager for handling scheduling"""
    def __init__(self):
        self.logger = get_logger()
        self.events = []
    
    def add_event(self, title, start_time, end_time, attendees=None, location=None, description=None):
        """Add a calendar event"""
        event = {
            "title": title,
            "start_time": start_time,
            "end_time": end_time,
            "attendees": attendees or [],
            "location": location,
            "description": description,
            "created": datetime.now()
        }
        self.events.append(event)
        return event
    
    def get_events(self, start_date=None, end_date=None):
        """Get events within a date range"""
        filtered_events = self.events
        
        if start_date:
            filtered_events = [e for e in filtered_events 
                             if e["start_time"].date() >= start_date]
        
        if end_date:
            filtered_events = [e for e in filtered_events 
                             if e["end_time"].date() <= end_date]
        
        return sorted(filtered_events, key=lambda x: x["start_time"])
    
    def get_conflicts(self, start_time, end_time):
        """Check for scheduling conflicts"""
        conflicts = []
        for event in self.events:
            if (start_time < event["end_time"] and 
                end_time > event["start_time"]):
                conflicts.append(event)
        return conflicts
    
    def suggest_meeting_times(self, duration_minutes, within_days=7):
        """Suggest available meeting slots"""
        suggestions = []
        start_date = datetime.now()
        end_date = start_date + timedelta(days=within_days)
        
        current = start_date
        while current < end_date:
            # Only suggest times during business hours (9 AM - 5 PM)
            if current.hour >= 9 and current.hour < 17:
                potential_end = current + timedelta(minutes=duration_minutes)
                if not self.get_conflicts(current, potential_end):
                    suggestions.append(current)
            current += timedelta(minutes=30)
        
        return suggestions[:5]  # Return top 5 suggestions