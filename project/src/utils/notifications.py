"""
Notifications module for smart alerts
"""
from datetime import datetime, timedelta
from src.utils.logger import get_logger

class NotificationManager:
    """Notification Manager for handling smart alerts"""
    def __init__(self):
        self.logger = get_logger()
        self.notifications = []
        self.preferences = {
            "deadline_warning": 24,  # hours
            "meeting_reminder": 15,  # minutes
            "daily_summary": True,
            "priority_alerts": True
        }
    
    def check_notifications(self, tasks, meetings=None):
        """Check and generate notifications"""
        try:
            current_time = datetime.now()
            notifications = []
            
            # Task deadline notifications
            for task in tasks:
                if task.completed:
                    continue
                    
                if task.due_date:
                    hours_until_due = (task.due_date - current_time).total_seconds() / 3600
                    
                    if 0 < hours_until_due <= self.preferences["deadline_warning"]:
                        urgency = "URGENT: " if task.priority in ["high", "critical"] else ""
                        notifications.append({
                            "type": "deadline",
                            "message": f"{urgency}Task '{task.title}' is due in {int(hours_until_due)} hours",
                            "task_id": task.id,
                            "timestamp": current_time,
                            "priority": "high" if hours_until_due < 4 else "medium"
                        })
            
            # Meeting reminders
            if meetings:
                for meeting in meetings:
                    minutes_until_meeting = (meeting["start_time"] - current_time).total_seconds() / 60
                    
                    if 0 < minutes_until_meeting <= self.preferences["meeting_reminder"]:
                        notifications.append({
                            "type": "meeting",
                            "message": f"Meeting '{meeting['title']}' starts in {int(minutes_until_meeting)} minutes",
                            "meeting_id": meeting.get("id"),
                            "timestamp": current_time,
                            "priority": "high"
                        })
            
            # Daily summary (if enabled)
            if self.preferences["daily_summary"]:
                current_hour = current_time.hour
                if current_hour == 9:  # 9 AM
                    due_today = [t for t in tasks if not t.completed and t.due_date and 
                               t.due_date.date() == current_time.date()]
                    if due_today:
                        notifications.append({
                            "type": "summary",
                            "message": f"You have {len(due_today)} tasks due today",
                            "timestamp": current_time,
                            "priority": "medium"
                        })
            
            return notifications
            
        except Exception as e:
            self.logger.error(f"Error checking notifications: {e}")
            return []
    
    def update_preferences(self, **kwargs):
        """Update notification preferences"""
        self.preferences.update(kwargs)
    
    def get_preferences(self):
        """Get current notification preferences"""
        return self.preferences.copy()
    
    def clear_notifications(self):
        """Clear all notifications"""
        self.notifications = []