"""
Diff functions for comparing configuration files.
"""

from typing import Any


def get_mcp_keys_gemini(data: dict) -> dict:
    """Get MCP servers from Gemini format."""
    return data.get("mcpServers", {})


def get_mcp_keys_opencode(data: dict) -> dict:
    """Get MCP servers from OpenCode format."""
    return data.get("mcp", {})


def get_mcp_keys_kilo(data: dict) -> dict:
    """Get MCP servers from Kilo format."""
    return data.get("mcp", {})


def get_mcp_keys_qwen(data: dict) -> dict:
    """Get MCP servers from Qwen format."""
    return data.get("mcpServers", {})


def get_mcp_data(data: dict, fmt: str) -> dict:
    """Get MCP data based on format."""
    if fmt == "gemini":
        return get_mcp_keys_gemini(data)
    elif fmt == "opencode":
        return get_mcp_keys_opencode(data)
    elif fmt == "kilo":
        return get_mcp_keys_kilo(data)
    elif fmt == "qwen":
        return get_mcp_keys_qwen(data)
    return {}


def get_model_ids_opencode(data: dict) -> dict:
    """Get all models from OpenCode format as flat dict {model_id: (provider, model_data)}."""
    models = {}
    providers = data.get("provider", {})
    for provider_name, provider_data in providers.items():
        for model_id, model_data in provider_data.get("models", {}).items():
            models[model_id] = (provider_name, model_data)
    return models


def get_model_ids_kilo(data: dict) -> dict:
    """Get all models from Kilo format as flat dict {model_id: (provider, model_data)}."""
    return get_model_ids_opencode(data)


def get_model_ids_qwen(data: dict) -> dict:
    """Get all models from Qwen format as flat dict {model_id: (provider, model_data)}."""
    models = {}
    model_providers = data.get("modelProviders", {})
    for provider_key, models_list in model_providers.items():
        for model in models_list:
            model_id = model.get("id", "")
            if model_id:
                models[model_id] = (provider_key, model)
    return models


def get_models_data(data: dict, fmt: str) -> dict:
    """Get models data based on format."""
    if fmt == "opencode":
        return get_model_ids_opencode(data)
    elif fmt == "kilo":
        return get_model_ids_kilo(data)
    elif fmt == "qwen":
        return get_model_ids_qwen(data)
    return {}


def compute_mcp_diff_full(source_data: dict, target_data: dict,
                          source_fmt: str, target_fmt: str) -> dict:
    """
    Compute MCP servers that exist in source but not in target.
    Returns the full missing MCP servers in source format.
    """
    source_mcp = get_mcp_data(source_data, source_fmt)
    target_mcp = get_mcp_data(target_data, target_fmt)
    
    source_keys = set(source_mcp.keys())
    target_keys = set(target_mcp.keys())
    
    missing_keys = source_keys - target_keys
    
    # Return missing servers in source format
    missing = {k: v for k, v in source_mcp.items() if k in missing_keys}
    return missing


def compute_model_diff_full(source_data: dict, target_data: dict,
                            source_fmt: str, target_fmt: str) -> dict:
    """
    Compute models that exist in source but not in target.
    Returns the full missing models in source format.
    For OpenCode: returns {provider_name: {model_id: model_data}}
    For Qwen: returns {provider_key: [model_list]}
    """
    source_models = get_models_data(source_data, source_fmt)
    target_models = get_models_data(target_data, target_fmt)
    
    source_ids = set(source_models.keys())
    target_ids = set(target_models.keys())
    
    missing_ids = source_ids - target_ids
    
    if source_fmt == "opencode":
        # Group by provider
        missing_by_provider = {}
        for model_id, (provider_name, model_data) in source_models.items():
            if model_id in missing_ids:
                if provider_name not in missing_by_provider:
                    missing_by_provider[provider_name] = {}
                missing_by_provider[provider_name][model_id] = model_data
        return missing_by_provider
    
    elif source_fmt == "qwen":
        # Group by provider key
        missing_by_provider = {}
        for model_id, (provider_key, model_data) in source_models.items():
            if model_id in missing_ids:
                if provider_key not in missing_by_provider:
                    missing_by_provider[provider_key] = []
                missing_by_provider[provider_key].append(model_data)
        return missing_by_provider
    
    return {}
