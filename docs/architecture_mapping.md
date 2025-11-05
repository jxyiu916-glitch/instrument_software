## Architecture mapping for mini-project collection

This document maps each mini-project to a concise architecture description,
highlighting inputs/outputs, data flow, testing hooks, C++ migration paths,
and where ML hooks are present. It's intended as a single place to understand
how the projects fit together and how to evolve them into a more integrated
instrument/pipeline codebase.

Format: For each project we list:
- Path: location in repo
- Contract: inputs/outputs and data shapes
- Key modules: core files to inspect
- Tests: locations of unit tests
- ML hook: whether a model_predict hook exists and where
- C++ path: whether a C++ stub exists and where

### projects/control
- Path: `projects/control/src/control/`
- Contract: 
  - Async control loops with real-time guarantees
  - Firmware management with safe updates
  - Hardware abstraction layer
- Key modules:
  - `async_control.py`: Thread-safe control system
  - `firmware.py`: Bootloader and version management
  - `hardware.py`: Register-level interface
- Tests: 
  - `test_async_control.py`: Threading and timing tests
  - `test_firmware.py`: Update and version tests
  - `test_hardware.py`: Interface tests
- Integration: Full system tests in `projects/tests/test_integration.py`
- C++ components: Hardware-critical components in C++

### projects/fleet_diagnostics
- Path: `projects/fleet_diagnostics/src/fleet/`
- Contract:
  - Distributed consensus and leader election
  - Fleet-wide telemetry collection
  - Real-time monitoring and alerts
- Key modules:
  - `distributed.py`: Raft consensus implementation
  - `telemetry.py`: Distributed data collection
  - `manager.py`: Fleet coordination
- Tests:
  - `test_distributed.py`: Consensus tests
  - `test_telemetry.py`: Collection tests
  - System tests in `projects/tests/test_integration.py`
- ML hook: Anomaly detection with model_predict interface
- Performance: C++ optimizations for heavy compute

### projects/umi_dedup
- Path: `projects/umi_dedup/src/umi/core.py`
- Contract: list of UMIs -> deduplicated set or clusters -> consensus seqs
- Key modules: `hamming_distance`, `cluster_umis`, `umi_consensus`
- Tests: `projects/umi_dedup/tests`
- ML hook: none
- C++ path: `projects/umi_dedup/cpp/` (for high-throughput grouping)

### projects/sequence_qc
- Path: `projects/sequence_qc/src/seqqc/core.py`
- Contract: reads -> QC metrics (GC, N fraction, length hist)
- Key modules: `basic_qc_stats`, `gc_content`, `per_base_n_fraction`
- Tests: `projects/sequence_qc/tests`
- ML hook: optional (adapter detection can be swapped for a model)
- C++ path: none (profiling not critical)

### projects/molecule_counting
- Path: `projects/molecule_counting/src/molecule/core.py`
- Contract: reads+UMIs -> per-gene molecule counts
- Tests: `projects/molecule_counting/tests`
- ML hook: none
- C++ path: `projects/molecule_counting/cpp/` possible for heavy counting

### projects/barcode_processing
- Path: `projects/barcode_processing/src/barcode/core.py`
- Contract: reads -> barcodes -> corrected barcodes and counts
- Key modules: whitelist building, hamming-based correction
- Tests: `projects/barcode_processing/tests`
- ML hook: none
- C++ path: `projects/barcode_processing/cpp/` for fast correction

### projects/alignment_qc
- Path: `projects/alignment_qc/src/seqqc/core.py` (alignment helpers)
- Contract: alignments -> mapping rate, softclip stats, insert-size
- Key modules: `parse_cigar`, `softclip_stats`, `insert_size_stats`
- Tests: `projects/alignment_qc/tests`
- ML hook: anomaly detectors may accept feature vectors
- C++ path: `projects/alignment_qc/cpp/` for high-speed parsing

### projects/visualization_plots
- Path: `projects/visualization_plots/src/viz/core.py`
- Contract: arrays/histograms -> plotting helpers (matrices, hist bins)
- Key modules: `histogram_bins`, `coverage_to_plot`, `ml_anomaly_wrapper`
- Tests: `projects/visualization_plots/tests`
- ML hook: yes (anomaly scoring wrapper accepts model_predict)
- C++ path: none (plotting is Python-first)

### projects/read_trimming
- Path: `projects/read_trimming/src/trim/core.py`
- Contract: reads -> trimmed reads
- Key modules: `trim_adapter_exact`, `sliding_window_trim`, `detect_adapter_ml`
- Tests: `projects/read_trimming/tests`
- ML hook: `detect_adapter_ml` accepts a model_predict callable
- C++ path: `projects/read_trimming/cpp/fast_trim.cpp` (present as stub)

### projects/variant_calling_demo
- Path: `projects/variant_calling_demo/src/variant/core.py`
- Contract: (ref: str, reads: Iterable[(start, seq)]) -> list of variant dicts
- Key modules: `pileup_from_reads`, `call_variants`, `pretty_print`
- Tests: `projects/variant_calling_demo/tests`
- ML hook: none
- C++ path: none (easy to port to C++ via same pileup/caller separation)

## Cross-cutting Architecture Principles

### 1. System Design
- **Modularity**: Clean interfaces between components
- **Concurrency**: Thread-safe designs throughout
- **Real-time**: Timing guarantees where needed
- **Distributed**: Consensus and coordination patterns

### 2. Implementation Patterns
- **Async/Await**: Modern Python concurrency
- **Thread Safety**: Proper synchronization
- **Error Handling**: Comprehensive error management
- **Resource Management**: RAII and cleanup

### 3. Integration Points
- **Hardware Layer**: Register-level access
- **Firmware**: Update and version management
- **ML Integration**: Model prediction interfaces
- **Distributed Systems**: Consensus protocols

### 4. Quality Assurance
- **Testing**: Unit, integration, and system tests
- **Performance**: Benchmarking and profiling
- **Documentation**: Complete API and design docs
- **Review Process**: Comprehensive guidelines
  models can be plugged in during runtime or replaced by fakes in tests.
- C++ migration: prefer a separation between data preparation (I/O, parsing)
  and core compute; port the compute-heavy parts to C++ and bind the Python
  port for glue and tests.
- CI recommendation: create a workflow that discovers `projects/*/tests`
  and runs pytest for each project; optionally add a separate job that runs
  bench scripts but marks them as optional or gated.

## Where to find things

- Project cores live under `projects/<project>/src/`.
- Tests are under `projects/<project>/tests`.
- Design docs and CODE_REVIEW_SUMMARY files are under `projects/<project>/docs`
  or root of the project folder for easy review.
