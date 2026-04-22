#!/usr/bin/env python3
"""
Agent Configuration Converter

Converts between Gemini, OpenCode, Qwen, Kilo, Nanobot, and Hermes configuration formats.
"""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
