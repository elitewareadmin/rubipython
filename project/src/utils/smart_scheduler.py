"""
Smart Scheduler module for intelligent task scheduling
"""
from datetime import datetime, timedelta
from src.utils.logger import get_logger

class SmartScheduler:
    """Smart Scheduler for intelligent task management"""
    def __init__(self):
        self.logger = get_logger()
        self.work_hours = {
            "start": 9,  # 9 AM
            "end": 17    # 5 PM
        }
        self.break_duration = 30  # minutes
        self.meeting_buffer = 15   # minutes
    
    def suggest_schedule(self, tasks, meetings=None):
        """Suggest an optimal schedule for tasks"""
        try:
            schedule = []
            current_time = datetime.now()
            end_of_day = current_time.replace(
                hour=self.work_hours["end"],
                minute=0,
                second=0,
                microsecond=0
            )
            
            # Sort tasks by priority and due date
            prioritized_tasks = sorted(
                [t for t in tasks if not t.completed],
                key=lambda x: (
                    self._priority_score(x.priority),
                    x.due_date if x.due_date else datetime.max
                )
            )
            
            # Account for meetings
            blocked_times = []
            if meetings:
                for meeting in meetings:
                    blocked_times.append({
                        "start": meeting["start_time"],
                        "end": meeting["end_time"]
                    })
            
            # Create schedule
            current_slot = current_time
            for task in prioritized_tasks:
                if current_slot >= end_of_day:
                    break
                
                # Find next available slot
                slot = self._find_next_slot(
                    current_slot,
                    blocked_times,
                    duration=60  # Default 1-hour slots
                )
                
                if slot:
                    schedule.append({
                        "task": task,
                        "start_time": slot["start"],
                        "end_time": slot["end"],
                        "priority": task.priority
                    })
                    current_slot = slot["end"] + timedelta(minutes=self.break_duration)
            
            return schedule
            
        except Exception as e:
            self.logger.error(f"Error suggesting schedule: {e}")
            return []
    
    def _priority_score(self, priority):
        """Convert priority to numeric score"""
        scores = {
            "critical": 0,
            "high": 1,
            "medium": 2,
            "low": 3
        }
        return scores.get(priority, 4)
    
    def _find_next_slot(self, start_time, blocked_times, duration):
        """Find next available time slot"""
        current = start_time
        
        while current.hour < self.work_hours["end"]:
            slot_end = current + timedelta(minutes=duration)
            
            # Check if slot is available
            is_available = True
            for blocked in blocked_times:
                if (current < blocked["end"] and 
                    slot_end > blocked["start"]):
                    is_available = False
                    current = blocked["end"]
                    break
            
            if is_available:
                return {
                    "start": current,
                    "end": slot_end
                }
            
            current += timedelta(minutes=self.meeting_buffer)
        
        return None
    
    def update_work_hours(self, start_hour, end_hour):
        """Update work hours"""
        self.work_hours["start"] = max(0, min(23, start_hour))
        self.work_hours["end"] = max(0, min(23, end_hour))
    
    def set_break_duration(self, minutes):
        """Set break duration between tasks"""
        self.break_duration = max(5, min(60, minutes))
    
    def set_meeting_buffer(self, minutes):
        """Set buffer time around meetings"""
        self.meeting_buffer = max(5, min(30, minutes))