# Hardware Interface Design

## Register Map

### Control System Registers

Base address: 0x1000_0000

| Offset | Name           | Access | Description                    |
|--------|---------------|---------|--------------------------------|
| 0x00   | MODE          | RW     | Control mode (0=manual, 1=PID) |
| 0x04   | SETPOINT      | RW     | Target value (float32)         |
| 0x08   | CURRENT_VALUE | R      | Current sensor value (float32) |
| 0x0C   | OUTPUT        | R      | Control output value (float32) |
| 0x10   | STATUS        | R      | Status flags                   |
| 0x14   | KP            | RW     | P gain (float32)              |
| 0x18   | KI            | RW     | I gain (float32)              |
| 0x1C   | KD            | RW     | D gain (float32)              |

### Status Register Bits

| Bit | Name         | Description                         |
|-----|-------------|-------------------------------------|
| 0   | ACTIVE      | Controller active                   |
| 1   | ERROR       | Error condition present             |
| 2   | SATURATED   | Output saturated                    |
| 3   | CONVERGED   | Within convergence bounds           |
| 4-31| RESERVED    | Reserved for future use             |

## Timing Requirements

### Control Loop

- Base frequency: 1kHz (1ms period)
- Jitter tolerance: ±50μs
- Phase requirements:
  1. Sensor read: ≤100μs
  2. Compute: ≤200μs
  3. Output write: ≤100μs
  4. Margin: 600μs

### Error Handling

- Sensor timeout: 200μs
- Output timeout: 150μs
- Error response latency: ≤50μs