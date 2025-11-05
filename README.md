# Staff-Level Engineering Project Collection


## Project Overview

This repository demonstrates staff-level engineering capabilities through a collection of interconnected projects focusing on instrumentation control, distributed systems, and real-time processing. Our implementation reflects our commitment to excellence and innovation in advancing biological research through cutting-edge technology.

## Key Components

### Control Systems (`projects/control/`)
- Async control loops with real-time guarantees
- Thread-safe sensor interfaces
- Hardware abstraction layer
- Firmware management system

### Fleet Diagnostics (`projects/fleet_diagnostics/`)
- Distributed consensus implementation
- Fleet-wide telemetry collection
- Cluster management
- Real-time monitoring

### Integration Testing (`projects/tests/`)
- System-level test scenarios
- Performance benchmarking
- Fault tolerance testing
- Timing verification

### Documentation (`docs/`)
- Team guidelines and processes
- Architecture documentation
- Onboarding guide
- Code review standards

Quick start (macOS / zsh):

```bash
# create virtualenv and activate
python3 -m venv .venv
source .venv/bin/activate

# install dev dependencies
pip install -r requirements.txt

# run tests
pytest -q

# run example
python -m src.cli data/example_small.json
```

Run the API locally (after installing deps into `.venv`):

```bash
make run-api
# then open http://127.0.0.1:8000/docs to try the /process endpoint
```

