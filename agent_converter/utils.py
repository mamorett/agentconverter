"""
Utility functions for file I/O and common helpers.
"""

import json
from typing import Any


def load_json_file(filepath: str) -> dict:
    """Load and parse a JSON file."""
    with open(filepath, "r") as f:
        return json.load(f)


def save_json_file(data: dict, filepath: str) -> None:
    """Save data to a JSON file."""
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


def filter_mcp_servers(mcp_dict: dict, specific_server: str | None) -> dict:
    """Filter MCP servers to include only the specified one if given."""
    if specific_server is None:
        return mcp_dict
    return {k: v for k, v in mcp_dict.items() if k == specific_server}


def filter_models_by_provider(provider_dict: dict, specific_model: str | None) -> dict:
    """Filter models to include only those containing the specified model ID."""
    if specific_model is None:
        return provider_dict
    
    result = {}
    for provider_key, models_list in provider_dict.items():
        filtered_models = [m for m in models_list if specific_model in m.get("id", "")]
        if filtered_models:
            result[provider_key] = filtered_models
    
    return result


def filter_opencode_models_by_id(provider_dict: dict, specific_model: str | None) -> dict:
    """Filter OpenCode models to include only the specified model."""
    if specific_model is None:
        return provider_dict
    
    result = {}
    for provider_key, provider_data in provider_dict.items():
        models = provider_data.get("models", {})
        filtered = {k: v for k, v in models.items() if specific_model in k}
        if filtered:
            result[provider_key] = {"models": filtered, **{k: v for k, v in provider_data.items() if k != "models"}}
    
    return result
