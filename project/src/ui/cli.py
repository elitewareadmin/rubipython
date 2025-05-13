import sys
import shlex
from datetime import datetime, timedelta
from src.utils.logger import get_logger
from src.utils.colors import Colors
from src.utils.virtual_assistant import VirtualAssistant
from src.utils.ai_assistant import AIAssistant
from src.utils.reports import ReportManager

class CommandLineInterface:
    def __init__(self, task_manager):
        self.task_manager = task_manager
        self.logger = get_logger()
        self.virtual_assistant = VirtualAssistant()
        self.ai_assistant = AIAssistant()
        self.report_manager = ReportManager()
        self.running = False
        self.commands = {
            "help": self.show_help,
            "add": self.add_task,
            "list": self.list_tasks,
            "view": self.view_task,
            "update": self.update_task,
            "complete": self.complete_task,
            "delete": self.delete_task,
            "search": self.search_tasks,
            "categories": self.list_categories,
            "add-subtask": self.add_subtask,
            "remove-subtask": self.remove_subtask,
            "complete-subtask": self.complete_subtask,
            "assistant": self.toggle_assistant,
            "advice": self.get_ai_advice,
            "analyze": self.analyze_tasks,
            "organize": self.get_organization_advice,
            "report": self.generate_report,
            "email-report": self.email_report,
            "exit": self.exit
        }
        self.assistant_enabled = True
    
    def start(self):
        """Start the CLI interface"""
        self.running = True
        greeting = self.virtual_assistant.get_greeting()
        print(f"\n{Colors.BLUE}{greeting}{Colors.RESET}")
        self.virtual_assistant.speak(greeting)
        
        while self.running:
            try:
                user_input = input(f"{Colors.GREEN}> {Colors.RESET}")
                if not user_input.strip():
                    continue
                
                parts = shlex.split(user_input)
                command = parts[0].lower()
                args = parts[1:]
                
                if command in self.commands:
                    result = self.commands[command](args)
                    if self.assistant_enabled and result:
                        self.virtual_assistant.speak(result)
                else:
                    msg = f"Unknown command: {command}\nType 'help' for a list of commands."
                    print(f"{Colors.RED}{msg}{Colors.RESET}")
                    if self.assistant_enabled:
                        self.virtual_assistant.speak(msg)
            except Exception as e:
                self.logger.error(f"Error processing command: {e}")
                print(f"{Colors.RED}Error: {e}{Colors.RESET}")
    
    def toggle_assistant(self, args=None):
        """Toggle virtual assistant"""
        self.assistant_enabled = not self.assistant_enabled
        status = "enabled" if self.assistant_enabled else "disabled"
        msg = f"Virtual assistant {status}"
        print(f"{Colors.GREEN}{msg}{Colors.RESET}")
        if self.assistant_enabled:
            self.virtual_assistant.speak(msg)
        return msg

    def show_help(self, args=None):
        """Show help information"""
        print(f"\n{Colors.BOLD}Available Commands:{Colors.RESET}")
        print(f"  {Colors.CYAN}help{Colors.RESET} - Show this help message")
        print(f"  {Colors.CYAN}add <title> [--desc <description>] [--priority <priority>] [--due <YYYY-MM-DD>] [--category <category>]{Colors.RESET}")
        print(f"    - Add a new task")
        print(f"  {Colors.CYAN}list [--all] [--completed] [--category <category>] [--priority <priority>]{Colors.RESET}")
        print(f"    - List tasks, default shows incomplete tasks")
        print(f"  {Colors.CYAN}view <task_id>{Colors.RESET}")
        print(f"    - View details of a specific task")
        print(f"  {Colors.CYAN}update <task_id> [--title <title>] [--desc <description>] [--priority <priority>] [--due <YYYY-MM-DD>] [--category <category>]{Colors.RESET}")
        print(f"    - Update a task")
        print(f"  {Colors.CYAN}complete <task_id>{Colors.RESET}")
        print(f"    - Mark a task as completed")
        print(f"  {Colors.CYAN}delete <task_id>{Colors.RESET}")
        print(f"    - Delete a task")
        print(f"  {Colors.CYAN}search <query>{Colors.RESET}")
        print(f"    - Search for tasks")
        print(f"  {Colors.CYAN}categories{Colors.RESET}")
        print(f"    - List all categories")
        print(f"  {Colors.CYAN}add-subtask <task_id> <title> [--desc <description>] [--priority <priority>]{Colors.RESET}")
        print(f"    - Add a subtask to a task")
        print(f"  {Colors.CYAN}remove-subtask <task_id> <subtask_id>{Colors.RESET}")
        print(f"    - Remove a subtask from a task")
        print(f"  {Colors.CYAN}complete-subtask <task_id> <subtask_id>{Colors.RESET}")
        print(f"    - Mark a subtask as completed")
        print(f"  {Colors.CYAN}assistant{Colors.RESET}")
        print(f"    - Toggle virtual assistant")
        print(f"  {Colors.CYAN}advice{Colors.RESET}")
        print(f"    - Get AI-powered advice about task management")
        print(f"  {Colors.CYAN}analyze{Colors.RESET}")
        print(f"    - Get AI analysis of current tasks")
        print(f"  {Colors.CYAN}organize{Colors.RESET}")
        print(f"    - Get AI suggestions for better task organization")
        print(f"  {Colors.CYAN}report <type>{Colors.RESET}")
        print(f"    - Generate a report (type: summary/detailed)")
        print(f"  {Colors.CYAN}email-report <email> <type>{Colors.RESET}")
        print(f"    - Email a report (type: summary/detailed)")
        print(f"  {Colors.CYAN}exit{Colors.RESET}")
        print(f"    - Exit the application\n")

    def _speak_task(self, task):
        """Generate speech output for a task"""
        status = "completed" if task.completed else "pending"
        due_str = f", due {task.due_date.strftime('%Y-%m-%d')}" if task.due_date else ""
        category_str = f" in category {task.category}" if task.category else ""
        return f"Task {task.title} is {status}{due_str}{category_str} with {task.priority} priority"

    def get_ai_advice(self, args=None):
        """Get AI-powered advice about task management"""
        tasks = self.task_manager.get_tasks()
        if not tasks:
            msg = "No tasks found to analyze."
            print(f"{Colors.YELLOW}{msg}{Colors.RESET}")
            return msg

        print(f"\n{Colors.BOLD}Getting AI advice...{Colors.RESET}")
        advice = self.ai_assistant.suggest_task_organization(tasks)
        print(f"\n{Colors.CYAN}{advice}{Colors.RESET}\n")
        return "Here's my advice for managing your tasks"

    def analyze_tasks(self, args=None):
        """Get AI analysis of current tasks"""
        tasks = self.task_manager.get_tasks()
        if not tasks:
            msg = "No tasks found to analyze."
            print(f"{Colors.YELLOW}{msg}{Colors.RESET}")
            return msg

        print(f"\n{Colors.BOLD}Analyzing tasks...{Colors.RESET}")
        analysis = self.ai_assistant.analyze_tasks(tasks)
        print(f"\n{Colors.CYAN}{analysis}{Colors.RESET}\n")
        return "I've analyzed your tasks"

    def get_organization_advice(self, args=None):
        """Get AI suggestions for better task organization"""
        tasks = self.task_manager.get_tasks()
        if not tasks:
            msg = "No tasks found to organize."
            print(f"{Colors.YELLOW}{msg}{Colors.RESET}")
            return msg

        print(f"\n{Colors.BOLD}Generating organization suggestions...{Colors.RESET}")
        suggestions = self.ai_assistant.suggest_task_organization(tasks)
        print(f"\n{Colors.CYAN}{suggestions}{Colors.RESET}\n")
        return "Here are my suggestions for organizing your tasks"

    def generate_report(self, args):
        """Generate a task report"""
        if not args:
            print(f"{Colors.RED}Error: Report type required (summary/detailed){Colors.RESET}")
            return

        report_type = args[0].lower()
        tasks = self.task_manager.get_tasks()

        if not tasks:
            msg = "No tasks found for report."
            print(f"{Colors.YELLOW}{msg}{Colors.RESET}")
            return msg

        if report_type == "summary":
            report = self.report_manager.generate_summary_report(tasks)
            print(f"\n{Colors.CYAN}Summary Report:{Colors.RESET}")
        elif report_type == "detailed":
            report = self.report_manager.generate_detailed_report(tasks)
            print(f"\n{Colors.CYAN}Detailed Report:{Colors.RESET}")
        else:
            print(f"{Colors.RED}Error: Invalid report type. Use 'summary' or 'detailed'{Colors.RESET}")
            return

        print(f"\n{report}\n")
        return "Report generated successfully"

    def email_report(self, args):
        """Email a task report"""
        if len(args) < 2:
            print(f"{Colors.RED}Error: Email address and report type required{Colors.RESET}")
            return

        email = args[0]
        report_type = args[1].lower()
        tasks = self.task_manager.get_tasks()

        if not tasks:
            msg = "No tasks found for report."
            print(f"{Colors.YELLOW}{msg}{Colors.RESET}")
            return msg

        # Generate report
        if report_type == "summary":
            report = self.report_manager.generate_summary_report(tasks)
            subject = "Task Manager - Summary Report"
        elif report_type == "detailed":
            report = self.report_manager.generate_detailed_report(tasks)
            subject = "Task Manager - Detailed Report"
        else:
            print(f"{Colors.RED}Error: Invalid report type. Use 'summary' or 'detailed'{Colors.RESET}")
            return

        # Send email
        print(f"\n{Colors.BOLD}Sending report to {email}...{Colors.RESET}")
        success = self.report_manager.send_report_email(email, subject, report)

        if success:
            msg = f"Report sent successfully to {email}"
            print(f"{Colors.GREEN}{msg}{Colors.RESET}")
            return msg
        else:
            msg = "Failed to send report"
            print(f"{Colors.RED}{msg}{Colors.RESET}")
            return msg

    def add_task(self, args):
        """Add a task"""
        if not args:
            print(f"{Colors.RED}Error: Title is required{Colors.RESET}")
            return
        
        title = args[0]
        description = ""
        priority = "medium"
        due_date = None
        category = None
        
        # Parse command arguments
        i = 1
        while i < len(args):
            if args[i] == "--desc" and i + 1 < len(args):
                description = args[i + 1]
                i += 2
            elif args[i] == "--priority" and i + 1 < len(args):
                if args[i + 1].lower() in ["low", "medium", "high", "critical"]:
                    priority = args[i + 1].lower()
                    i += 2
                else:
                    print(f"{Colors.RED}Invalid priority. Using 'medium'.{Colors.RESET}")
                    i += 2
            elif args[i] == "--due" and i + 1 < len(args):
                try:
                    due_date = datetime.strptime(args[i + 1], "%Y-%m-%d")
                    i += 2
                except ValueError:
                    print(f"{Colors.RED}Invalid date format. Use YYYY-MM-DD.{Colors.RESET}")
                    i += 2
            elif args[i] == "--category" and i + 1 < len(args):
                category = args[i + 1]
                i += 2
            else:
                i += 1
        
        task = self.task_manager.add_task(
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            category=category
        )
        
        msg = f"Task added successfully!\nID: {task.id}\nTitle: {task.title}"
        print(f"{Colors.GREEN}{msg}{Colors.RESET}")
        return self._speak_task(task)

    def list_tasks(self, args):
        """List tasks with optional filtering"""
        show_completed = False
        show_all = False
        category = None
        priority = None
        
        # Parse command arguments
        i = 0
        while i < len(args):
            if args[i] == "--all":
                show_all = True
                i += 1
            elif args[i] == "--completed":
                show_completed = True
                i += 1
            elif args[i] == "--category" and i + 1 < len(args):
                category = args[i + 1]
                i += 2
            elif args[i] == "--priority" and i + 1 < len(args):
                if args[i + 1].lower() in ["low", "medium", "high", "critical"]:
                    priority = args[i + 1].lower()
                    i += 2
                else:
                    print(f"{Colors.RED}Invalid priority. Ignoring filter.{Colors.RESET}")
                    i += 2
            else:
                i += 1
        
        if show_all:
            tasks = self.task_manager.get_tasks(filter_category=category, filter_priority=priority)
            status = "all"
        elif show_completed:
            tasks = self.task_manager.get_tasks(filter_completed=True, filter_category=category, filter_priority=priority)
            status = "completed"
        else:
            tasks = self.task_manager.get_tasks(filter_completed=False, filter_category=category, filter_priority=priority)
            status = "incomplete"
        
        if not tasks:
            msg = f"No {status} tasks found."
            print(f"{Colors.YELLOW}{msg}{Colors.RESET}")
            return msg
        
        print(f"\n{Colors.BOLD}Tasks ({len(tasks)} {status}):{Colors.RESET}")
        
        for task in tasks:
            self._print_task_line(task)
        print()
        
        return f"Found {len(tasks)} {status} tasks"

    def view_task(self, args):
        """View details of a specific task"""
        if not args:
            print(f"{Colors.RED}Error: Task ID is required{Colors.RESET}")
            return
        
        task_id = args[0]
        task = self.task_manager.get_task_by_id(task_id)
        
        if not task:
            msg = "Error: Task not found"
            print(f"{Colors.RED}{msg}{Colors.RESET}")
            return msg
        
        print(f"\n{Colors.BOLD}Task Details:{Colors.RESET}")
        print(f"  {Colors.CYAN}ID:{Colors.RESET} {task.id}")
        print(f"  {Colors.CYAN}Title:{Colors.RESET} {task.title}")
        print(f"  {Colors.CYAN}Description:{Colors.RESET} {task.description or '(No description)'}")
        
        # Show priority with color based on level
        if task.priority == "low":
            priority_color = Colors.BLUE
        elif task.priority == "medium":
            priority_color = Colors.GREEN
        elif task.priority == "high":
            priority_color = Colors.YELLOW
        else:  # critical
            priority_color = Colors.RED
        
        print(f"  {Colors.CYAN}Priority:{Colors.RESET} {priority_color}{task.priority.upper()}{Colors.RESET}")
        
        # Show category if available
        if task.category:
            print(f"  {Colors.CYAN}Category:{Colors.RESET} {task.category}")
        
        # Show due date if available
        if task.due_date:
            # Format due date
            date_str = task.due_date.strftime("%Y-%m-%d")
            days_left = (task.due_date.date() - datetime.now().date()).days
            
            if days_left < 0:
                due_str = f"{Colors.RED}OVERDUE by {abs(days_left)} days{Colors.RESET}"
            elif days_left == 0:
                due_str = f"{Colors.YELLOW}DUE TODAY{Colors.RESET}"
            else:
                due_str = f"in {days_left} days"
            
            print(f"  {Colors.CYAN}Due Date:{Colors.RESET} {date_str} ({due_str})")
        
        # Show completion status
        status = f"{Colors.GREEN}Yes - {task.completed_date.strftime('%Y-%m-%d')}{Colors.RESET}" if task.completed else "No"
        print(f"  {Colors.CYAN}Completed:{Colors.RESET} {status}")
        
        # Show creation and modification dates
        print(f"  {Colors.CYAN}Created:{Colors.RESET} {task.created.strftime('%Y-%m-%d %H:%M')}")
        print(f"  {Colors.CYAN}Last Modified:{Colors.RESET} {task.modified.strftime('%Y-%m-%d %H:%M')}")
        
        # Show subtasks if any
        if task.subtasks:
            print(f"\n  {Colors.CYAN}Subtasks:{Colors.RESET}")
            for subtask in task.subtasks:
                self._print_task_line(subtask, indent="    ")
        
        print()
        return self._speak_task(task)

    def update_task(self, args):
        """Update a task"""
        if not args:
            print(f"{Colors.RED}Error: Task ID is required{Colors.RESET}")
            return
        
        task_id = args[0]
        task = self.task_manager.get_task_by_id(task_id)
        
        if not task:
            msg = "Error: Task not found"
            print(f"{Colors.RED}{msg}{Colors.RESET}")
            return msg
        
        # Parse command arguments
        updates = {}
        i = 1
        while i < len(args):
            if args[i] == "--title" and i + 1 < len(args):
                updates["title"] = args[i + 1]
                i += 2
            elif args[i] == "--desc" and i + 1 < len(args):
                updates["description"] = args[i + 1]
                i += 2
            elif args[i] == "--priority" and i + 1 < len(args):
                if args[i + 1].lower() in ["low", "medium", "high", "critical"]:
                    updates["priority"] = args[i + 1].lower()
                    i += 2
                else:
                    print(f"{Colors.RED}Invalid priority. Skipping update.{Colors.RESET}")
                    i += 2
            elif args[i] == "--due" and i + 1 < len(args):
                try:
                    updates["due_date"] = datetime.strptime(args[i + 1], "%Y-%m-%d")
                    i += 2
                except ValueError:
                    print(f"{Colors.RED}Invalid date format. Use YYYY-MM-DD.{Colors.RESET}")
                    i += 2
            elif args[i] == "--category" and i + 1 < len(args):
                updates["category"] = args[i + 1]
                i += 2
            else:
                i += 1
        
        if not updates:
            print(f"{Colors.RED}Error: No updates specified{Colors.RESET}")
            return
        
        task = self.task_manager.update_task(task_id, **updates)
        msg = f"Task updated successfully!\nID: {task.id}\nTitle: {task.title}"
        print(f"{Colors.GREEN}{msg}{Colors.RESET}")
        return self._speak_task(task)