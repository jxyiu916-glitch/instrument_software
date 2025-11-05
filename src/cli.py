"""Command Line Interface for 10x Instrument Control and Diagnostics.

This CLI provides access to core system functionality including:
- Control system management
- Firmware updates
- Fleet diagnostics
- System monitoring

Usage:
    python -m src.cli control start      # Start control system
    python -m src.cli control status     # Get control system status
    python -m src.cli firmware update    # Update firmware
    python -m src.cli fleet status       # Get fleet status
    python -m src.cli monitor           # Start monitoring dashboard
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any

from control.async_control import AsyncControlLoop
from control.firmware import FirmwareManager, FirmwareVersion
from fleet.distributed import FleetManager


class SystemManager:
    """Central system manager for all components."""
    
    def __init__(self):
        self.control = AsyncControlLoop()
        self.firmware = FirmwareManager("/dev/ttyUSB0")
        self.fleet = FleetManager("local_node", "localhost", 8000)
        
    async def start(self):
        """Start all system components."""
        await self.firmware.initialize()
        await self.fleet.start()
        await self.control.start()
        
    async def stop(self):
        """Stop all system components."""
        await self.control.stop()
        
    async def get_status(self) -> Dict[str, Any]:
        """Get system-wide status."""
        metrics = {}
        
        # Get control system metrics
        for sensor_id, buffer in self.control._sensor_buffers.items():
            readings = buffer.get_latest(10)
            if readings:
                values = [r.value for r in readings]
                metrics[f"{sensor_id}_latest"] = values[-1]
                
        # Get fleet metrics
        metrics["cluster_size"] = self.fleet.get_cluster_size()
        metrics["is_leader"] = self.fleet.is_leader()
        metrics["cluster_stats"] = self.fleet.get_cluster_stats()
        
        return {
            "status": "running",
            "metrics": metrics,
            "firmware_version": str(await self.firmware.get_version())
        }

async def handle_control_command(manager: SystemManager, command: str) -> Dict[str, Any]:
    """Handle control system commands."""
    if command == "start":
        await manager.start()
        return {"status": "started"}
    elif command == "stop":
        await manager.stop()
        return {"status": "stopped"}
    elif command == "status":
        return await manager.get_status()
    else:
        raise ValueError(f"Unknown control command: {command}")

async def handle_firmware_command(manager: SystemManager, command: str) -> Dict[str, Any]:
    """Handle firmware commands."""
    if command == "version":
        version = await manager.firmware.get_version()
        return {"version": str(version)}
    elif command == "update":
        # Simulate firmware update
        test_firmware = bytes([0xFF] * 1024)
        current = await manager.firmware.get_version()
        new_version = FirmwareVersion(
            current.major,
            current.minor + 1,
            0,
            "testupdate"
        )
        await manager.firmware.update_firmware(test_firmware, new_version)
        return {"status": "updated", "version": str(new_version)}
    else:
        raise ValueError(f"Unknown firmware command: {command}")

async def handle_fleet_command(manager: SystemManager, command: str) -> Dict[str, Any]:
    """Handle fleet commands."""
    if command == "status":
        return {
            "cluster_size": manager.fleet.get_cluster_size(),
            "is_leader": manager.fleet.is_leader(),
            "stats": manager.fleet.get_cluster_stats()
        }
    else:
        raise ValueError(f"Unknown fleet command: {command}")

async def async_main(argv: List[str]) -> Dict[str, Any]:
    """Async entry point."""
    if len(argv) < 2:
        raise ValueError("Usage: python -m src.cli <component> <command>")
        
    component = argv[0]
    command = argv[1]
    
    manager = SystemManager()
    
    if component == "control":
        return await handle_control_command(manager, command)
    elif component == "firmware":
        return await handle_firmware_command(manager, command)
    elif component == "fleet":
        return await handle_fleet_command(manager, command)
    elif component == "monitor":
        # Start monitoring and return initial status
        await manager.start()
        return await manager.get_status()
    else:
        raise ValueError(f"Unknown component: {component}")

def main(argv: List[str] | None = None) -> int:
    """Synchronous entry point."""
    argv = argv or sys.argv[1:]
    try:
        result = asyncio.run(async_main(argv))
        print(json.dumps(result, indent=2))
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
