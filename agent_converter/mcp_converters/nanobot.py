"""
MCP conversion functions for Nanobot format.

Nanobot format uses tools.mcpServers structure with command, args, and env.
"""

from typing import Any


def to_nanobot(mcp_data: dict) -> dict:
    """
    Convert generic MCP data to Nanobot format.
    
    Args:
        mcp_data: MCP data in generic format {name: {command, args, env}}
    
    Returns:
        Dict in Nanobot format {tools: {mcpServers: {...}}}
    """
    result = {}
    for name, config in mcp_data.items():
        command = config.get("command", [])
        
        # Split command into command (first element) and args (rest)
        if isinstance(command, list):
            cmd = command[0] if command else ""
            args = command[1:] if len(command) > 1 else []
        else:
            cmd = str(command)
            args = []
        
        entry = {
            "command": cmd,
            "args": args
        }
        
        # Add environment if present
        if config.get("env"):
            entry["env"] = dict(config["env"])
        elif config.get("environment"):
            entry["env"] = dict(config["environment"])
        
        result[name] = entry
    
    return {"tools": {"mcpServers": result}}


def from_nanobot(nanobot_data: dict) -> dict:
    """
    Convert Nanobot MCP format to generic format.
    
    Args:
        nanobot_data: Dict with tools.mcpServers structure
    
    Returns:
        Generic MCP dict {name: {command, args, env}}
    """
    mcp_servers = nanobot_data.get("tools", {}).get("mcpServers", {})
    result = {}
    
    for name, config in mcp_servers.items():
        command = config.get("command", [])
        
        # Split command into command (first element) and args (rest)
        if isinstance(command, list):
            cmd = command[0] if command else ""
            args = command[1:] if len(command) > 1 else []
        else:
            cmd = str(command)
            args = []
        
        entry = {
            "command": cmd,
            "args": args
        }
        
        # Add environment if present
        if config.get("env"):
            entry["env"] = dict(config["env"])
        elif config.get("environment"):
            entry["env"] = dict(config["environment"])
        
        result[name] = entry
    
    return result
