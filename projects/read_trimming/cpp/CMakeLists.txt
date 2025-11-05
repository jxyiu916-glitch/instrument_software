cmake_minimum_required(VERSION 3.15)
project(fast_trim)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Enable AVX-512 if available
include(CheckCXXCompilerFlag)
check_cxx_compiler_flag("-mavx512f" COMPILER_SUPPORTS_AVX512)
if(COMPILER_SUPPORTS_AVX512)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -mavx512f")
endif()

# Find Python and pybind11
find_package(Python COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 CONFIG REQUIRED)

# Add the C++ library
add_library(fast_trim INTERFACE)
target_include_directories(fast_trim INTERFACE ${CMAKE_CURRENT_SOURCE_DIR})

# Create the Python module
pybind11_add_module(cpp_fast_trim bindings.cpp)
target_link_libraries(cpp_fast_trim PRIVATE fast_trim)