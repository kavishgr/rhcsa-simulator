"""
Systemd service management tasks for RHCSA exam.
"""

import random
import logging
from tasks.base import BaseTask
from tasks.registry import TaskRegistry
from core.validator import ValidationCheck, ValidationResult
from validators.command_validators import (
    validate_service_exists, validate_service_state,
    validate_service_enabled, get_service_status
)


logger = logging.getLogger(__name__)


@TaskRegistry.register("services")
class EnableStartServiceTask(BaseTask):
    """Enable and start a systemd service."""

    def __init__(self):
        super().__init__(
            id="service_enable_001",
            category="services",
            difficulty="easy",
            points=5
        )
        self.service_name = None

    def generate(self, **params):
        """Generate service enable/start task."""
        # Common services that might be installed
        services = ['httpd', 'nginx', 'sshd', 'chronyd', 'firewalld']
        self.service_name = params.get('service', random.choice(services))

        self.description = (
            f"Configure the '{self.service_name}' service:\n"
            f"  - Start the service\n"
            f"  - Enable the service to start at boot"
        )

        self.hints = [
            "Use 'systemctl start <service>' to start",
            "Use 'systemctl enable <service>' to enable at boot",
            "Verify with 'systemctl status <service>'",
            "Check enabled status with 'systemctl is-enabled <service>'"
        ]

        return self

    def validate(self):
        """Validate service configuration."""
        checks = []
        total_points = 0

        # Check 1: Service is active (3 points)
        if validate_service_state(self.service_name, 'active'):
            checks.append(ValidationCheck(
                name="service_active",
                passed=True,
                points=3,
                message=f"Service '{self.service_name}' is running"
            ))
            total_points += 3
        else:
            checks.append(ValidationCheck(
                name="service_active",
                passed=False,
                points=0,
                max_points=3,
                message=f"Service '{self.service_name}' is not running"
            ))

        # Check 2: Service is enabled (2 points)
        if validate_service_enabled(self.service_name, True):
            checks.append(ValidationCheck(
                name="service_enabled",
                passed=True,
                points=2,
                message=f"Service '{self.service_name}' is enabled at boot"
            ))
            total_points += 2
        else:
            checks.append(ValidationCheck(
                name="service_enabled",
                passed=False,
                points=0,
                max_points=2,
                message=f"Service '{self.service_name}' is not enabled at boot"
            ))

        passed = total_points >= (self.points * 0.6)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("services")
class DisableStopServiceTask(BaseTask):
    """Disable and stop a systemd service."""

    def __init__(self):
        super().__init__(
            id="service_disable_001",
            category="services",
            difficulty="easy",
            points=5
        )
        self.service_name = None

    def generate(self, **params):
        """Generate service disable/stop task."""
        services = ['postfix', 'bluetooth', 'cups', 'avahi-daemon']
        self.service_name = params.get('service', random.choice(services))

        self.description = (
            f"Configure the '{self.service_name}' service:\n"
            f"  - Stop the service\n"
            f"  - Disable the service from starting at boot"
        )

        self.hints = [
            "Use 'systemctl stop <service>' to stop",
            "Use 'systemctl disable <service>' to prevent boot startup",
            "Verify with 'systemctl status <service>'"
        ]

        return self

    def validate(self):
        """Validate service is stopped and disabled."""
        checks = []
        total_points = 0

        # Check 1: Service is not active (3 points)
        if validate_service_state(self.service_name, 'inactive'):
            checks.append(ValidationCheck(
                name="service_inactive",
                passed=True,
                points=3,
                message=f"Service '{self.service_name}' is stopped"
            ))
            total_points += 3
        else:
            checks.append(ValidationCheck(
                name="service_inactive",
                passed=False,
                points=0,
                max_points=3,
                message=f"Service '{self.service_name}' is still running"
            ))

        # Check 2: Service is disabled (2 points)
        if validate_service_enabled(self.service_name, False):
            checks.append(ValidationCheck(
                name="service_disabled",
                passed=True,
                points=2,
                message=f"Service '{self.service_name}' is disabled"
            ))
            total_points += 2
        else:
            checks.append(ValidationCheck(
                name="service_disabled",
                passed=False,
                points=0,
                max_points=2,
                message=f"Service '{self.service_name}' is still enabled"
            ))

        passed = total_points >= (self.points * 0.6)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("services")
class RestartServiceTask(BaseTask):
    """Restart a service and ensure it stays running."""

    def __init__(self):
        super().__init__(
            id="service_restart_001",
            category="services",
            difficulty="exam",
            points=6
        )
        self.service_name = None

    def generate(self, **params):
        """Generate service restart task."""
        services = ['sshd', 'httpd', 'nginx', 'chronyd']
        self.service_name = params.get('service', random.choice(services))

        self.description = (
            f"Ensure the '{self.service_name}' service is:\n"
            f"  - Currently running\n"
            f"  - Enabled to start at boot\n"
            f"  - Restart the service to apply any configuration changes"
        )

        self.hints = [
            "Use 'systemctl restart <service>'",
            "Or use 'systemctl reload <service>' if configuration reload is sufficient",
            "Enable with 'systemctl enable <service>'",
            "Verify with 'systemctl status <service>'"
        ]

        return self

    def validate(self):
        """Validate service is running and enabled."""
        checks = []
        total_points = 0

        status = get_service_status(self.service_name)

        # Check 1: Service exists (1 point)
        if status['exists']:
            checks.append(ValidationCheck(
                name="service_exists",
                passed=True,
                points=1,
                message=f"Service '{self.service_name}' exists"
            ))
            total_points += 1
        else:
            checks.append(ValidationCheck(
                name="service_exists",
                passed=False,
                points=0,
                max_points=1,
                message=f"Service '{self.service_name}' not found"
            ))
            return ValidationResult(self.id, False, total_points, self.points, checks)

        # Check 2: Service is active (3 points)
        if status['active']:
            checks.append(ValidationCheck(
                name="service_active",
                passed=True,
                points=3,
                message=f"Service is running"
            ))
            total_points += 3
        else:
            checks.append(ValidationCheck(
                name="service_active",
                passed=False,
                points=0,
                max_points=3,
                message=f"Service is not running (state: {status['state']})"
            ))

        # Check 3: Service is enabled (2 points)
        if status['enabled']:
            checks.append(ValidationCheck(
                name="service_enabled",
                passed=True,
                points=2,
                message=f"Service is enabled at boot"
            ))
            total_points += 2
        else:
            checks.append(ValidationCheck(
                name="service_enabled",
                passed=False,
                points=0,
                max_points=2,
                message=f"Service is not enabled at boot"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("services")
class MaskServiceTask(BaseTask):
    """Mask a service to prevent it from starting."""

    def __init__(self):
        super().__init__(
            id="service_mask_001",
            category="services",
            difficulty="medium",
            points=8
        )
        self.service_name = None

    def generate(self, **params):
        services = ['cups', 'bluetooth', 'postfix', 'avahi-daemon']
        self.service_name = params.get('service', random.choice(services))

        self.description = (
            f"Mask the '{self.service_name}' service:\n"
            f"  - Stop the service if running\n"
            f"  - Mask the service to prevent any start\n"
            f"  - Verify the service is masked"
        )

        self.hints = [
            f"Stop service: systemctl stop {self.service_name}",
            f"Mask service: systemctl mask {self.service_name}",
            f"Verify: systemctl status {self.service_name}",
            "Masked services cannot be started even manually",
            f"To unmask later: systemctl unmask {self.service_name}"
        ]

        return self

    def validate(self):
        checks = []
        total_points = 0
        from validators.safe_executor import execute_safe

        # Check: Service is masked
        result = execute_safe(['systemctl', 'is-enabled', self.service_name])
        if result.success and 'masked' in result.stdout:
            checks.append(ValidationCheck(
                name="service_masked",
                passed=True,
                points=8,
                message=f"Service '{self.service_name}' is masked"
            ))
            total_points += 8
        else:
            checks.append(ValidationCheck(
                name="service_masked",
                passed=False,
                points=0,
                max_points=8,
                message=f"Service '{self.service_name}' is not masked"
            ))

        passed = total_points >= (self.points * 0.8)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("services")
class CreateCustomServiceTask(BaseTask):
    """Create a custom systemd service unit."""

    def __init__(self):
        super().__init__(
            id="service_custom_001",
            category="services",
            difficulty="exam",
            points=15
        )
        self.service_name = None
        self.script_path = None
        self.description_text = None

    def generate(self, **params):
        suffix = random.randint(1, 99)
        self.service_name = params.get('service_name', f'myservice{suffix}')
        self.script_path = params.get('script', f'/usr/local/bin/myservice{suffix}.sh')
        self.description_text = params.get('description', 'Custom Service')

        self.description = (
            f"Create a custom systemd service:\n"
            f"  - Service name: {self.service_name}.service\n"
            f"  - Unit file: /etc/systemd/system/{self.service_name}.service\n"
            f"  - Runs script: {self.script_path}\n"
            f"  - Type: simple\n"
            f"  - Description: {self.description_text}\n"
            f"  - Enable and start the service"
        )

        self.hints = [
            f"Create script: echo '#!/bin/bash\\nwhile true; do sleep 60; done' > {self.script_path}",
            f"Make executable: chmod +x {self.script_path}",
            f"Create unit file: /etc/systemd/system/{self.service_name}.service",
            "[Unit]\\nDescription=<description>\\n[Service]\\nType=simple\\nExecStart=<script>\\n[Install]\\nWantedBy=multi-user.target",
            "Reload: systemctl daemon-reload",
            f"Enable and start: systemctl enable --now {self.service_name}"
        ]

        return self

    def validate(self):
        checks = []
        total_points = 0
        import os
        from validators.safe_executor import execute_safe

        unit_file = f'/etc/systemd/system/{self.service_name}.service'

        # Check 1: Unit file exists (5 points)
        if os.path.exists(unit_file):
            checks.append(ValidationCheck(
                name="unit_file_exists",
                passed=True,
                points=5,
                message=f"Unit file exists"
            ))
            total_points += 5
        else:
            checks.append(ValidationCheck(
                name="unit_file_exists",
                passed=False,
                points=0,
                max_points=5,
                message=f"Unit file not found"
            ))
            return ValidationResult(self.id, False, total_points, self.points, checks)

        # Check 2: Service is enabled (5 points)
        result = execute_safe(['systemctl', 'is-enabled', self.service_name])
        if result.success and 'enabled' in result.stdout:
            checks.append(ValidationCheck(
                name="service_enabled",
                passed=True,
                points=5,
                message=f"Service is enabled"
            ))
            total_points += 5
        else:
            checks.append(ValidationCheck(
                name="service_enabled",
                passed=False,
                points=0,
                max_points=5,
                message=f"Service is not enabled"
            ))

        # Check 3: Service is active (5 points)
        result = execute_safe(['systemctl', 'is-active', self.service_name])
        if result.success and result.stdout.strip() == 'active':
            checks.append(ValidationCheck(
                name="service_active",
                passed=True,
                points=5,
                message=f"Service is running"
            ))
            total_points += 5
        else:
            checks.append(ValidationCheck(
                name="service_active",
                passed=False,
                points=0,
                max_points=5,
                message=f"Service is not running"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("services")
class ViewServiceLogsTask(BaseTask):
    """View and analyze service logs using journalctl."""

    def __init__(self):
        super().__init__(
            id="service_logs_001",
            category="services",
            difficulty="medium",
            points=8
        )
        self.service_name = None
        self.output_file = None

    def generate(self, **params):
        services = ['sshd', 'httpd', 'chronyd', 'firewalld']
        self.service_name = params.get('service', random.choice(services))
        self.output_file = params.get('output', f'/tmp/{self.service_name}_logs.txt')

        self.description = (
            f"Extract service logs:\n"
            f"  - Service: {self.service_name}\n"
            f"  - Use journalctl to view logs\n"
            f"  - Save last 50 lines to: {self.output_file}\n"
            f"  - Include timestamps"
        )

        self.hints = [
            f"View service logs: journalctl -u {self.service_name}",
            f"Last 50 lines: journalctl -u {self.service_name} -n 50",
            f"Save to file: journalctl -u {self.service_name} -n 50 > {self.output_file}",
            "Add timestamps: journalctl -u <service> --since 'today'",
            "Follow logs: journalctl -u <service> -f"
        ]

        return self

    def validate(self):
        checks = []
        total_points = 0
        from validators.file_validators import validate_file_exists

        # Check: Output file exists and has content
        if validate_file_exists(self.output_file):
            checks.append(ValidationCheck(
                name="output_file_exists",
                passed=True,
                points=4,
                message=f"Output file exists"
            ))
            total_points += 4

            try:
                with open(self.output_file, 'r') as f:
                    content = f.read()
                    if content.strip():
                        checks.append(ValidationCheck(
                            name="has_content",
                            passed=True,
                            points=4,
                            message=f"File contains log entries"
                        ))
                        total_points += 4
                    else:
                        checks.append(ValidationCheck(
                            name="has_content",
                            passed=False,
                            points=0,
                            max_points=4,
                            message=f"File is empty"
                        ))
            except Exception:
                checks.append(ValidationCheck(
                    name="has_content",
                    passed=False,
                    points=0,
                    max_points=4,
                    message=f"Could not read file"
                ))
        else:
            checks.append(ValidationCheck(
                name="output_file_exists",
                passed=False,
                points=0,
                max_points=4,
                message=f"Output file not found"
            ))

        passed = total_points >= (self.points * 0.6)
        return ValidationResult(self.id, passed, total_points, self.points, checks)
