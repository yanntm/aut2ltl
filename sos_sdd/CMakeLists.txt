# Builds the _core pybind11 extension and places it inside the package
# directory, so `import sos_sdd` works from the repo root without install.
#   cmake -B build && cmake --build build
# libDDD: headers under include/, static lib under lib/ of LIBDDD_HOME
# (cache variable or environment); the DDD link is commented until the
# core actually uses it.

cmake_minimum_required(VERSION 3.18)
project(sos_sdd CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

find_package(Python3 COMPONENTS Interpreter Development.Module REQUIRED)
if(NOT DEFINED pybind11_DIR)
  execute_process(
    COMMAND ${Python3_EXECUTABLE} -m pybind11 --cmakedir
    OUTPUT_VARIABLE pybind11_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE)
endif()
find_package(pybind11 CONFIG REQUIRED)

pybind11_add_module(_core src/module.cpp)
target_compile_options(_core PRIVATE -Wall -Wextra)

if(NOT DEFINED LIBDDD_HOME AND DEFINED ENV{LIBDDD_HOME})
  set(LIBDDD_HOME $ENV{LIBDDD_HOME})
endif()
if(DEFINED LIBDDD_HOME)
  target_include_directories(_core PRIVATE ${LIBDDD_HOME}/include)
  target_link_directories(_core PRIVATE ${LIBDDD_HOME}/lib)
  # target_link_libraries(_core PRIVATE DDD)
endif()

set_target_properties(_core PROPERTIES
  LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
