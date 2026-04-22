"""
Format detection utilities for identifying configuration file formats.
"""

from typing import Any


def detect_format(data: dict) -> str:
    """
    Detect the configuration format from the data structure.
    
    Returns one of: 'nanobot', 'hermes', 'opencode', 'kilo', 'qwen', 'gemini', 'unknown'
    """
    # Nanobot detection: has "agents" and "providers" and "gateway"
    if "agents" in data and "providers" in data and "gateway" in data:
        return "nanobot"
    
    # Hermes detection: has "model" with "default" and "toolsets" array
    if "model" in data and isinstance(data.get("model"), dict) and "toolsets" in data:
        return "hermes"
    
    # OpenCode/Kilo detection: has "provider" and "mcp"
    if "provider" in data and "mcp" in data:
        # Distinguish between opencode and kilo by checking for "permission" key
        if "permission" in data:
            return "kilo"
        return "opencode"
    
    # Qwen detection: has "modelProviders"
    if "modelProviders" in data:
        return "qwen"
    
    # Gemini detection: has "mcpServers" without "provider" or "modelProviders"
    if "mcpServers" in data and "provider" not in data and "modelProviders" not in data:
        return "gemini"
    
    # Fallback detection
    if "mcpServers" in data:
        return "gemini"
    elif "mcp" in data and "provider" in data:
        if "permission" in data:
            return "kilo"
        return "opencode"
    elif "modelProviders" in data:
        return "qwen"
    
    return "unknown"
