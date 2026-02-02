#!/usr/bin/env python3
"""
RHCSA Mock Exam Simulator v2.0.0 - Main Entry Point

A realistic RHCSA exam simulator with auto-cleanup between tasks.
"""

import sys
import os
import logging
import argparse

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.helpers import require_root
from utils.logging import setup_logging
from core.menu import MenuSystem
from core.exam import run_exam_mode
from core.practice import run_practice_mode
from core.practice_enhanced import run_guided_practice
from core.learn import run_learn_mode
from core.command_recall import run_command_recall
from core.flashcard_mode import run_flashcard_mode
from core.results import get_results_manager
from core.scenario_mode import run_scenario_mode
from core.troubleshoot_mode import run_troubleshoot_mode
from config import settings


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='RHCSA Mock Exam Simulator v2.0.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Quick Start Examples:
  %(prog)s --quick              5 random tasks with auto-cleanup
  %(prog)s --quick lvm          5 LVM tasks with auto-cleanup
  %(prog)s --exam               Start full exam immediately
  %(prog)s --learn users        Jump to users learning mode
  %(prog)s --practice lvm       Practice LVM category
        """
    )

    parser.add_argument('--quick', nargs='?', const='all', metavar='CATEGORY',
                        help='Quick practice (5 tasks). Optionally specify category.')
    parser.add_argument('--exam', action='store_true',
                        help='Start mock exam immediately')
    parser.add_argument('--learn', metavar='CATEGORY',
                        help='Jump to learn mode for a category')
    parser.add_argument('--practice', metavar='CATEGORY',
                        help='Start practice mode for a category')
    parser.add_argument('--list-categories', action='store_true',
                        help='List available categories')
    parser.add_argument('--version', action='version',
                        version=f'%(prog)s {settings.VERSION}')

    return parser.parse_args()


def run_quick_practice_cli(category=None):
    """Run quick practice from CLI with optional category filter."""
    from tasks.registry import TaskRegistry
    from core.validator import get_validator
    from device import get_device_manager
    from utils import formatters as fmt
    from utils.helpers import confirm_action

    TaskRegistry.initialize()

    fmt.clear_screen()
    fmt.print_header("QUICK PRACTICE")

    if category and category != 'all':
        print(f"5 {fmt.format_category_name(category)} tasks with auto-cleanup.")
    else:
        print("5 random tasks across all categories with auto-cleanup.")
    print()

    device_manager = get_device_manager()
    device = device_manager.get_practice_device()
    if device:
        print(fmt.info(f"Practice device: {device}"))
        print(fmt.dim("Resources will be cleaned up automatically after each task."))
    print()

    # Get tasks
    if category and category != 'all':
        tasks = TaskRegistry.get_practice_tasks(category, 'exam', 5)
    else:
        tasks = TaskRegistry.get_exam_tasks(5)

    if not tasks:
        print(fmt.error("Could not generate tasks"))
        return

    validator = get_validator()
    completed = 0
    passed = 0

    for i, task in enumerate(tasks, 1):
        with device_manager.task_context(task.id, auto_cleanup=True):
            fmt.clear_screen()
            print(f"Quick Practice - Task {i}/{len(tasks)}")
            print("=" * 60)
            print()
            print(fmt.bold("Task:"))
            print(task.description)
            print()
            print(fmt.bold(f"Category: {fmt.format_category_name(task.category)}"))
            print(fmt.bold(f"Points: {task.points}"))
            print()

            if task.hints and confirm_action("Show hints?", default=False):
                print()
                for j, hint in enumerate(task.hints, 1):
                    print(f"  {j}. {hint}")
                print()

            input("Complete the task, then press Enter to validate...")

            result = validator.validate_task(task)
            completed += 1

            print()
            if result.passed:
                passed += 1
                print(fmt.success(f"✓ PASSED - {result.score}/{result.max_score} points"))
            else:
                print(fmt.error(f"✗ FAILED - {result.score}/{result.max_score} points"))
                for check in result.checks:
                    if not check.passed:
                        print(f"    - {check.message}")

            print()
            if i < len(tasks):
                print(fmt.dim("Cleaning up resources..."))
                if not confirm_action("Continue to next task?", default=True):
                    break

    # Summary
    print()
    fmt.print_header("QUICK PRACTICE COMPLETE")
    print(f"Tasks completed: {completed}/{len(tasks)}")
    print(f"Tasks passed: {passed}/{completed}")
    if completed > 0:
        print(f"Success rate: {passed/completed*100:.0f}%")
    print()

    device_manager.cleanup_all_resources(force=True)
    print(fmt.success("All resources cleaned up."))


def run_quick_practice():
    """Run quick practice mode - 5 random tasks with auto-cleanup."""
    from tasks.registry import TaskRegistry
    from core.validator import get_validator
    from device import get_device_manager
    from utils import formatters as fmt
    from utils.helpers import confirm_action

    TaskRegistry.initialize()

    fmt.clear_screen()
    fmt.print_header("QUICK PRACTICE")

    print("5 random tasks across all categories with auto-cleanup.")
    print()

    device_manager = get_device_manager()
    device = device_manager.get_practice_device()
    if device:
        print(fmt.info(f"Practice device: {device}"))
        print(fmt.dim("Resources will be cleaned up automatically after each task."))
    print()

    if not confirm_action("Ready to start?", default=True):
        return

    # Get 5 random tasks across categories
    tasks = TaskRegistry.get_exam_tasks(5)

    if not tasks:
        print(fmt.error("Could not generate tasks"))
        return

    validator = get_validator()
    completed = 0
    passed = 0

    for i, task in enumerate(tasks, 1):
        with device_manager.task_context(task.id, auto_cleanup=True):
            fmt.clear_screen()
            print(f"Quick Practice - Task {i}/5")
            print("=" * 60)
            print()
            print(fmt.bold("Task:"))
            print(task.description)
            print()
            print(fmt.bold(f"Category: {fmt.format_category_name(task.category)}"))
            print(fmt.bold(f"Points: {task.points}"))
            print()

            # Show hints on request
            if task.hints and confirm_action("Show hints?", default=False):
                print()
                for j, hint in enumerate(task.hints, 1):
                    print(f"  {j}. {hint}")
                print()

            input("Complete the task, then press Enter to validate...")

            # Validate
            result = validator.validate_task(task)
            completed += 1

            print()
            if result.passed:
                passed += 1
                print(fmt.success(f"✓ PASSED - {result.score}/{result.max_score} points"))
            else:
                print(fmt.error(f"✗ FAILED - {result.score}/{result.max_score} points"))
                for check in result.checks:
                    if not check.passed:
                        print(f"    - {check.message}")

            print()
            if i < 5:
                print(fmt.dim("Cleaning up resources..."))
                if not confirm_action("Continue to next task?", default=True):
                    break

    # Summary
    print()
    fmt.print_header("QUICK PRACTICE COMPLETE")
    print(f"Tasks completed: {completed}/5")
    print(f"Tasks passed: {passed}/{completed}")
    print(f"Success rate: {passed/completed*100:.0f}%" if completed > 0 else "N/A")
    print()

    # Final cleanup
    device_manager.cleanup_all_resources(force=True)
    print(fmt.success("All resources cleaned up."))


def main():
    """Main application entry point."""
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)

    # Parse command line arguments
    args = parse_args()

    # Handle --list-categories without root
    if args.list_categories:
        from tasks.registry import TaskRegistry
        TaskRegistry.initialize()
        print("Available categories:")
        for cat in sorted(TaskRegistry.get_all_categories()):
            count = TaskRegistry.get_task_count(cat)
            print(f"  {cat}: {count} tasks")
        return 0

    # Check root privileges
    try:
        require_root()
    except SystemExit:
        return 1

    # Handle CLI quick modes
    if args.quick:
        run_quick_practice_cli(args.quick)
        return 0

    if args.exam:
        run_exam_mode()
        return 0

    if args.learn:
        from tasks.registry import TaskRegistry
        TaskRegistry.initialize()
        if args.learn in TaskRegistry.get_all_categories():
            run_learn_mode(category=args.learn)
        else:
            print(f"Unknown category: {args.learn}")
            print("Use --list-categories to see available categories")
            return 1
        return 0

    if args.practice:
        from tasks.registry import TaskRegistry
        TaskRegistry.initialize()
        if args.practice in TaskRegistry.get_all_categories():
            # Import and run practice for specific category
            from core.practice import PracticeSession
            session = PracticeSession()
            session.category = args.practice
            session.difficulty = 'exam'
            session.start()
        else:
            print(f"Unknown category: {args.practice}")
            print("Use --list-categories to see available categories")
            return 1
        return 0

    # Initialize menu system
    menu = MenuSystem()

    # Main loop
    while True:
        try:
            choice = menu.display_main_menu()

            if choice == 'learn':
                run_learn_mode()
                input("\nPress Enter to return to menu...")

            elif choice == 'guided_practice':
                run_guided_practice()
                input("\nPress Enter to return to menu...")

            elif choice == 'command_recall':
                run_command_recall()
                input("\nPress Enter to return to menu...")

            elif choice == 'flashcard':
                run_flashcard_mode()

            elif choice == 'quick_practice':
                run_quick_practice()
                input("\nPress Enter to return to menu...")

            elif choice == 'exam':
                run_exam_mode()
                input("\nPress Enter to return to menu...")

            elif choice == 'practice':
                run_practice_mode()
                input("\nPress Enter to return to menu...")

            elif choice == 'scenario':
                run_scenario_mode()

            elif choice == 'troubleshoot':
                run_troubleshoot_mode()

            elif choice == 'dashboard':
                menu.show_dashboard()

            elif choice == 'export':
                menu.export_report()

            elif choice == 'setup':
                menu.show_setup()

            elif choice == 'help':
                menu.show_help()

            elif choice == 'exit':
                # Final cleanup before exit
                try:
                    from device import get_device_manager
                    dm = get_device_manager()
                    dm.cleanup_all_resources(force=True)
                except Exception:
                    pass

                print("\nThank you for using RHCSA Mock Exam Simulator!")
                print("Good luck with your certification!")
                return 0

        except KeyboardInterrupt:
            print("\n\nInterrupted by user.")
            confirm = input("Are you sure you want to exit? [y/N]: ").strip().lower()
            if confirm in ['y', 'yes']:
                return 0

        except Exception as e:
            logger.exception("Unexpected error in main loop")
            print(f"\nError: {e}")
            print("Please report this issue if it persists.")
            input("Press Enter to return to menu...")


if __name__ == '__main__':
    sys.exit(main())
