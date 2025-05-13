"""
Reports module for task management
Provides report generation and email functionality
"""
import os
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.utils.logger import get_logger

class ReportManager:
    """Report Manager class for generating and sending task reports"""
    def __init__(self):
        self.logger = get_logger()
    
    def generate_summary_report(self, tasks):
        """Generate a summary report of tasks"""
        try:
            # Calculate statistics
            total_tasks = len(tasks)
            completed_tasks = len([t for t in tasks if t.completed])
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            # Count tasks by priority
            priority_counts = {
                "critical": len([t for t in tasks if t.priority == "critical"]),
                "high": len([t for t in tasks if t.priority == "high"]),
                "medium": len([t for t in tasks if t.priority == "medium"]),
                "low": len([t for t in tasks if t.priority == "low"])
            }
            
            # Count tasks by category
            categories = {}
            for task in tasks:
                if task.category:
                    categories[task.category] = categories.get(task.category, 0) + 1
            
            # Generate report
            report = []
            report.append("Task Management Summary Report")
            report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            report.append("\nOverall Statistics:")
            report.append(f"- Total Tasks: {total_tasks}")
            report.append(f"- Completed Tasks: {completed_tasks}")
            report.append(f"- Completion Rate: {completion_rate:.1f}%")
            
            report.append("\nTasks by Priority:")
            for priority, count in priority_counts.items():
                report.append(f"- {priority.capitalize()}: {count}")
            
            if categories:
                report.append("\nTasks by Category:")
                for category, count in categories.items():
                    report.append(f"- {category}: {count}")
            
            # Add overdue tasks
            overdue_tasks = [t for t in tasks if t.due_date and 
                           t.due_date.date() < datetime.now().date() and 
                           not t.completed]
            if overdue_tasks:
                report.append("\nOverdue Tasks:")
                for task in overdue_tasks:
                    report.append(f"- {task.title} (Due: {task.due_date.strftime('%Y-%m-%d')})")
            
            return "\n".join(report)
            
        except Exception as e:
            self.logger.error(f"Error generating summary report: {e}")
            return "Error generating report"
    
    def generate_detailed_report(self, tasks):
        """Generate a detailed report of all tasks"""
        try:
            report = []
            report.append("Detailed Task Report")
            report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            
            # Group tasks by status
            active_tasks = [t for t in tasks if not t.completed]
            completed_tasks = [t for t in tasks if t.completed]
            
            if active_tasks:
                report.append("\nActive Tasks:")
                for task in active_tasks:
                    report.append(f"\nTask: {task.title}")
                    report.append(f"ID: {task.id}")
                    report.append(f"Priority: {task.priority.upper()}")
                    if task.description:
                        report.append(f"Description: {task.description}")
                    if task.due_date:
                        report.append(f"Due Date: {task.due_date.strftime('%Y-%m-%d')}")
                    if task.category:
                        report.append(f"Category: {task.category}")
                    if task.tags:
                        report.append(f"Tags: {', '.join(task.tags)}")
                    if task.progress > 0:
                        report.append(f"Progress: {task.progress}%")
            
            if completed_tasks:
                report.append("\nCompleted Tasks:")
                for task in completed_tasks:
                    report.append(f"\nTask: {task.title}")
                    report.append(f"Completed on: {task.completed_date.strftime('%Y-%m-%d')}")
                    if task.category:
                        report.append(f"Category: {task.category}")
            
            return "\n".join(report)
            
        except Exception as e:
            self.logger.error(f"Error generating detailed report: {e}")
            return "Error generating report"
    
    def send_report_email(self, recipient, subject, report_content):
        """Send a report via email"""
        try:
            # Email configuration
            sender_email = os.getenv("EMAIL_SENDER")
            sender_password = os.getenv("EMAIL_PASSWORD")
            smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            
            if not all([sender_email, sender_password]):
                raise ValueError("Email configuration is incomplete")
            
            # Create message
            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["To"] = recipient
            msg["Subject"] = subject
            
            # Add report content
            msg.attach(MIMEText(report_content, "plain"))
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending email: {e}")
            return False