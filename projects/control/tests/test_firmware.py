"""Tests for firmware interface components."""
import pytest
import asyncio
from ..src.control.firmware import (
    FirmwareManager,
    FirmwareVersion,
    FirmwareRegistry,
    FirmwareState,
    BootloaderProtocol
)

@pytest.fixture
def firmware_version():
    return FirmwareVersion(1, 2, 3, "abcd1234")

@pytest.fixture
def firmware_manager():
    return FirmwareManager("/dev/ttyUSB0")

@pytest.fixture
def firmware_registry():
    return FirmwareRegistry()

def test_firmware_version_formatting(firmware_version):
    assert str(firmware_version) == "1.2.3-abcd1234"
    
def test_firmware_version_parsing():
    data = bytes([1, 2, 3]) + bytes.fromhex("abcd1234")
    version = FirmwareVersion.from_bytes(data)
    assert version.major == 1
    assert version.minor == 2
    assert version.patch == 3
    assert version.git_hash == "abcd1234"

@pytest.mark.asyncio
async def test_bootloader_protocol():
    protocol = BootloaderProtocol("/dev/ttyUSB0")
    await protocol.connect()
    
    # Test version command
    response = await protocol.send_command(BootloaderProtocol.CMD_VERSION)
    version = FirmwareVersion.from_bytes(response)
    assert version.major == 1
    assert version.minor == 2
    assert version.patch == 3

@pytest.mark.asyncio
async def test_firmware_manager_initialization(firmware_manager):
    await firmware_manager.initialize()
    assert firmware_manager._state == FirmwareState.APPLICATION
    assert firmware_manager._current_version is not None

@pytest.mark.asyncio
async def test_firmware_update(firmware_manager):
    # Create test firmware image
    firmware_data = bytes([0xFF] * 1024)
    version = FirmwareVersion(1, 2, 4, "deadbeef")
    
    # Perform update
    await firmware_manager.initialize()
    await firmware_manager.update_firmware(firmware_data, version)
    
    # Verify state after update
    assert firmware_manager._state == FirmwareState.APPLICATION

def test_firmware_registry(firmware_registry, firmware_version):
    # Register versions
    firmware_registry.register_version("device1", firmware_version)
    firmware_registry.register_version(
        "device1",
        FirmwareVersion(1, 2, 4, "deadbeef")
    )
    
    # Get latest version
    latest = firmware_registry.get_latest_version("device1")
    assert latest.patch == 4  # Should get newer patch version
    
    # Check compatibility
    assert firmware_registry.check_compatibility(
        "device1",
        firmware_version,
        latest
    )
    
    # Major version changes should be incompatible
    incompatible = FirmwareVersion(2, 0, 0, "feedface")
    assert not firmware_registry.check_compatibility(
        "device1",
        firmware_version,
        incompatible
    )