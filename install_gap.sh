#!/usr/bin/env bash
# install_gap.sh — Install GAP + SgpDec for the Krohn-Rhodes construction path.
#
# Everything lands in a prefix inside the repo (opt/gap by default), never in
# $HOME and never system-wide: a checkout is self-contained, and a machine
# without root can still be provisioned.
#
# GAP itself is taken from the distro when one is available and already has it;
# otherwise it is built from source into the prefix. SgpDec is always installed
# into the prefix, as a GAP root, so it is found without touching any GAP that
# happens to be installed elsewhere.
#
# The prefix exposes bin/gap: a wrapper that adds the prefix as a GAP root. It
# is what callers get from PATH (see aut2ltl/bls/gap/runner.py, which spawns a
# bare `gap`), and what cluster/env.sh puts there.
#
# Usage:
#   ./install_gap.sh                  # distro GAP if present, else build
#   ./install_gap.sh --from-source    # never touch the distro, always build
#   ./install_gap.sh --check-only     # verify an existing install, change nothing
#   GAP_PREFIX=/some/where ./install_gap.sh
#
set -euo pipefail

GAP_MIN_VERSION="4.12"
GAP_VERSION="${GAP_VERSION:-4.13.1}"
GAP_URL="https://github.com/gap-system/gap/releases/download/v${GAP_VERSION}/gap-${GAP_VERSION}.tar.gz"

SGPDEC_VERSION="v1.2.0"   # Update when a new release appears
SGPDEC_TARBALL="sgpdec-1.2.0.tar.gz"
SGPDEC_URL="https://github.com/gap-packages/sgpdec/releases/download/${SGPDEC_VERSION}/${SGPDEC_TARBALL}"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Repo-local by default. Root-anchored in .gitignore.
GAP_PREFIX="${GAP_PREFIX:-${ROOT}/opt/gap}"
GAP_PKG_DIR="${GAP_PREFIX}/pkg"
GAP_BIN_DIR="${GAP_PREFIX}/bin"
GAP_BUILD_DIR="${ROOT}/build/gap-${GAP_VERSION}"

log() { echo "[bls/install] $*"; }
warn() { echo "[bls/install] WARNING: $*" >&2; }
die() { echo "[bls/install] ERROR: $*" >&2; exit 1; }

check_only=false
from_source=false
for arg in "$@"; do
  case "$arg" in
    --check-only)  check_only=true ;;
    --from-source) from_source=true ;;
    -h|--help)     sed -n '2,20p' "$0"; exit 0 ;;
    *)             die "unknown option: $arg" ;;
  esac
done

have_cmd() { command -v "$1" >/dev/null 2>&1; }

detect_distro() {
  if [[ -f /etc/fedora-release ]] || have_cmd dnf; then
    echo "fedora"
  elif [[ -f /etc/debian_version ]] || have_cmd apt-get; then
    echo "debian"
  else
    echo "unknown"
  fi
}

# Path of the real GAP executable the wrapper should call: a previous
# source build in the prefix, else whatever the distro put on PATH. Never the
# wrapper itself, which would recurse.
real_gap() {
  if [[ -x "${GAP_PREFIX}/gap-inst/bin/gap" ]]; then
    echo "${GAP_PREFIX}/gap-inst/bin/gap"
  elif have_cmd gap && [[ "$(command -v gap)" != "${GAP_BIN_DIR}/gap" ]]; then
    command -v gap
  fi
}

build_gap_from_source() {
  have_cmd make || die "no make; cannot build GAP from source"
  have_cmd cc || have_cmd gcc || die "no C compiler; cannot build GAP from source"

  log "Building GAP ${GAP_VERSION} from source into ${GAP_PREFIX}/gap-inst"
  mkdir -p "$GAP_BUILD_DIR"
  local tarball="${GAP_BUILD_DIR}/gap-${GAP_VERSION}.tar.gz"

  if [[ ! -f "$tarball" ]]; then
    curl -fL --progress-bar -o "$tarball" "$GAP_URL" \
      || wget -q --show-progress -O "$tarball" "$GAP_URL" \
      || die "could not download $GAP_URL"
  fi

  local src="${GAP_BUILD_DIR}/gap-${GAP_VERSION}"
  [[ -d "$src" ]] || tar -xzf "$tarball" -C "$GAP_BUILD_DIR"

  # Out of caution rather than taste: GAP's build wants to live in its source
  # tree, so the tree lives under build/ and only the install lands in opt/.
  # A fixed width, never nproc: under a scheduler's cpuset nproc reports the
  # whole machine rather than what was allocated, and a build that wide would
  # oversubscribe it.
  local jobs="${BUILD_JOBS:-10}"

  (
    cd "$src"
    ./configure --prefix="${GAP_PREFIX}/gap-inst"
    make -j"$jobs"
    make install
  )
  [[ -x "${GAP_PREFIX}/gap-inst/bin/gap" ]] || die "GAP build finished but no bin/gap"
  log "GAP built."
}

ensure_gap_base() {
  local existing
  existing="$(real_gap)"

  if [[ -n "$existing" ]] && ! $from_source; then
    # -q silences the banner and the prompt, which otherwise land in the capture
    # as terminal escapes; QUIT keeps GAP from waiting on stdin.
    local ver
    ver=$("$existing" --no-window --bare -q -c 'Print(GAPInfo.Version, "\n"); QUIT;' 2>/dev/null \
          | tr -d '\r' | grep -oE '^[0-9]+\.[0-9.]+' | head -1 || true)
    log "Found GAP: ${ver:-unknown} ($existing)"
    return 0
  fi

  if $check_only; then
    die "GAP not found (check-only mode)."
  fi

  if $from_source; then
    build_gap_from_source
    return 0
  fi

  local distro
  distro=$(detect_distro)
  log "GAP not found in PATH. distro=$distro"

  # The distro path needs root. Where we cannot have it — a cluster node, a
  # container — fall through to the source build rather than failing.
  if ! have_cmd sudo; then
    warn "no sudo available; building GAP from source instead"
    build_gap_from_source
    return 0
  fi

  case "$distro" in
    fedora)
      log "Attempting dnf install (you may be prompted for sudo password)..."
      sudo dnf install -y gap gap-core gap-pkg-semigroups gap-pkg-digraphs gap-pkg-io gap-pkg-json || {
        warn "dnf install of some gap-pkg-* may have failed or been partial."
      }
      ;;
    debian)
      log "Attempting apt install (sudo may be required)..."
      sudo apt-get update -qq || true
      sudo apt-get install -y gap gap-core gap-dev gap-doc gap-online-help \
        gap-pkg-semigroups gap-pkg-digraphs gap-pkg-io || {
        warn "apt may not have all the -pkg packages under those exact names; check 'apt search gap'."
      }
      ;;
    *)
      warn "Unknown distro; building GAP from source."
      build_gap_from_source
      return 0
      ;;
  esac

  [[ -n "$(real_gap)" ]] || die "GAP still not found after attempted install."
  log "GAP now available."
}

install_sgpdec_local() {
  mkdir -p "$GAP_PKG_DIR"
  local target_dir="${GAP_PKG_DIR}/sgpdec"

  if [[ -d "$target_dir" ]]; then
    log "SgpDec directory already exists at $target_dir — skipping download."
    return 0
  fi

  if $check_only; then
    die "SgpDec not installed in ${GAP_PKG_DIR} (check-only)."
  fi

  log "Downloading SgpDec ${SGPDEC_VERSION} into ${GAP_PKG_DIR}..."
  local tmp
  tmp=$(mktemp -d)
  # The path is baked into the trap now, not read from a variable when it fires:
  # EXIT runs after this function has returned, where a local `tmp` is gone and
  # `set -u` would abort an otherwise successful script.
  trap "rm -rf '$tmp' 2>/dev/null || true" EXIT

  curl -fL --progress-bar -o "$tmp/${SGPDEC_TARBALL}" "$SGPDEC_URL" || {
    # Fallback: try to clone the repo if release tarball layout changes
    warn "Direct release tarball download failed; trying git clone of tag..."
    git clone --depth 1 --branch "$SGPDEC_VERSION" https://github.com/gap-packages/sgpdec.git "$tmp/sgpdec-src" || \
      die "Could not obtain SgpDec sources."
    (cd "$tmp/sgpdec-src" && tar czf "$tmp/${SGPDEC_TARBALL}" .)
  }

  tar -xzf "$tmp/${SGPDEC_TARBALL}" -C "$tmp"
  # The tarball usually unpacks to a directory named sgpdec-1.2.0 or just "sgpdec"
  local unpacked
  unpacked=$(find "$tmp" -maxdepth 1 -type d -name "sgpdec*" | head -1)
  if [[ -z "$unpacked" ]]; then
    # Sometimes the tarball root is the package contents directly
    mkdir -p "$tmp/sgpdec-fallback"
    tar -xzf "$tmp/${SGPDEC_TARBALL}" -C "$tmp/sgpdec-fallback"
    unpacked="$tmp/sgpdec-fallback"
  fi

  cp -r "$unpacked" "$target_dir"
  log "Installed SgpDec to $target_dir"
}

# The prefix is handed to GAP as an extra root (trailing ';' keeps the defaults),
# which is how pkg/sgpdec becomes loadable without writing to any GAP tree.
write_gap_wrapper() {
  local target
  target="$(real_gap)"
  [[ -n "$target" ]] || die "no real GAP to wrap"

  if $check_only; then
    [[ -x "${GAP_BIN_DIR}/gap" ]] || die "no gap wrapper at ${GAP_BIN_DIR}/gap (check-only)."
    return 0
  fi

  mkdir -p "$GAP_BIN_DIR"
  cat >"${GAP_BIN_DIR}/gap" <<EOF
#!/usr/bin/env bash
# Generated by install_gap.sh. Runs GAP with this prefix as an extra GAP root,
# so pkg/sgpdec loads. Callers spawn a bare 'gap' from PATH; this is it.
exec "$target" -l "${GAP_PREFIX};" "\$@"
EOF
  chmod +x "${GAP_BIN_DIR}/gap"
  log "Wrote wrapper ${GAP_BIN_DIR}/gap -> $target"
}

verify_sgpdec() {
  log "Verifying SgpDec can be loaded..."
  local logf
  logf=$(mktemp)
  # Keep verification minimal and robust: we only care that LoadPackage succeeds.
  # Do not rely on specific globals like SgpDecVersion (they may not be bound at top level in all versions).
  if "${GAP_BIN_DIR}/gap" --no-window --bare -c '
    if LoadPackage("SgpDec") = fail then
      Print("LOAD_FAIL\n");
    else
      Print("LOAD_OK\n");
    fi;
    QUIT;
  ' 2>&1 | tee "$logf" | grep -q "LOAD_OK"; then
    log "SUCCESS: SgpDec loads correctly."
    rm -f "$logf"
    return 0
  else
    cat "$logf" || true
    rm -f "$logf"
    die "SgpDec failed to load. See log above. Check that ${GAP_PKG_DIR}/sgpdec is visible to GAP."
  fi
}

main() {
  log "GAP + SgpDec setup for BuchiToLTL/bls; prefix ${GAP_PREFIX}"
  ensure_gap_base
  install_sgpdec_local
  write_gap_wrapper
  verify_sgpdec

  log "All done. Put ${GAP_BIN_DIR} on PATH (cluster/env.sh does this)."
  log "Example verification command:"
  echo "    ${GAP_BIN_DIR}/gap --no-window -c 'LoadPackage(\"SgpDec\"); T:=Semigroup([Transformation([2,1,3])]); Print(HolonomyCascadeSemigroup(T), \"\\n\"); QUIT;'"
}

main "$@"
