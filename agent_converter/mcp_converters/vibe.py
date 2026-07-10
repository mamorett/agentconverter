"""
MCP conversion functions for Vibe format.

This is a one-way conversion only (to Vibe format).
"""

from typing import Any


def to_vibe(mcp_data: dict) -> list[dict]:
    """
    Convert generic MCP data to Vibe format list.

    Args:
        mcp_data: MCP data in generic format {name: {command, args, env}}

    Returns:
        List of dicts in Vibe format [[mcp_servers]] entries
    """
    result = []
    for name, config in mcp_data.items():
        # Handle command (can be list or string)
        cmd = config.get("command", "")
        args = config.get("args", [])

        if isinstance(cmd, list):
            # If command is a list, split first element as command, rest as args
            command_str = cmd[0] if cmd else ""
            args_list = cmd[1:] + list(args)
        else:
            command_str = str(cmd)
            args_list = list(args)

        entry = {
            "name": name,
            "transport": "stdio",  # Default to stdio
            "command": command_str,
            "args": args_list
        }

        # Add environment if present
        env_data = config.get("env") or config.get("environment")
        if env_data:
            entry["env"] = dict(env_data)

        result.append(entry)

    return result


def from_vibe(vibe_data: Any) -> dict:
    """
    Convert Vibe MCP format to generic format.
    Not implemented as Vibe is one-way only.
    """
    raise NotImplementedError("Vibe format is one-way conversion only (to Vibe)")
