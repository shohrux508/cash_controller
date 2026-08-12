#!/usr/bin/env python3
"""Unified quality check pipeline: ruff + mypy + pytest."""

from __future__ import annotations

import subprocess
import sys

# ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"


def _run_step(name: str, cmd: list[str]) -> bool:
    """Run a single check step and return True if it passed."""
    print(f"\n{BOLD}{YELLOW}{'=' * 60}{RESET}")
    print(f"{BOLD}  > {name}{RESET}")
    print(f"{YELLOW}{'=' * 60}{RESET}\n")

    result = subprocess.run(cmd, cwd=".")  # noqa: S603
    passed = result.returncode == 0

    if passed:
        print(f"\n{GREEN}  + {name} — PASSED{RESET}")
    else:
        print(f"\n{RED}  - {name} — FAILED{RESET}")

    return passed


def main() -> None:
    """Run all quality checks sequentially."""
    steps: list[tuple[str, list[str]]] = [
        ("Ruff Lint", [sys.executable, "-m", "ruff", "check", "."]),
        ("Ruff Format", [sys.executable, "-m", "ruff", "format", "--check", "."]),
        ("Mypy", [sys.executable, "-m", "mypy", "."]),
        (
            "Pytest + Coverage",
            [
                sys.executable,
                "-m",
                "pytest",
                "--cov=app",
                "--cov-report=term-missing",
                "-v",
            ],
        ),
    ]

    results: list[tuple[str, bool]] = []
    for name, cmd in steps:
        passed = _run_step(name, cmd)
        results.append((name, passed))

    # Summary
    print(f"\n{BOLD}{'=' * 60}{RESET}")
    print(f"{BOLD}  SUMMARY{RESET}")
    print(f"{'=' * 60}")
    all_passed = True
    for name, passed in results:
        icon = f"{GREEN}+{RESET}" if passed else f"{RED}-{RESET}"
        print(f"  {icon} {name}")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print(f"{GREEN}{BOLD}  All checks passed!{RESET}")
        sys.exit(0)
    else:
        print(f"{RED}{BOLD}  Some checks failed.{RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
