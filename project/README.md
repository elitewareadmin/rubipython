# Python Task Manager

A simple command-line task management application built in Python.

## Features

- Create and manage tasks with titles, descriptions, priorities, due dates, and categories
- Mark tasks as complete
- View task details and lists
- Search and filter tasks
- Persist data using JSON storage
- Color-coded CLI interface

## Getting Started

1. Ensure you have Python 3.6+ installed
2. Clone this repository
3. Run the application:

```bash
python main.py
```

## Command Examples

- Add a task:
  ```
  add "Complete project" --desc "Finish the Python project" --priority high --due 2025-05-15 --category Work
  ```

- List tasks:
  ```
  list
  list --all
  list --completed
  list --category Work
  list --priority high
  ```

- View task details:
  ```
  view <task_id>
  ```

- Update a task:
  ```
  update <task_id> --title "New title" --priority low
  ```

- Complete a task:
  ```
  complete <task_id>
  ```

- Search for tasks:
  ```
  search Python
  ```

- View categories:
  ```
  categories
  ```

- Get help:
  ```
  help
  ```

- Exit the application:
  ```
  exit
  ```

## Project Structure

```
task_manager/
├── main.py              # Application entry point
├── src/
│   ├── models/          # Data models
│   │   ├── __init__.py
│   │   └── task.py      # Task model class
│   ├── ui/              # User interface
│   │   ├── __init__.py
│   │   └── cli.py       # Command-line interface
│   ├── utils/           # Utility functions
│   │   ├── __init__.py
│   │   ├── colors.py    # Terminal colors
│   │   └── logger.py    # Logging configuration
│   ├── __init__.py
│   └── task_manager.py  # Core task management logic
├── data/                # Data storage directory
│   └── tasks.json       # Task data file
└── logs/                # Log files directory
```

## Requirements

- Python 3.6+
- No external dependencies required

## License

MIT