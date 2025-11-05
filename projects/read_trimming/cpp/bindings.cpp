// Python bindings for fast read trimming
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "fast_trim.hpp"

namespace py = pybind11;

PYBIND11_MODULE(cpp_fast_trim, m) {
    m.doc() = "Fast read trimming with SIMD acceleration";
    
    py::class_<trim::TrimAccelerator>(m, "TrimAccelerator")
        .def(py::init<uint8_t>())
        .def("trim_batch_simd", &trim::TrimAccelerator::trim_batch_simd)
        .def("try_hardware_accel", &trim::TrimAccelerator::try_hardware_accel);
}