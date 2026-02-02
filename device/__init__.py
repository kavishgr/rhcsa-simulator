"""
Device management module for RHCSA Simulator v2.0.0

Provides automatic cleanup of practice resources between tasks.
"""

from device.device_manager import DeviceManager, get_device_manager, ResourceType
from device.cleanup_strategies import (
    CleanupStrategy,
    LVMCleanupStrategy,
    MountCleanupStrategy,
    SwapCleanupStrategy,
    UserCleanupStrategy,
    FstabCleanupStrategy,
)

__all__ = [
    'DeviceManager',
    'get_device_manager',
    'ResourceType',
    'CleanupStrategy',
    'LVMCleanupStrategy',
    'MountCleanupStrategy',
    'SwapCleanupStrategy',
    'UserCleanupStrategy',
    'FstabCleanupStrategy',
]
