#!/usr/bin/env python3
"""Repository-level wrapper for the prompt-compressor skill CLI."""
from pathlib import Path
import runpy

SCRIPT = Path(__file__).resolve().parents[1] / "skills" / "prompt-compressor" / "scripts" / "refine_prompt.py"
runpy.run_path(str(SCRIPT), run_name="__main__")
