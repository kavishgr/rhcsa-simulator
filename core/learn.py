"""
Learn Mode - Instructional content for RHCSA topics.
Provides explanations, commands, and common mistakes for each topic.
"""

import logging
from utils import formatters as fmt
from utils.helpers import confirm_action


logger = logging.getLogger(__name__)


class LearnContent:
    """
    Educational content for RHCSA topics.
    Each topic includes: explanation, commands, examples, and common mistakes.
    """

    TOPICS = {
        "users_groups": {
            "name": "Users & Groups Management",
            "explanation": """
User and group management is fundamental to Linux system administration.
You'll need to create users with specific UIDs, assign them to groups,
configure sudo access, and manage user properties. The exam tests your
ability to use useradd, usermod, groupadd, and sudo configuration.

KEY FILES TO KNOW:
  /etc/passwd    - User account info (username:x:UID:GID:comment:home:shell)
  /etc/shadow    - Encrypted passwords and aging info
  /etc/group     - Group definitions (groupname:x:GID:members)
  /etc/gshadow   - Group passwords
  /etc/login.defs - Default settings for new users
  /etc/skel/     - Template files copied to new home directories
  /etc/sudoers.d/ - Drop-in sudo configuration files

UID RANGES (RHEL defaults):
  0         - root
  1-999     - System accounts
  1000+     - Regular users
            """,
            "commands": [
                {
                    "name": "Create User with UID",
                    "syntax": "useradd -u <UID> -m <username>",
                    "example": "useradd -u 2500 -m -c 'Exam User' examuser",
                    "flags": {
                        "-u": "Specify user ID (UID)",
                        "-m": "Create home directory",
                        "-M": "Do NOT create home directory",
                        "-g": "Primary group (name or GID)",
                        "-G": "Supplementary groups (comma-separated)",
                        "-s": "Login shell",
                        "-c": "Comment/GECOS field (full name)",
                        "-d": "Home directory path",
                        "-e": "Account expiration date (YYYY-MM-DD)",
                        "-r": "Create system account (UID < 1000)"
                    }
                },
                {
                    "name": "Modify User",
                    "syntax": "usermod [OPTIONS] <username>",
                    "example": "usermod -aG wheel,developers examuser",
                    "flags": {
                        "-aG": "Add to supplementary groups (APPEND - critical!)",
                        "-G": "Set supplementary groups (REPLACES all existing!)",
                        "-L": "Lock account (adds ! to password in shadow)",
                        "-U": "Unlock account",
                        "-s": "Change login shell",
                        "-l": "Change login name",
                        "-d": "Change home directory",
                        "-m": "Move home directory contents (use with -d)",
                        "-e": "Set account expiration date"
                    }
                },
                {
                    "name": "Delete User",
                    "syntax": "userdel [-r] <username>",
                    "example": "userdel -r olduser",
                    "flags": {
                        "userdel user": "Delete user (keeps home directory)",
                        "-r": "Remove home directory and mail spool",
                        "-f": "Force deletion even if user logged in"
                    }
                },
                {
                    "name": "Set Password",
                    "syntax": "passwd <username>",
                    "example": "passwd examuser",
                    "flags": {
                        "passwd": "Change own password",
                        "passwd user": "Change another user's password (root)",
                        "--stdin": "Read password from stdin (scripting)",
                        "-l": "Lock account",
                        "-u": "Unlock account",
                        "-d": "Delete password (passwordless)",
                        "-e": "Expire password (force change on next login)"
                    }
                },
                {
                    "name": "Password Aging (chage)",
                    "syntax": "chage [OPTIONS] <username>",
                    "example": "chage -M 90 -W 7 examuser",
                    "flags": {
                        "-l": "List password aging info",
                        "-d 0": "Force password change on next login",
                        "-M": "Maximum days between password changes",
                        "-m": "Minimum days between password changes",
                        "-W": "Warning days before expiration",
                        "-I": "Inactive days after password expires",
                        "-E": "Account expiration date (YYYY-MM-DD)"
                    }
                },
                {
                    "name": "Configure Sudo Access",
                    "syntax": "echo 'user ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/user",
                    "example": "echo 'examuser ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/examuser && chmod 0440 /etc/sudoers.d/examuser",
                    "flags": {
                        "ALL=(ALL)": "Run as any user on any host",
                        "NOPASSWD:": "No password required",
                        "ALL": "Can run any command",
                        "%groupname": "Apply to group (e.g., %wheel)",
                        "visudo": "Safe way to edit sudoers (checks syntax)"
                    }
                },
                {
                    "name": "Create Group",
                    "syntax": "groupadd -g <GID> <groupname>",
                    "example": "groupadd -g 3000 developers",
                    "flags": {
                        "-g": "Specify group ID (GID)",
                        "-r": "Create system group (GID < 1000)"
                    }
                },
                {
                    "name": "Modify/Delete Group",
                    "syntax": "groupmod / groupdel",
                    "example": "groupmod -n newname oldname",
                    "flags": {
                        "groupmod -n": "Rename group",
                        "groupmod -g": "Change GID",
                        "groupdel": "Delete group (must have no users)"
                    }
                },
                {
                    "name": "View User/Group Info",
                    "syntax": "id / groups / getent",
                    "example": "id examuser && groups examuser",
                    "flags": {
                        "id user": "Show UID, GID, and groups",
                        "groups user": "Show group memberships",
                        "getent passwd user": "Query user from all sources",
                        "getent group grp": "Query group from all sources"
                    }
                }
            ],
            "common_mistakes": [
                "Forgetting -m flag -> No home directory created",
                "Using -G without -a -> REMOVES user from ALL existing groups (critical!)",
                "Sudo file wrong permissions (must be 0440 or 0400)",
                "Creating sudo file in /etc/sudoers instead of /etc/sudoers.d/",
                "Not using visudo -> Syntax errors can break ALL sudo access",
                "Forgetting to run 'chage -d 0' when password change on login is required",
                "Using userdel without -r leaves orphaned files",
                "Not verifying with 'id username' after user creation"
            ],
            "exam_tricks": [
                "Exam may specify exact UID - don't let system auto-assign",
                "Multiple supplementary groups - must add ALL of them",
                "Persistent sudo access - must survive reboot (use /etc/sudoers.d/)",
                "User must exist but account might need to be locked (usermod -L)",
                "'Password must change on next login' = chage -d 0 username",
                "Account expiry vs password expiry - they're different!",
                "Always verify with 'id username' and 'sudo -l -U username'"
            ]
        },

        "permissions": {
            "name": "File Permissions & ACLs",
            "explanation": """
Linux permissions control file access using owner, group, and other.
Special permissions (setuid, setgid, sticky) add advanced functionality.
ACLs (Access Control Lists) provide fine-grained access control beyond
traditional permissions. The exam tests chmod, chown, setfacl, and
understanding of permission inheritance and special bits.

PERMISSION STRUCTURE:
  -rwxrwxrwx = type + owner + group + others

  Type: - (file), d (directory), l (link), b (block), c (char)

NUMERIC VALUES:
  r = 4 (read)
  w = 2 (write)
  x = 1 (execute)

  Example: rwxr-xr-- = 754
    Owner: rwx = 4+2+1 = 7
    Group: r-x = 4+0+1 = 5
    Others: r-- = 4+0+0 = 4

DIRECTORY PERMISSIONS:
  r = list contents (ls)
  w = create/delete files within
  x = access/traverse (cd into)

  Note: Without x, you can't access files even with r!

SPECIAL PERMISSIONS:
  SUID (4) - setuid: File runs as FILE OWNER
  SGID (2) - setgid: File runs as GROUP / Dir inherits group
  Sticky (1) - Only owner can delete their files (e.g., /tmp)

  ls -l shows: s (SUID/SGID with x), S (without x), t (sticky with x), T (without x)
            """,
            "commands": [
                {
                    "name": "Set Permissions (Octal)",
                    "syntax": "chmod <octal> <file>",
                    "example": "chmod 755 /usr/local/bin/myscript",
                    "flags": {
                        "4": "Read permission",
                        "2": "Write permission",
                        "1": "Execute permission",
                        "Owner": "First digit (rwx = 7)",
                        "Group": "Second digit (r-x = 5)",
                        "Other": "Third digit (r-- = 4)",
                        "-R": "Recursive (apply to all files in directory)"
                    }
                },
                {
                    "name": "Set Permissions (Symbolic)",
                    "syntax": "chmod [ugoa][+-=][rwx] <file>",
                    "example": "chmod u+x,g-w,o=r script.sh",
                    "flags": {
                        "u": "User (owner)",
                        "g": "Group",
                        "o": "Others",
                        "a": "All (u+g+o)",
                        "+": "Add permission",
                        "-": "Remove permission",
                        "=": "Set exact permission"
                    }
                },
                {
                    "name": "Set Special Permissions",
                    "syntax": "chmod <special><perms> <file>",
                    "example": "chmod 2755 /shared/directory",
                    "flags": {
                        "4xxx": "Setuid (4755) - file executes as owner",
                        "2xxx": "Setgid (2755) - file as group / dir inherits group",
                        "1xxx": "Sticky bit (1777) - only owner can delete files",
                        "u+s": "Set SUID (symbolic)",
                        "g+s": "Set SGID (symbolic)",
                        "+t": "Set sticky bit (symbolic)"
                    }
                },
                {
                    "name": "Change Ownership",
                    "syntax": "chown <user>:<group> <file>",
                    "example": "chown apache:apache /var/www/html/index.html",
                    "flags": {
                        "user:group": "Set both owner and group",
                        "user": "Set owner only",
                        "user:": "Set owner, group to user's login group",
                        ":group": "Set group only (or use chgrp)",
                        "-R": "Recursive (for directories)",
                        "--reference=file": "Copy ownership from another file"
                    }
                },
                {
                    "name": "Change Group",
                    "syntax": "chgrp <group> <file>",
                    "example": "chgrp developers /project/code",
                    "flags": {
                        "chgrp group file": "Change group ownership",
                        "-R": "Recursive"
                    }
                },
                {
                    "name": "Set Default Permissions (umask)",
                    "syntax": "umask <mask>",
                    "example": "umask 027",
                    "flags": {
                        "umask": "Display current umask",
                        "umask 022": "Files: 644, Dirs: 755 (default)",
                        "umask 027": "Files: 640, Dirs: 750",
                        "umask 077": "Files: 600, Dirs: 700 (private)",
                        "/etc/bashrc": "Set persistent umask here",
                        "Calculation": "666-umask (files), 777-umask (dirs)"
                    }
                },
                {
                    "name": "Set ACL",
                    "syntax": "setfacl -m u:<user>:<perms> <file>",
                    "example": "setfacl -m u:nginx:rw /var/log/app.log",
                    "flags": {
                        "-m": "Modify ACL (add/change entry)",
                        "u:user:rwx": "User ACL entry",
                        "g:group:rx": "Group ACL entry",
                        "o::r": "Others entry",
                        "-x u:user": "Remove specific ACL entry",
                        "-b": "Remove ALL ACLs",
                        "-R": "Recursive",
                        "-d": "Set DEFAULT ACL (new files inherit, dirs only)",
                        "--set": "Replace all ACLs"
                    }
                },
                {
                    "name": "View ACL",
                    "syntax": "getfacl <file>",
                    "example": "getfacl /data/shared",
                    "flags": {
                        "getfacl file": "Show all ACL entries",
                        "ls -l": "+ at end indicates ACL exists",
                        "mask::": "Maximum effective permissions"
                    }
                },
                {
                    "name": "Default ACLs (Inheritance)",
                    "syntax": "setfacl -d -m u:<user>:<perms> <directory>",
                    "example": "setfacl -d -m u:developer:rwx /projects",
                    "flags": {
                        "-d -m": "Set default ACL (affects NEW files)",
                        "d:u:user:rwx": "Default user ACL",
                        "d:g:group:rx": "Default group ACL",
                        "Note": "Default ACLs ONLY work on directories"
                    }
                }
            ],
            "common_mistakes": [
                "Mixing symbolic and octal notation in same command",
                "Forgetting -R flag for recursive changes on directories",
                "Wrong order in chown (it's user:group, not group:user)",
                "ACL syntax errors (missing colons in u:user:perms)",
                "Not setting DEFAULT ACLs on directories (new files won't inherit)",
                "chmod 755 removes any special permissions - use chmod 2755 to keep SGID",
                "Forgetting x permission on directories (can't cd or access files)",
                "Setting ACL but not checking mask (mask limits effective permissions)",
                "Using chcon instead of setfacl (chcon is for SELinux contexts)"
            ],
            "exam_tricks": [
                "May ask for special permissions - know 4/2/1 prefix (SUID/SGID/Sticky)",
                "SGID on directories = new files inherit group ownership (common exam task)",
                "Sticky bit on shared dirs = users can only delete their own files",
                "ACL + sign in ls -l output indicates ACL exists",
                "Default ACLs (-d) only apply to NEW files/dirs, not existing ones",
                "Verify ACLs with getfacl, not ls -l (ls only shows +)",
                "Capital S or T in ls -l means special permission WITHOUT execute",
                "umask 027 is common for restricting others' access"
            ]
        },

        "services": {
            "name": "Service Management (systemd)",
            "explanation": """
Systemd is the init system and service manager in RHEL 8/9.
You must know how to start, stop, enable, disable, and check service status.
Understanding the difference between 'start' (now) and 'enable' (at boot)
is crucial. The exam tests service manipulation, unit file creation,
and boot target management.
            """,
            "commands": [
                {
                    "name": "Start Service (Immediately)",
                    "syntax": "systemctl start <service>",
                    "example": "systemctl start httpd",
                    "flags": {
                        "start": "Start service now (doesn't survive reboot)",
                        "stop": "Stop service now",
                        "restart": "Stop then start",
                        "reload": "Reload config without stopping"
                    }
                },
                {
                    "name": "Enable Service (At Boot)",
                    "syntax": "systemctl enable <service>",
                    "example": "systemctl enable httpd",
                    "flags": {
                        "enable": "Start at boot (doesn't start now)",
                        "disable": "Don't start at boot",
                        "enable --now": "Enable AND start immediately"
                    }
                },
                {
                    "name": "Check Service Status",
                    "syntax": "systemctl status <service>",
                    "example": "systemctl status sshd",
                    "flags": {
                        "status": "Show current status and recent logs",
                        "is-active": "Check if running (active/inactive)",
                        "is-enabled": "Check if enabled at boot"
                    }
                },
                {
                    "name": "Mask Service (Prevent Start)",
                    "syntax": "systemctl mask <service>",
                    "example": "systemctl mask postfix",
                    "flags": {
                        "mask": "Completely prevent service from starting",
                        "unmask": "Remove mask"
                    }
                }
            ],
            "common_mistakes": [
                "Only starting service (forgetting to enable)",
                "Only enabling service (forgetting to start)",
                "Using service name without .service suffix sometimes needed",
                "Not reloading systemd after editing unit files",
                "Checking wrong service name"
            ],
            "exam_tricks": [
                "Task says 'configure to start at boot' = enable + start",
                "Service might already be masked - must unmask first",
                "May need to reload daemon: systemctl daemon-reload",
                "Check both is-active AND is-enabled"
            ]
        },

        "selinux": {
            "name": "SELinux Security",
            "explanation": """
SELinux (Security-Enhanced Linux) provides mandatory access control.
You must understand contexts (user:role:type:level), booleans, and modes.
The exam tests setting file contexts with semanage/restorecon,
toggling booleans with setsebool, and changing SELinux modes.
Always make changes persistent!
            """,
            "commands": [
                {
                    "name": "Set File Context (Persistent)",
                    "syntax": "semanage fcontext -a -t <type> '<path>(/.*)?' && restorecon -Rv <path>",
                    "example": "semanage fcontext -a -t httpd_sys_content_t '/web(/.*)?'\nrestorecon -Rv /web",
                    "flags": {
                        "-a": "Add policy rule",
                        "-t": "Set type context",
                        "'<path>(/.*)?'": "Regex for path and subdirs",
                        "restorecon -Rv": "Apply the context now"
                    }
                },
                {
                    "name": "Set Boolean (Persistent)",
                    "syntax": "setsebool -P <boolean> on|off",
                    "example": "setsebool -P httpd_can_network_connect on",
                    "flags": {
                        "-P": "Make change persistent (CRITICAL!)",
                        "on": "Enable boolean",
                        "off": "Disable boolean"
                    }
                },
                {
                    "name": "Change SELinux Mode",
                    "syntax": "setenforce 0|1 && edit /etc/selinux/config",
                    "example": "setenforce 0\nvi /etc/selinux/config (set SELINUX=permissive)",
                    "flags": {
                        "0": "Permissive mode (now)",
                        "1": "Enforcing mode (now)",
                        "/etc/selinux/config": "Persistent setting",
                        "SELINUX=": "enforcing, permissive, or disabled"
                    }
                },
                {
                    "name": "Check Context",
                    "syntax": "ls -Z <file>",
                    "example": "ls -Zd /var/www/html",
                    "flags": {
                        "-Z": "Show SELinux context",
                        "getenforce": "Show current mode",
                        "getsebool -a": "List all booleans"
                    }
                }
            ],
            "common_mistakes": [
                "Forgetting -P flag on setsebool (not persistent!)",
                "Not running restorecon after semanage",
                "Wrong regex pattern in semanage (missing (/.*)?)",
                "Setting mode without editing /etc/selinux/config",
                "Using chcon instead of semanage (not persistent)"
            ],
            "exam_tricks": [
                "Exam always wants persistent changes - use -P and semanage",
                "File context needs BOTH semanage AND restorecon",
                "Boolean might already be set but not persistent",
                "Context format is user:role:type:level (you usually change type)"
            ]
        },

        "lvm": {
            "name": "LVM (Logical Volume Management)",
            "explanation": """
LVM provides flexible disk management with physical volumes (PV),
volume groups (VG), and logical volumes (LV). The hierarchy is:
Disk → PV → VG → LV → Filesystem. You must know creation, extension,
and reduction operations. The exam tests your ability to create the
full LVM stack and resize volumes.
            """,
            "commands": [
                {
                    "name": "Create Physical Volume",
                    "syntax": "pvcreate <device>",
                    "example": "pvcreate /dev/sdb",
                    "flags": {
                        "/dev/sdX": "Block device to use",
                        "pvdisplay": "Show PV details",
                        "pvs": "List PVs (short)"
                    }
                },
                {
                    "name": "Create Volume Group",
                    "syntax": "vgcreate <vgname> <pv>",
                    "example": "vgcreate vgdata /dev/sdb",
                    "flags": {
                        "vgname": "Name for volume group",
                        "pv": "Physical volume(s) to include",
                        "vgdisplay": "Show VG details",
                        "vgs": "List VGs (short)"
                    }
                },
                {
                    "name": "Create Logical Volume",
                    "syntax": "lvcreate -n <lvname> -L <size> <vgname>",
                    "example": "lvcreate -n lvdata -L 500M vgdata",
                    "flags": {
                        "-n": "Logical volume name",
                        "-L": "Size (M, G, T)",
                        "-l": "Size in extents (e.g., -l 100%FREE)",
                        "lvdisplay": "Show LV details",
                        "lvs": "List LVs (short)"
                    }
                },
                {
                    "name": "Extend Logical Volume",
                    "syntax": "lvextend -L +<size> <lv_path> && resize2fs/xfs_growfs",
                    "example": "lvextend -L +1G /dev/vgdata/lvdata\nxfs_growfs /dev/vgdata/lvdata",
                    "flags": {
                        "-L +size": "Increase by size",
                        "-L size": "Set to absolute size",
                        "-r": "Resize filesystem automatically",
                        "resize2fs": "For ext4 filesystems",
                        "xfs_growfs": "For XFS filesystems"
                    }
                }
            ],
            "common_mistakes": [
                "Wrong order: must create PV → VG → LV",
                "Forgetting to resize filesystem after extending LV",
                "Using wrong filesystem resize command (ext4 vs XFS)",
                "Not using -r flag to auto-resize",
                "Insufficient space in VG for LV"
            ],
            "exam_tricks": [
                "Exam specifies exact size - watch units (M vs MB vs MiB)",
                "May ask to extend existing LV (not create new)",
                "Filesystem resize is separate step (unless -r flag)",
                "Path is /dev/vgname/lvname or /dev/mapper/vgname-lvname"
            ]
        },

        "networking": {
            "name": "Networking Configuration",
            "explanation": """
Network configuration in RHEL 8/9 uses NetworkManager and the nmcli command.
You must understand the difference between CONNECTIONS and DEVICES:
  - DEVICE: Physical or virtual network interface (eth0, enp0s3)
  - CONNECTION: Configuration profile that can be applied to a device

Key concepts:
  - One device can have multiple connection profiles (only one active)
  - Connection names may differ from device/interface names
  - Use 'nmcli con' for persistent config, 'ip' for temporary changes
  - Config files stored in /etc/NetworkManager/system-connections/

The exam tests: static IP configuration, DNS, hostname, creating connections,
and troubleshooting network issues using nmcli and ip commands.
            """,
            "commands": [
                {
                    "name": "Show Connections & Devices",
                    "syntax": "nmcli connection show / nmcli device status",
                    "example": "nmcli con show --active",
                    "flags": {
                        "con show": "List all connection profiles",
                        "con show --active": "Show only active connections",
                        "con show <name>": "Show detailed connection info",
                        "device status": "Show all devices and their state",
                        "device show <dev>": "Show device details",
                        "general status": "Show overall NetworkManager status"
                    }
                },
                {
                    "name": "Create New Connection",
                    "syntax": "nmcli con add type ethernet con-name <name> ifname <device>",
                    "example": "nmcli con add type ethernet con-name office ifname eth1 ipv4.addresses 10.0.0.50/24 ipv4.method manual",
                    "flags": {
                        "con add": "Create a new connection profile",
                        "type ethernet": "Wired connection (also: wifi, bond, team)",
                        "con-name": "Name for the connection profile",
                        "ifname": "Physical interface to bind to",
                        "autoconnect yes/no": "Auto-activate on boot"
                    }
                },
                {
                    "name": "Configure Static IP",
                    "syntax": "nmcli con mod <name> ipv4.addresses <ip>/<prefix> ipv4.gateway <gw> ipv4.method manual",
                    "example": "nmcli con mod eth0 ipv4.addresses 192.168.1.100/24 ipv4.gateway 192.168.1.1 ipv4.method manual",
                    "flags": {
                        "ipv4.addresses": "IP with CIDR prefix (required)",
                        "ipv4.gateway": "Default gateway",
                        "ipv4.method manual": "Static IP (CRITICAL - must set!)",
                        "ipv4.method auto": "DHCP",
                        "+ipv4.addresses": "Add secondary IP"
                    }
                },
                {
                    "name": "Set DNS Servers",
                    "syntax": "nmcli con mod <name> ipv4.dns '<dns1> <dns2>'",
                    "example": "nmcli con mod eth0 ipv4.dns '8.8.8.8 8.8.4.4'",
                    "flags": {
                        "ipv4.dns": "Space-separated DNS IPs (quoted)",
                        "+ipv4.dns": "Add DNS server to existing",
                        "-ipv4.dns": "Remove DNS server",
                        "ipv4.ignore-auto-dns yes": "Ignore DHCP-provided DNS"
                    }
                },
                {
                    "name": "Set Hostname",
                    "syntax": "hostnamectl set-hostname <hostname>",
                    "example": "hostnamectl set-hostname server1.example.com",
                    "flags": {
                        "set-hostname": "Set all hostname types (persistent)",
                        "status": "Show current hostname info",
                        "--static": "Set only static hostname",
                        "--transient": "Set only transient (temporary)",
                        "--pretty": "Set pretty/display hostname"
                    }
                },
                {
                    "name": "Activate/Deactivate Connection",
                    "syntax": "nmcli con up/down <name>",
                    "example": "nmcli con up eth0",
                    "flags": {
                        "con up <name>": "Activate connection profile",
                        "con down <name>": "Deactivate connection",
                        "con reload": "Reload all connection files",
                        "device connect <dev>": "Activate device with best profile",
                        "device disconnect <dev>": "Disconnect device"
                    }
                },
                {
                    "name": "Delete Connection",
                    "syntax": "nmcli con delete <name>",
                    "example": "nmcli con delete old-connection",
                    "flags": {
                        "con delete": "Remove connection profile permanently",
                        "con delete id <name>": "Delete by connection name"
                    }
                },
                {
                    "name": "Troubleshooting Commands",
                    "syntax": "ip addr / ip route / ss -tuln",
                    "example": "ip addr show eth0",
                    "flags": {
                        "ip addr": "Show IP addresses on all interfaces",
                        "ip addr show <dev>": "Show IP for specific device",
                        "ip route": "Show routing table",
                        "ip route show default": "Show default gateway",
                        "ss -tuln": "Show listening ports (TCP/UDP)",
                        "ping -c 3 <host>": "Test connectivity",
                        "nmcli -f all con show <name>": "Show all connection properties"
                    }
                },
                {
                    "name": "Network Teaming",
                    "syntax": "nmcli con add type team con-name <name> ifname <team> team.runner <mode>",
                    "example": "nmcli con add type team con-name team0 ifname team0 team.runner activebackup",
                    "flags": {
                        "type team": "Create team master interface",
                        "type team-slave": "Create team port/slave",
                        "team.runner": "Mode: activebackup, roundrobin, loadbalance, lacp",
                        "master <team>": "Assign slave to master team"
                    }
                }
            ],
            "common_mistakes": [
                "Forgetting ipv4.method manual (IP set but DHCP still used)",
                "Forgetting CIDR notation (/24) in IP address",
                "Not quoting DNS servers when space-separated",
                "Using 'nmcli device' to configure (use 'nmcli connection')",
                "Forgetting 'nmcli con up' to apply changes",
                "Confusing connection name with interface/device name",
                "Not checking 'nmcli con show' to verify config before activating"
            ],
            "exam_tricks": [
                "Always use nmcli, never edit config files directly on exam",
                "Connection names can be anything - don't assume they match interface",
                "'nmcli con mod' only saves config; 'nmcli con up' applies it",
                "Use 'nmcli con show <name>' to verify settings before activation",
                "If hostname must be FQDN, include domain (server.example.com)",
                "ip commands are temporary - reboot loses changes; nmcli persists",
                "Check 'nmcli device status' to see which connections are active"
            ]
        },

        "firewall": {
            "name": "Firewall Configuration",
            "explanation": """
RHEL uses firewalld for dynamic firewall management. Key concepts:

ZONES: Pre-defined security levels applied to interfaces
  - public: Default, untrusted networks (allows ssh, dhcpv6-client)
  - trusted: All traffic allowed
  - home/work/internal: More permissive than public
  - dmz: Limited access for DMZ servers
  - external: For NAT/masquerading
  - block: Reject all incoming (outgoing allowed)
  - drop: Drop all incoming silently

SERVICES vs PORTS:
  - Services: Named rules (http, https, ssh) - preferred method
  - Ports: Numeric (80/tcp, 443/tcp) - for custom apps

PERMANENT vs RUNTIME:
  - Without --permanent: Active now, lost on reload/reboot
  - With --permanent: Saved to config, needs --reload to apply
  - Best practice: Use --permanent then --reload
            """,
            "commands": [
                {
                    "name": "Zone Management",
                    "syntax": "firewall-cmd --get-zones / --get-default-zone / --set-default-zone=<zone>",
                    "example": "firewall-cmd --set-default-zone=trusted",
                    "flags": {
                        "--get-zones": "List all available zones",
                        "--get-default-zone": "Show current default zone",
                        "--set-default-zone=": "Change default zone (auto-permanent)",
                        "--get-active-zones": "Show zones with assigned interfaces",
                        "--zone=<zone> --list-all": "Show all settings for a zone"
                    }
                },
                {
                    "name": "Allow Service",
                    "syntax": "firewall-cmd --zone=<zone> --add-service=<service> --permanent",
                    "example": "firewall-cmd --add-service=http --permanent && firewall-cmd --reload",
                    "flags": {
                        "--add-service=": "Allow a service (http, https, ssh, nfs, etc.)",
                        "--remove-service=": "Remove a service",
                        "--list-services": "List allowed services",
                        "--get-services": "List all available service names",
                        "--permanent": "Make change persistent"
                    }
                },
                {
                    "name": "Allow Port",
                    "syntax": "firewall-cmd --zone=<zone> --add-port=<port>/<protocol> --permanent",
                    "example": "firewall-cmd --add-port=8080/tcp --permanent && firewall-cmd --reload",
                    "flags": {
                        "--add-port=": "Allow port (e.g., 8080/tcp, 53/udp)",
                        "--remove-port=": "Remove port rule",
                        "--list-ports": "List allowed ports",
                        "--permanent": "Make change persistent"
                    }
                },
                {
                    "name": "Rich Rules",
                    "syntax": "firewall-cmd --add-rich-rule='rule family=ipv4 source address=<ip> port port=<port> protocol=tcp accept'",
                    "example": "firewall-cmd --add-rich-rule='rule family=\"ipv4\" source address=\"192.168.1.0/24\" service name=\"http\" accept' --permanent",
                    "flags": {
                        "rule family=": "ipv4 or ipv6",
                        "source address=": "Source IP or network",
                        "port port=": "Destination port",
                        "protocol=": "tcp or udp",
                        "service name=": "Use service name instead of port",
                        "accept/reject/drop": "Action to take"
                    }
                },
                {
                    "name": "Reload & Status",
                    "syntax": "firewall-cmd --reload / systemctl status firewalld",
                    "example": "firewall-cmd --reload",
                    "flags": {
                        "--reload": "Apply permanent changes to runtime",
                        "--complete-reload": "Full reload (drops connections)",
                        "--state": "Check if firewalld is running",
                        "systemctl status firewalld": "Full service status"
                    }
                },
                {
                    "name": "Interface to Zone",
                    "syntax": "firewall-cmd --zone=<zone> --change-interface=<iface> --permanent",
                    "example": "firewall-cmd --zone=trusted --change-interface=eth1 --permanent",
                    "flags": {
                        "--change-interface=": "Move interface to zone",
                        "--add-interface=": "Add interface to zone",
                        "--remove-interface=": "Remove interface from zone",
                        "--get-zone-of-interface=": "Check which zone an interface is in"
                    }
                }
            ],
            "common_mistakes": [
                "Forgetting --permanent (changes lost on reload/reboot)",
                "Forgetting --reload after --permanent (changes not active)",
                "Using wrong zone (check --get-active-zones)",
                "Port format errors (must be port/protocol like 80/tcp)",
                "Rich rule quoting issues (use single quotes outside, escaped doubles inside)",
                "Firewalld not running (systemctl start firewalld)"
            ],
            "exam_tricks": [
                "Always use --permanent then --reload for persistent changes",
                "--set-default-zone is automatically permanent (no --reload needed)",
                "Prefer services over ports when available (--get-services to list)",
                "Rich rules for source IP restrictions (common exam question)",
                "Check firewalld is enabled: systemctl enable --now firewalld",
                "Verify with --list-all after making changes"
            ]
        },

        "filesystems": {
            "name": "File Systems & Mounting",
            "explanation": """
File system management includes creating filesystems, mounting them,
and configuring persistent mounts via /etc/fstab. RHEL 8/9 defaults
to XFS but also supports ext4. You must know mkfs commands, mount/umount,
UUID-based fstab entries, and mount options. The exam tests creating
filesystems on partitions or LVs and making mounts persistent.
            """,
            "commands": [
                {"name": "Create XFS Filesystem", "syntax": "mkfs.xfs <device>", "example": "mkfs.xfs /dev/vgdata/lvdata", "flags": {"mkfs.xfs": "Create XFS filesystem (RHEL default)", "-f": "Force overwrite existing filesystem", "-L": "Set filesystem label"}},
                {"name": "Create ext4 Filesystem", "syntax": "mkfs.ext4 <device>", "example": "mkfs.ext4 /dev/sdb1", "flags": {"mkfs.ext4": "Create ext4 filesystem", "-L": "Set filesystem label", "-m": "Reserved blocks percentage"}},
                {"name": "Mount Filesystem (Temporary)", "syntax": "mount <device> <mountpoint>", "example": "mount /dev/vgdata/lvdata /mnt/data", "flags": {"mount": "Mount filesystem now (not persistent)", "-t": "Specify filesystem type", "-o": "Mount options (ro, rw, noexec, etc.)", "umount": "Unmount filesystem"}},
                {"name": "Get UUID", "syntax": "blkid <device>", "example": "blkid /dev/vgdata/lvdata", "flags": {"blkid": "Show UUID and filesystem type", "-s UUID -o value": "Show only UUID", "lsblk -f": "Alternative to see UUIDs"}},
                {"name": "Add to fstab (Persistent)", "syntax": "echo 'UUID=<uuid> <mount> <type> defaults 0 0' >> /etc/fstab", "example": "echo 'UUID=abc123... /mnt/data xfs defaults 0 0' >> /etc/fstab; mount -a", "flags": {"UUID=": "Use UUID (preferred over device path)", "<mount>": "Mount point directory", "<type>": "Filesystem type (xfs, ext4)", "defaults": "Default mount options", "0 0": "Dump and fsck order", "mount -a": "Mount all fstab entries (test)"}}
            ],
            "common_mistakes": ["Using device path instead of UUID in fstab", "Mount point doesn't exist (must create with mkdir)", "Wrong filesystem type in fstab", "Not testing with 'mount -a' before reboot", "Typos in fstab can prevent boot"],
            "exam_tricks": ["Always use UUID in fstab, not /dev/sdX", "Create mount point directory first (mkdir)", "Test with 'mount -a' to verify fstab syntax", "XFS is default in RHEL 8/9 unless specified otherwise"]
        },

        "boot": {
            "name": "Boot Process, GRUB & Recovery",
            "explanation": """
The RHCSA exam heavily tests boot process knowledge including:
- Systemd targets (replacing runlevels)
- GRUB bootloader configuration
- Root password reset procedure (CRITICAL EXAM SKILL!)
- Boot troubleshooting and log analysis
- initramfs management with dracut

BOOT SEQUENCE:
  1. BIOS/UEFI → 2. GRUB2 → 3. Kernel + initramfs → 4. systemd → 5. Target

SYSTEMD TARGETS (vs Runlevels):
  poweroff.target    = runlevel 0 (halt)
  rescue.target      = runlevel 1 (single user)
  multi-user.target  = runlevel 3 (CLI, no GUI)
  graphical.target   = runlevel 5 (GUI)
  reboot.target      = runlevel 6 (reboot)
  emergency.target   = minimal shell (root fs read-only)

KEY FILES:
  /etc/default/grub          - GRUB configuration source
  /boot/grub2/grub.cfg       - Generated GRUB config (BIOS)
  /boot/efi/EFI/redhat/grub.cfg - Generated GRUB config (UEFI)
  /etc/fstab                 - Filesystem mount table
  /boot/initramfs-*.img      - Initial RAM filesystem

ROOT PASSWORD RESET PROCEDURE (MEMORIZE THIS!):
  1. Reboot system
  2. At GRUB menu, press 'e' to edit
  3. Find the 'linux' line, add 'rd.break' at the end
  4. Press Ctrl+X to boot
  5. mount -o remount,rw /sysroot
  6. chroot /sysroot
  7. passwd root
  8. touch /.autorelabel
  9. exit (twice)
  10. System reboots and relabels
            """,
            "commands": [
                {
                    "name": "Show/Set Default Target",
                    "syntax": "systemctl get-default / set-default <target>",
                    "example": "systemctl set-default multi-user.target",
                    "flags": {
                        "get-default": "Show current default boot target",
                        "set-default": "Set persistent default target",
                        "multi-user.target": "CLI mode (no GUI)",
                        "graphical.target": "GUI mode",
                        "rescue.target": "Single-user mode",
                        "emergency.target": "Minimal shell"
                    }
                },
                {
                    "name": "Switch Target Immediately",
                    "syntax": "systemctl isolate <target>",
                    "example": "systemctl isolate rescue.target",
                    "flags": {
                        "isolate": "Switch to target NOW (temporary)",
                        "Does NOT change default": "Reverts on reboot",
                        "rescue.target": "Enter rescue mode",
                        "emergency.target": "Enter emergency mode"
                    }
                },
                {
                    "name": "Modify GRUB Timeout",
                    "syntax": "Edit /etc/default/grub then grub2-mkconfig",
                    "example": "vi /etc/default/grub  # Set GRUB_TIMEOUT=5\ngrub2-mkconfig -o /boot/grub2/grub.cfg",
                    "flags": {
                        "GRUB_TIMEOUT": "Seconds to show menu (0 = instant boot)",
                        "GRUB_CMDLINE_LINUX": "Kernel parameters",
                        "grub2-mkconfig -o": "Regenerate GRUB config",
                        "/boot/grub2/grub.cfg": "BIOS systems",
                        "/boot/efi/EFI/redhat/grub.cfg": "UEFI systems"
                    }
                },
                {
                    "name": "Add/Remove Kernel Parameters",
                    "syntax": "Edit GRUB_CMDLINE_LINUX in /etc/default/grub",
                    "example": "GRUB_CMDLINE_LINUX=\"... quiet rhgb\"\ngrub2-mkconfig -o /boot/grub2/grub.cfg",
                    "flags": {
                        "quiet": "Suppress boot messages",
                        "rhgb": "Red Hat graphical boot",
                        "rd.break": "Break into emergency shell (password reset)",
                        "systemd.unit=rescue.target": "Boot to rescue",
                        "init=/bin/bash": "Boot to bash (alternative recovery)"
                    }
                },
                {
                    "name": "Analyze Boot Time",
                    "syntax": "systemd-analyze [blame|critical-chain]",
                    "example": "systemd-analyze blame | head -10",
                    "flags": {
                        "systemd-analyze": "Show total boot time",
                        "blame": "Show time per service (slowest first)",
                        "critical-chain": "Show critical path dependencies",
                        "plot > boot.svg": "Generate boot chart"
                    }
                },
                {
                    "name": "View Boot Logs",
                    "syntax": "journalctl -b [N] [-p priority]",
                    "example": "journalctl -b -p err",
                    "flags": {
                        "-b": "Current boot only",
                        "-b -1": "Previous boot",
                        "-b -2": "Two boots ago",
                        "--list-boots": "List all recorded boots",
                        "-p err": "Errors only",
                        "-p warning": "Warnings and above",
                        "-p err..warning": "Errors and warnings only"
                    }
                },
                {
                    "name": "Validate fstab Before Reboot",
                    "syntax": "findmnt --verify && mount -a",
                    "example": "findmnt --verify --verbose",
                    "flags": {
                        "findmnt --verify": "Check fstab syntax",
                        "--verbose": "Show detailed info",
                        "mount -a": "Try to mount all entries",
                        "CRITICAL": "Bad fstab = system won't boot!"
                    }
                },
                {
                    "name": "Rebuild initramfs",
                    "syntax": "dracut -f [path] [kernel-version]",
                    "example": "dracut -f",
                    "flags": {
                        "dracut -f": "Force rebuild for current kernel",
                        "dracut -f /boot/initramfs-$(uname -r).img": "Explicit path",
                        "lsinitrd": "List initramfs contents",
                        "When to rebuild": "After adding kernel modules"
                    }
                },
                {
                    "name": "List Boot Entries (grubby)",
                    "syntax": "grubby --info=ALL / --default-kernel",
                    "example": "grubby --info=ALL",
                    "flags": {
                        "--info=ALL": "Show all boot entries",
                        "--default-kernel": "Show default kernel path",
                        "--default-index": "Show default entry number",
                        "--set-default": "Set default kernel"
                    }
                },
                {
                    "name": "Schedule SELinux Relabel",
                    "syntax": "touch /.autorelabel",
                    "example": "touch /.autorelabel",
                    "flags": {
                        "/.autorelabel": "Triggers relabel on next boot",
                        "Required after": "Password reset, major changes",
                        "fixfiles -F onboot": "Alternative method",
                        "Takes time": "Can take 10+ minutes on large systems"
                    }
                },
                {
                    "name": "Chroot into System (Recovery)",
                    "syntax": "mount -o remount,rw /sysroot && chroot /sysroot",
                    "example": "mount -o remount,rw /sysroot\nchroot /sysroot\npasswd root\ntouch /.autorelabel\nexit",
                    "flags": {
                        "After rd.break": "You're in minimal environment",
                        "/sysroot": "The real root filesystem",
                        "remount,rw": "Make it writable",
                        "chroot": "Change root to /sysroot",
                        "exit twice": "First exits chroot, second continues boot"
                    }
                }
            ],
            "common_mistakes": [
                "Using 'isolate' when permanent change is needed (use set-default)",
                "Forgetting to run grub2-mkconfig after editing /etc/default/grub",
                "Wrong grub.cfg path (BIOS vs UEFI systems)",
                "Forgetting 'touch /.autorelabel' after password reset (SELinux blocks login!)",
                "Not testing fstab with 'mount -a' before reboot",
                "Typos in fstab can completely prevent boot",
                "Forgetting to remount /sysroot as read-write before chroot",
                "Exiting only once after chroot (need to exit twice)"
            ],
            "exam_tricks": [
                "ROOT PASSWORD RESET: rd.break → remount,rw → chroot → passwd → autorelabel → exit×2",
                "'Boot into X target' = systemctl set-default (permanent)",
                "'Switch to X target' = systemctl isolate (temporary)",
                "ALWAYS verify GRUB changes: grep GRUB_TIMEOUT /etc/default/grub",
                "ALWAYS run grub2-mkconfig after editing /etc/default/grub",
                "Check boot errors: journalctl -b -p err",
                "Find slow services: systemd-analyze blame | head",
                "Bad fstab = rescue mode needed. Use 'mount -o remount,rw /' to fix",
                "Emergency vs Rescue: Emergency = minimal, Rescue = more services",
                "UEFI path: /boot/efi/EFI/redhat/grub.cfg (not /boot/grub2/)"
            ]
        },

        "containers": {
            "name": "Container Management (Podman)",
            "explanation": """
Podman is the container engine in RHEL 8/9, compatible with Docker commands.
You must know how to run containers, manage images, configure port mapping,
set environment variables, and make containers persistent with systemd.
The exam tests basic podman commands: run, ps, images, exec, and creating
systemd unit files for rootless containers.
            """,
            "commands": [
                {"name": "Run Container", "syntax": "podman run -d --name <name> -p <host>:<container> <image>", "example": "podman run -d --name web -p 8080:80 nginx", "flags": {"-d": "Detached mode (background)", "--name": "Container name", "-p": "Port mapping (host:container)", "-e": "Environment variable", "-v": "Volume mount (host:container)"}},
                {"name": "List Containers", "syntax": "podman ps -a", "example": "podman ps -a", "flags": {"ps": "List running containers", "-a": "Show all (including stopped)", "ps -l": "Show latest container"}},
                {"name": "List Images", "syntax": "podman images", "example": "podman images", "flags": {"images": "List all local images", "pull <image>": "Download image", "rmi <image>": "Remove image"}},
                {"name": "Execute in Container", "syntax": "podman exec -it <container> <command>", "example": "podman exec -it web /bin/bash", "flags": {"exec": "Run command in running container", "-it": "Interactive terminal", "logs <container>": "View container logs"}},
                {"name": "Generate Systemd Unit", "syntax": "podman generate systemd --name <container> --files --new", "example": "podman generate systemd --name web --files --new", "flags": {"generate systemd": "Create systemd unit file", "--name": "Use container name", "--files": "Write to file", "--new": "Create new container on start", "systemctl --user": "User service (rootless)"}}
            ],
            "common_mistakes": ["Forgetting -d flag (container runs in foreground)", "Port already in use on host", "Not pulling image before running", "Wrong systemd path for user services", "Forgetting to enable systemd service"],
            "exam_tricks": ["Rootless containers use systemctl --user", "User systemd units go in ~/.config/systemd/user/", "Must enable AND start systemd service", "Container name must match in systemd commands"]
        },

        "essential_tools": {
            "name": "Essential Command-Line Tools (Files, Find, Tar)",
            "explanation": """
Essential tools include file operations, searching (find, grep),
archiving (tar), compression (gzip, bzip2, xz), and I/O redirection.
The exam tests your ability to efficiently search for files, create
and extract archives, and use links.

FILE TYPES IN LINUX:
  - (regular file)
  d (directory)
  l (symbolic link)
  b (block device)
  c (character device)
  s (socket)
  p (named pipe/FIFO)

HARD LINKS vs SYMBOLIC LINKS:
  Hard Link:
    - Points directly to inode (data blocks)
    - Cannot cross filesystems
    - Cannot link to directories
    - Survives if original deleted (same inode)
    - Same permissions as original

  Symbolic (Soft) Link:
    - Points to filename/path
    - CAN cross filesystems
    - CAN link to directories
    - Breaks if original deleted (dangling link)
    - lrwxrwxrwx permissions (always 777)

TAR COMPRESSION OPTIONS:
  z = gzip  (.tar.gz or .tgz)   - fastest, moderate compression
  j = bzip2 (.tar.bz2)          - slower, better compression
  J = xz    (.tar.xz)           - slowest, best compression
            """,
            "commands": [
                {
                    "name": "Find Files by Name",
                    "syntax": "find <path> -name '<pattern>'",
                    "example": "find /etc -name '*.conf'",
                    "flags": {
                        "-name": "Match filename (case-sensitive, use quotes!)",
                        "-iname": "Match filename (case-insensitive)",
                        "-type f": "Files only",
                        "-type d": "Directories only",
                        "-type l": "Symbolic links only"
                    }
                },
                {
                    "name": "Find Files by Owner/Group",
                    "syntax": "find <path> -user/-group <name>",
                    "example": "find /home -user alice",
                    "flags": {
                        "-user name": "Files owned by user",
                        "-group name": "Files owned by group",
                        "-uid N": "Files with specific UID",
                        "-gid N": "Files with specific GID",
                        "-nouser": "Files with no valid owner (orphaned)",
                        "-nogroup": "Files with no valid group"
                    }
                },
                {
                    "name": "Find Files by Permissions",
                    "syntax": "find <path> -perm <mode>",
                    "example": "find / -perm -4000 2>/dev/null",
                    "flags": {
                        "-perm 755": "Exact permissions (exactly 755)",
                        "-perm -755": "At least these permissions (755 or more)",
                        "-perm /222": "Any of these permissions (u OR g OR o write)",
                        "-perm -4000": "Find SUID files",
                        "-perm -2000": "Find SGID files",
                        "-perm -1000": "Find sticky bit files"
                    }
                },
                {
                    "name": "Find Files by Size/Time",
                    "syntax": "find <path> -size/-mtime <value>",
                    "example": "find /var -size +100M -mtime -7",
                    "flags": {
                        "-size +100M": "Larger than 100MB",
                        "-size -10k": "Smaller than 10KB",
                        "-size 50M": "Exactly 50MB",
                        "-mtime -7": "Modified in last 7 days",
                        "-mtime +30": "Modified more than 30 days ago",
                        "-mmin -60": "Modified in last 60 minutes",
                        "-newer file": "Newer than reference file"
                    }
                },
                {
                    "name": "Find and Execute",
                    "syntax": "find <path> <criteria> -exec <cmd> {} \\;",
                    "example": "find /tmp -name '*.tmp' -exec rm {} \\;",
                    "flags": {
                        "-exec cmd {} \\;": "Run cmd for each file (one at a time)",
                        "-exec cmd {} +": "Run cmd with all files at once (faster)",
                        "-ok cmd {} \\;": "Like -exec but prompts for confirmation",
                        "-delete": "Delete matching files (careful!)",
                        "{}": "Placeholder for found filename"
                    }
                },
                {
                    "name": "Search Text with Grep",
                    "syntax": "grep [OPTIONS] '<pattern>' <file>",
                    "example": "grep -i 'error' /var/log/messages",
                    "flags": {
                        "-i": "Case-insensitive search",
                        "-r": "Recursive search in directories",
                        "-n": "Show line numbers",
                        "-c": "Count matching lines",
                        "-v": "Invert match (lines NOT containing)",
                        "-l": "List filenames only (not content)",
                        "-w": "Match whole words only",
                        "-E": "Extended regex (egrep)",
                        "-A N": "Show N lines after match",
                        "-B N": "Show N lines before match"
                    }
                },
                {
                    "name": "Create Hard Link",
                    "syntax": "ln <target> <linkname>",
                    "example": "ln /data/file.txt /data/file_hardlink.txt",
                    "flags": {
                        "ln target link": "Create hard link to file",
                        "Same inode": "Hard links share same inode number",
                        "Cannot cross FS": "Must be on same filesystem",
                        "No directories": "Cannot hard link directories"
                    }
                },
                {
                    "name": "Create Symbolic Link",
                    "syntax": "ln -s <target> <linkname>",
                    "example": "ln -s /var/log /home/user/logs",
                    "flags": {
                        "-s": "Create symbolic (soft) link",
                        "Can cross FS": "Can link across filesystems",
                        "Can link dirs": "Can create symlinks to directories",
                        "ls -l": "Shows link target: link -> target"
                    }
                },
                {
                    "name": "Copy Files",
                    "syntax": "cp [OPTIONS] <source> <dest>",
                    "example": "cp -a /etc /backup/etc_backup",
                    "flags": {
                        "-r": "Recursive (copy directories)",
                        "-a": "Archive (preserve all: permissions, ownership, timestamps)",
                        "-p": "Preserve permissions and timestamps",
                        "-v": "Verbose (show progress)",
                        "-i": "Interactive (prompt before overwrite)",
                        "-u": "Update (only if source is newer)"
                    }
                },
                {
                    "name": "Create Tar Archive",
                    "syntax": "tar -cvf <archive.tar> <files>",
                    "example": "tar -czvf backup.tar.gz /etc /home",
                    "flags": {
                        "-c": "Create archive",
                        "-v": "Verbose (list files)",
                        "-f": "Specify archive filename (must be last before filename!)",
                        "-z": "Compress with gzip (.tar.gz)",
                        "-j": "Compress with bzip2 (.tar.bz2)",
                        "-J": "Compress with xz (.tar.xz)",
                        "-p": "Preserve permissions",
                        "--exclude='*.log'": "Exclude files matching pattern"
                    }
                },
                {
                    "name": "Extract Tar Archive",
                    "syntax": "tar -xvf <archive.tar> [-C <dir>]",
                    "example": "tar -xzvf backup.tar.gz -C /restore",
                    "flags": {
                        "-x": "Extract archive",
                        "-v": "Verbose",
                        "-f": "Specify archive filename",
                        "-C": "Change to directory before extracting",
                        "-z/-j/-J": "Specify compression (optional, auto-detected)",
                        "--strip-components=N": "Strip N leading directories"
                    }
                },
                {
                    "name": "List Tar Contents",
                    "syntax": "tar -tvf <archive.tar>",
                    "example": "tar -tzvf backup.tar.gz",
                    "flags": {
                        "-t": "List contents (don't extract)",
                        "-v": "Verbose (show permissions, owner, size)",
                        "-f": "Specify archive filename"
                    }
                },
                {
                    "name": "I/O Redirection",
                    "syntax": "command > file / command >> file",
                    "example": "find /etc -name '*.conf' > configs.txt 2>&1",
                    "flags": {
                        ">": "Redirect stdout to file (overwrite)",
                        ">>": "Redirect stdout to file (append)",
                        "2>": "Redirect stderr to file",
                        "2>&1": "Redirect stderr to stdout",
                        "&>": "Redirect both stdout and stderr",
                        "|": "Pipe output to another command",
                        "< file": "Read input from file"
                    }
                }
            ],
            "common_mistakes": [
                "Wrong tar flag order - f must be last before filename",
                "Forgetting quotes in find -name pattern (shell expansion)",
                "Using find -perm 755 when you mean -perm -755 (exact vs minimum)",
                "Creating symlink with relative path (breaks if you move it)",
                "tar -czf backup.tar (forgetting .gz extension with -z)",
                "Extracting tar without -C (extracts to current directory)",
                "Hard linking directories (not allowed)",
                "Forgetting 2>/dev/null to suppress find permission errors"
            ],
            "exam_tricks": [
                "Find SUID files: find / -perm -4000 2>/dev/null",
                "Find SGID files: find / -perm -2000 2>/dev/null",
                "Find files by permission mode: -perm for exact, -perm - for minimum",
                "tar auto-detects compression on extract (no need for -z/-j/-J)",
                "Hard link = same inode, symlink = different inode (check with ls -i)",
                "Find orphaned files: find / -nouser -o -nogroup",
                "Copy preserving everything: cp -a (same as cp -dR --preserve=all)",
                "Remember: -z=gzip, -j=bzip2, -J=xz (lowercase=less compression)"
            ]
        },

        "processes": {
            "name": "Process Management",
            "explanation": """
Process management includes viewing processes, killing processes,
changing priorities, and managing jobs. You must know ps, top, kill,
nice/renice commands.
            """,
            "commands": [
                {"name": "List Processes", "syntax": "ps aux", "example": "ps aux | grep httpd", "flags": {"aux": "All processes"}},
                {"name": "Kill Process", "syntax": "kill <PID>", "example": "kill 1234", "flags": {"kill": "SIGTERM", "-9": "Force"}},
                {"name": "Change Priority", "syntax": "nice -n <value> <command>", "example": "nice -n 10 backup.sh", "flags": {"-n": "Nice value (-20 to 19)"}}
            ],
            "common_mistakes": ["Using kill -9 first", "Confusing nice values"],
            "exam_tricks": ["Find PID: pgrep or pidof", "Nice: -20 = high, 19 = low"]
        },

        "scheduling": {
            "name": "Task Scheduling (cron & at)",
            "explanation": """
Task scheduling uses cron for recurring jobs and at for one-time jobs.
You must know crontab syntax (minute hour day month weekday).
            """,
            "commands": [
                {"name": "Edit Crontab", "syntax": "crontab -e -u <user>", "example": "crontab -e -u alice", "flags": {"-e": "Edit", "-l": "List"}},
                {"name": "Crontab Syntax", "syntax": "MIN HOUR DAY MONTH WEEKDAY COMMAND", "example": "30 2 * * * /usr/local/bin/backup.sh", "flags": {"*": "Every", "*/N": "Every N"}},
                {"name": "One-Time Task", "syntax": "at <time>", "example": "echo '/usr/bin/report.sh' | at 22:00", "flags": {"at": "Schedule once", "atq": "List jobs"}}
            ],
            "common_mistakes": ["Wrong field order", "Forgetting absolute paths"],
            "exam_tricks": ["Crontab: MIN HOUR DAY MONTH WEEKDAY", "0 2 * * * = 2 AM daily"]
        },

        "scripting": {
            "name": "Shell Scripting (Bash)",
            "explanation": """
Shell scripting is essential for automating tasks in Linux. The RHCSA exam
tests your ability to write basic bash scripts with conditionals, loops,
command-line arguments, and proper exit codes.

SCRIPT STRUCTURE:
  #!/bin/bash          - Shebang (interpreter directive)
  # Comments           - Explain your code
  commands             - Script body
  exit 0               - Exit with success status

VARIABLES:
  name="value"         - Assignment (NO spaces around =)
  $name or ${name}     - Variable expansion
  "$name"              - Quoted expansion (preserves spaces)
  $1, $2, ...          - Positional parameters (arguments)
  $#                   - Number of arguments
  $@                   - All arguments as separate words
  $*                   - All arguments as single word
  $?                   - Exit status of last command
  $$                   - Current script's PID

EXIT CODES:
  0                    - Success
  1-255                - Various error conditions
  exit N               - Exit with specific code
            """,
            "commands": [
                {
                    "name": "Basic Script Structure",
                    "syntax": "#!/bin/bash\\n# Description\\ncommands\\nexit 0",
                    "example": "#!/bin/bash\\necho 'Hello World'\\nexit 0",
                    "flags": {
                        "#!/bin/bash": "Shebang - specifies interpreter",
                        "chmod +x": "Make script executable",
                        "./script.sh": "Execute script",
                        "bash script.sh": "Run with bash explicitly"
                    }
                },
                {
                    "name": "Conditionals (if/else)",
                    "syntax": "if [ condition ]; then\\n  commands\\nfi",
                    "example": "if [ -f /etc/passwd ]; then\\n  echo 'File exists'\\nfi",
                    "flags": {
                        "[ ]": "Test command (spaces required!)",
                        "[[ ]]": "Extended test (bash-specific)",
                        "-f file": "File exists and is regular file",
                        "-d dir": "Directory exists",
                        "-e path": "Path exists (file or dir)",
                        "-r/-w/-x": "Readable/writable/executable",
                        "-z string": "String is empty",
                        "-n string": "String is not empty",
                        "str1 = str2": "Strings are equal",
                        "-eq/-ne/-lt/-gt/-le/-ge": "Numeric comparisons"
                    }
                },
                {
                    "name": "Loops (for)",
                    "syntax": "for var in list; do\\n  commands\\ndone",
                    "example": "for file in /etc/*.conf; do\\n  echo $file\\ndone",
                    "flags": {
                        "for i in 1 2 3": "Iterate over list",
                        "for i in {1..10}": "Brace expansion range",
                        "for i in $(seq 1 10)": "Command substitution",
                        "for file in *.txt": "Glob patterns",
                        "for arg in \"$@\"": "Iterate over arguments"
                    }
                },
                {
                    "name": "Loops (while)",
                    "syntax": "while [ condition ]; do\\n  commands\\ndone",
                    "example": "count=1\\nwhile [ $count -le 5 ]; do\\n  echo $count\\n  ((count++))\\ndone",
                    "flags": {
                        "while true": "Infinite loop",
                        "while read line": "Read file line by line",
                        "break": "Exit loop immediately",
                        "continue": "Skip to next iteration"
                    }
                },
                {
                    "name": "Command-Line Arguments",
                    "syntax": "$1, $2, $#, $@",
                    "example": "#!/bin/bash\\necho \"Script: $0\"\\necho \"First arg: $1\"\\necho \"All args: $@\"\\necho \"Count: $#\"",
                    "flags": {
                        "$0": "Script name",
                        "$1, $2, ...": "Positional arguments",
                        "$#": "Number of arguments",
                        "$@": "All arguments (preserves quoting)",
                        "$*": "All arguments (single string)",
                        "shift": "Shift arguments left"
                    }
                },
                {
                    "name": "Exit Codes",
                    "syntax": "exit N",
                    "example": "if [ ! -f \"$1\" ]; then\\n  echo 'File not found'\\n  exit 1\\nfi\\nexit 0",
                    "flags": {
                        "exit 0": "Success",
                        "exit 1": "General error",
                        "$?": "Check last exit code",
                        "command && echo 'ok'": "Run if success",
                        "command || echo 'failed'": "Run if failure"
                    }
                },
                {
                    "name": "Command Substitution",
                    "syntax": "$(command) or `command`",
                    "example": "today=$(date +%Y-%m-%d)\\nfiles=$(ls -1 | wc -l)",
                    "flags": {
                        "$(command)": "Preferred syntax",
                        "`command`": "Legacy syntax (avoid)",
                        "Nesting": "$(cmd1 $(cmd2)) works with $()"
                    }
                }
            ],
            "common_mistakes": [
                "Missing spaces in [ ] test: [ $a -eq 1 ] not [$a -eq 1]",
                "Using = for numeric comparison (use -eq instead)",
                "Forgetting quotes around variables with spaces",
                "Missing shebang line (#!/bin/bash)",
                "Script not executable (chmod +x needed)",
                "Spaces around = in assignment: var=value not var = value",
                "Using single [ ] with && or || (use [[ ]] instead)",
                "Forgetting 'then' after if condition"
            ],
            "exam_tricks": [
                "Always start with #!/bin/bash shebang",
                "Always chmod +x your script",
                "Test conditions: -f for files, -d for directories",
                "Use \"$@\" (quoted) to preserve argument spacing",
                "Exit 0 for success, non-zero for errors",
                "Use $? to check if previous command succeeded",
                "bash -n script.sh to check syntax without running"
            ]
        },

        "packages": {
            "name": "Package Management (dnf/rpm)",
            "explanation": """
Package management in RHEL 8/9 uses DNF (Dandified YUM) as the primary tool.
RPM is the underlying package format. You must know how to install, remove,
query packages, manage repositories, and work with module streams.

KEY CONCEPTS:
  Package: Software bundled with metadata (name-version-release.arch.rpm)
  Repository: Collection of packages with metadata
  Module Stream: Version stream of related packages (e.g., nodejs:18, php:8.1)
  Group: Collection of packages installed together (e.g., "Development Tools")

IMPORTANT DIRECTORIES:
  /etc/yum.repos.d/       - Repository configuration files
  /var/cache/dnf/         - Package cache
  /var/log/dnf.log        - DNF transaction log
            """,
            "commands": [
                {
                    "name": "Install Package",
                    "syntax": "dnf install <package>",
                    "example": "dnf install httpd vim-enhanced",
                    "flags": {
                        "install": "Install package(s)",
                        "-y": "Assume yes to prompts",
                        "--downloadonly": "Download without installing",
                        "reinstall": "Reinstall package"
                    }
                },
                {
                    "name": "Remove Package",
                    "syntax": "dnf remove <package>",
                    "example": "dnf remove httpd",
                    "flags": {
                        "remove": "Remove package and unused deps",
                        "autoremove": "Remove orphaned dependencies",
                        "-y": "Assume yes"
                    }
                },
                {
                    "name": "Search Packages",
                    "syntax": "dnf search <keyword>",
                    "example": "dnf search web server",
                    "flags": {
                        "search": "Search package names and descriptions",
                        "provides": "Find which package provides a file",
                        "info": "Show package details"
                    }
                },
                {
                    "name": "Query Installed (RPM)",
                    "syntax": "rpm -q <package>",
                    "example": "rpm -qa | grep httpd",
                    "flags": {
                        "-q": "Query package",
                        "-qa": "Query all installed",
                        "-qi": "Query info",
                        "-ql": "Query file list",
                        "-qf /path/file": "Which package owns file",
                        "-qc": "Query config files",
                        "-qd": "Query documentation files"
                    }
                },
                {
                    "name": "Repository Management",
                    "syntax": "dnf repolist / dnf config-manager",
                    "example": "dnf config-manager --enable powertools",
                    "flags": {
                        "repolist": "List enabled repos",
                        "repolist all": "List all repos",
                        "repoinfo": "Show repo details",
                        "--enable": "Enable repository",
                        "--disable": "Disable repository"
                    }
                },
                {
                    "name": "Package Groups",
                    "syntax": "dnf group install '<group>'",
                    "example": "dnf group install 'Development Tools'",
                    "flags": {
                        "group list": "List available groups",
                        "group install": "Install group",
                        "group remove": "Remove group",
                        "group info": "Show group contents"
                    }
                },
                {
                    "name": "Module Streams",
                    "syntax": "dnf module list/enable/install",
                    "example": "dnf module enable nodejs:18\\ndnf module install nodejs:18",
                    "flags": {
                        "module list": "List available modules",
                        "module enable": "Enable stream",
                        "module disable": "Disable module",
                        "module install": "Install module profile",
                        "module reset": "Reset module state"
                    }
                },
                {
                    "name": "Transaction History",
                    "syntax": "dnf history",
                    "example": "dnf history\\ndnf history undo 15",
                    "flags": {
                        "history": "List transactions",
                        "history info N": "Show transaction details",
                        "history undo N": "Undo transaction",
                        "history redo N": "Redo transaction"
                    }
                }
            ],
            "common_mistakes": [
                "Using yum instead of dnf (works but dnf is preferred)",
                "Forgetting -y flag in scripts",
                "Not enabling required repository",
                "Wrong module stream syntax (use name:stream format)",
                "Forgetting to run 'module enable' before 'module install'"
            ],
            "exam_tricks": [
                "rpm -qf /path/to/file - find which package owns a file",
                "dnf provides /path/to/file - find package that provides file",
                "Module streams: enable first, then install",
                "Group names often need quotes: 'Development Tools'",
                "Check dnf history if something breaks - you can undo"
            ]
        },

        "time_services": {
            "name": "Time Services (Chrony/NTP)",
            "explanation": """
Time synchronization is critical for logging, authentication, and distributed
systems. RHEL 8/9 uses chrony as the default NTP implementation.

KEY CONCEPTS:
  NTP: Network Time Protocol - synchronizes clocks
  Chrony: Modern NTP implementation (replaced ntpd)
  Timezone: Geographic time offset from UTC
  Hardware Clock (RTC): System's hardware clock
  System Clock: OS-maintained time

KEY FILES:
  /etc/chrony.conf        - Chrony configuration
  /etc/localtime          - Symlink to timezone file
  /usr/share/zoneinfo/    - Timezone database

CHRONY TERMS:
  server: Single NTP time source
  pool: Multiple NTP servers (load balanced)
  iburst: Fast initial synchronization
  stratum: Distance from reference clock (1=atomic, 2=synced to 1, etc.)
            """,
            "commands": [
                {
                    "name": "Set Timezone",
                    "syntax": "timedatectl set-timezone <zone>",
                    "example": "timedatectl set-timezone America/New_York",
                    "flags": {
                        "set-timezone": "Set system timezone",
                        "list-timezones": "List available timezones",
                        "timedatectl": "Show current settings"
                    }
                },
                {
                    "name": "Enable NTP Sync",
                    "syntax": "timedatectl set-ntp true",
                    "example": "timedatectl set-ntp true",
                    "flags": {
                        "set-ntp true": "Enable NTP synchronization",
                        "set-ntp false": "Disable NTP (for manual time)",
                        "Requires": "chronyd or ntpd service running"
                    }
                },
                {
                    "name": "Configure Chrony",
                    "syntax": "Edit /etc/chrony.conf",
                    "example": "server time.example.com iburst\\npool pool.ntp.org iburst",
                    "flags": {
                        "server <host>": "Add NTP server",
                        "pool <host>": "Add NTP pool",
                        "iburst": "Fast initial sync",
                        "prefer": "Prefer this source"
                    }
                },
                {
                    "name": "Check Chrony Status",
                    "syntax": "chronyc sources / tracking",
                    "example": "chronyc sources -v",
                    "flags": {
                        "sources": "Show NTP sources",
                        "sources -v": "Verbose source info",
                        "tracking": "Show sync status",
                        "activity": "Show server activity"
                    }
                },
                {
                    "name": "Manage Chrony Service",
                    "syntax": "systemctl enable --now chronyd",
                    "example": "systemctl enable --now chronyd",
                    "flags": {
                        "enable --now": "Enable and start",
                        "restart chronyd": "Apply config changes",
                        "status chronyd": "Check service status"
                    }
                },
                {
                    "name": "Set Time Manually",
                    "syntax": "timedatectl set-time 'YYYY-MM-DD HH:MM:SS'",
                    "example": "timedatectl set-ntp false\\ntimedatectl set-time '2025-06-15 14:30:00'",
                    "flags": {
                        "set-time": "Set date and time",
                        "Requires": "NTP must be disabled first",
                        "Format": "YYYY-MM-DD HH:MM:SS"
                    }
                }
            ],
            "common_mistakes": [
                "Forgetting to restart chronyd after config changes",
                "Not enabling chronyd service (not persistent)",
                "Trying to set time with NTP enabled (must disable first)",
                "Wrong timezone format (use timedatectl list-timezones)",
                "Forgetting iburst option (slow initial sync)"
            ],
            "exam_tricks": [
                "Always use iburst for faster initial sync",
                "timedatectl shows everything: timezone, NTP, sync status",
                "chronyc sources shows * for selected source",
                "After editing /etc/chrony.conf, restart chronyd",
                "Timezone is persistent automatically"
            ]
        },

        "partitioning": {
            "name": "Disk Partitioning (fdisk/parted)",
            "explanation": """
Disk partitioning creates separate regions on storage devices. RHEL supports
MBR (Master Boot Record) and GPT (GUID Partition Table) schemes.

MBR vs GPT:
  MBR (msdos):
    - Up to 4 primary partitions (or 3 primary + 1 extended)
    - Maximum disk size: 2TB
    - Legacy BIOS boot

  GPT (GUID):
    - Up to 128 partitions
    - Maximum disk size: 9.4 ZB (practically unlimited)
    - Required for UEFI boot
    - Includes backup partition table

PARTITION TYPES:
  Linux filesystem (83/8300): Standard Linux partitions
  Linux LVM (8e/8e00): For LVM physical volumes
  Linux swap (82/8200): Swap partitions
  EFI System (ef00): EFI boot partitions

TOOLS:
  fdisk: Interactive MBR/GPT partitioning
  parted: Scriptable MBR/GPT partitioning
  gdisk: GPT-specific tool
  partprobe: Update kernel partition table
            """,
            "commands": [
                {
                    "name": "View Partition Table",
                    "syntax": "fdisk -l <device> / parted <device> print",
                    "example": "fdisk -l /dev/sdb\\nparted /dev/sdb print",
                    "flags": {
                        "fdisk -l": "List partitions (all or specific disk)",
                        "parted print": "Show partition table",
                        "lsblk": "Tree view of block devices"
                    }
                },
                {
                    "name": "Create Partition (fdisk)",
                    "syntax": "fdisk <device>",
                    "example": "fdisk /dev/sdb\\n  n (new)\\n  p (primary)\\n  1 (number)\\n  <enter> (default start)\\n  +500M (size)\\n  w (write)",
                    "flags": {
                        "n": "New partition",
                        "p": "Primary partition",
                        "e": "Extended partition",
                        "t": "Change partition type",
                        "d": "Delete partition",
                        "w": "Write changes and exit",
                        "q": "Quit without saving"
                    }
                },
                {
                    "name": "Create Partition (parted)",
                    "syntax": "parted <device> mkpart <type> <fstype> <start> <end>",
                    "example": "parted /dev/sdb mkpart primary ext4 0% 500MiB",
                    "flags": {
                        "mklabel gpt/msdos": "Create partition table",
                        "mkpart": "Create partition",
                        "rm N": "Remove partition N",
                        "print": "Show partitions",
                        "set N lvm on": "Set LVM flag"
                    }
                },
                {
                    "name": "Create GPT Label",
                    "syntax": "parted <device> mklabel gpt",
                    "example": "parted /dev/sdb mklabel gpt\\nparted /dev/sdb mkpart data ext4 0% 100%",
                    "flags": {
                        "mklabel gpt": "Create GPT partition table",
                        "mklabel msdos": "Create MBR partition table",
                        "WARNING": "Destroys all existing partitions!"
                    }
                },
                {
                    "name": "Set LVM Type",
                    "syntax": "fdisk: t, 8e / parted: set N lvm on",
                    "example": "parted /dev/sdb set 1 lvm on",
                    "flags": {
                        "fdisk t, 8e": "Set type to Linux LVM",
                        "parted set N lvm on": "Enable LVM flag",
                        "Required for": "LVM physical volumes"
                    }
                },
                {
                    "name": "Update Kernel",
                    "syntax": "partprobe <device>",
                    "example": "partprobe /dev/sdb",
                    "flags": {
                        "partprobe": "Inform kernel of partition changes",
                        "Without device": "Scans all disks",
                        "Required after": "Creating/deleting partitions"
                    }
                }
            ],
            "common_mistakes": [
                "Forgetting to run partprobe after changes",
                "Wrong partition type for LVM (must be 8e)",
                "Creating MBR when GPT is needed (>2TB disk)",
                "Forgetting to write changes in fdisk (w command)",
                "Partition table type mismatch with boot mode (UEFI needs GPT)"
            ],
            "exam_tricks": [
                "parted is scriptable: parted -s /dev/sdb mkpart ...",
                "For LVM: create partition, set type to 8e, then pvcreate",
                "partprobe updates kernel without reboot",
                "GPT allows more partitions and larger disks",
                "Check with lsblk after partitioning"
            ]
        },

        "ssh": {
            "name": "SSH Configuration",
            "explanation": """
SSH (Secure Shell) provides encrypted remote access. The RHCSA tests key-based
authentication, SSH client configuration, and basic SSH server security.

KEY CONCEPTS:
  Key-based auth: More secure than passwords
  Public key: Shared with remote servers (~/.ssh/id_*.pub)
  Private key: Kept secret (~/.ssh/id_*)
  authorized_keys: Lists public keys allowed to connect

KEY FILES:
  ~/.ssh/id_rsa           - Private key (RSA)
  ~/.ssh/id_ed25519       - Private key (Ed25519)
  ~/.ssh/*.pub            - Public keys
  ~/.ssh/authorized_keys  - Accepted public keys
  ~/.ssh/config           - Client configuration
  /etc/ssh/sshd_config    - Server configuration

PERMISSIONS (Critical!):
  ~/.ssh/                 - 700 (drwx------)
  ~/.ssh/id_*             - 600 (-rw-------)
  ~/.ssh/*.pub            - 644 (-rw-r--r--)
  ~/.ssh/authorized_keys  - 600 (-rw-------)
            """,
            "commands": [
                {
                    "name": "Generate SSH Key",
                    "syntax": "ssh-keygen -t <type> [-f <path>] [-N '<passphrase>']",
                    "example": "ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N ''",
                    "flags": {
                        "-t rsa": "RSA key (traditional)",
                        "-t ed25519": "Ed25519 key (modern, preferred)",
                        "-f path": "Output file path",
                        "-N ''": "Empty passphrase (for automation)",
                        "-b 4096": "Key size (RSA only)"
                    }
                },
                {
                    "name": "Copy Key to Server",
                    "syntax": "ssh-copy-id [-i <key>] <user>@<host>",
                    "example": "ssh-copy-id -i ~/.ssh/id_ed25519.pub user@server",
                    "flags": {
                        "ssh-copy-id": "Copy public key to remote",
                        "-i": "Specify key file",
                        "Adds to": "~/.ssh/authorized_keys on remote"
                    }
                },
                {
                    "name": "Manual Key Copy",
                    "syntax": "cat ~/.ssh/id_*.pub >> ~/.ssh/authorized_keys",
                    "example": "mkdir -p ~/.ssh\\nchmod 700 ~/.ssh\\ncat /tmp/key.pub >> ~/.ssh/authorized_keys\\nchmod 600 ~/.ssh/authorized_keys",
                    "flags": {
                        "mkdir -p ~/.ssh": "Create directory",
                        "chmod 700": "Directory permissions",
                        "chmod 600": "Key file permissions",
                        "chown user:user": "Fix ownership"
                    }
                },
                {
                    "name": "SSH Client Config",
                    "syntax": "~/.ssh/config",
                    "example": "Host webserver\\n    HostName server1.example.com\\n    User admin\\n    IdentityFile ~/.ssh/id_ed25519",
                    "flags": {
                        "Host <alias>": "Connection alias",
                        "HostName": "Actual hostname/IP",
                        "User": "Remote username",
                        "IdentityFile": "Private key to use",
                        "Port": "SSH port (default 22)"
                    }
                },
                {
                    "name": "Secure SSHD",
                    "syntax": "Edit /etc/ssh/sshd_config",
                    "example": "PermitRootLogin no\\nPasswordAuthentication no",
                    "flags": {
                        "PermitRootLogin no": "Disable root SSH login",
                        "PasswordAuthentication no": "Require key-based auth",
                        "Port 2222": "Change SSH port",
                        "AllowUsers user1 user2": "Whitelist users"
                    }
                },
                {
                    "name": "Restart SSHD",
                    "syntax": "systemctl restart sshd",
                    "example": "systemctl restart sshd",
                    "flags": {
                        "restart": "Apply config changes",
                        "reload": "Reload without disconnect",
                        "status": "Check service status"
                    }
                }
            ],
            "common_mistakes": [
                "Wrong permissions on .ssh directory (must be 700)",
                "Wrong permissions on private key (must be 600)",
                "Copying private key instead of public key",
                "Not restarting sshd after config changes",
                "Locking yourself out by disabling password before setting up keys"
            ],
            "exam_tricks": [
                "ed25519 is modern and preferred over RSA",
                "-N '' sets empty passphrase (no prompt)",
                "ssh-copy-id is easiest way to deploy keys",
                "Test SSH access before disabling password auth!",
                "chmod 600 for private keys, 644 for public keys"
            ]
        },

        "storage": {
            "name": "Advanced Storage (RAID/Stratis)",
            "explanation": """
Advanced storage includes RAID arrays for redundancy and Stratis for
modern storage management. RAID provides fault tolerance, while Stratis
offers easy-to-use pooled storage with snapshots.

RAID LEVELS:
  RAID 0: Striping (no redundancy, max performance)
  RAID 1: Mirroring (2+ disks, 50% capacity)
  RAID 5: Striping with parity (3+ disks, n-1 capacity)
  RAID 6: Dual parity (4+ disks, n-2 capacity)
  RAID 10: Mirrored stripes (4+ disks, 50% capacity)

STRATIS CONCEPTS:
  Pool: Collection of block devices
  Filesystem: XFS filesystems on pools
  Snapshots: Point-in-time copies

KEY FILES:
  /etc/mdadm.conf         - RAID configuration
  /proc/mdstat            - RAID status
  /dev/md*                - RAID devices
  /dev/stratis/<pool>/<fs> - Stratis filesystems
            """,
            "commands": [
                {
                    "name": "Create RAID Array",
                    "syntax": "mdadm --create /dev/md0 --level=N --raid-devices=N <devices>",
                    "example": "mdadm --create /dev/md0 --level=1 --raid-devices=2 /dev/sdb1 /dev/sdc1",
                    "flags": {
                        "--create": "Create new array",
                        "--level": "RAID level (0,1,5,6,10)",
                        "--raid-devices": "Number of devices",
                        "--spare-devices": "Number of spares"
                    }
                },
                {
                    "name": "Check RAID Status",
                    "syntax": "cat /proc/mdstat / mdadm --detail /dev/md0",
                    "example": "mdadm --detail /dev/md0",
                    "flags": {
                        "/proc/mdstat": "Quick status overview",
                        "--detail": "Detailed array info",
                        "--examine": "Examine device superblock"
                    }
                },
                {
                    "name": "Save RAID Config",
                    "syntax": "mdadm --detail --scan >> /etc/mdadm.conf",
                    "example": "mdadm --detail --scan >> /etc/mdadm.conf\\ndracut -f",
                    "flags": {
                        "--detail --scan": "Generate config line",
                        "/etc/mdadm.conf": "Persistent config",
                        "dracut -f": "Rebuild initramfs"
                    }
                },
                {
                    "name": "Stop/Remove RAID",
                    "syntax": "mdadm --stop /dev/md0",
                    "example": "umount /mnt/raid\\nmdadm --stop /dev/md0\\nmdadm --zero-superblock /dev/sdb1 /dev/sdc1",
                    "flags": {
                        "--stop": "Stop array",
                        "--zero-superblock": "Clear RAID metadata",
                        "Unmount first": "Must unmount before stop"
                    }
                },
                {
                    "name": "Create Stratis Pool",
                    "syntax": "stratis pool create <poolname> <devices>",
                    "example": "stratis pool create datapool /dev/sdb /dev/sdc",
                    "flags": {
                        "pool create": "Create storage pool",
                        "pool list": "List pools",
                        "pool add-data": "Add devices to pool"
                    }
                },
                {
                    "name": "Create Stratis Filesystem",
                    "syntax": "stratis filesystem create <pool> <fsname>",
                    "example": "stratis filesystem create datapool data1\\nmount /dev/stratis/datapool/data1 /mnt",
                    "flags": {
                        "filesystem create": "Create filesystem on pool",
                        "filesystem list": "List filesystems",
                        "filesystem snapshot": "Create snapshot"
                    }
                }
            ],
            "common_mistakes": [
                "Not saving RAID config to /etc/mdadm.conf (lost on reboot)",
                "Forgetting to rebuild initramfs after RAID config",
                "Not enabling stratisd service",
                "Wrong mount options for Stratis in fstab",
                "Forgetting to unmount before stopping RAID"
            ],
            "exam_tricks": [
                "RAID 1 requires 2+ devices, RAID 5 requires 3+",
                "Save RAID config: mdadm --detail --scan >> /etc/mdadm.conf",
                "Stratis filesystems are XFS automatically",
                "Stratis fstab needs: x-systemd.requires=stratisd.service",
                "Check RAID sync: cat /proc/mdstat"
            ]
        },

        "network_storage": {
            "name": "Network Storage (NFS/CIFS/Autofs)",
            "explanation": """
Network storage allows mounting remote filesystems. NFS is for Linux-to-Linux,
CIFS/SMB is for Windows shares. Autofs provides on-demand mounting.

NFS (Network File System):
  - Native Linux network filesystem
  - Uses showmount to discover exports
  - Mount options: rw, ro, sync, soft, hard

CIFS/SMB (Common Internet File System):
  - Windows-compatible network shares
  - Requires cifs-utils package
  - Uses credentials file for security

AUTOFS:
  - Automatic mount on access
  - Unmounts after timeout
  - Configured in /etc/auto.master

KEY FILES:
  /etc/fstab              - Persistent mounts
  /etc/auto.master        - Autofs master map
  /etc/auto.*             - Autofs submaps
  /etc/cifs-credentials   - CIFS credentials file
            """,
            "commands": [
                {
                    "name": "List NFS Exports",
                    "syntax": "showmount -e <server>",
                    "example": "showmount -e nfs.example.com",
                    "flags": {
                        "-e": "Show exports",
                        "-a": "Show all mounts",
                        "Requires": "nfs-utils package"
                    }
                },
                {
                    "name": "Mount NFS Share",
                    "syntax": "mount -t nfs <server>:<export> <mountpoint>",
                    "example": "mount -t nfs server:/data /mnt/nfs",
                    "flags": {
                        "-t nfs": "NFS filesystem type",
                        "-o rw": "Read-write mount",
                        "-o ro": "Read-only mount",
                        "-o sync": "Synchronous writes"
                    }
                },
                {
                    "name": "NFS fstab Entry",
                    "syntax": "server:/export /mount nfs defaults 0 0",
                    "example": "nfs.example.com:/data /mnt/nfs nfs defaults,_netdev 0 0",
                    "flags": {
                        "_netdev": "Wait for network (recommended)",
                        "defaults": "Standard mount options",
                        "rw,sync": "Custom options"
                    }
                },
                {
                    "name": "Mount CIFS Share",
                    "syntax": "mount -t cifs //<server>/<share> <mountpoint> -o credentials=<file>",
                    "example": "mount -t cifs //server/share /mnt/cifs -o credentials=/etc/cifs-creds",
                    "flags": {
                        "-t cifs": "CIFS filesystem type",
                        "-o credentials=": "Credentials file path",
                        "-o username=,password=": "Inline credentials (insecure)"
                    }
                },
                {
                    "name": "CIFS Credentials File",
                    "syntax": "/etc/cifs-credentials",
                    "example": "username=smbuser\\npassword=secret\\ndomain=WORKGROUP\\n\\nchmod 600 /etc/cifs-credentials",
                    "flags": {
                        "username=": "SMB username",
                        "password=": "SMB password",
                        "domain=": "Windows domain",
                        "chmod 600": "Secure the file!"
                    }
                },
                {
                    "name": "Configure Autofs",
                    "syntax": "Edit /etc/auto.master and submaps",
                    "example": "# /etc/auto.master\\n/mnt/auto  /etc/auto.nfs\\n\\n# /etc/auto.nfs\\ndata  -rw,sync  server:/data",
                    "flags": {
                        "/etc/auto.master": "Master map file",
                        "Mount point": "Parent directory",
                        "Map file": "Submap with mount definitions",
                        "Key": "Subdirectory name",
                        "Options": "Mount options",
                        "Location": "server:/export"
                    }
                },
                {
                    "name": "Autofs Home Directories",
                    "syntax": "/etc/auto.master with wildcard",
                    "example": "# /etc/auto.master\\n/home/remote  /etc/auto.home\\n\\n# /etc/auto.home\\n*  -rw  nfs:/home/&",
                    "flags": {
                        "*": "Wildcard - match any key",
                        "&": "Substitute matched key",
                        "Result": "/home/remote/user mounts nfs:/home/user"
                    }
                },
                {
                    "name": "Enable Autofs",
                    "syntax": "systemctl enable --now autofs",
                    "example": "systemctl enable --now autofs",
                    "flags": {
                        "enable --now": "Enable and start",
                        "restart": "Apply config changes",
                        "status": "Check service status"
                    }
                }
            ],
            "common_mistakes": [
                "Forgetting _netdev option for network mounts in fstab",
                "Wrong permissions on credentials file (must be 600)",
                "Not installing cifs-utils for CIFS mounts",
                "Autofs syntax errors (check with automount -v)",
                "Not restarting autofs after config changes"
            ],
            "exam_tricks": [
                "NFS: showmount -e server to see exports",
                "CIFS: use credentials file, chmod 600",
                "Autofs: * and & for home directory wildcards",
                "fstab: use _netdev for network filesystems",
                "Test autofs: ls /mnt/auto/mountname triggers mount"
            ]
        }
    }

    @classmethod
    def get_topic(cls, category):
        """Get learning content for a topic."""
        return cls.TOPICS.get(category)

    @classmethod
    def get_all_topics(cls):
        """Get all available learning topics."""
        return list(cls.TOPICS.keys())


class LearnMode:
    """
    Learn Mode interface - displays instructional content.
    """

    def __init__(self):
        """Initialize learn mode."""
        self.logger = logging.getLogger(__name__)

    def start(self):
        """Start learn mode - let user choose topic."""
        while True:
            fmt.clear_screen()
            fmt.print_header("LEARN MODE - Choose a Topic")

            topics = LearnContent.get_all_topics()

            # Display topics
            for i, topic_key in enumerate(sorted(topics), 1):
                topic = LearnContent.get_topic(topic_key)
                fmt.print_menu_option(i, topic['name'])

            fmt.print_menu_option('Q', "Back to Main Menu")

            choice = input("\nSelect topic (number or Q): ").strip()

            if choice.lower() == 'q':
                return

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(topics):
                    topic_key = sorted(topics)[idx]
                    self._display_topic(topic_key)
                else:
                    print(fmt.error("Invalid selection"))
                    input("Press Enter to continue...")
            except ValueError:
                print(fmt.error("Please enter a number or Q"))
                input("Press Enter to continue...")

    def _display_topic(self, topic_key):
        """Display learning content for a topic."""
        topic = LearnContent.get_topic(topic_key)

        fmt.clear_screen()
        fmt.print_header(f"LEARN: {topic['name']}")

        # Explanation
        print(fmt.bold("📖 CONCEPT OVERVIEW:"))
        print(topic['explanation'].strip())
        print()

        # Commands
        print(fmt.bold("💻 ESSENTIAL COMMANDS:"))
        print("=" * 70)
        for cmd in topic['commands']:
            print()
            print(fmt.success(f"▸ {cmd['name']}"))
            print()
            print(fmt.bold("  Syntax:"))
            print(f"    {fmt.info(cmd['syntax'])}")
            print()
            print(fmt.bold("  Example:"))
            print(f"    $ {cmd['example']}")
            print()
            print(fmt.bold("  Flags:"))
            for flag, description in cmd['flags'].items():
                print(f"    {fmt.warning(flag):20} → {description}")
            print()

        # Common Mistakes
        print("=" * 70)
        print(fmt.bold("⚠️  COMMON MISTAKES:"))
        for i, mistake in enumerate(topic['common_mistakes'], 1):
            print(f"  {i}. {fmt.error('✗')} {mistake}")
        print()

        # Exam Tricks
        print(fmt.bold("🎯 EXAM TIPS:"))
        for i, trick in enumerate(topic['exam_tricks'], 1):
            print(f"  {i}. {fmt.warning('!')} {trick}")
        print()

        # Navigate
        print("=" * 70)
        choice = input("\n[P] Practice this topic  [B] Back to topics  [Q] Main menu: ").strip().lower()

        if choice == 'p':
            # Launch practice mode for this topic
            from core.practice import PracticeSession
            session = PracticeSession()
            session.category = topic_key
            session.difficulty = 'exam'
            session.task_count = 3

            tasks_module = __import__(f'tasks.{topic_key}', fromlist=[''])
            from tasks.registry import TaskRegistry
            TaskRegistry.initialize()

            tasks = TaskRegistry.get_practice_tasks(topic_key, 'exam', 3)
            if tasks:
                for i, task in enumerate(tasks, 1):
                    session._practice_task(task, i, len(tasks))
            else:
                print(fmt.warning("No practice tasks available for this topic yet."))
                input("Press Enter to continue...")


def run_learn_mode(category=None):
    """Run learn mode (convenience function).

    Args:
        category: Optional category to jump directly to
    """
    mode = LearnMode()
    if category:
        mode.category = category
        mode._show_topic_menu()
    else:
        mode.start()
