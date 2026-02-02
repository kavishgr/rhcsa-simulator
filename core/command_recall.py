"""
Command Recall Training Mode - Practice typing commands before executing.
"""

import logging
import re
from difflib import SequenceMatcher
from tasks.registry import TaskRegistry
from utils import formatters as fmt
from utils.helpers import confirm_action
from config import settings


logger = logging.getLogger(__name__)


class CommandRecallSession:
    """
    Command recall training mode where users type commands before execution.
    Validates command syntax and structure to build muscle memory.
    """

    def __init__(self):
        """Initialize command recall session."""
        self.category = None
        self.difficulty = "exam"
        self.task_count = 5
        self.correct_commands = 0
        self.total_commands = 0
        self.logger = logging.getLogger(__name__)

    def start(self):
        """Start command recall training session."""
        # Initialize registry
        TaskRegistry.initialize()

        # Select category
        self.category = self._select_category()
        if not self.category:
            return

        # Select difficulty
        self.difficulty = self._select_difficulty()

        # Get tasks
        tasks = TaskRegistry.get_practice_tasks(
            self.category,
            self.difficulty,
            self.task_count
        )

        if not tasks:
            print(fmt.error(f"No tasks available for {self.category}"))
            return

        # Practice command recall for each task
        for i, task in enumerate(tasks, 1):
            self._practice_command_recall(task, i, len(tasks))

        # Show summary
        self._show_recall_summary()

    def _practice_command_recall(self, task, current, total):
        """
        Practice recalling commands for a single task.

        Args:
            task: The task to practice
            current: Current task number
            total: Total number of tasks
        """
        fmt.clear_screen()

        print(f"Command Recall Training - Task {current}/{total}")
        print("=" * 70)
        print()

        # Display task
        print(fmt.bold("📋 TASK:"))
        print(task.description)
        print()
        print(fmt.bold(f"Category: {fmt.format_category_name(task.category)}"))
        print(fmt.bold(f"Difficulty: {fmt.format_difficulty(task.difficulty)}"))
        print()

        # Get expected commands from hints
        expected_commands = self._extract_commands_from_task(task)

        if not expected_commands:
            print(fmt.warning("No command examples available for this task."))
            print()
            if current < total:
                input("Press Enter to continue to next task...")
            return

        print(fmt.dim("💡 Type the command(s) you would use to complete this task"))
        print(fmt.dim("   Type 'hint' to see a hint, or 'skip' to skip this task"))
        print(fmt.dim("   Type 'done' when you've entered all commands"))
        print()

        # Track commands entered
        user_commands = []
        hints_shown = 0

        while True:
            cmd_num = len(user_commands) + 1
            user_input = input(f"Command {cmd_num}> ").strip()

            if not user_input:
                continue

            if user_input.lower() == 'done':
                if not user_commands:
                    print(fmt.warning("You haven't entered any commands yet!"))
                    continue
                break

            elif user_input.lower() == 'skip':
                print(fmt.warning("Skipping task..."))
                print()
                if current < total:
                    input("Press Enter to continue to next task...")
                return

            elif user_input.lower() == 'hint':
                hints_shown += 1
                self._show_command_hint(task, hints_shown, expected_commands)
                continue

            elif user_input.lower() == 'help':
                print(fmt.info("Commands: type your command, 'hint' (get help), 'done' (finish), 'skip' (skip task)"))
                print()
                continue

            else:
                # Validate command
                user_commands.append(user_input)
                print(fmt.dim(f"  → Recorded: {user_input}"))
                print()

        # Evaluate commands
        print()
        print(fmt.bold("🔍 Evaluating your commands..."))
        print()

        self._evaluate_commands(user_commands, expected_commands, task)

        # Update stats
        self.total_commands += len(expected_commands)

        # Continue?
        if current < total:
            print()
            if not confirm_action("Continue to next task?", default=True):
                return

    def _extract_commands_from_task(self, task):
        """
        Extract expected commands from task hints.

        Returns:
            list: List of expected command patterns
        """
        commands = []

        if not task.hints:
            return commands

        # Common command patterns for different categories
        command_patterns = {
            'users_groups': [r'useradd', r'usermod', r'groupadd', r'gpasswd', r'passwd', r'userdel', r'groupdel', r'chage'],
            'permissions': [r'chmod', r'chown', r'chgrp', r'setfacl', r'getfacl', r'umask'],
            'services': [r'systemctl\s*(start|stop|enable|disable|restart|status|is-active|is-enabled)?', r'journalctl'],
            'selinux': [r'semanage', r'restorecon', r'setsebool', r'getsebool', r'chcon', r'getenforce', r'setenforce'],
            'lvm': [r'pvcreate', r'vgcreate', r'lvcreate', r'pvs', r'vgs', r'lvs', r'lvextend', r'vgextend', r'pvremove', r'vgremove', r'lvremove'],
            'filesystems': [r'mkfs\.?\w*', r'mount', r'umount', r'blkid', r'lsblk', r'mkswap', r'swapon', r'swapoff', r'xfs_growfs', r'resize2fs', r'findmnt', r'df'],
            'networking': [r'nmcli', r'ip\s+(addr|link|route)', r'hostnamectl', r'ss', r'ping', r'firewall-cmd'],
            'boot': [r'systemctl\s+(set-default|get-default|isolate)', r'grub2?-mkconfig', r'dracut'],
            'scheduling': [r'crontab', r'at\b', r'systemctl.*timer'],
            'containers': [r'podman', r'docker', r'buildah', r'skopeo'],
            'essential_tools': [r'tar', r'gzip', r'bzip2', r'xz', r'find', r'grep', r'sed', r'awk', r'vim?', r'ssh', r'scp', r'rsync'],
            'processes': [r'ps', r'top', r'htop', r'kill', r'pkill', r'nice', r'renice', r'nohup', r'bg', r'fg', r'jobs'],
        }

        category_patterns = command_patterns.get(task.category, [])

        # Extract commands from hints
        for hint in task.hints:
            # Skip hints that are just explanatory text (too long or no command indicators)
            if len(hint) > 100 and ':' not in hint:
                continue

            # First, try to extract command after a colon (common format: "Description: command args")
            if ':' in hint:
                parts = hint.split(':', 1)
                if len(parts) == 2:
                    cmd_part = parts[1].strip()
                    # Check if it looks like a command
                    for pattern in category_patterns:
                        if re.match(pattern, cmd_part.split()[0] if cmd_part.split() else '', re.IGNORECASE):
                            commands.append(cmd_part.rstrip('.,;:'))
                            break

            # Try backtick extraction
            backtick_match = re.search(r'`([^`]+)`', hint)
            if backtick_match:
                cmd = backtick_match.group(1)
                if cmd not in commands:
                    commands.append(cmd)
                continue

            # Look for command-like patterns in hints
            for pattern in category_patterns:
                if re.search(pattern, hint, re.IGNORECASE):
                    # Extract command starting from the pattern match
                    words = hint.split()
                    for i, word in enumerate(words):
                        # Clean the word of common prefixes like numbers/bullets
                        clean_word = re.sub(r'^[\d.)\-\*]+\s*', '', word)
                        if re.match(pattern, clean_word, re.IGNORECASE):
                            # Get command and following arguments (up to 6 words or until punctuation)
                            cmd_words = [clean_word]
                            for j in range(i+1, min(i+6, len(words))):
                                next_word = words[j].rstrip('.,;:')
                                # Stop at certain keywords
                                if next_word.lower() in ['or', 'and', 'to', 'the', 'for', 'with']:
                                    break
                                cmd_words.append(next_word)
                            cmd = ' '.join(cmd_words).strip('.,;:')
                            if cmd and cmd not in commands:
                                commands.append(cmd)
                            break

        # Deduplicate while preserving order
        seen = set()
        unique_commands = []
        for cmd in commands:
            if cmd not in seen:
                seen.add(cmd)
                unique_commands.append(cmd)

        return unique_commands[:5]  # Return up to 5 commands

    def _evaluate_commands(self, user_commands, expected_commands, task):
        """
        Evaluate user's commands against expected commands.

        Args:
            user_commands: List of commands entered by user
            expected_commands: List of expected command patterns
            task: The task being evaluated
        """
        print("=" * 70)
        print(fmt.bold("📊 COMMAND EVALUATION:"))
        print("=" * 70)
        print()

        if not expected_commands:
            print(fmt.warning("No reference commands available for comparison."))
            return

        # Track matches
        matched = set()

        # Check each user command
        for i, user_cmd in enumerate(user_commands, 1):
            print(fmt.bold(f"Command {i}: {user_cmd}"))

            best_match = None
            best_score = 0

            # Find best matching expected command
            for j, expected_cmd in enumerate(expected_commands):
                if j in matched:
                    continue

                score = self._calculate_command_similarity(user_cmd, expected_cmd)
                if score > best_score:
                    best_score = score
                    best_match = j

            # Evaluate match
            if best_score > 0.7:  # Strong match
                matched.add(best_match)
                self.correct_commands += 1
                print(fmt.success(f"  ✓ Correct! ({int(best_score * 100)}% match)"))
                if best_score < 1.0:
                    print(fmt.dim(f"  Expected: {expected_commands[best_match]}"))
            elif best_score > 0.4:  # Partial match
                matched.add(best_match)
                print(fmt.warning(f"  ~ Close! ({int(best_score * 100)}% match)"))
                print(fmt.dim(f"  Expected: {expected_commands[best_match]}"))
                self._explain_command_difference(user_cmd, expected_commands[best_match])
            else:  # No match
                print(fmt.error(f"  ✗ Not quite right"))
                self._suggest_correct_command(user_cmd, expected_commands, task)

            print()

        # Check for missing commands
        if len(matched) < len(expected_commands):
            print(fmt.warning("Missing commands:"))
            for j, expected_cmd in enumerate(expected_commands):
                if j not in matched:
                    print(f"  • {expected_cmd}")
            print()

        # Overall feedback
        accuracy = (self.correct_commands / max(len(expected_commands), len(user_commands))) if expected_commands else 0

        if accuracy >= 0.9:
            print(fmt.success("🌟 Excellent command recall!"))
        elif accuracy >= 0.7:
            print(fmt.success("👍 Good job! Keep practicing!"))
        elif accuracy >= 0.5:
            print(fmt.warning("📚 Getting there! Review the commands and try again."))
        else:
            print(fmt.warning("📖 Keep studying! Focus on command syntax and structure."))

        print("=" * 70)

    def _calculate_command_similarity(self, user_cmd, expected_cmd):
        """
        Calculate similarity between user command and expected command.

        Returns:
            float: Similarity score (0.0 to 1.0)
        """
        # Normalize commands
        user_norm = user_cmd.lower().strip()
        expected_norm = expected_cmd.lower().strip()

        # Exact match
        if user_norm == expected_norm:
            return 1.0

        # Get base commands
        user_parts = user_norm.split()
        expected_parts = expected_norm.split()

        if not user_parts or not expected_parts:
            return 0.0

        user_base = user_parts[0]
        expected_base = expected_parts[0]

        # Handle compound commands (e.g., mkfs.xfs vs mkfs)
        user_base_root = user_base.split('.')[0]
        expected_base_root = expected_base.split('.')[0]

        # Check for base command match
        base_match = False
        if user_base == expected_base:
            base_match = True
            base_score = 0.6  # 60% for exact base match
        elif user_base_root == expected_base_root:
            base_match = True
            base_score = 0.55  # 55% for root match (e.g., mkfs.xfs ~ mkfs.ext4)
        elif user_base in expected_base or expected_base in user_base:
            base_match = True
            base_score = 0.5  # 50% for partial match

        if not base_match:
            # Check if commands are related (same category)
            related_commands = {
                'mkfs': ['mkfs.xfs', 'mkfs.ext4', 'mkfs.ext3'],
                'mkswap': ['swapon', 'swapoff'],
                'swapon': ['mkswap', 'swapoff'],
                'mount': ['umount', 'findmnt'],
                'systemctl': ['service', 'journalctl'],
                'useradd': ['usermod', 'userdel'],
                'groupadd': ['groupmod', 'groupdel'],
                'pvcreate': ['vgcreate', 'lvcreate'],
                'lvextend': ['lvresize', 'vgextend'],
            }

            related = related_commands.get(user_base, [])
            if expected_base in related or expected_base_root in related:
                base_score = 0.4  # 40% for related command
            else:
                # Completely different command - use sequence matching
                return SequenceMatcher(None, user_norm, expected_norm).ratio() * 0.3

        # Compare arguments (paths, flags, values)
        user_args = set(user_parts[1:])
        expected_args = set(expected_parts[1:])

        if not expected_args and not user_args:
            arg_score = 0.4  # Both have no args
        elif not expected_args:
            arg_score = 0.3  # User has args but expected doesn't
        else:
            # Calculate argument overlap
            common_args = user_args & expected_args

            # Also check for partial path matches (e.g., /dev/sdd matches /dev/sdc)
            partial_matches = 0
            for u_arg in user_args:
                for e_arg in expected_args:
                    if u_arg not in common_args and e_arg not in common_args:
                        # Check for partial match (same prefix)
                        if u_arg.startswith('/dev/') and e_arg.startswith('/dev/'):
                            partial_matches += 0.5
                        elif u_arg.startswith('/mnt/') and e_arg.startswith('/mnt/'):
                            partial_matches += 0.5
                        elif u_arg.startswith('-') and e_arg.startswith('-'):
                            # Same type of flag
                            if u_arg[1:2] == e_arg[1:2]:  # Same first letter
                                partial_matches += 0.3

            total_matches = len(common_args) + partial_matches
            arg_score = min(1.0, total_matches / len(expected_args)) * 0.4

        # Combined score
        return base_score + arg_score

    def _explain_command_difference(self, user_cmd, expected_cmd):
        """Explain the difference between user and expected command."""
        user_parts = user_cmd.split()
        expected_parts = expected_cmd.split()

        # Check for missing flags/arguments
        expected_set = set(expected_parts[1:])
        user_set = set(user_parts[1:])

        missing = expected_set - user_set
        extra = user_set - expected_set

        if missing:
            print(fmt.dim(f"  Missing: {' '.join(missing)}"))
        if extra:
            print(fmt.dim(f"  Extra: {' '.join(extra)}"))

    def _suggest_correct_command(self, user_cmd, expected_commands, task):
        """Suggest the correct command based on task category."""
        print(fmt.dim(f"  💡 Hint: This is a {task.category} task"))

        if expected_commands:
            print(fmt.dim(f"  Try a command like: {expected_commands[0]}"))

    def _show_command_hint(self, task, hint_level, expected_commands):
        """Show progressive hints about the command."""
        print()
        print(fmt.warning(f"━━━ HINT {hint_level} ━━━"))

        if hint_level == 1:
            # Hint 1: Command category
            print(fmt.bold("💭 Command Category:"))
            category_hints = {
                'users_groups': "User and group management commands (useradd, usermod, groupadd)",
                'permissions': "Permission and ACL commands (chmod, chown, setfacl)",
                'services': "Systemd service commands (systemctl)",
                'selinux': "SELinux commands (semanage, restorecon, setsebool)",
                'lvm': "LVM commands (pvcreate, vgcreate, lvcreate)",
                'filesystems': "Filesystem commands (mkfs, mount)",
                'networking': "Network commands (nmcli, ip, hostnamectl)",
            }
            hint = category_hints.get(task.category, "Check the task requirements carefully")
            print(f"   {hint}")

        elif hint_level == 2:
            # Hint 2: Base command
            print(fmt.bold("🔧 Base Command:"))
            if expected_commands:
                base_cmd = expected_commands[0].split()[0]
                print(f"   Start with: {fmt.info(base_cmd)}")

        elif hint_level >= 3:
            # Hint 3: Full command structure
            print(fmt.bold("✨ Full Command:"))
            if expected_commands:
                print(f"   {fmt.info(expected_commands[0])}")
            if task.hints:
                print()
                print(fmt.dim("Additional hints:"))
                for hint in task.hints[:2]:
                    print(f"   • {hint}")

        print("━━━━━━━━━━━")
        print()

    def _select_category(self):
        """Select practice category."""
        fmt.clear_screen()
        fmt.print_header("COMMAND RECALL TRAINING - Select Category")

        categories = TaskRegistry.get_all_categories()

        if not categories:
            print(fmt.error("No task categories available"))
            return None

        # Display categories
        for i, cat in enumerate(sorted(categories), 1):
            count = TaskRegistry.get_task_count(cat)
            fmt.print_menu_option(
                i,
                fmt.format_category_name(cat),
                f"{count} tasks available"
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
        fmt.print_menu_option(1, "Easy", "Simpler commands")
        fmt.print_menu_option(2, "Exam", "Exam-level commands (recommended)")
        fmt.print_menu_option(3, "Hard", "Complex commands")

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

    def _show_recall_summary(self):
        """Show summary of command recall session."""
        print()
        fmt.print_header("COMMAND RECALL SESSION COMPLETE!")

        print(fmt.bold("📊 Summary:"))
        print(f"   Commands attempted: {self.total_commands}")
        print(f"   Commands correct: {self.correct_commands}")

        accuracy = (self.correct_commands / self.total_commands * 100) if self.total_commands > 0 else 0
        print(f"   Accuracy: {accuracy:.0f}%")
        print()

        # Performance feedback
        if accuracy >= 90:
            print(fmt.success("   🌟 Outstanding! You have excellent command recall!"))
        elif accuracy >= 75:
            print(fmt.success("   👍 Great job! Your command recall is strong!"))
        elif accuracy >= 60:
            print(fmt.info("   📚 Good progress! Keep practicing to improve recall."))
        else:
            print(fmt.warning("   📖 Keep studying! Practice typing commands regularly."))

        print()
        print(fmt.dim("💡 Tip: Regular practice builds muscle memory for exam commands!"))
        print()


def run_command_recall():
    """Run command recall training (convenience function)."""
    session = CommandRecallSession()
    session.start()
