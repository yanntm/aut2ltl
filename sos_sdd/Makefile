# Builds the _core pybind11 extension in place (sos_sdd/_core<ext-suffix>).
# libDDD is taken from $(LIBDDD_HOME): headers under include/, static lib
# under lib/. The -lDDD link is commented until the core actually uses it.

PY ?= python3
CXX ?= g++
LIBDDD_HOME ?= /usr/local

EXT_SUFFIX := $(shell $(PY) -c "import sysconfig; print(sysconfig.get_config_var('EXT_SUFFIX'))")
PYBIND_INCLUDES := $(shell $(PY) -m pybind11 --includes)

CXXFLAGS += -std=c++17 -O2 -fPIC -Wall -Wextra $(PYBIND_INCLUDES) -I$(LIBDDD_HOME)/include
LDFLAGS += -L$(LIBDDD_HOME)/lib

TARGET := _core$(EXT_SUFFIX)
SRCS := $(wildcard src/*.cpp)

$(TARGET): $(SRCS)
	$(CXX) $(CXXFLAGS) -shared $(SRCS) -o $@ $(LDFLAGS) # -lDDD

clean:
	rm -f _core*.so

.PHONY: clean
