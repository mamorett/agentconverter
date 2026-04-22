#!/usr/bin/env python3
"""
Agent Configuration Converter - CLI entry point.

This script provides the command-line interface for converting between
different agent configuration formats (Gemini, OpenCode, Qwen, Kilo, Nanobot, Hermes).

Usage:
    python -m agent_converter -i input.json -t qwen
    python agent_converter.py -i input.json -t qwen
"""

import sys
import os

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_converter.cli import main

if __name__ == "__main__":
    sys.exit(main())
