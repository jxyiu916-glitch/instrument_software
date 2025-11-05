#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "umi_dedup.hpp"

namespace py = pybind11;

PYBIND11_MODULE(cpp_umi_dedup, m) {
    m.doc() = "Fast UMI deduplication in C++";
    
    // Wrap the UMI counter for Python
    py::class_<umi::UMICounter<std::string_view>>(m, "UMICounter")
        .def(py::init<size_t>(), py::arg("max_distance") = 0)
        .def("count_umis", &umi::UMICounter<std::string_view>::count_umis,
             "Count UMIs with optional clustering");
             
    // Expose hamming_distance helper
    m.def("hamming_distance", &umi::hamming_distance<std::string_view>,
          "Compute Hamming distance between two sequences");
}