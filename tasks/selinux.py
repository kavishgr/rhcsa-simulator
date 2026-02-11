"""
SELinux management tasks for RHCSA exam.
"""

import random
import logging
from tasks.base import BaseTask
from tasks.registry import TaskRegistry
from core.validator import ValidationCheck, ValidationResult
from validators.file_validators import (
    validate_file_exists, get_selinux_type,
    validate_selinux_context, get_selinux_boolean,
    validate_selinux_boolean, get_selinux_mode
)
from validators.safe_executor import execute_safe


logger = logging.getLogger(__name__)


@TaskRegistry.register("selinux")
class SetSELinuxContextTask(BaseTask):
    """Set SELinux context on a directory."""

    def __init__(self):
        super().__init__(
            id="selinux_context_001",
            category="selinux",
            difficulty="exam",
            points=10
        )
        self.directory = None
        self.context_type = None

    def generate(self, **params):
        """Generate SELinux context task."""
        dir_suffix = random.randint(1, 99)
        self.directory = params.get('directory', f'/srv/web{dir_suffix}')

        context_options = [
            ('httpd_sys_content_t', 'web server content'),
            ('public_content_t', 'public read-only content'),
            ('samba_share_t', 'Samba share'),
        ]

        self.context_type, context_desc = random.choice(context_options)

        self.description = (
            f"Configure SELinux context for directory '{self.directory}':\n"
            f"  - Set SELinux type to: {self.context_type}\n"
            f"  - Apply context recursively to all files\n"
            f"  - Make the change persistent across relabels\n"
            f"\n"
            f"Purpose: This directory will be used for {context_desc}"
        )

        self.hints = [
            "Use 'semanage fcontext' to make changes persistent",
            "Format: semanage fcontext -a -t <type> '<path>(/.*)?'",
            "Use 'restorecon -Rv' to apply the context",
            "Verify with 'ls -Zd <directory>'"
        ]

        return self

    def validate(self):
        """Validate SELinux context configuration."""
        checks = []
        total_points = 0

        # Check 1: Directory exists (2 points)
        if validate_file_exists(self.directory, file_type='directory'):
            checks.append(ValidationCheck(
                name="directory_exists",
                passed=True,
                points=2,
                message=f"Directory '{self.directory}' exists"
            ))
            total_points += 2
        else:
            checks.append(ValidationCheck(
                name="directory_exists",
                passed=False,
                points=0,
                max_points=2,
                message=f"Directory '{self.directory}' not found"
            ))
            return ValidationResult(self.id, False, total_points, self.points, checks)

        # Check 2: Current context is correct (4 points)
        if validate_selinux_context(self.directory, self.context_type):
            checks.append(ValidationCheck(
                name="current_context",
                passed=True,
                points=4,
                message=f"SELinux context is correct: {self.context_type}"
            ))
            total_points += 4
        else:
            actual_type = get_selinux_type(self.directory)
            checks.append(ValidationCheck(
                name="current_context",
                passed=False,
                points=0,
                max_points=4,
                message=f"Context mismatch: expected {self.context_type}, got {actual_type}"
            ))

        # Check 3: Persistent context configured (4 points)
        result = execute_safe(['semanage', 'fcontext', '-l'])
        if result.success and self.directory in result.stdout and self.context_type in result.stdout:
            checks.append(ValidationCheck(
                name="persistent_context",
                passed=True,
                points=4,
                message=f"Persistent context configured with semanage"
            ))
            total_points += 4
        else:
            checks.append(ValidationCheck(
                name="persistent_context",
                passed=False,
                points=0,
                max_points=4,
                message=f"Persistent context not configured (check 'semanage fcontext -l')"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("selinux")
class SetSELinuxBooleanTask(BaseTask):
    """Configure SELinux boolean."""

    def __init__(self):
        super().__init__(
            id="selinux_boolean_001",
            category="selinux",
            difficulty="exam",
            points=6
        )
        self.boolean_name = None
        self.boolean_value = None

    def generate(self, **params):
        """Generate SELinux boolean task."""
        boolean_options = [
            ('httpd_can_network_connect', 'on', 'allow Apache to make network connections'),
            ('httpd_enable_homedirs', 'on', 'allow Apache to access user home directories'),
            ('ftpd_anon_write', 'on', 'allow anonymous FTP uploads'),
            ('samba_enable_home_dirs', 'on', 'allow Samba to share home directories'),
        ]

        self.boolean_name, self.boolean_value, purpose = random.choice(boolean_options)

        self.description = (
            f"Configure SELinux boolean '{self.boolean_name}':\n"
            f"  - Set value to: {self.boolean_value}\n"
            f"  - Make the change persistent across reboots\n"
            f"\n"
            f"Purpose: {purpose}"
        )

        self.hints = [
            "Use 'setsebool' command with -P flag for persistence",
            "Format: setsebool -P <boolean> <value>",
            "Verify with 'getsebool <boolean>'",
            "List all booleans with 'getsebool -a'"
        ]

        return self

    def validate(self):
        """Validate SELinux boolean configuration."""
        checks = []
        total_points = 0

        # Check 1: Current boolean value (3 points)
        actual_value = get_selinux_boolean(self.boolean_name)
        if actual_value == self.boolean_value:
            checks.append(ValidationCheck(
                name="boolean_value",
                passed=True,
                points=3,
                message=f"Boolean '{self.boolean_name}' is set to {self.boolean_value}"
            ))
            total_points += 3
        else:
            checks.append(ValidationCheck(
                name="boolean_value",
                passed=False,
                points=0,
                max_points=3,
                message=f"Boolean value incorrect: expected {self.boolean_value}, got {actual_value}"
            ))

        # Check 2: Persistent configuration (3 points)
        result = execute_safe(['semanage', 'boolean', '-l'])
        if result.success:
            found = False
            for line in result.stdout.split('\n'):
                if line.startswith(self.boolean_name) and self.boolean_value in line:
                    found = True
                    break

            if found:
                checks.append(ValidationCheck(
                    name="persistent_boolean",
                    passed=True,
                    points=3,
                    message=f"Boolean persistently configured"
                ))
                total_points += 3
            else:
                checks.append(ValidationCheck(
                    name="persistent_boolean",
                    passed=False,
                    points=0,
                    max_points=3,
                    message=f"Boolean not persistently configured (use -P flag)"
                ))
        else:
            checks.append(ValidationCheck(
                name="persistent_boolean",
                passed=False,
                points=0,
                max_points=3,
                message=f"Could not check persistent configuration"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("selinux")
class SetSELinuxModeTask(BaseTask):
    """Set SELinux mode (enforcing/permissive)."""

    def __init__(self):
        super().__init__(
            id="selinux_mode_001",
            category="selinux",
            difficulty="easy",
            points=5
        )
        self.mode = None

    def generate(self, **params):
        """Generate SELinux mode task."""
        self.mode = params.get('mode', random.choice(['Enforcing', 'Permissive']))

        self.description = (
            f"Set SELinux to {self.mode} mode:\n"
            f"  - Change the current mode to {self.mode}\n"
            f"  - Ensure mode persists after reboot (modify /etc/selinux/config)"
        )

        self.hints = [
            f"Use 'setenforce {0 if self.mode == 'Permissive' else 1}' for immediate change",
            "Edit /etc/selinux/config and set SELINUX= line",
            "Verify current mode with 'getenforce'",
            "Verify persistent config with 'grep ^SELINUX= /etc/selinux/config'"
        ]

        return self

    def validate(self):
        """Validate SELinux mode."""
        checks = []
        total_points = 0

        # Check 1: Current mode (2 points)
        current_mode = get_selinux_mode()
        if current_mode == self.mode:
            checks.append(ValidationCheck(
                name="current_mode",
                passed=True,
                points=2,
                message=f"SELinux is in {self.mode} mode"
            ))
            total_points += 2
        else:
            checks.append(ValidationCheck(
                name="current_mode",
                passed=False,
                points=0,
                max_points=2,
                message=f"SELinux mode incorrect: expected {self.mode}, got {current_mode}"
            ))

        # Check 2: Persistent configuration (3 points)
        result = execute_safe(['grep', '^SELINUX=', '/etc/selinux/config'])
        if result.success:
            expected_line = f"selinux={self.mode.lower()}"
            if expected_line in result.stdout.lower():
                checks.append(ValidationCheck(
                    name="persistent_mode",
                    passed=True,
                    points=3,
                    message=f"SELinux mode persistently configured in /etc/selinux/config"
                ))
                total_points += 3
            else:
                checks.append(ValidationCheck(
                    name="persistent_mode",
                    passed=False,
                    points=0,
                    max_points=3,
                    message=f"/etc/selinux/config not updated correctly"
                ))
        else:
            checks.append(ValidationCheck(
                name="persistent_mode",
                passed=False,
                points=0,
                max_points=3,
                message=f"Could not verify /etc/selinux/config"
            ))

        passed = total_points >= (self.points * 0.6)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("selinux")
class SetSELinuxPortTask(BaseTask):
    """Configure SELinux port context."""

    def __init__(self):
        super().__init__(
            id="selinux_port_001",
            category="selinux",
            difficulty="exam",
            points=10
        )
        self.port = None
        self.protocol = None
        self.context_type = None

    def generate(self, **params):
        port_options = [
            (8080, 'tcp', 'http_port_t', 'HTTP'),
            (8443, 'tcp', 'http_port_t', 'HTTPS'),
            (2222, 'tcp', 'ssh_port_t', 'SSH'),
        ]

        choice = random.choice(port_options)
        self.port = params.get('port', choice[0])
        self.protocol = params.get('protocol', choice[1])
        self.context_type = params.get('context', choice[2])
        port_desc = choice[3] if len(choice) > 3 else 'custom'

        self.description = (
            f"Configure SELinux port context:\n"
            f"  - Port: {self.port}/{self.protocol}\n"
            f"  - SELinux type: {self.context_type}\n"
            f"  - Purpose: Allow {port_desc} service on non-standard port\n"
            f"  - Make the change persistent"
        )

        self.hints = [
            f"Add port context: semanage port -a -t {self.context_type} -p {self.protocol} {self.port}",
            f"List port contexts: semanage port -l | grep {self.context_type}",
            f"Verify: semanage port -l | grep {self.port}",
            "Use -m to modify existing, -a to add new",
            "Common port types: http_port_t, ssh_port_t, ftp_port_t"
        ]

        return self

    def validate(self):
        checks = []
        total_points = 0

        # Check: Port context is configured
        result = execute_safe(['semanage', 'port', '-l'])
        if result.success:
            # Look for port in output
            found = False
            for line in result.stdout.split('\n'):
                if str(self.port) in line and self.context_type in line:
                    found = True
                    break

            if found:
                checks.append(ValidationCheck(
                    name="port_context_set",
                    passed=True,
                    points=10,
                    message=f"Port {self.port} has context {self.context_type}"
                ))
                total_points += 10
            else:
                checks.append(ValidationCheck(
                    name="port_context_set",
                    passed=False,
                    points=0,
                    max_points=10,
                    message=f"Port {self.port} context not configured"
                ))
        else:
            checks.append(ValidationCheck(
                name="port_context_set",
                passed=False,
                points=0,
                max_points=10,
                message=f"Could not check SELinux port contexts"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("selinux")
class TroubleshootSELinuxTask(BaseTask):
    """Diagnose and fix SELinux issues."""

    def __init__(self):
        super().__init__(
            id="selinux_troubleshoot_001",
            category="selinux",
            difficulty="exam",
            points=12
        )
        self.service = None
        self.directory = None
        self.expected_context = None

    def generate(self, **params):
        scenarios = [
            ('httpd', '/var/www/custom', 'httpd_sys_content_t'),
            ('samba', '/srv/shares', 'samba_share_t'),
        ]

        scenario = random.choice(scenarios)
        self.service = params.get('service', scenario[0])
        self.directory = params.get('directory', scenario[1])
        self.expected_context = params.get('context', scenario[2])

        self.description = (
            f"Troubleshoot SELinux access denial:\n"
            f"  - Service: {self.service}\n"
            f"  - Directory: {self.directory}\n"
            f"  - The service cannot access files in this directory\n"
            f"  - Fix the SELinux context\n"
            f"  - Make the fix persistent across relabels"
        )

        self.hints = [
            "Check for denials: ausearch -m avc -ts recent",
            "Or: cat /var/log/audit/audit.log | grep denied",
            f"Check current context: ls -Zd {self.directory}",
            f"Set permanent context: semanage fcontext -a -t {self.expected_context} '{self.directory}(/.*)?'",
            f"Apply context: restorecon -Rv {self.directory}",
            "Use audit2why to analyze denials"
        ]

        return self

    def validate(self):
        checks = []
        total_points = 0

        # Check 1: Directory exists (3 points)
        if validate_file_exists(self.directory, file_type='directory'):
            checks.append(ValidationCheck(
                name="directory_exists",
                passed=True,
                points=3,
                message=f"Directory exists"
            ))
            total_points += 3
        else:
            checks.append(ValidationCheck(
                name="directory_exists",
                passed=False,
                points=0,
                max_points=3,
                message=f"Directory not found"
            ))
            return ValidationResult(self.id, False, total_points, self.points, checks)

        # Check 2: Context is correct (5 points)
        actual_type = get_selinux_type(self.directory)
        if actual_type == self.expected_context:
            checks.append(ValidationCheck(
                name="context_correct",
                passed=True,
                points=5,
                message=f"SELinux context is correct"
            ))
            total_points += 5
        else:
            checks.append(ValidationCheck(
                name="context_correct",
                passed=False,
                points=0,
                max_points=5,
                message=f"Context is {actual_type}, expected {self.expected_context}"
            ))

        # Check 3: Persistent configuration (4 points)
        result = execute_safe(['semanage', 'fcontext', '-l'])
        if result.success and self.directory in result.stdout and self.expected_context in result.stdout:
            checks.append(ValidationCheck(
                name="context_persistent",
                passed=True,
                points=4,
                message=f"Context configured permanently"
            ))
            total_points += 4
        else:
            checks.append(ValidationCheck(
                name="context_persistent",
                passed=False,
                points=0,
                max_points=4,
                message=f"Context not configured permanently"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)
