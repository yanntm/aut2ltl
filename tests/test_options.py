#!/usr/bin/env python3
"""
tests/test_options.py

Unit checks for the contract-floor `Options` (the flags compartment):
- lazy default resolution via OptionSpec (bare Options() == "all defaults");
- stored override wins over the spec default;
- bare-key get with an explicit default;
- clone(overrides) is an independent variant;
- from_specs seeds + coerces from the legacy env var (migration bridge);
- effective() materializes the full config without mutating the store.

No spot, no GAP — pure, fast. Run from project root:
    python3 tests/test_options.py
"""
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from aut2ltl.options import OptionSpec, Options

FLAG = OptionSpec("demo.flag", True, "a demo bool", env="DEMO_FLAG")
LIMIT = OptionSpec("demo.limit", 30, "a demo int limit", env="DEMO_LIMIT")
SPECS = [FLAG, LIMIT]


def test_lazy_default() -> None:
    o = Options()                      # empty store == all defaults
    assert o.get(FLAG) is True
    assert o.get(LIMIT) == 30
    assert "demo.flag" not in o        # nothing stored


def test_override_wins() -> None:
    o = Options({"demo.flag": False})
    assert o.get(FLAG) is False
    assert o.get(LIMIT) == 30          # still the spec default


def test_bare_key_default() -> None:
    o = Options()
    assert o.get("unknown.key", 7) == 7
    assert o.get("unknown.key") is None


def test_clone_is_independent() -> None:
    base = Options({"demo.flag": False})
    variant = base.clone({"demo.limit": 5})
    assert variant.get(FLAG) is False and variant.get(LIMIT) == 5
    assert base.get(LIMIT) == 30       # parent unchanged
    base.set("demo.limit", 99)
    assert variant.get(LIMIT) == 5     # variant unaffected by later parent edits


def test_from_specs_env_seeding() -> None:
    saved = {k: os.environ.get(k) for k in ("DEMO_FLAG", "DEMO_LIMIT")}
    try:
        os.environ["DEMO_FLAG"] = "0"      # bool: "0" -> False
        os.environ["DEMO_LIMIT"] = "12"    # int  -> 12
        o = Options.from_specs(SPECS, env=True)
        assert o.get(FLAG) is False
        assert o.get(LIMIT) == 12
        # env=False ignores the env vars -> all defaults
        o2 = Options.from_specs(SPECS, env=False)
        assert o2.get(FLAG) is True and o2.get(LIMIT) == 30
        # explicit overrides win over env
        o3 = Options.from_specs(SPECS, env=True, overrides={"demo.flag": True})
        assert o3.get(FLAG) is True
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def test_effective_is_pure() -> None:
    o = Options({"demo.flag": False})
    eff = o.effective(SPECS)
    assert eff == {"demo.flag": False, "demo.limit": 30}
    assert o.as_dict() == {"demo.flag": False}   # not mutated by effective()


def main() -> int:
    tests = [
        test_lazy_default,
        test_override_wins,
        test_bare_key_default,
        test_clone_is_independent,
        test_from_specs_env_seeding,
        test_effective_is_pure,
    ]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS  {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL  {t.__name__}: {e}")
    print(f"\n{'ALL PASS' if not failed else f'{failed} FAILED'} ({len(tests)} checks)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
