"""
MCP conversion functions for Hermes format.

Hermes format uses YAML with mcp_servers containing full server configurations.
"""

from typing import Any


def to_hermes(mcp_data: dict) -> dict:
    """
    Convert generic MCP data to Hermes format.

    Hermes stores MCP servers as mcp_servers dict with full configurations.

    Args:
        mcp_data: MCP data in generic format {name: {command, args, env}}
                  or OpenCode format {name: {command: [], type, environment}}

    Returns:
        Dict in Hermes format {mcp_servers: {name: {command, args, env, allowed_tools}}}
    """
    result = {"mcp_servers": {}}

    for name, config in mcp_data.items():
        entry = {}

        # Handle command - can be string or list
        cmd = config.get("command", "")
        if isinstance(cmd, list):
            # If command is a list, first element is command, rest are args
            entry["command"] = cmd[0] if cmd else ""
            entry["args"] = cmd[1:] if len(cmd) > 1 else []
        else:
            entry["command"] = str(cmd)
            entry["args"] = list(config.get("args", []))

        # Add environment if present (handle both 'env' and 'environment')
        env_data = config.get("env") or config.get("environment")
        if env_data:
            entry["env"] = dict(env_data)

        # Add allowed_tools if present (Hermes specific)
        if config.get("allowed_tools"):
            entry["allowed_tools"] = list(config["allowed_tools"])

        result["mcp_servers"][name] = entry

    return result


def from_hermes(hermes_data: dict) -> dict:
    """
    Convert Hermes MCP format to generic format.

    Args:
        hermes_data: Dict with mcp_servers containing full configurations

    Returns:
        Generic MCP dict {name: {command, args, env, allowed_tools}}
    """
    result = {}
    mcp_servers = hermes_data.get("mcp_servers", {})

    for name, config in mcp_servers.items():
        entry = {
            "command": config.get("command", ""),
            "args": list(config.get("args", []))
        }

        # Add environment if present
        if config.get("env"):
            entry["env"] = dict(config["env"])

        # Add allowed_tools if present (Hermes specific)
        if config.get("allowed_tools"):
            entry["allowed_tools"] = list(config["allowed_tools"])

        result[name] = entry

    return result
