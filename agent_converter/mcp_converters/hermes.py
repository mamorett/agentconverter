"""
MCP conversion functions for Hermes format.

Hermes format uses tools.mcpServers as a simple list of server names.
"""

from typing import Any


def to_hermes(mcp_data: dict) -> list:
    """
    Convert generic MCP data to Hermes format.
    
    Hermes stores MCP servers as a flat list of server names.
    
    Args:
        mcp_data: MCP data in generic format {name: {command, args, env}}
    
    Returns:
        List of server names
    """
    # Hermes format is a simple list of enabled MCP server names
    return list(mcp_data.keys())


def from_hermes(hermes_data: dict) -> dict:
    """
    Convert Hermes MCP format to generic format.
    
    Args:
        hermes_data: Dict with tools.mcpServers as list of server names
    
    Returns:
        Generic MCP dict {name: {command, args, env}} - empty since
        Hermes only stores names, not full config
    """
    # Hermes only stores server names, not full configuration
    # Return empty dict as we can't reconstruct full config from names only
    mcp_servers = hermes_data.get("tools", {}).get("mcpServers", [])
    result = {}
    
    for name in mcp_servers:
        result[name] = {}
    
    return result
