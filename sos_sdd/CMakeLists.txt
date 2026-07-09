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

# libDDD: an installed prefix (include/ddd/DDD.h + lib/libDDD.*) or a
# built source tree (ddd/DDD.h + ddd/.libs/libDDD.*). The local deps/
# prefix (populated by ./install_deps.sh, untracked) is the canonical
# location; LIBDDD_HOME (cache or environment) overrides, the sibling
# checkout and system prefixes are fallbacks.
set(_libddd_hints)
if(DEFINED LIBDDD_HOME)
  list(APPEND _libddd_hints ${LIBDDD_HOME})
endif()
if(DEFINED ENV{LIBDDD_HOME})
  list(APPEND _libddd_hints $ENV{LIBDDD_HOME})
endif()
list(APPEND _libddd_hints ${CMAKE_CURRENT_SOURCE_DIR}/deps
     $ENV{HOME}/git/libDDD /usr/local /usr)

find_path(DDD_INCLUDE_DIR ddd/DDD.h HINTS ${_libddd_hints} PATH_SUFFIXES include)
# The static archive is the library's supported linking mode (its shared
# build exports almost no symbols); prefer libDDD.a explicitly.
find_library(DDD_LIBRARY NAMES libDDD.a DDD HINTS ${_libddd_hints} PATH_SUFFIXES lib ddd/.libs)
if(NOT DDD_INCLUDE_DIR OR NOT DDD_LIBRARY)
  message(FATAL_ERROR "libDDD not found (searched: ${_libddd_hints}); set LIBDDD_HOME")
endif()
message(STATUS "libDDD headers: ${DDD_INCLUDE_DIR}; library: ${DDD_LIBRARY}")

# libITS: the gal component (ExprHom — Phase 2's indexed read) joins at
# Phase 2. Same prefix conventions as libDDD; static archive, linked
# before libDDD (it depends on it).
find_path(ITS_INCLUDE_DIR its/gal/ExprHom.hpp HINTS ${_libddd_hints}
          PATH_SUFFIXES include)
find_library(ITS_LIBRARY NAMES libITS.a ITS HINTS ${_libddd_hints}
             PATH_SUFFIXES lib)
if(NOT ITS_INCLUDE_DIR OR NOT ITS_LIBRARY)
  message(FATAL_ERROR "libITS not found (searched: ${_libddd_hints}); run ./install_deps.sh")
endif()
message(STATUS "libITS headers: ${ITS_INCLUDE_DIR}; library: ${ITS_LIBRARY}")

target_include_directories(_core PRIVATE ${DDD_INCLUDE_DIR} ${ITS_INCLUDE_DIR})
target_link_libraries(_core PRIVATE ${ITS_LIBRARY} ${DDD_LIBRARY})
get_filename_component(_ddd_libdir ${DDD_LIBRARY} DIRECTORY)
set_target_properties(_core PROPERTIES
  BUILD_RPATH ${_ddd_libdir}
  INSTALL_RPATH ${_ddd_libdir})

set_target_properties(_core PROPERTIES
  LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
