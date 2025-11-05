"""
Firmware interface module for hardware control and updates.
Handles bootloader communication, version management, and firmware updates.
"""
from dataclasses import dataclass
from enum import Enum
import struct
import asyncio
from typing import Optional, List, Dict
import hashlib
import logging

logger = logging.getLogger(__name__)

class FirmwareState(Enum):
    BOOTLOADER = "bootloader"
    APPLICATION = "application"
    UPDATING = "updating"
    ERROR = "error"

@dataclass
class FirmwareVersion:
    major: int
    minor: int
    patch: int
    git_hash: str
    
    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}-{self.git_hash[:8]}"
    
    @classmethod
    def from_bytes(cls, data: bytes) -> "FirmwareVersion":
        """Parse version from firmware response."""
        major, minor, patch = struct.unpack("<BBB", data[:3])
        git_hash = data[3:11].hex()
        return cls(major, minor, patch, git_hash)

class BootloaderProtocol:
    """Low-level bootloader protocol implementation."""
    
    # Command codes
    CMD_PING = 0x01
    CMD_VERSION = 0x02
    CMD_ERASE = 0x03
    CMD_WRITE = 0x04
    CMD_VERIFY = 0x05
    CMD_RESET = 0x06
    
    def __init__(self, port: str):
        self._port = port
        self._sequence = 0
        
    async def connect(self):
        """Establish connection with bootloader."""
        # Simulate serial connection
        await asyncio.sleep(0.1)
        
    def _calculate_checksum(self, data: bytes) -> int:
        """Calculate packet checksum."""
        return sum(data) & 0xFF
        
    async def send_command(self, command: int, data: bytes = b"") -> bytes:
        """Send command to bootloader with proper framing."""
        packet = struct.pack("<BBH", command, self._sequence, len(data))
        packet += data
        checksum = self._calculate_checksum(packet)
        packet += bytes([checksum])
        
        # Simulate send/receive
        await asyncio.sleep(0.01)
        self._sequence = (self._sequence + 1) & 0xFF
        
        # Simulate response
        if command == self.CMD_VERSION:
            return struct.pack("<BBB", 1, 2, 3) + bytes.fromhex("abcd1234")
        return b"\x00"  # OK response

class FirmwareManager:
    """High-level firmware management interface."""
    def __init__(self, port: str):
        self._bootloader = BootloaderProtocol(port)
        self._state = FirmwareState.APPLICATION
        self._current_version: Optional[FirmwareVersion] = None
        
    async def initialize(self):
        """Initialize firmware interface."""
        await self._bootloader.connect()
        await self.get_version()
        
    async def get_version(self) -> FirmwareVersion:
        """Get current firmware version."""
        response = await self._bootloader.send_command(
            BootloaderProtocol.CMD_VERSION
        )
        self._current_version = FirmwareVersion.from_bytes(response)
        return self._current_version
        
    async def enter_bootloader(self):
        """Enter bootloader mode."""
        if self._state != FirmwareState.APPLICATION:
            raise RuntimeError("Not in application mode")
            
        await self._bootloader.send_command(BootloaderProtocol.CMD_RESET)
        self._state = FirmwareState.BOOTLOADER
        await asyncio.sleep(0.5)  # Wait for bootloader
        
    async def update_firmware(self, firmware_data: bytes, version: FirmwareVersion):
        """Perform firmware update."""
        if self._state != FirmwareState.BOOTLOADER:
            await self.enter_bootloader()
            
        try:
            self._state = FirmwareState.UPDATING
            
            # Verify firmware image
            expected_hash = hashlib.sha256(firmware_data).hexdigest()
            
            # Erase flash
            await self._bootloader.send_command(BootloaderProtocol.CMD_ERASE)
            
            # Write firmware in chunks
            chunk_size = 256
            for i in range(0, len(firmware_data), chunk_size):
                chunk = firmware_data[i:i + chunk_size]
                await self._bootloader.send_command(
                    BootloaderProtocol.CMD_WRITE,
                    struct.pack("<L", i) + chunk
                )
                
            # Verify written data
            await self._bootloader.send_command(
                BootloaderProtocol.CMD_VERIFY,
                expected_hash.encode()
            )
            
            # Reset to application
            await self._bootloader.send_command(BootloaderProtocol.CMD_RESET)
            self._state = FirmwareState.APPLICATION
            await asyncio.sleep(1.0)  # Wait for application start
            
            # Verify new version
            new_version = await self.get_version()
            assert new_version == version, "Version mismatch after update"
            
        except Exception as e:
            self._state = FirmwareState.ERROR
            logger.error(f"Firmware update failed: {e}")
            raise

class FirmwareRegistry:
    """Registry of known firmware versions and compatibility."""
    def __init__(self):
        self._versions: Dict[str, List[FirmwareVersion]] = {}
        
    def register_version(self, device_type: str, version: FirmwareVersion):
        """Register a new firmware version."""
        if device_type not in self._versions:
            self._versions[device_type] = []
        self._versions[device_type].append(version)
        
    def get_latest_version(self, device_type: str) -> Optional[FirmwareVersion]:
        """Get latest known firmware version for device type."""
        if device_type not in self._versions:
            return None
        return sorted(
            self._versions[device_type],
            key=lambda v: (v.major, v.minor, v.patch)
        )[-1]
        
    def check_compatibility(
        self,
        device_type: str,
        current: FirmwareVersion,
        target: FirmwareVersion
    ) -> bool:
        """Check if upgrade path is valid."""
        if current.major != target.major:
            return False  # Major version changes require manual intervention
        return True