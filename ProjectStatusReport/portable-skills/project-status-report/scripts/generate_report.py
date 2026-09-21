#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL / "runtime"))

from project_status_report.cli import main

raise SystemExit(main())
