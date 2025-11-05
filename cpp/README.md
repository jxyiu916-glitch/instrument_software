C++ control core scaffold

This folder contains a minimal C++ implementation sketch of the Plant and PID controller.

It is intended as a starting point if you want to implement the core in C++ and expose it to Python via pybind11 or a custom extension.

Build notes (local dev):
- Install pybind11 and a C++17 toolchain.
- A recommended approach is to use a small `CMakeLists.txt` and pybind11's CMake integration.

Example (not executed here):

mkdir build && cd build
cmake ..
make

Then import the built module from Python.

This scaffold intentionally does not include a full build as CI/machine toolchains vary.
