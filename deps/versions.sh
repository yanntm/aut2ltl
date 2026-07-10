# Which revision of each native dependency this tree builds.
#
# Sourced by the build_*.sh scripts. Holds versions, source locations and the
# build width -- nothing about where a build runs, and nothing a built tree
# needs at run time (that is env.sh). Every value may be overridden from the
# caller's environment.

# make -j for every dependency. A fixed width, never nproc: under a scheduler's
# cpuset nproc reports the whole machine rather than the allocation, and the
# heavier translation units here want memory more than they want lanes.
: "${BUILD_JOBS:=10}"

# Source of truth for which Spot release we track: build_spot.sh clones it to
# read the version and the tarball URL, then applies its own configure flags.
# That repo's own recipe targets ITS-Tools and builds no Python bindings.
: "${SPOT_SRC_REPO:=https://github.com/yanntm/Spot-BinaryBuilds}"

# GAP, built from source like Spot: never a distro package, or a result would
# depend on which machine it ran on rather than on the commit. Keep this recent:
# GAP vendors GMP, and older bundles fail configure's long-long check under a
# modern gcc ("could not find a working compiler").
: "${GAP_VERSION:=4.15.1}"
: "${GAP_URL:=https://github.com/gap-system/gap/releases/download/v${GAP_VERSION}/gap-${GAP_VERSION}.tar.gz}"

# SgpDec, the GAP package the Krohn-Rhodes path consumes. Cloned at its tag: it
# is pure GAP, and the tarball its release page advertises is not served.
: "${SGPDEC_VERSION:=v1.2.0}"
: "${SGPDEC_REPO:=https://github.com/gap-packages/sgpdec.git}"

# SgpDec's transitive dependencies, in the GAP distribution but not installed by
# GAP's `make install`. semigroups vendors libsemigroups and dominates the build
# time. Order is irrelevant, BuildPackages.sh sorts it out.
: "${GAP_PKGS:=gapdoc io orb datastructures digraphs genss images semigroups}"

# The subset of GAP_PKGS that compiles a kernel module. Their source directory
# exists whether or not the compile succeeded, so only the presence of a built
# .so distinguishes a finished package from a failed one. The rest are pure GAP,
# where the directory is the installation.
: "${GAP_KERNEL_PKGS:=io orb datastructures digraphs semigroups}"

# libDDD and libITS, for the symbolic path. Cloned into build/, installed into
# opt/its; only libITS's gal expression component is consumed.
: "${LIBDDD_REPO:=https://github.com/lip6/libDDD}"
: "${LIBITS_REPO:=https://github.com/lip6/libITS}"
