cmake_minimum_required(VERSION 3.15)
project(umi_dedup)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Python and pybind11
find_package(Python COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 CONFIG REQUIRED)

# Add the C++ library
add_library(umi_dedup INTERFACE)
target_include_directories(umi_dedup INTERFACE ${CMAKE_CURRENT_SOURCE_DIR})

# Create the Python module
pybind11_add_module(cpp_umi_dedup bindings.cpp)
target_link_libraries(cpp_umi_dedup PRIVATE umi_dedup)