"""
Model conversion functions for Vibe format.

This is a one-way conversion only (to Vibe format).
"""

from typing import Any


def format_toml_value(v: Any) -> str:
    """Format a python value to its TOML representation."""
    if isinstance(v, bool):
        return "true" if v else "false"
    elif isinstance(v, (int, float)):
        return str(v)
    elif isinstance(v, str):
        # escape backslashes and double quotes
        escaped = v.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    elif isinstance(v, list):
        items = [format_toml_value(item) for item in v]
        return "[" + ", ".join(items) + "]"
    elif isinstance(v, dict):
        # inline table
        items = []
        for k, val in v.items():
            items.append(f'{k} = {format_toml_value(val)}')
        return "{" + ", ".join(items) + "}"
    else:
        return str(v)


def to_vibe_toml(data: dict) -> str:
    """Serialize a dictionary of vibe configurations to TOML string."""
    lines = []

    # 1. Write top-level scalar and array fields
    top_level_fields = [
        "default_agent",
        "active_model",
        "skill_paths",
        "enabled_skills",
        "disabled_skills",
        "enabled_tools",
        "disabled_tools",
        "enable_auto_update",
        "enable_notifications",
        "enable_telemetry"
    ]

    for field in top_level_fields:
        if field in data and data[field] is not None:
            lines.append(f"{field} = {format_toml_value(data[field])}")

    # Add a newline if we wrote any top-level fields
    if lines:
        lines.append("")

    # 2. Write [[providers]]
    if "providers" in data and isinstance(data["providers"], list):
        for provider in data["providers"]:
            lines.append("[[providers]]")
            for k, v in provider.items():
                if v is not None:
                    lines.append(f"{k} = {format_toml_value(v)}")
            lines.append("")

    # 3. Write [[models]]
    if "models" in data and isinstance(data["models"], list):
        for model in data["models"]:
            lines.append("[[models]]")
            for k, v in model.items():
                if v is not None:
                    lines.append(f"{k} = {format_toml_value(v)}")
            lines.append("")

    # 4. Write [[mcp_servers]]
    if "mcp_servers" in data and isinstance(data["mcp_servers"], list):
        for mcp in data["mcp_servers"]:
            lines.append("[[mcp_servers]]")
            for k, v in mcp.items():
                if v is not None:
                    lines.append(f"{k} = {format_toml_value(v)}")
            lines.append("")

    # Join with newlines and clean up trailing/duplicate blank lines
    output = "\n".join(lines).strip()
    if output:
        output += "\n"
    return output


def to_vibe(provider_data: dict) -> dict:
    """
    Convert generic provider data to Vibe format (providers and models lists).

    Args:
        provider_data: Generic provider data with models

    Returns:
        Dict in Vibe format containing 'providers' and 'models' keys
    """
    vibe_providers = []
    vibe_models = []

    for provider_name, provider_info in provider_data.items():
        base_url = ""
        models_dict = {}
        if isinstance(provider_info, dict):
            base_url = provider_info.get("options", {}).get("baseURL", "")
            models_dict = provider_info.get("models", {})

        # Generate environment variable name for api key
        normalized = provider_name.upper().replace(" ", "_").replace("-", "_")
        api_key_env_var = f"{normalized}_API_KEY"

        provider_entry = {
            "name": provider_name,
            "api_base": base_url if base_url else "",
            "api_key_env_var": api_key_env_var,
            "api_style": "openai",
            "backend": "generic"
        }
        vibe_providers.append(provider_entry)

        for model_id, model_info in models_dict.items():
            model_entry = {
                "name": model_id,
                "provider": provider_name,
                "alias": model_id
            }
            if isinstance(model_info, dict) and "temperature" in model_info:
                model_entry["temperature"] = model_info["temperature"]

            vibe_models.append(model_entry)

    result = {
        "providers": vibe_providers,
        "models": vibe_models
    }
    if vibe_models:
        result["active_model"] = vibe_models[0]["alias"]

    return result


def from_vibe(vibe_data: Any) -> dict:
    """
    Convert Vibe format to generic format.
    Not implemented as Vibe is one-way only.
    """
    raise NotImplementedError("Vibe format is one-way conversion only (to Vibe)")
