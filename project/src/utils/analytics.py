"""
Analytics module for task and productivity insights
"""
from datetime import datetime, timedelta
from collections import defaultdict
from src.utils.logger import get_logger

class AnalyticsManager:
    """Analytics Manager for generating insights"""
    def __init__(self):
        self.logger = get_logger()
    
    def generate_productivity_report(self, tasks, days=30):
        """Generate productivity insights"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Task completion trends
            completed_tasks = defaultdict(int)
            completion_times = []
            categories = defaultdict(int)
            priorities = defaultdict(int)
            
            for task in tasks:
                if task.completed and task.completed_date:
                    if start_date <= task.completed_date <= end_date:
                        date_key = task.completed_date.strftime('%Y-%m-%d')
                        completed_tasks[date_key] += 1
                        
                        # Calculate completion time
                        time_to_complete = task.completed_date - task.created
                        completion_times.append(time_to_complete.total_seconds() / 3600)  # hours
                
                if task.category:
                    categories[task.category] += 1
                priorities[task.priority] += 1
            
            # Calculate metrics
            total_completed = sum(completed_tasks.values())
            avg_daily_completion = total_completed / days if days > 0 else 0
            avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
            
            return {
                "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                "total_completed": total_completed,
                "avg_daily_completion": round(avg_daily_completion, 2),
                "avg_completion_time": round(avg_completion_time, 2),  # hours
                "completion_trend": dict(completed_tasks),
                "category_distribution": dict(categories),
                "priority_distribution": dict(priorities)
            }
            
        except Exception as e:
            self.logger.error(f"Error generating analytics: {e}")
            return None
    
    def get_productivity_score(self, tasks, days=7):
        """Calculate productivity score (0-100)"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            total_tasks = 0
            completed_on_time = 0
            overdue_completed = 0
            still_overdue = 0
            
            for task in tasks:
                if not task.due_date:
                    continue
                
                if start_date <= task.due_date <= end_date:
                    total_tasks += 1
                    
                    if task.completed:
                        if task.completed_date <= task.due_date:
                            completed_on_time += 1
                        else:
                            overdue_completed += 1
                    elif task.due_date < datetime.now():
                        still_overdue += 1
            
            if total_tasks == 0:
                return 100  # Perfect score if no tasks were due
            
            # Score calculation:
            # - Completed on time: 100%
            # - Completed late: 50%
            # - Still overdue: 0%
            score = (completed_on_time * 100 + overdue_completed * 50) / total_tasks
            
            return round(min(100, max(0, score)))
            
        except Exception as e:
            self.logger.error(f"Error calculating productivity score: {e}")
            return None
    
    def get_task_suggestions(self, tasks):
        """Generate task management suggestions"""
        try:
            suggestions = []
            now = datetime.now()
            
            # Check for overdue tasks
            overdue = [t for t in tasks if not t.completed and t.due_date and t.due_date < now]
            if overdue:
                suggestions.append(f"You have {len(overdue)} overdue tasks. Consider prioritizing these.")
            
            # Check workload distribution
            due_this_week = [t for t in tasks if not t.completed and t.due_date and 
                           t.due_date <= now + timedelta(days=7)]
            if len(due_this_week) > 10:
                suggestions.append("Heavy workload this week. Consider delegating or rescheduling some tasks.")
            
            # Check category balance
            categories = defaultdict(int)
            for task in tasks:
                if not task.completed and task.category:
                    categories[task.category] += 1
            
            max_category = max(categories.items(), key=lambda x: x[1], default=(None, 0))
            if max_category[1] > len(tasks) * 0.5:
                suggestions.append(f"Many tasks in category '{max_category[0]}'. Consider diversifying your focus.")
            
            return suggestions
            
        except Exception as e:
            self.logger.error(f"Error generating task suggestions: {e}")
            return []