#!/usr/bin/env python3
"""Deterministic placeholder for dataset construction.

This entry point intentionally performs no scientific data synthesis until source
records exist. It verifies the expected dataset lifecycle directories instead.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for relative in ["datasets/canonical", "datasets/comparative", "datasets/exports"]:
    if not (ROOT / relative).is_dir():
        raise SystemExit(f"missing dataset directory: {relative}")
print("dataset build placeholder passed")
