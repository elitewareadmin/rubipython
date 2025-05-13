"""
Meeting management module for handling meetings and summaries
"""
from datetime import datetime
import json
from src.utils.logger import get_logger
from src.utils.ai_assistant import AIAssistant

class MeetingManager:
    """Meeting Manager for handling meetings and generating summaries"""
    def __init__(self):
        self.logger = get_logger()
        self.meetings = {}
        self.summaries = {}
        self.ai_assistant = AIAssistant()
        
    def create_meeting(self, title, date, attendees, agenda=None):
        """Create a new meeting"""
        try:
            meeting_id = f"meet_{len(self.meetings) + 1}"
            meeting = {
                "id": meeting_id,
                "title": title,
                "date": date,
                "attendees": attendees,
                "agenda": agenda or [],
                "notes": [],
                "action_items": [],
                "decisions": [],
                "status": "scheduled",
                "created_at": datetime.now()
            }
            
            self.meetings[meeting_id] = meeting
            return meeting_id
        except Exception as e:
            self.logger.error(f"Error creating meeting: {e}")
            return None
    
    def add_meeting_note(self, meeting_id, note, author):
        """Add a note to the meeting"""
        try:
            meeting = self.meetings.get(meeting_id)
            if not meeting:
                return False
            
            note_entry = {
                "content": note,
                "author": author,
                "timestamp": datetime.now()
            }
            
            meeting["notes"].append(note_entry)
            return True
        except Exception as e:
            self.logger.error(f"Error adding meeting note: {e}")
            return False
    
    def add_action_item(self, meeting_id, description, assignee, due_date=None):
        """Add an action item from the meeting"""
        try:
            meeting = self.meetings.get(meeting_id)
            if not meeting:
                return False
            
            action_item = {
                "description": description,
                "assignee": assignee,
                "due_date": due_date,
                "status": "pending",
                "created_at": datetime.now()
            }
            
            meeting["action_items"].append(action_item)
            return True
        except Exception as e:
            self.logger.error(f"Error adding action item: {e}")
            return False
    
    def add_decision(self, meeting_id, decision, context=None):
        """Record a decision made during the meeting"""
        try:
            meeting = self.meetings.get(meeting_id)
            if not meeting:
                return False
            
            decision_entry = {
                "decision": decision,
                "context": context,
                "timestamp": datetime.now()
            }
            
            meeting["decisions"].append(decision_entry)
            return True
        except Exception as e:
            self.logger.error(f"Error adding decision: {e}")
            return False
    
    def generate_summary(self, meeting_id):
        """Generate a comprehensive meeting summary"""
        try:
            meeting = self.meetings.get(meeting_id)
            if not meeting:
                return None
            
            # Organize meeting information
            summary = {
                "title": meeting["title"],
                "date": meeting["date"].strftime("%Y-%m-%d %H:%M"),
                "attendees": meeting["attendees"],
                "key_points": self._extract_key_points(meeting["notes"]),
                "decisions": meeting["decisions"],
                "action_items": self._format_action_items(meeting["action_items"]),
                "next_steps": self._generate_next_steps(meeting),
                "generated_at": datetime.now()
            }
            
            self.summaries[meeting_id] = summary
            return summary
        except Exception as e:
            self.logger.error(f"Error generating summary: {e}")
            return None
    
    def _extract_key_points(self, notes):
        """Extract key points from meeting notes"""
        try:
            key_points = []
            current_topic = None
            
            for note in notes:
                # Use AI to identify important points
                importance = self.ai_assistant.analyze_importance(note["content"])
                if importance > 0.7:  # Threshold for importance
                    key_points.append({
                        "point": note["content"],
                        "author": note["author"],
                        "topic": current_topic
                    })
            
            return key_points
        except Exception as e:
            self.logger.error(f"Error extracting key points: {e}")
            return []
    
    def _format_action_items(self, action_items):
        """Format action items for the summary"""
        formatted_items = []
        for item in action_items:
            due_date_str = item["due_date"].strftime("%Y-%m-%d") if item["due_date"] else "No due date"
            formatted_items.append({
                "task": item["description"],
                "assignee": item["assignee"],
                "due_date": due_date_str,
                "status": item["status"]
            })
        return formatted_items
    
    def _generate_next_steps(self, meeting):
        """Generate next steps based on meeting content"""
        next_steps = []
        
        # Add incomplete action items
        for item in meeting["action_items"]:
            if item["status"] == "pending":
                next_steps.append(f"Follow up with {item['assignee']} on: {item['description']}")
        
        # Add follow-up meeting if needed
        if self._needs_followup(meeting):
            next_steps.append("Schedule follow-up meeting to discuss remaining items")
        
        return next_steps
    
    def _needs_followup(self, meeting):
        """Determine if a follow-up meeting is needed"""
        # Check for pending action items
        pending_items = len([item for item in meeting["action_items"] 
                           if item["status"] == "pending"])
        
        # Check for unresolved decisions
        unresolved_decisions = self._count_unresolved_decisions(meeting["notes"])
        
        return pending_items > 3 or unresolved_decisions > 0
    
    def _count_unresolved_decisions(self, notes):
        """Count unresolved decision points in notes"""
        unresolved = 0
        for note in notes:
            if "decision needed" in note["content"].lower() or \
               "to be decided" in note["content"].lower():
                unresolved += 1
        return unresolved
    
    def export_summary(self, meeting_id, format="markdown"):
        """Export meeting summary in various formats"""
        try:
            summary = self.summaries.get(meeting_id)
            if not summary:
                summary = self.generate_summary(meeting_id)
            
            if format == "markdown":
                return self._format_markdown_summary(summary)
            elif format == "json":
                return json.dumps(summary, indent=2)
            else:
                return None
        except Exception as e:
            self.logger.error(f"Error exporting summary: {e}")
            return None
    
    def _format_markdown_summary(self, summary):
        """Format summary in markdown"""
        md = []
        md.append(f"# Meeting Summary: {summary['title']}")
        md.append(f"\nDate: {summary['date']}")
        md.append(f"\nAttendees: {', '.join(summary['attendees'])}")
        
        md.append("\n## Key Points")
        for point in summary['key_points']:
            md.append(f"- {point['point']}")
        
        md.append("\n## Decisions")
        for decision in summary['decisions']:
            md.append(f"- {decision['decision']}")
            if decision['context']:
                md.append(f"  - Context: {decision['context']}")
        
        md.append("\n## Action Items")
        for item in summary['action_items']:
            md.append(f"- {item['task']}")
            md.append(f"  - Assignee: {item['assignee']}")
            md.append(f"  - Due: {item['due_date']}")
            md.append(f"  - Status: {item['status']}")
        
        md.append("\n## Next Steps")
        for step in summary['next_steps']:
            md.append(f"- {step}")
        
        return "\n".join(md)