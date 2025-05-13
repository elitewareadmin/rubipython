#!/usr/bin/env python3
"""
Task Manager CLI Application
Main entry point for the application
"""
import sys
from src.task_manager import TaskManager
from src.ui.cli import CommandLineInterface
from src.utils.logger import setup_logger

def main():
    """Main function to start the application"""
    # Setup logger
    logger = setup_logger()
    logger.info("Starting Task Manager application")
    
    # Initialize the task manager
    task_manager = TaskManager()
    
    # Initialize CLI
    cli = CommandLineInterface(task_manager)
    
    try:
        # Start the CLI
        cli.start()
    except KeyboardInterrupt:
        print("\nExiting Task Manager. Goodbye!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()