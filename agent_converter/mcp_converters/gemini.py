"""
MCP conversion functions for Gemini format.

Gemini format uses mcpServers with command, args, and env.
"""

from typing import Any


def to_gemini(mcp_data: dict) -> dict:
    """
    Convert generic MCP data to Gemini format.
    
    Args:
        mcp_data: MCP data in generic format {name: {command, args, env}}
    
    Returns:
        Dict in Gemini format {mcpServers: {...}}
    """
    result = {}
    for name, config in mcp_data.items():
        entry = {
            "command": config.get("command", ""),
            "args": list(config.get("args", []))
        }
        if config.get("env"):
            entry["env"] = dict(config["env"])
        result[name] = entry
    return result


def from_gemini(gemini_mcp: dict) -> dict:
    """
    Convert Gemini MCP format to generic format.
    
    Args:
        gemini_mcp: Dict with {name: {command, args, env}} (mcpServers content)
    
    Returns:
        Generic MCP dict {name: {command, args, env}}
    """
    result = {}
    for name, config in gemini_mcp.items():
        # Get command - can be string or list
        command = config.get("command", "")
        args = config.get("args", [])
        
        # If command is a list, split into command + args
        if isinstance(command, list):
            cmd = command[0] if command else ""
            cmd_args = command[1:] if len(command) > 1 else []
            # Merge with existing args
            if isinstance(args, list):
                args = cmd_args + args
            else:
                args = cmd_args
        else:
            cmd = str(command)
        
        entry = {
            "command": cmd,
            "args": list(args) if isinstance(args, list) else []
        }
        
        # Add environment if present
        if config.get("env"):
            entry["env"] = dict(config["env"])
        elif config.get("environment"):
            entry["env"] = dict(config["environment"])
        
        result[name] = entry
    
    return result
