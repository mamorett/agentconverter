"""
MCP conversion functions for OpenCode format.

OpenCode format uses mcp with command array, type, and environment.
"""

from typing import Any


def to_opencode(mcp_data: dict) -> dict:
    """
    Convert generic MCP data to OpenCode format.

    OpenCode format uses command as a single array (no command/args separation).
    If input has command as array, it's preserved as-is.
    If input has command + args separate, they are combined into one array.

    Args:
        mcp_data: MCP data in generic format {name: {command, args, env}}
                  command can be string or array

    Returns:
        Dict in OpenCode format {name: {command: [], type, environment}}
    """
    result = {}
    for name, config in mcp_data.items():
        # Build command array - handle both string and array formats
        command = []
        
        cmd = config.get("command")
        if isinstance(cmd, str):
            command.append(cmd)
        elif isinstance(cmd, list):
            # Command is already an array - use it directly
            command.extend(cmd)
        
        # Append args if present (for backward compatibility)
        if isinstance(config.get("args"), list):
            command.extend(config["args"])

        entry = {
            "command": command,
            "type": "local"
        }

        # Add environment if present
        if config.get("env"):
            entry["environment"] = dict(config["env"])

        result[name] = entry

    return result


def from_opencode(opencode_mcp: dict) -> dict:
    """
    Convert OpenCode MCP format to generic format.

    OpenCode uses command as an array (no separation between command and args).
    We need to split the array into command (first element) and args (rest).

    Args:
        opencode_mcp: Dict with {name: {command: [], type, environment}}

    Returns:
        Generic MCP dict {name: {command, args, env}}
    """
    result = {}
    for name, config in opencode_mcp.items():
        command = config.get("command", [])

        # OpenCode has command as array - split into command + args
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
        if config.get("environment"):
            entry["env"] = dict(config["environment"])

        result[name] = entry

    return result
