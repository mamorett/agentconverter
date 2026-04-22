"""
MCP conversion functions for Kilo format.

Kilo format is identical to OpenCode format.
"""

from typing import Any


def to_kilo(mcp_data: dict) -> dict:
    """
    Convert generic MCP data to Kilo format (identical to OpenCode).
    
    Args:
        mcp_data: MCP data in generic format {name: {command, args, env}}
    
    Returns:
        Dict in Kilo format {name: {command: [], type, environment}}
    """
    # Kilo is identical to OpenCode
    from . import opencode
    return opencode.to_opencode(mcp_data)


def from_kilo(kilo_mcp: dict) -> dict:
    """
    Convert Kilo MCP format to generic format (identical to OpenCode).
    
    Args:
        kilo_mcp: Dict with {name: {command: [], type, environment}}
    
    Returns:
        Generic MCP dict {name: {command, args, env}}
    """
    # Kilo is identical to OpenCode
    from . import opencode
    return opencode.from_opencode(kilo_mcp)
