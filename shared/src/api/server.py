"""REST API server for system management."""

from typing import Dict, List, Optional
from enum import Enum

from fastapi import FastAPI, WebSocket, HTTPException
from pydantic import BaseModel, Field

from control.async_control import AsyncControlLoop
from control.firmware import FirmwareManager, FirmwareVersion
from fleet.distributed import FleetManager
from app.core import SystemMonitor, SystemMetrics, SystemStatus

# API Models
class CommandRequest(BaseModel):
    """Generic command request."""
    command: str
    parameters: Dict = Field(default_factory=dict)

class SystemState(BaseModel):
    """System state response."""
    status: SystemStatus
    metrics: Optional[Dict] = None
    firmware_version: Optional[str] = None
    cluster_size: Optional[int] = None
    is_leader: Optional[bool] = None

class FirmwareUpdate(BaseModel):
    """Firmware update request."""
    version: str
    data: bytes

# Initialize application
app = FastAPI(title="10x Instrument Control API")

# System components
control = AsyncControlLoop()
firmware = FirmwareManager("/dev/ttyUSB0")
fleet = FleetManager("api_node", "localhost", 8000)
monitor = SystemMonitor()

@app.on_event("startup")
async def startup():
    """Initialize system on startup."""
    await firmware.initialize()
    await fleet.start()
    await monitor.start()

@app.on_event("shutdown")
async def shutdown():
    """Clean shutdown."""
    await control.stop()
    await monitor.stop()

# Control System Endpoints
@app.post("/control/start")
async def start_control():
    """Start control system."""
    await control.start()
    return {"status": "started"}

@app.post("/control/stop")
async def stop_control():
    """Stop control system."""
    await control.stop()
    return {"status": "stopped"}

@app.get("/control/status")
async def get_control_status():
    """Get control system status."""
    metrics = {}
    for sensor_id, buffer in control._sensor_buffers.items():
        readings = buffer.get_latest(10)
        if readings:
            metrics[sensor_id] = [r.value for r in readings]
    return {"metrics": metrics}

# Firmware Endpoints
@app.get("/firmware/version")
async def get_firmware_version():
    """Get current firmware version."""
    version = await firmware.get_version()
    return {"version": str(version)}

@app.post("/firmware/update")
async def update_firmware(update: FirmwareUpdate):
    """Perform firmware update."""
    try:
        # Parse version string
        major, minor, patch = map(int, update.version.split("."))
        new_version = FirmwareVersion(
            major, minor, patch,
            "api_update"
        )
        await firmware.update_firmware(update.data, new_version)
        return {"status": "updated", "version": str(new_version)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Fleet Management Endpoints
@app.get("/fleet/status")
async def get_fleet_status():
    """Get fleet status."""
    return {
        "cluster_size": fleet.get_cluster_size(),
        "is_leader": fleet.is_leader(),
        "stats": fleet.get_cluster_stats()
    }

# Real-time Monitoring
@app.websocket("/ws/metrics")
async def metrics_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time metrics."""
    await websocket.accept()
    
    # Subscribe to metrics updates
    queue = await monitor.subscribe()
    
    try:
        while True:
            # Wait for metrics update
            metrics = await queue.get()
            
            # Send to client
            await websocket.send_json({
                "type": "metrics",
                "data": metrics
            })
    except:
        pass
    finally:
        # Clean up
        monitor._subscribers.remove(queue)
        await websocket.close()

@app.get("/system/status")
async def get_system_status() -> SystemState:
    """Get complete system status."""
    metrics = monitor.metrics.to_dict() if monitor.metrics else None
    
    return SystemState(
        status=monitor.status,
        metrics=metrics,
        firmware_version=str(await firmware.get_version()),
        cluster_size=fleet.get_cluster_size(),
        is_leader=fleet.is_leader()
    )
