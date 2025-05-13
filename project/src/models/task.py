"""
Task model
Defines the Task class representing a task in the system
"""
import uuid
from datetime import datetime

class Task:
    """Task class representing a single task"""
    PRIORITY_LEVELS = ["low", "medium", "high", "critical"]
    
    def __init__(
        self, 
        title, 
        description="", 
        priority="medium", 
        due_date=None, 
        category=None,
        completed=False, 
        completed_date=None,
        id=None,
        created=None,
        modified=None,
        subtasks=None,
        tags=None,
        dependencies=None,
        notes=None,
        time_spent=0,
        progress=0,
        template=False,
        shared_with=None,
        reminder=None,
        history=None
    ):
        self.id = id or str(uuid.uuid4())
        self.title = title
        self.description = description
        self.priority = priority if priority in self.PRIORITY_LEVELS else "medium"
        self.due_date = due_date  # Should be a datetime object or None
        self.category = category
        self.completed = completed
        self.completed_date = completed_date  # Should be a datetime object or None
        self.created = created or datetime.now()
        self.modified = modified or datetime.now()
        self.subtasks = subtasks or []
        self.tags = tags or []
        self.dependencies = dependencies or []  # List of task IDs this task depends on
        self.notes = notes or []  # List of {text, timestamp, author} dictionaries
        self.time_spent = time_spent  # Time spent in minutes
        self.progress = min(max(progress, 0), 100)  # Progress percentage (0-100)
        self.template = template  # Whether this is a template task
        self.shared_with = shared_with or []  # List of user IDs
        self.reminder = reminder  # Datetime for reminder
        self.history = history or []  # List of {field, old_value, new_value, timestamp} dictionaries
    
    def to_dict(self):
        """Convert task to dictionary for serialization"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "category": self.category,
            "completed": self.completed,
            "completed_date": self.completed_date.isoformat() if self.completed_date else None,
            "created": self.created.isoformat(),
            "modified": self.modified.isoformat(),
            "subtasks": [subtask.to_dict() for subtask in self.subtasks],
            "tags": self.tags,
            "dependencies": self.dependencies,
            "notes": self.notes,
            "time_spent": self.time_spent,
            "progress": self.progress,
            "template": self.template,
            "shared_with": self.shared_with,
            "reminder": self.reminder.isoformat() if self.reminder else None,
            "history": self.history
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a task from a dictionary"""
        # Convert ISO format dates back to datetime objects
        due_date = datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None
        completed_date = datetime.fromisoformat(data["completed_date"]) if data.get("completed_date") else None
        created = datetime.fromisoformat(data["created"]) if data.get("created") else None
        modified = datetime.fromisoformat(data["modified"]) if data.get("modified") else None
        reminder = datetime.fromisoformat(data["reminder"]) if data.get("reminder") else None
        
        # Convert subtasks
        subtasks = [cls.from_dict(subtask) for subtask in data.get("subtasks", [])]
        
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            priority=data.get("priority", "medium"),
            due_date=due_date,
            category=data.get("category"),
            completed=data.get("completed", False),
            completed_date=completed_date,
            created=created,
            modified=modified,
            subtasks=subtasks,
            tags=data.get("tags", []),
            dependencies=data.get("dependencies", []),
            notes=data.get("notes", []),
            time_spent=data.get("time_spent", 0),
            progress=data.get("progress", 0),
            template=data.get("template", False),
            shared_with=data.get("shared_with", []),
            reminder=reminder,
            history=data.get("history", [])
        )
    
    def _record_change(self, field, old_value, new_value):
        """Record a change in the task's history"""
        change = {
            "field": field,
            "old_value": old_value,
            "new_value": new_value,
            "timestamp": datetime.now()
        }
        self.history.append(change)
    
    def add_subtask(self, title, description="", priority="medium"):
        """Add a subtask to this task"""
        subtask = Task(
            title=title,
            description=description,
            priority=priority,
            category=self.category
        )
        old_subtasks = len(self.subtasks)
        self.subtasks.append(subtask)
        self._record_change("subtasks", old_subtasks, len(self.subtasks))
        self.modified = datetime.now()
        return subtask
    
    def remove_subtask(self, subtask_id):
        """Remove a subtask by its ID"""
        old_subtasks = len(self.subtasks)
        self.subtasks = [st for st in self.subtasks if st.id != subtask_id]
        self._record_change("subtasks", old_subtasks, len(self.subtasks))
        self.modified = datetime.now()
    
    def get_subtask(self, subtask_id):
        """Get a subtask by its ID"""
        for subtask in self.subtasks:
            if subtask.id == subtask_id:
                return subtask
        return None
    
    def add_note(self, text, author="system"):
        """Add a note to the task"""
        note = {
            "text": text,
            "timestamp": datetime.now(),
            "author": author
        }
        old_notes = len(self.notes)
        self.notes.append(note)
        self._record_change("notes", old_notes, len(self.notes))
        self.modified = datetime.now()
    
    def add_tag(self, tag):
        """Add a tag to the task"""
        if tag not in self.tags:
            old_tags = self.tags.copy()
            self.tags.append(tag)
            self._record_change("tags", old_tags, self.tags)
            self.modified = datetime.now()
    
    def remove_tag(self, tag):
        """Remove a tag from the task"""
        if tag in self.tags:
            old_tags = self.tags.copy()
            self.tags.remove(tag)
            self._record_change("tags", old_tags, self.tags)
            self.modified = datetime.now()
    
    def add_dependency(self, task_id):
        """Add a dependency to the task"""
        if task_id not in self.dependencies:
            old_deps = self.dependencies.copy()
            self.dependencies.append(task_id)
            self._record_change("dependencies", old_deps, self.dependencies)
            self.modified = datetime.now()
    
    def remove_dependency(self, task_id):
        """Remove a dependency from the task"""
        if task_id in self.dependencies:
            old_deps = self.dependencies.copy()
            self.dependencies.remove(task_id)
            self._record_change("dependencies", old_deps, self.dependencies)
            self.modified = datetime.now()
    
    def update_progress(self, progress):
        """Update the task progress"""
        old_progress = self.progress
        self.progress = min(max(progress, 0), 100)
        self._record_change("progress", old_progress, self.progress)
        self.modified = datetime.now()
    
    def add_time(self, minutes):
        """Add time spent to the task"""
        old_time = self.time_spent
        self.time_spent += minutes
        self._record_change("time_spent", old_time, self.time_spent)
        self.modified = datetime.now()
    
    def share_with(self, user_id):
        """Share the task with a user"""
        if user_id not in self.shared_with:
            old_shared = self.shared_with.copy()
            self.shared_with.append(user_id)
            self._record_change("shared_with", old_shared, self.shared_with)
            self.modified = datetime.now()
    
    def unshare_with(self, user_id):
        """Unshare the task with a user"""
        if user_id in self.shared_with:
            old_shared = self.shared_with.copy()
            self.shared_with.remove(user_id)
            self._record_change("shared_with", old_shared, self.shared_with)
            self.modified = datetime.now()
    
    def set_reminder(self, reminder_time):
        """Set a reminder for the task"""
        old_reminder = self.reminder
        self.reminder = reminder_time
        self._record_change("reminder", old_reminder, reminder_time)
        self.modified = datetime.now()
    
    def clear_reminder(self):
        """Clear the reminder for the task"""
        old_reminder = self.reminder
        self.reminder = None
        self._record_change("reminder", old_reminder, None)
        self.modified = datetime.now()
    
    def get_history(self, field=None, start_date=None, end_date=None):
        """Get task history with optional filtering"""
        filtered_history = self.history
        
        if field:
            filtered_history = [h for h in filtered_history if h["field"] == field]
        
        if start_date:
            filtered_history = [h for h in filtered_history if h["timestamp"] >= start_date]
        
        if end_date:
            filtered_history = [h for h in filtered_history if h["timestamp"] <= end_date]
        
        return filtered_history
    
    def __str__(self):
        """String representation of the task"""
        status = "✓" if self.completed else "☐"
        due_date_str = f", due: {self.due_date.strftime('%Y-%m-%d')}" if self.due_date else ""
        progress_str = f" [{self.progress}%]" if self.progress > 0 else ""
        tags_str = f" #{',#'.join(self.tags)}" if self.tags else ""
        return f"[{status}] [{self.priority.upper()}] {self.title}{due_date_str}{progress_str}{tags_str}"