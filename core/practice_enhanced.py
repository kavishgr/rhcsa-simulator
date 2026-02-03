"""
Enhanced Practice Mode with Guided Hints and Adaptive Feedback.
"""

import logging
from tasks.registry import TaskRegistry
from core.validator import get_validator
from core.learn import LearnContent
from core.ai_feedback import get_ai_agent
from core.command_analyzer import CommandHistoryAnalyzer
from device import get_device_manager
from utils import formatters as fmt
from utils.helpers import confirm_action
from config import settings


logger = logging.getLogger(__name__)


class GuidedPracticeSession:
    """
    Enhanced practice mode with progressive hints and adaptive feedback.
    """

    def __init__(self):
        """Initialize guided practice session."""
        self.category = None
        self.difficulty = "exam"
        self.task_count = settings.DEFAULT_PRACTICE_TASKS
        self.hints_used = []  # Track hints per task
        self.logger = logging.getLogger(__name__)
        self.ai_agent = get_ai_agent()
        self.command_analyzer = CommandHistoryAnalyzer()

    def start(self):
        """Start guided practice session."""
        # Initialize registry
        TaskRegistry.initialize()

        # Select category
        self.category = self._select_category()
        if not self.category:
            return

        # Select difficulty
        self.difficulty = self._select_difficulty()

        # Offer to view learning content first
        if confirm_action("Would you like to review the learning content for this topic first?", default=False):
            self._show_learning_content()

        # Get tasks
        tasks = TaskRegistry.get_practice_tasks(
            self.category,
            self.difficulty,
            self.task_count
        )

        if not tasks:
            print(fmt.error(f"No tasks available for {self.category}"))
            return

        # Get device manager for auto-cleanup
        device_manager = get_device_manager()

        # Check if this category needs disk cleanup
        disk_categories = {'lvm', 'filesystems', 'storage_advanced'}
        needs_cleanup = self.category in disk_categories

        if needs_cleanup:
            device = device_manager.get_practice_device()
            if device:
                print(fmt.info(f"Practice device: {device}"))
                print(fmt.dim("Resources will be cleaned up automatically after each task."))
                print()

        # Practice each task with guided hints
        total_hints_used = 0
        for i, task in enumerate(tasks, 1):
            if needs_cleanup:
                # Use auto-cleanup context for disk tasks
                with device_manager.task_context(task.id, auto_cleanup=True):
                    hints_for_task = self._guided_practice_task(task, i, len(tasks))
                    total_hints_used += hints_for_task
                    self.hints_used.append(hints_for_task)
                if i < len(tasks):
                    print(fmt.dim("Cleaning up resources..."))
            else:
                hints_for_task = self._guided_practice_task(task, i, len(tasks))
                total_hints_used += hints_for_task
                self.hints_used.append(hints_for_task)

        # Final cleanup
        if needs_cleanup:
            device_manager.cleanup_all_resources(force=True)

        # Show summary
        self._show_practice_summary(len(tasks), total_hints_used)

    def _show_learning_content(self):
        """Show brief learning content for the category."""
        content = LearnContent.get_topic(self.category)
        if not content:
            print(fmt.warning("No learning content available for this topic yet."))
            input("Press Enter to continue...")
            return

        fmt.clear_screen()
        fmt.print_header(f"Quick Review: {content['name']}")

        print(fmt.bold("📖 Key Concept:"))
        print(content['explanation'].strip())
        print()

        print(fmt.bold("💻 Most Important Commands:"))
        for cmd in content['commands'][:2]:  # Show first 2 commands
            print(f"\n  {fmt.success('▸')} {cmd['name']}")
            print(f"     {fmt.info(cmd['syntax'])}")
            print(f"     Example: {cmd['example']}")

        print()
        input("Press Enter to start practicing...")

    def _guided_practice_task(self, task, current, total):
        """
        Practice a single task with progressive hint system.

        Returns:
            int: Number of hints used for this task
        """
        hints_used = 0
        fmt.clear_screen()

        print(f"Guided Practice Task {current}/{total}")
        print("=" * 70)
        print()

        # Start command tracking for this task
        self.command_analyzer.start_session()

        # Display task
        print(fmt.bold("📋 TASK:"))
        print(task.description)
        print()
        print(fmt.bold(f"Points: {task.points}"))
        print(fmt.bold(f"Difficulty: {fmt.format_difficulty(task.difficulty)}"))
        print()

        # Show AI availability
        if self.ai_agent.is_available():
            print(fmt.success("🤖 AI-powered feedback enabled"))
        else:
            print(fmt.dim("💡 Set ANTHROPIC_API_KEY for AI-powered feedback"))
        print()

        # Progressive hint system
        print(fmt.dim("💡 Hints available: [1] Concept  [2] Command Structure  [3] Full Solution"))
        print(fmt.dim("Type 'hint' for next hint, 'done' when ready to validate"))
        print()

        # Wait for user to request hints or complete task
        hint_level = 0
        max_hints = 3

        while True:
            action = input("> ").strip().lower()

            if action == 'hint' and hint_level < max_hints:
                hint_level += 1
                hints_used += 1
                self._show_hint(task, hint_level)
                print()

            elif action == 'hint' and hint_level >= max_hints:
                print(fmt.warning("All hints have been shown!"))
                print()

            elif action == 'done':
                break

            elif action == 'help':
                print(fmt.info("Commands: 'hint' (get next hint), 'done' (validate), 'help' (this message)"))
                print()

            else:
                print(fmt.dim("Type 'hint' for help, or 'done' when ready to validate"))
                print()

        # Validate
        print()
        print(fmt.bold("🔍 Validating your work..."))
        print()

        validator = get_validator()
        result = validator.validate_task(task)

        # Get commands used during this task
        commands_used = self.command_analyzer.get_session_commands()

        # Display adaptive feedback with AI analysis
        self._show_adaptive_feedback(task, result, hints_used, commands_used)

        # Continue?
        if current < total:
            print()
            if not confirm_action("Continue to next task?", default=True):
                return hints_used

        return hints_used

    def _show_hint(self, task, level):
        """
        Show progressive hints based on level.

        Level 1: Concept reminder
        Level 2: Command structure (flags hidden)
        Level 3: Full command solution
        """
        print()
        print(fmt.warning(f"━━━ HINT {level}/3 ━━━"))

        if level == 1:
            # Hint 1: Concept reminder
            print(fmt.bold("💭 Concept Reminder:"))
            if task.hints and len(task.hints) > 0:
                print(f"   {task.hints[0]}")
            else:
                print("   Think about what commands are used for this type of task.")

            # Add concept from learning content if available
            content = LearnContent.get_topic(task.category)
            if content:
                relevant_cmd = self._find_relevant_command(task, content)
                if relevant_cmd:
                    print()
                    print(f"   Key command: {fmt.info(relevant_cmd['name'])}")

        elif level == 2:
            # Hint 2: Command structure (flags hidden)
            print(fmt.bold("🔧 Command Structure:"))
            if task.hints and len(task.hints) > 1:
                print(f"   {task.hints[1]}")

            content = LearnContent.get_topic(task.category)
            if content:
                relevant_cmd = self._find_relevant_command(task, content)
                if relevant_cmd:
                    # Show syntax with placeholders
                    print()
                    print(f"   Syntax: {fmt.info(relevant_cmd['syntax'])}")
                    print()
                    print("   Fill in the specific values for this task")

        elif level == 3:
            # Hint 3: Full solution
            print(fmt.bold("✨ Full Solution:"))
            if task.hints:
                # Show all hints
                for i, hint in enumerate(task.hints, 1):
                    print(f"   {i}. {hint}")

            content = LearnContent.get_topic(task.category)
            if content:
                relevant_cmd = self._find_relevant_command(task, content)
                if relevant_cmd:
                    print()
                    print(fmt.success("   Example command:"))
                    print(f"   $ {relevant_cmd['example']}")

        print("━━━━━━━━━━━")

    def _find_relevant_command(self, task, content):
        """Find the most relevant command from learning content for this task."""
        # Score-based matching - find command with most matching words
        task_desc = task.description.lower()

        best_cmd = None
        best_score = 0

        for cmd in content['commands']:
            cmd_name = cmd['name'].lower()
            # Count how many words from cmd_name appear in task description
            words = [w for w in cmd_name.split() if len(w) > 2]  # Skip short words
            score = sum(1 for word in words if word in task_desc)

            if score > best_score:
                best_score = score
                best_cmd = cmd

        # Return best match or first command if no match
        return best_cmd if best_cmd else (content['commands'][0] if content['commands'] else None)

    def _show_adaptive_feedback(self, task, result, hints_used, commands_used):
        """
        Show detailed, adaptive feedback based on results.
        Explains what was expected vs what was found.
        Includes AI-powered analysis if available.
        """
        print(fmt.bold("📊 VALIDATION RESULTS:"))
        print("=" * 70)

        # Show each check with detailed feedback
        for check in result.checks:
            if check.passed:
                symbol = fmt.success("✓")
                status = fmt.success("PASS")
            else:
                symbol = fmt.error("✗")
                status = fmt.error("FAIL")

            print(f"\n{symbol} {check.name.replace('_', ' ').title()}: {status}")
            print(f"   {check.message}")

            # Add detailed explanation for failures
            if not check.passed:
                self._explain_failure(check, task, commands_used)

        # Overall result
        print()
        print("=" * 70)

        if result.passed:
            print(fmt.success(f"✓ TASK PASSED!"))
            print(f"   Score: {result.score}/{result.max_score} points ({result.percentage:.0f}%)")

            # Feedback based on hints used
            if hints_used == 0:
                print(fmt.success("   🌟 Perfect! Solved without hints!"))
            elif hints_used == 1:
                print(fmt.info("   👍 Good job! Used 1 hint"))
            elif hints_used == 2:
                print(fmt.warning("   📚 Keep practicing! Used 2 hints"))
            else:
                print(fmt.warning("   📖 Review the concepts! Used all hints"))

            # AI: Show approach comparison if available
            if self.ai_agent.is_available() and commands_used:
                print()
                print(fmt.bold("🤖 AI FEEDBACK:"))
                try:
                    feedback = self.ai_agent.compare_approaches(
                        task.description,
                        commands_used,
                        task.hints[:3],  # Pass hints for context
                        result
                    )
                    print(fmt.info(feedback))
                except Exception as e:
                    logger.debug(f"AI feedback failed: {e}")
        else:
            print(fmt.error(f"✗ TASK FAILED"))
            print(f"   Score: {result.score}/{result.max_score} points ({result.percentage:.0f}%)")

            # AI: Show detailed analysis for failed tasks
            if self.ai_agent.is_available():
                print()
                print(fmt.bold("🤖 AI ANALYSIS:"))
                try:
                    feedback = self.ai_agent.analyze_attempt(
                        task.description,
                        task.hints,
                        result,
                        commands_used
                    )
                    print(fmt.info(feedback))
                except Exception as e:
                    logger.debug(f"AI analysis failed: {e}")
                    # Fallback to manual next steps
                    print()
                    print(fmt.warning("   🔧 Next Steps:"))
                    print("      1. Review the failed checks above")
                    print("      2. Check what commands you ran")
                    print("      3. Verify the configuration")
                    print("      4. Try again!")
            else:
                print()
                print(fmt.warning("   🔧 Next Steps:"))
                print("      1. Review the failed checks above")
                print("      2. Check what commands you ran")
                print("      3. Verify the configuration")
                print("      4. Try again!")

        # Show commands used (if any were tracked)
        if commands_used:
            print()
            print(fmt.dim("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"))
            print(fmt.dim(f"Commands executed: {len(commands_used)}"))
            if len(commands_used) <= 10:
                for cmd in commands_used:
                    print(fmt.dim(f"  {cmd['sequence']}. {cmd['command']}"))
            else:
                print(fmt.dim(f"  (Run 'history' to see all commands)"))

        print("=" * 70)

    def _explain_failure(self, check, task, commands_used):
        """Provide detailed explanation for why a check failed."""
        # Try AI explanation first
        if self.ai_agent.is_available():
            try:
                ai_explanation = self.ai_agent.explain_failure(
                    check.name,
                    check.message,
                    task.description,
                    commands_used
                )
                print(f"   💡 {fmt.warning(ai_explanation)}")
                return
            except Exception as e:
                logger.debug(f"AI explanation failed: {e}")

        # Fallback to hardcoded explanations
        explanations = {
            "user_exists": "The user account was not found. Did you run useradd?",
            "correct_uid": "The UID doesn't match. Check the -u flag value.",
            "correct_gid": "The GID doesn't match. Check the -g flag value.",
            "home_directory": "Home directory missing. Use -m flag with useradd.",
            "correct_shell": "Shell is incorrect. Use -s flag to specify shell.",
            "correct_groups": "User is not in all required groups. Use -G flag.",
            "sudo_access": "Sudo access not configured. Create file in /etc/sudoers.d/",
            "file_exists": "File or directory not found. Check the path.",
            "permissions": "Permissions don't match. Use chmod with correct octal value.",
            "correct_owner": "Owner is incorrect. Use chown user:group filename.",
            "acl_entry": "ACL not set correctly. Use setfacl -m u:user:perms file.",
            "service_active": "Service is not running. Use systemctl start.",
            "service_enabled": "Service not enabled at boot. Use systemctl enable.",
            "current_context": "SELinux context incorrect. Use semanage fcontext + restorecon.",
            "persistent_context": "Context not persistent. Did you use semanage?",
            "boolean_value": "Boolean value wrong. Use setsebool -P.",
            "lv_exists": "Logical volume not found. Use lvcreate.",
        }

        explanation = explanations.get(check.name)
        if explanation:
            print(f"   💡 {fmt.warning(explanation)}")

    def _select_category(self):
        """Select practice category."""
        fmt.clear_screen()
        fmt.print_header("GUIDED PRACTICE - Select Category")

        categories = TaskRegistry.get_all_categories()

        if not categories:
            print(fmt.error("No task categories available"))
            return None

        # Display categories
        for i, cat in enumerate(sorted(categories), 1):
            count = TaskRegistry.get_task_count(cat)

            # Check if learning content exists
            has_content = "📚" if LearnContent.get_topic(cat) else "  "

            fmt.print_menu_option(
                i,
                fmt.format_category_name(cat),
                f"{count} tasks available {has_content}"
            )

        fmt.print_menu_option('Q', "Back to Main Menu")

        # Get selection
        while True:
            choice = input("\nSelect category (number or Q): ").strip()

            if choice.lower() == 'q':
                return None

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(categories):
                    return sorted(categories)[idx]
                else:
                    print(fmt.error("Invalid selection"))
            except ValueError:
                print(fmt.error("Please enter a number or Q"))

    def _select_difficulty(self):
        """Select difficulty level."""
        print()
        print(fmt.bold("Select Difficulty:"))
        fmt.print_menu_option(1, "Easy", "Simpler tasks, more guidance")
        fmt.print_menu_option(2, "Exam", "Exam-level difficulty (recommended)")
        fmt.print_menu_option(3, "Hard", "Challenging tasks")

        while True:
            choice = input("\nSelect difficulty [2]: ").strip() or '2'

            if choice == '1':
                return 'easy'
            elif choice == '2':
                return 'exam'
            elif choice == '3':
                return 'hard'
            else:
                print(fmt.error("Invalid selection"))

    def _show_practice_summary(self, total_tasks, total_hints):
        """Show summary of practice session."""
        print()
        fmt.print_header("PRACTICE SESSION COMPLETE!")

        print(fmt.bold("📊 Summary:"))
        print(f"   Tasks completed: {total_tasks}")
        print(f"   Total hints used: {total_hints}")
        print(f"   Average hints per task: {total_hints / total_tasks:.1f}")
        print()

        # Performance feedback
        avg_hints = total_hints / total_tasks if total_tasks > 0 else 0
        if avg_hints == 0:
            print(fmt.success("   🌟 Excellent! You didn't need any hints!"))
        elif avg_hints < 1:
            print(fmt.success("   👍 Great job! Very few hints needed"))
        elif avg_hints < 2:
            print(fmt.info("   📚 Good progress! Keep practicing"))
        else:
            print(fmt.warning("   📖 Review the learning content to improve"))

        print()


def run_guided_practice():
    """Run guided practice mode (convenience function)."""
    session = GuidedPracticeSession()
    session.start()
