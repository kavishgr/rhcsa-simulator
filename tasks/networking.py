"""
Network configuration tasks for RHCSA exam.
"""

import random
import logging
from tasks.base import BaseTask
from tasks.registry import TaskRegistry
from core.validator import ValidationCheck, ValidationResult
from validators.system_validators import (
    get_ip_address, get_interface_state, validate_interface_ip,
    get_default_gateway, get_dns_servers, validate_dns_server,
    get_nmcli_connection_info
)
from validators.file_validators import validate_file_contains


logger = logging.getLogger(__name__)


@TaskRegistry.register("networking")
class ConfigureStaticIPTask(BaseTask):
    """Configure static IP address using nmcli."""

    def __init__(self):
        super().__init__(
            id="net_static_ip_001",
            category="networking",
            difficulty="medium",
            points=12
        )
        self.interface = None
        self.ip_address = None
        self.netmask = None
        self.connection_name = None

    def generate(self, **params):
        """Generate static IP configuration task."""
        self.interface = params.get('interface', 'eth0')
        self.ip_address = params.get('ip', f'192.168.{random.randint(1,254)}.{random.randint(10,250)}')
        self.netmask = params.get('netmask', '24')
        self.connection_name = params.get('connection', self.interface)

        self.description = (
            f"Configure static IP address:\n"
            f"  - Interface: {self.interface}\n"
            f"  - IP Address: {self.ip_address}/{self.netmask}\n"
            f"  - Connection name: {self.connection_name}\n"
            f"  - Use nmcli to configure\n"
            f"  - Configuration must persist across reboots\n"
            f"  - Activate the connection"
        )

        self.hints = [
            f"Use nmcli to modify connection: nmcli con mod {self.connection_name}",
            f"Set IP: nmcli con mod {self.connection_name} ipv4.addresses {self.ip_address}/{self.netmask}",
            f"Set method to manual: nmcli con mod {self.connection_name} ipv4.method manual",
            f"Activate: nmcli con up {self.connection_name}",
            f"Verify: ip addr show {self.interface} or nmcli con show {self.connection_name}",
            f"Check persistent config: nmcli -f ipv4 con show {self.connection_name}"
        ]

        return self

    def validate(self):
        """Validate static IP configuration."""
        checks = []
        total_points = 0

        # Check 1: Interface has correct IP (6 points)
        actual_ip = get_ip_address(self.interface)
        if actual_ip == self.ip_address:
            checks.append(ValidationCheck(
                name="ip_address_set",
                passed=True,
                points=6,
                message=f"IP address {self.ip_address} correctly configured"
            ))
            total_points += 6
        else:
            checks.append(ValidationCheck(
                name="ip_address_set",
                passed=False,
                points=0,
                max_points=6,
                message=f"IP address is {actual_ip}, expected {self.ip_address}"
            ))

        # Check 2: Interface is UP (3 points)
        state = get_interface_state(self.interface)
        if state == 'UP':
            checks.append(ValidationCheck(
                name="interface_up",
                passed=True,
                points=3,
                message=f"Interface {self.interface} is UP"
            ))
            total_points += 3
        else:
            checks.append(ValidationCheck(
                name="interface_up",
                passed=False,
                points=0,
                max_points=3,
                message=f"Interface {self.interface} is {state}"
            ))

        # Check 3: Connection configured persistently (3 points)
        conn_info = get_nmcli_connection_info(self.connection_name)
        if conn_info:
            # Check if ipv4.method is manual
            if conn_info.get('ipv4.method') == 'manual':
                checks.append(ValidationCheck(
                    name="persistent_config",
                    passed=True,
                    points=3,
                    message=f"Connection configured with manual IPv4"
                ))
                total_points += 3
            else:
                checks.append(ValidationCheck(
                    name="persistent_config",
                    passed=True,
                    points=2,
                    message=f"Connection exists but IPv4 method is {conn_info.get('ipv4.method')} (partial credit)"
                ))
                total_points += 2
        else:
            checks.append(ValidationCheck(
                name="persistent_config",
                passed=False,
                points=0,
                max_points=3,
                message=f"Connection {self.connection_name} not found"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("networking")
class ConfigureDefaultGatewayTask(BaseTask):
    """Configure default gateway."""

    def __init__(self):
        super().__init__(
            id="net_gateway_001",
            category="networking",
            difficulty="easy",
            points=8
        )
        self.gateway = None
        self.connection_name = None

    def generate(self, **params):
        """Generate gateway configuration task."""
        self.gateway = params.get('gateway', f'192.168.{random.randint(1,254)}.1')
        self.connection_name = params.get('connection', 'eth0')

        self.description = (
            f"Configure default gateway:\n"
            f"  - Gateway IP: {self.gateway}\n"
            f"  - Connection: {self.connection_name}\n"
            f"  - Use nmcli to configure\n"
            f"  - Configuration must be persistent"
        )

        self.hints = [
            f"Set gateway: nmcli con mod {self.connection_name} ipv4.gateway {self.gateway}",
            f"Activate connection: nmcli con up {self.connection_name}",
            "Verify: ip route show default",
            f"Or verify: nmcli -f ipv4 con show {self.connection_name}"
        ]

        return self

    def validate(self):
        """Validate gateway configuration."""
        checks = []
        total_points = 0

        # Check 1: Default gateway is set (5 points)
        current_gateway = get_default_gateway()
        if current_gateway == self.gateway:
            checks.append(ValidationCheck(
                name="gateway_set",
                passed=True,
                points=5,
                message=f"Default gateway is {self.gateway}"
            ))
            total_points += 5
        else:
            checks.append(ValidationCheck(
                name="gateway_set",
                passed=False,
                points=0,
                max_points=5,
                message=f"Default gateway is {current_gateway}, expected {self.gateway}"
            ))

        # Check 2: Gateway configured persistently in connection (3 points)
        conn_info = get_nmcli_connection_info(self.connection_name)
        if conn_info and self.gateway in str(conn_info.get('ipv4.gateway', '')):
            checks.append(ValidationCheck(
                name="gateway_persistent",
                passed=True,
                points=3,
                message=f"Gateway configured persistently"
            ))
            total_points += 3
        else:
            checks.append(ValidationCheck(
                name="gateway_persistent",
                passed=False,
                points=0,
                max_points=3,
                message=f"Gateway not configured persistently in connection"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("networking")
class ConfigureDNSTask(BaseTask):
    """Configure DNS servers."""

    def __init__(self):
        super().__init__(
            id="net_dns_001",
            category="networking",
            difficulty="easy",
            points=8
        )
        self.dns_servers = None
        self.connection_name = None

    def generate(self, **params):
        """Generate DNS configuration task."""
        self.dns_servers = params.get('dns', ['8.8.8.8', '8.8.4.4'])
        if isinstance(self.dns_servers, str):
            self.dns_servers = [self.dns_servers]
        self.connection_name = params.get('connection', 'eth0')

        dns_list = ' '.join(self.dns_servers)

        self.description = (
            f"Configure DNS servers:\n"
            f"  - DNS servers: {', '.join(self.dns_servers)}\n"
            f"  - Connection: {self.connection_name}\n"
            f"  - Use nmcli to configure\n"
            f"  - Configuration must be persistent"
        )

        self.hints = [
            f"Set DNS: nmcli con mod {self.connection_name} ipv4.dns \"{dns_list}\"",
            f"Activate: nmcli con up {self.connection_name}",
            "Verify: cat /etc/resolv.conf",
            f"Or verify: nmcli -f ipv4 con show {self.connection_name}"
        ]

        return self

    def validate(self):
        """Validate DNS configuration."""
        checks = []
        total_points = 0

        # Check 1: DNS servers are configured (5 points)
        current_dns = get_dns_servers()
        dns_configured = all(dns in current_dns for dns in self.dns_servers)

        if dns_configured:
            checks.append(ValidationCheck(
                name="dns_configured",
                passed=True,
                points=5,
                message=f"DNS servers correctly configured"
            ))
            total_points += 5
        elif any(dns in current_dns for dns in self.dns_servers):
            checks.append(ValidationCheck(
                name="dns_configured",
                passed=True,
                points=3,
                message=f"Some DNS servers configured (partial credit)"
            ))
            total_points += 3
        else:
            checks.append(ValidationCheck(
                name="dns_configured",
                passed=False,
                points=0,
                max_points=5,
                message=f"DNS servers not configured. Current: {current_dns}"
            ))

        # Check 2: DNS configured persistently (3 points)
        conn_info = get_nmcli_connection_info(self.connection_name)
        if conn_info and any(dns in str(conn_info.get('ipv4.dns', '')) for dns in self.dns_servers):
            checks.append(ValidationCheck(
                name="dns_persistent",
                passed=True,
                points=3,
                message=f"DNS configured persistently"
            ))
            total_points += 3
        else:
            checks.append(ValidationCheck(
                name="dns_persistent",
                passed=False,
                points=0,
                max_points=3,
                message=f"DNS not configured persistently in connection"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("networking")
class SetHostnameTask(BaseTask):
    """Set system hostname."""

    def __init__(self):
        super().__init__(
            id="net_hostname_001",
            category="networking",
            difficulty="easy",
            points=6
        )
        self.hostname = None

    def generate(self, **params):
        """Generate hostname task."""
        hostnames = ['server1.example.com', 'rhel9.lab.local', 'workstation.test.net']
        self.hostname = params.get('hostname', random.choice(hostnames))

        self.description = (
            f"Set system hostname:\n"
            f"  - Hostname: {self.hostname}\n"
            f"  - Use hostnamectl command\n"
            f"  - Configuration must be persistent across reboots"
        )

        self.hints = [
            f"Set hostname: hostnamectl set-hostname {self.hostname}",
            "Verify: hostnamectl status",
            "Or verify: hostname",
            "Check persistent config: cat /etc/hostname"
        ]

        return self

    def validate(self):
        """Validate hostname configuration."""
        checks = []
        total_points = 0

        from validators.safe_executor import execute_safe

        # Check 1: Current hostname (3 points)
        result = execute_safe(['hostname'])
        current_hostname = result.stdout.strip() if result.success else None

        if current_hostname == self.hostname:
            checks.append(ValidationCheck(
                name="current_hostname",
                passed=True,
                points=3,
                message=f"Hostname is {self.hostname}"
            ))
            total_points += 3
        else:
            checks.append(ValidationCheck(
                name="current_hostname",
                passed=False,
                points=0,
                max_points=3,
                message=f"Hostname is {current_hostname}, expected {self.hostname}"
            ))

        # Check 2: Persistent hostname in /etc/hostname (3 points)
        if validate_file_contains('/etc/hostname', self.hostname):
            checks.append(ValidationCheck(
                name="persistent_hostname",
                passed=True,
                points=3,
                message=f"Hostname configured persistently"
            ))
            total_points += 3
        else:
            checks.append(ValidationCheck(
                name="persistent_hostname",
                passed=False,
                points=0,
                max_points=3,
                message=f"Hostname not in /etc/hostname"
            ))

        passed = total_points >= (self.points * 0.8)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("networking")
class ConfigureNetworkFullTask(BaseTask):
    """Complete network configuration (compound task)."""

    def __init__(self):
        super().__init__(
            id="net_full_config_001",
            category="networking",
            difficulty="exam",
            points=15
        )
        self.interface = None
        self.ip_address = None
        self.netmask = None
        self.gateway = None
        self.dns = None
        self.connection_name = None

    def generate(self, **params):
        """Generate complete network configuration task."""
        self.interface = params.get('interface', 'eth0')
        self.ip_address = params.get('ip', f'192.168.{random.randint(1,254)}.{random.randint(10,250)}')
        self.netmask = params.get('netmask', '24')
        self.gateway = params.get('gateway', f'192.168.{self.ip_address.split(".")[2]}.1')
        self.dns = params.get('dns', ['8.8.8.8', '8.8.4.4'])
        if isinstance(self.dns, str):
            self.dns = [self.dns]
        self.connection_name = params.get('connection', self.interface)

        self.description = (
            f"Configure complete network settings:\n"
            f"  - Interface: {self.interface}\n"
            f"  - IP Address: {self.ip_address}/{self.netmask}\n"
            f"  - Gateway: {self.gateway}\n"
            f"  - DNS Servers: {', '.join(self.dns)}\n"
            f"  - Connection: {self.connection_name}\n"
            f"  - All configuration must persist across reboots\n"
            f"  - Use nmcli for configuration"
        )

        dns_list = ' '.join(self.dns)

        self.hints = [
            f"Set static IP: nmcli con mod {self.connection_name} ipv4.addresses {self.ip_address}/{self.netmask}",
            f"Set method: nmcli con mod {self.connection_name} ipv4.method manual",
            f"Set gateway: nmcli con mod {self.connection_name} ipv4.gateway {self.gateway}",
            f"Set DNS: nmcli con mod {self.connection_name} ipv4.dns \"{dns_list}\"",
            f"Activate: nmcli con up {self.connection_name}",
            "Verify: ip addr show; ip route; cat /etc/resolv.conf"
        ]

        return self

    def validate(self):
        """Validate complete network configuration."""
        checks = []
        total_points = 0

        # Check 1: IP address (5 points)
        actual_ip = get_ip_address(self.interface)
        if actual_ip == self.ip_address:
            checks.append(ValidationCheck(
                name="ip_configured",
                passed=True,
                points=5,
                message=f"IP address correctly configured"
            ))
            total_points += 5
        else:
            checks.append(ValidationCheck(
                name="ip_configured",
                passed=False,
                points=0,
                max_points=5,
                message=f"IP is {actual_ip}, expected {self.ip_address}"
            ))

        # Check 2: Gateway (4 points)
        current_gateway = get_default_gateway()
        if current_gateway == self.gateway:
            checks.append(ValidationCheck(
                name="gateway_configured",
                passed=True,
                points=4,
                message=f"Gateway correctly configured"
            ))
            total_points += 4
        else:
            checks.append(ValidationCheck(
                name="gateway_configured",
                passed=False,
                points=0,
                max_points=4,
                message=f"Gateway is {current_gateway}, expected {self.gateway}"
            ))

        # Check 3: DNS (3 points)
        current_dns = get_dns_servers()
        dns_ok = all(dns in current_dns for dns in self.dns)
        if dns_ok:
            checks.append(ValidationCheck(
                name="dns_configured",
                passed=True,
                points=3,
                message=f"DNS servers correctly configured"
            ))
            total_points += 3
        else:
            checks.append(ValidationCheck(
                name="dns_configured",
                passed=False,
                points=0,
                max_points=3,
                message=f"DNS not fully configured"
            ))

        # Check 4: Interface UP (3 points)
        state = get_interface_state(self.interface)
        if state == 'UP':
            checks.append(ValidationCheck(
                name="interface_up",
                passed=True,
                points=3,
                message=f"Interface is UP"
            ))
            total_points += 3
        else:
            checks.append(ValidationCheck(
                name="interface_up",
                passed=False,
                points=0,
                max_points=3,
                message=f"Interface is {state}"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("networking")
class ConfigureFirewallServiceTask(BaseTask):
    """Allow a service through the firewall."""

    def __init__(self):
        super().__init__(
            id="net_firewall_service_001",
            category="networking",
            difficulty="medium",
            points=8
        )
        self.service = None
        self.zone = None

    def generate(self, **params):
        services = ['http', 'https', 'ssh', 'nfs', 'samba', 'ftp']
        self.service = params.get('service', random.choice(services))
        self.zone = params.get('zone', 'public')

        self.description = (
            f"Configure firewall to allow a service:\n"
            f"  - Service: {self.service}\n"
            f"  - Zone: {self.zone}\n"
            f"  - Make the change permanent\n"
            f"  - Ensure firewalld is running"
        )

        self.hints = [
            "Ensure firewalld is running: systemctl status firewalld",
            f"Add service: firewall-cmd --zone={self.zone} --add-service={self.service} --permanent",
            "Reload firewall: firewall-cmd --reload",
            f"Verify: firewall-cmd --zone={self.zone} --list-services",
            "Without --permanent, changes are lost on reload/reboot"
        ]

        return self

    def validate(self):
        checks = []
        total_points = 0
        from validators.safe_executor import execute_safe

        # Check 1: Firewalld is running (3 points)
        result = execute_safe(['systemctl', 'is-active', 'firewalld'])
        if result.success and result.stdout.strip() == 'active':
            checks.append(ValidationCheck(
                name="firewalld_running",
                passed=True,
                points=3,
                message=f"firewalld is running"
            ))
            total_points += 3
        else:
            checks.append(ValidationCheck(
                name="firewalld_running",
                passed=False,
                points=0,
                max_points=3,
                message=f"firewalld is not running"
            ))

        # Check 2: Service is allowed (5 points)
        result = execute_safe(['firewall-cmd', f'--zone={self.zone}', '--list-services'])
        if result.success and self.service in result.stdout:
            checks.append(ValidationCheck(
                name="service_allowed",
                passed=True,
                points=5,
                message=f"Service '{self.service}' is allowed in zone {self.zone}"
            ))
            total_points += 5
        else:
            checks.append(ValidationCheck(
                name="service_allowed",
                passed=False,
                points=0,
                max_points=5,
                message=f"Service '{self.service}' is not allowed"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("networking")
class ConfigureFirewallPortTask(BaseTask):
    """Allow a specific port through the firewall."""

    def __init__(self):
        super().__init__(
            id="net_firewall_port_001",
            category="networking",
            difficulty="medium",
            points=8
        )
        self.port = None
        self.protocol = None
        self.zone = None

    def generate(self, **params):
        ports = [8080, 8443, 3000, 5000, 9090]
        self.port = params.get('port', random.choice(ports))
        self.protocol = params.get('protocol', 'tcp')
        self.zone = params.get('zone', 'public')

        self.description = (
            f"Configure firewall to allow a port:\n"
            f"  - Port: {self.port}/{self.protocol}\n"
            f"  - Zone: {self.zone}\n"
            f"  - Make the change permanent\n"
            f"  - Reload firewall to apply"
        )

        self.hints = [
            f"Add port: firewall-cmd --zone={self.zone} --add-port={self.port}/{self.protocol} --permanent",
            "Reload: firewall-cmd --reload",
            f"Verify: firewall-cmd --zone={self.zone} --list-ports",
            "Port format: <port>/<protocol> (e.g., 8080/tcp)",
            "Check current zone: firewall-cmd --get-active-zones"
        ]

        return self

    def validate(self):
        checks = []
        total_points = 0
        from validators.safe_executor import execute_safe

        # Check 1: Firewalld is running (3 points)
        result = execute_safe(['systemctl', 'is-active', 'firewalld'])
        if result.success and result.stdout.strip() == 'active':
            checks.append(ValidationCheck(
                name="firewalld_running",
                passed=True,
                points=3,
                message=f"firewalld is running"
            ))
            total_points += 3
        else:
            checks.append(ValidationCheck(
                name="firewalld_running",
                passed=False,
                points=0,
                max_points=3,
                message=f"firewalld is not running"
            ))

        # Check 2: Port is allowed (5 points)
        result = execute_safe(['firewall-cmd', f'--zone={self.zone}', '--list-ports'])
        port_str = f'{self.port}/{self.protocol}'
        if result.success and port_str in result.stdout:
            checks.append(ValidationCheck(
                name="port_allowed",
                passed=True,
                points=5,
                message=f"Port {port_str} is allowed"
            ))
            total_points += 5
        else:
            checks.append(ValidationCheck(
                name="port_allowed",
                passed=False,
                points=0,
                max_points=5,
                message=f"Port {port_str} is not allowed"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)


@TaskRegistry.register("networking")
class ConfigureFirewallRichRuleTask(BaseTask):
    """Configure a rich rule in firewalld."""

    def __init__(self):
        super().__init__(
            id="net_firewall_rich_001",
            category="networking",
            difficulty="exam",
            points=12
        )
        self.source_ip = None
        self.port = None
        self.action = None

    def generate(self, **params):
        self.source_ip = params.get('source', f'192.168.{random.randint(1,254)}.0/24')
        self.port = params.get('port', random.choice([22, 80, 443, 8080]))
        self.action = params.get('action', 'accept')

        self.description = (
            f"Configure a firewall rich rule:\n"
            f"  - Allow traffic from: {self.source_ip}\n"
            f"  - To port: {self.port}/tcp\n"
            f"  - Action: {self.action}\n"
            f"  - Make the rule permanent\n"
            f"  - Reload firewall to apply"
        )

        self.hints = [
            f"Rich rule format: rule family='ipv4' source address='{self.source_ip}' port port={self.port} protocol=tcp accept",
            f"Add rule: firewall-cmd --add-rich-rule='rule family=\"ipv4\" source address=\"{self.source_ip}\" port port=\"{self.port}\" protocol=\"tcp\" accept' --permanent",
            "Reload: firewall-cmd --reload",
            "List rich rules: firewall-cmd --list-rich-rules",
            "Rich rules allow more complex firewall configurations"
        ]

        return self

    def validate(self):
        checks = []
        total_points = 0
        from validators.safe_executor import execute_safe

        # Check 1: Firewalld is running (4 points)
        result = execute_safe(['systemctl', 'is-active', 'firewalld'])
        if result.success and result.stdout.strip() == 'active':
            checks.append(ValidationCheck(
                name="firewalld_running",
                passed=True,
                points=4,
                message=f"firewalld is running"
            ))
            total_points += 4
        else:
            checks.append(ValidationCheck(
                name="firewalld_running",
                passed=False,
                points=0,
                max_points=4,
                message=f"firewalld is not running"
            ))

        # Check 2: Rich rule exists (8 points)
        result = execute_safe(['firewall-cmd', '--list-rich-rules'])
        if result.success and self.source_ip in result.stdout and str(self.port) in result.stdout:
            checks.append(ValidationCheck(
                name="rich_rule_exists",
                passed=True,
                points=8,
                message=f"Rich rule configured correctly"
            ))
            total_points += 8
        else:
            checks.append(ValidationCheck(
                name="rich_rule_exists",
                passed=False,
                points=0,
                max_points=8,
                message=f"Rich rule not found or incomplete"
            ))

        passed = total_points >= (self.points * 0.7)
        return ValidationResult(self.id, passed, total_points, self.points, checks)
