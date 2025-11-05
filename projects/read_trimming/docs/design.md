Read trimming — design notes

Goal
----
Provide a small, interview-friendly read trimming utility with: exact and fuzzy adapter trimming, quality-based tail trimming, sliding-window trimming, and an ML hook for adapter detection. Include a C++ stub for a future fast trimming implementation and design notes for architecture and long-term evolution.

Components
----------
- `src/trim/core.py`: trimming helpers and ML-detection hook.
- `tests/test_trimming.py`: unit/smoke tests.
- `bench_trim.py`: simple timing harness.
- `cpp/fast_trim.cpp`: C++ stub for future high-performance trimming.

Architecture notes
------------------
- Keep pure-Python reference implementations small and correct for interview clarity.
- Provide a C++ core for performance-critical loops; wrap via pybind11 or CFFI and provide a thin Python API that falls back to Python when C++ not available.
- Add CI jobs that compile and smoke-test the C++ build optionally (matrix job).

AI integration
--------------
- Provide ML hook `detect_adapter_ml(seq, model_predict=...)` so a trained binary classifier can flag reads likely containing adapters. Avoid bundling models in repo; document how to plug a model in.

Long-term evolution
-------------------
- Add comprehensive benchmarks, micro-optimizations, and vectorized (SIMD) implementations in C++ for throughput.
- Keep stable Python API; evolve C++ implementation behind the same API to maintain backward compatibility.
