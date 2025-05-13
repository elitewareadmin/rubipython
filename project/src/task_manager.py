"""
Task Manager module
Handles the core business logic for managing tasks
"""
import os
import json
from datetime import datetime
from src.models.task import Task
from src.utils.logger import get_logger

class TaskManager:
    """Task Manager class for handling task operations"""
    def __init__(self, data_file="data/tasks.json"):
        self.logger = get_logger()
        self.data_file = data_file
        self.tasks = []
        self.load_tasks()
    
    def load_tasks(self):
        """Load tasks from the data file"""
        try:
            # Create data directory if it doesn't exist
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            # Load tasks from file if it exists
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    task_data = json.load(f)
                    self.tasks = [Task.from_dict(task) for task in task_data]
                    self.logger.info(f"Loaded {len(self.tasks)} tasks from {self.data_file}")
            else:
                # Create empty file
                self.save_tasks()
                self.logger.info(f"Created new task file at {self.data_file}")
        except Exception as e:
            self.logger.error(f"Error loading tasks: {e}")
            self.tasks = []
    
    def save_tasks(self):
        """Save tasks to the data file"""
        try:
            # Create data directory if it doesn't exist
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            # Save tasks to file
            task_data = [task.to_dict() for task in self.tasks]
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(task_data, f, indent=2)
            self.logger.info(f"Saved {len(self.tasks)} tasks to {self.data_file}")
        except Exception as e:
            self.logger.error(f"Error saving tasks: {e}")
    
    def add_task(self, title, description="", priority="medium", due_date=None, category=None):
        """Add a new task"""
        task = Task(
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            category=category
        )
        self.tasks.append(task)
        self.save_tasks()
        self.logger.info(f"Added task: {task.id} - {task.title}")
        return task
    
    def get_tasks(self, filter_completed=None, filter_category=None, filter_priority=None):
        """Get tasks with optional filtering"""
        filtered_tasks = self.tasks
        
        if filter_completed is not None:
            filtered_tasks = [task for task in filtered_tasks if task.completed == filter_completed]
        
        if filter_category:
            filtered_tasks = [task for task in filtered_tasks if task.category == filter_category]
        
        if filter_priority:
            filtered_tasks = [task for task in filtered_tasks if task.priority == filter_priority]
        
        return filtered_tasks
    
    def get_task_by_id(self, task_id):
        """Get a task by its ID"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def update_task(self, task_id, **kwargs):
        """Update a task with the given ID"""
        task = self.get_task_by_id(task_id)
        if task:
            for key, value in kwargs.items():
                if hasattr(task, key):
                    old_value = getattr(task, key)
                    setattr(task, key, value)
                    task._record_change(key, old_value, value)
            
            # Update the modified time
            task.modified = datetime.now()
            self.save_tasks()
            self.logger.info(f"Updated task: {task_id}")
            return task
        return None
    
    def complete_task(self, task_id):
        """Mark a task as completed"""
        task = self.get_task_by_id(task_id)
        if task:
            old_completed = task.completed
            task.completed = True
            task.completed_date = datetime.now()
            task.modified = datetime.now()
            task._record_change("completed", old_completed, True)
            task._record_change("completed_date", None, task.completed_date)
            self.save_tasks()
            self.logger.info(f"Completed task: {task_id}")
            return task
        return None
    
    def delete_task(self, task_id):
        """Delete a task by its ID"""
        task = self.get_task_by_id(task_id)
        if task:
            self.tasks.remove(task)
            self.save_tasks()
            self.logger.info(f"Deleted task: {task_id}")
            return True
        return False
    
    def search_tasks(self, query):
        """Search tasks for a given query"""
        if not query:
            return []
        
        query = query.lower()
        results = []
        
        for task in self.tasks:
            if (query in task.title.lower() or 
                query in task.description.lower() or 
                (task.category and query in task.category.lower())):
                results.append(task)
        
        self.logger.info(f"Search for '{query}' returned {len(results)} results")
        return results
    
    def get_categories(self):
        """Get list of all unique categories"""
        categories = set()
        for task in self.tasks:
            if task.category:
                categories.add(task.category)
        return sorted(list(categories))
    
    def get_task_history(self, task_id, field=None, start_date=None, end_date=None):
        """Get history for a specific task"""
        task = self.get_task_by_id(task_id)
        if task:
            return task.get_history(field, start_date, end_date)
        return []