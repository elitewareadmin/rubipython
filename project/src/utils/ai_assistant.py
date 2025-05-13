"""
AI Assistant module for task management
Provides AI-powered assistance for task management
"""
from datetime import datetime, timedelta
from src.utils.logger import get_logger

class AIAssistant:
    """AI Assistant class for providing task management help"""
    def __init__(self):
        self.logger = get_logger()
    
    def analyze_tasks(self, tasks):
        """Analyze tasks and provide insights with emotional intelligence"""
        try:
            # Analyze tasks
            overdue_tasks = []
            urgent_tasks = []
            upcoming_tasks = []
            today = datetime.now().date()
            
            for task in tasks:
                if task.due_date:
                    days_until_due = (task.due_date.date() - today).days
                    if days_until_due < 0 and not task.completed:
                        overdue_tasks.append(task)
                    elif days_until_due <= 3 and not task.completed:
                        urgent_tasks.append(task)
                    elif days_until_due <= 7 and not task.completed:
                        upcoming_tasks.append(task)
            
            # Generate empathetic insights
            insights = []
            
            # Handle overdue tasks with empathy
            if overdue_tasks:
                insights.append("I notice you have some overdue tasks. Don't worry, it happens to everyone! " +
                              f"Let's work together to tackle these {len(overdue_tasks)} tasks first.")
            
            # Address urgent tasks with encouragement
            if urgent_tasks:
                insights.append(f"\nYou have {len(urgent_tasks)} tasks due soon. I know it might feel overwhelming, " +
                              "but we can break this down into manageable steps.")
            
            if upcoming_tasks:
                insights.append(f"\nLooking ahead, you have {len(upcoming_tasks)} tasks coming up this week. " +
                              "Great job planning ahead!")
            
            # Add positive reinforcement for progress
            total_tasks = len(tasks)
            completed_tasks = len([t for t in tasks if t.completed])
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            if completion_rate >= 70:
                insights.append(f"\nOutstanding work! You've completed {completion_rate:.1f}% of your tasks. " +
                              "Keep up the great momentum!")
            elif completion_rate >= 40:
                insights.append(f"\nYou're making good progress with a {completion_rate:.1f}% completion rate. " +
                              "Every step forward counts!")
            else:
                insights.append(f"\nI see you're at {completion_rate:.1f}% completion. Remember, every journey " +
                              "begins with a single step. Let's tackle these tasks together!")
            
            insights.append(f"\nTask Overview:")
            insights.append(f"- Total Tasks: {total_tasks}")
            insights.append(f"- Completed: {completed_tasks}")
            
            # Add priority distribution with supportive messaging
            priority_counts = {
                "critical": len([t for t in tasks if t.priority == "critical" and not t.completed]),
                "high": len([t for t in tasks if t.priority == "high" and not t.completed]),
                "medium": len([t for t in tasks if t.priority == "medium" and not t.completed]),
                "low": len([t for t in tasks if t.priority == "low" and not t.completed])
            }
            
            if priority_counts["critical"] > 0 or priority_counts["high"] > 0:
                insights.append("\nI notice you have some high-priority tasks:")
                for priority, count in priority_counts.items():
                    if count > 0:
                        insights.append(f"- {priority.capitalize()}: {count} tasks")
                insights.append("\nRemember to take breaks and pace yourself. Your well-being matters!")
            
            return "\n".join(insights)
            
        except Exception as e:
            self.logger.error(f"Error analyzing tasks: {e}")
            return "I encountered an error while analyzing the tasks. Let's try again!"
    
    def suggest_task_organization(self, tasks):
        """Suggest how to better organize tasks with emotional support"""
        try:
            # Analyze current organization
            categories = {}
            uncategorized = []
            
            for task in tasks:
                if task.category:
                    if task.category not in categories:
                        categories[task.category] = []
                    categories[task.category].append(task)
                else:
                    uncategorized.append(task)
            
            # Generate empathetic suggestions
            suggestions = ["I've looked at your tasks and have some friendly suggestions to help you stay organized:"]
            
            # Category suggestions with encouragement
            if uncategorized:
                suggestions.append(f"\n1. I notice you have {len(uncategorized)} tasks without categories. " +
                                "That's perfectly fine! Would you like to try organizing them into groups? " +
                                "This might help make things feel more manageable.")
            
            # Priority management with emotional support
            suggestions.append("\n2. Let's look at your priorities:")
            critical_tasks = [t for t in tasks if t.priority == "critical" and not t.completed]
            high_priority = [t for t in tasks if t.priority == "high" and not t.completed]
            
            if critical_tasks:
                suggestions.append(f"   - I see {len(critical_tasks)} critical tasks. Remember, it's okay to ask for help " +
                                "if you need it!")
            if high_priority:
                suggestions.append(f"   - There are {len(high_priority)} high-priority tasks. Let's break these down " +
                                "into smaller, more manageable steps.")
            
            # Time management with understanding
            suggestions.append("\n3. About your schedule:")
            today = datetime.now().date()
            this_week = [t for t in tasks if t.due_date and 
                        (t.due_date.date() - today).days <= 7 and 
                        not t.completed]
            
            if this_week:
                suggestions.append(f"   - You have {len(this_week)} tasks due this week. I know this might feel like a lot, " +
                                "but let's take it one day at a time.")
                suggestions.append("   - Consider setting aside specific times for different tasks - and don't forget " +
                                "to schedule breaks too!")
            
            # Category organization with positive reinforcement
            if categories:
                suggestions.append("\n4. You're doing great with categorizing tasks! Here's the current breakdown:")
                for category, cat_tasks in categories.items():
                    active_tasks = [t for t in cat_tasks if not t.completed]
                    if active_tasks:
                        suggestions.append(f"   - {category}: {len(active_tasks)} active tasks")
            
            suggestions.append("\nRemember: Progress isn't always linear, and that's okay! " +
                             "Take care of yourself while working through these tasks. " +
                             "If you're feeling overwhelmed, we can break things down further.")
            
            return "\n".join(suggestions)
            
        except Exception as e:
            self.logger.error(f"Error generating suggestions: {e}")
            return "I encountered a small hiccup while preparing suggestions. Let's try again!"