"""
MCP conversion functions for Qwen format.

Qwen format uses mcpServers with command, args, and env (same as Gemini).
"""

from typing import Any


def to_qwen(mcp_data: dict) -> dict:
    """
    Convert generic MCP data to Qwen format.
    
    Args:
        mcp_data: MCP data in generic format {name: {command, args, env}}
    
    Returns:
        Dict in Qwen format {name: {command, args, env}}
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


def from_qwen(qwen_mcp: dict) -> dict:
    """
    Convert Qwen MCP format to generic format.
    
    Args:
        qwen_mcp: Dict with {name: {command, args, env}}
    
    Returns:
        Generic MCP dict {name: {command, args, env}}
    """
    result = {}
    for name, config in qwen_mcp.items():
        entry = {
            "command": config.get("command", ""),
            "args": list(config.get("args", []))
        }
        
        if config.get("env"):
            entry["env"] = dict(config["env"])
        
        result[name] = entry
    
    return result
