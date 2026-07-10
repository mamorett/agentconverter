"""
Main conversion orchestrator for agent configuration files.

Handles full file conversion and section-specific conversion between formats.
"""

from typing import Any

from .format_detection import detect_format
from . import mcp_converters
from . import model_converters
from .utils import filter_mcp_servers, filter_opencode_models_by_id


def convert_full_file(data: dict, source_format: str, target_format: str) -> dict:
    """Convert a full configuration file from source to target format."""
    if target_format == "gemini":
        return convert_to_gemini(data, source_format)
    elif target_format == "opencode":
        return convert_to_opencode(data, source_format)
    elif target_format == "qwen":
        return convert_to_qwen(data, source_format)
    elif target_format == "kilo":
        return convert_to_kilo(data, source_format)
    elif target_format == "nanobot":
        return convert_to_nanobot(data, source_format)
    elif target_format == "hermes":
        return convert_to_hermes(data, source_format)
    elif target_format == "configmappo":
        return convert_to_configmappo(data, source_format)
    elif target_format == "vibe":
        return convert_to_vibe(data, source_format)
    else:
        raise ValueError(f"Unknown target format: {target_format}")


def convert_to_gemini(data: dict, source_format: str) -> dict:
    """Convert to Gemini format."""
    result = {}
    
    # MCP conversion
    if source_format == "gemini" and "mcpServers" in data:
        result["mcpServers"] = data["mcpServers"]
    elif source_format == "opencode" and "mcp" in data:
        result["mcpServers"] = mcp_converters.opencode.from_opencode(data.get("mcp", {}))
    elif source_format == "kilo" and "mcp" in data:
        result["mcpServers"] = mcp_converters.kilo.from_kilo(data.get("mcp", {}))
    elif source_format == "qwen" and "mcpServers" in data:
        result["mcpServers"] = mcp_converters.qwen.from_qwen(data.get("mcpServers", {}))
    
    # Copy other sections that exist in Gemini
    if "security" in data:
        result["security"] = data["security"]
    if "ui" in data:
        result["ui"] = data["ui"]
    if "general" in data:
        result["general"] = data["general"]
    
    return result


def convert_to_opencode(data: dict, source_format: str) -> dict:
    """Convert to OpenCode format."""
    result = {
        "$schema": "https://opencode.ai/config.json",
        "autoupdate": True
    }

    # MCP conversion
    if source_format == "opencode" and "mcp" in data:
        result["mcp"] = data["mcp"]
    elif source_format == "kilo" and "mcp" in data:
        # Kilo to generic, then generic to opencode
        generic_mcp = mcp_converters.kilo.from_kilo(data.get("mcp", {}))
        result["mcp"] = mcp_converters.opencode.to_opencode(generic_mcp)
    elif source_format == "gemini" and "mcpServers" in data:
        # Gemini to generic, then generic to opencode
        generic_mcp = mcp_converters.gemini.from_gemini(data.get("mcpServers", {}))
        result["mcp"] = mcp_converters.opencode.to_opencode(generic_mcp)
    elif source_format == "qwen" and "mcpServers" in data:
        # Qwen to generic, then generic to opencode
        generic_mcp = mcp_converters.qwen.from_qwen(data.get("mcpServers", {}))
        result["mcp"] = mcp_converters.opencode.to_opencode(generic_mcp)

    # Models conversion
    if "provider" in data:
        if source_format == "opencode":
            result["provider"] = data["provider"]
        elif source_format == "kilo":
            result["provider"] = data["provider"]
        elif source_format == "gemini":
            result["provider"] = model_converters.gemini.from_gemini(data)
        elif source_format == "qwen":
            result["provider"] = model_converters.qwen.from_qwen(data)
    else:
        # Even if no provider in source, try to convert from Qwen modelProviders
        if source_format == "qwen" and "modelProviders" in data:
            result["provider"] = model_converters.qwen.from_qwen(data)

    return result


def convert_to_qwen(data: dict, source_format: str) -> dict:
    """Convert to Qwen format."""
    result = {
        "$version": 3
    }
    
    # MCP conversion
    if source_format == "qwen" and "mcpServers" in data:
        result["mcpServers"] = data["mcpServers"]
    elif source_format == "gemini" and "mcpServers" in data:
        result["mcpServers"] = mcp_converters.gemini.from_gemini(data.get("mcpServers", {}))
    elif source_format == "opencode" and "mcp" in data:
        result["mcpServers"] = mcp_converters.opencode.from_opencode(data.get("mcp", {}))
    elif source_format == "kilo" and "mcp" in data:
        result["mcpServers"] = mcp_converters.kilo.from_kilo(data.get("mcp", {}))
    
    # Models conversion
    if "modelProviders" in data or "provider" in data:
        if source_format == "qwen":
            result["modelProviders"] = data.get("modelProviders", {})
            result["env"] = data.get("env", {})
        elif source_format == "gemini":
            result["modelProviders"] = {}
            result["env"] = {}
        elif source_format == "opencode":
            model_providers, env_vars = model_converters.opencode.from_opencode(data)
            result["modelProviders"] = model_providers
            result["env"] = env_vars
        elif source_format == "kilo":
            model_providers, env_vars = model_converters.opencode.from_opencode({"provider": data.get("provider", {})})
            result["modelProviders"] = model_providers
            if env_vars:
                result["env"] = env_vars
    
    # Copy other sections
    if "security" in data:
        result["security"] = data["security"]
    if "general" in data:
        result["general"] = data["general"]
    if "model" in data:
        result["model"] = data["model"]
    
    return result


def convert_to_kilo(data: dict, source_format: str) -> dict:
    """Convert to Kilo format (identical to OpenCode but with permission section)."""
    result = {
        "$schema": "https://opencode.ai/config.json",
        "autoupdate": True,
        "permission": {
            "bash": "allow"
        }
    }

    # MCP conversion
    if source_format == "kilo" and "mcp" in data:
        result["mcp"] = data["mcp"]
    elif source_format == "opencode" and "mcp" in data:
        # Opencode to generic, then generic to kilo
        generic_mcp = mcp_converters.opencode.from_opencode(data.get("mcp", {}))
        result["mcp"] = mcp_converters.kilo.to_kilo(generic_mcp)
    elif source_format == "gemini" and "mcpServers" in data:
        # Gemini to generic, then generic to kilo
        generic_mcp = mcp_converters.gemini.from_gemini(data.get("mcpServers", {}))
        result["mcp"] = mcp_converters.kilo.to_kilo(generic_mcp)
    elif source_format == "qwen" and "mcpServers" in data:
        # Qwen to generic, then generic to kilo
        generic_mcp = mcp_converters.qwen.from_qwen(data.get("mcpServers", {}))
        result["mcp"] = mcp_converters.kilo.to_kilo(generic_mcp)

    # Models conversion
    if "provider" in data:
        if source_format == "kilo":
            result["provider"] = data["provider"]
        elif source_format == "opencode":
            result["provider"] = data["provider"]
        elif source_format == "gemini":
            result["provider"] = model_converters.gemini.from_gemini(data)
        elif source_format == "qwen":
            result["provider"] = model_converters.qwen.from_qwen(data)
    else:
        # Even if no provider in source, try to convert from Qwen modelProviders
        if source_format == "qwen" and "modelProviders" in data:
            result["provider"] = model_converters.qwen.from_qwen(data)

    return result


def convert_to_nanobot(data: dict, source_format: str) -> dict:
    """Convert to Nanobot format (MCP + models only as per user requirement)."""
    result = {}
    
    # MCP conversion
    if source_format == "nanobot" and "tools" in data and "mcpServers" in data.get("tools", {}):
        result["tools"] = {"mcpServers": data["tools"]["mcpServers"]}
    elif source_format == "opencode" and "mcp" in data:
        result["tools"] = {"mcpServers": mcp_converters.opencode.from_opencode(data.get("mcp", {}))}
    elif source_format == "kilo" and "mcp" in data:
        result["tools"] = {"mcpServers": mcp_converters.kilo.from_kilo(data.get("mcp", {}))}
    elif source_format == "gemini" and "mcpServers" in data:
        result["tools"] = {"mcpServers": mcp_converters.gemini.from_gemini(data.get("mcpServers", {}))}
    elif source_format == "qwen" and "mcpServers" in data:
        result["tools"] = {"mcpServers": mcp_converters.qwen.from_qwen(data.get("mcpServers", {}))}
    
    # Models conversion
    if source_format == "opencode" and "provider" in data:
        provider_data = data.get("provider", {})
        nanobot_providers = model_converters.nanobot.to_nanobot(provider_data)
        if nanobot_providers:
            result["providers"] = nanobot_providers
            result["agents"] = {
                "defaults": {
                    "workspace": "~/.nanobot/workspace",
                    "model": list(nanobot_providers.keys())[0] + "/default",
                    "maxTokens": 110000,
                    "temperature": 0.7,
                    "maxToolIterations": 20,
                    "memoryWindow": 50
                }
            }
    elif source_format == "kilo" and "provider" in data:
        provider_data = data.get("provider", {})
        nanobot_providers = model_converters.nanobot.to_nanobot(provider_data)
        if nanobot_providers:
            result["providers"] = nanobot_providers
            result["agents"] = {
                "defaults": {
                    "workspace": "~/.nanobot/workspace",
                    "model": list(nanobot_providers.keys())[0] + "/default",
                    "maxTokens": 110000,
                    "temperature": 0.7,
                    "maxToolIterations": 20,
                    "memoryWindow": 50
                }
            }
    elif source_format == "qwen" and "modelProviders" in data:
        model_providers = data.get("modelProviders", {})
        provider_dict = {}
        for provider_key, models_list in model_providers.items():
            provider_dict[provider_key] = {"models": {m.get("id", ""): m for m in models_list}}
        nanobot_providers = model_converters.nanobot.to_nanobot(provider_dict)
        if nanobot_providers:
            result["providers"] = nanobot_providers
            result["agents"] = {
                "defaults": {
                    "workspace": "~/.nanobot/workspace",
                    "model": list(nanobot_providers.keys())[0] + "/default",
                    "maxTokens": 110000,
                    "temperature": 0.7,
                    "maxToolIterations": 20,
                    "memoryWindow": 50
                }
            }
    
    return result


def convert_to_hermes(data: dict, source_format: str) -> dict:
    """Convert to Hermes format (MCP + models only as per user requirement)."""
    result = {
        "toolsets": ["all"],
        "agent": {
            "max_turns": 60,
            "verbose": False,
            "reasoning_effort": "medium"
        }
    }

    # MCP conversion - Hermes uses mcp_servers dict with full configurations
    if source_format == "hermes" and "mcp_servers" in data:
        result["mcp_servers"] = data["mcp_servers"]
    elif source_format == "opencode" and "mcp" in data:
        result["mcp_servers"] = mcp_converters.hermes.to_hermes(data.get("mcp", {}))["mcp_servers"]
    elif source_format == "kilo" and "mcp" in data:
        result["mcp_servers"] = mcp_converters.hermes.to_hermes(data.get("mcp", {}))["mcp_servers"]
    elif source_format == "gemini" and "mcpServers" in data:
        result["mcp_servers"] = mcp_converters.hermes.to_hermes(data.get("mcpServers", {}))["mcp_servers"]
    elif source_format == "qwen" and "mcpServers" in data:
        result["mcp_servers"] = mcp_converters.hermes.to_hermes(data.get("mcpServers", {}))["mcp_servers"]

    # Models conversion
    if source_format == "opencode" and "provider" in data:
        provider_data = data.get("provider", {})
        hermes_models = model_converters.opencode.to_opencode(provider_data)
        hermes_models = model_converters.hermes.to_hermes(hermes_models)
        if hermes_models.get("model"):
            result["model"] = hermes_models["model"]
            result["provider"] = hermes_models["provider"]
    elif source_format == "kilo" and "provider" in data:
        provider_data = data.get("provider", {})
        hermes_models = model_converters.opencode.to_opencode(provider_data)
        hermes_models = model_converters.hermes.to_hermes(hermes_models)
        if hermes_models.get("model"):
            result["model"] = hermes_models["model"]
            result["provider"] = hermes_models["provider"]
    elif source_format == "qwen" and "modelProviders" in data:
        model_providers = data.get("modelProviders", {})
        provider_dict = {}
        for provider_key, models_list in model_providers.items():
            provider_dict[provider_key] = {"models": {m.get("id", ""): m for m in models_list}}
        hermes_models = model_converters.hermes.to_hermes(provider_dict)
        if hermes_models.get("model"):
            result["model"] = hermes_models["model"]
            result["provider"] = hermes_models["provider"]

    return result


def convert_to_configmappo(data: dict, source_format: str) -> str:
    """Convert models section to LiteLLM ConfigMap YAML format (one-way only)."""
    # ConfigMap format is models-only, one-way conversion
    return convert_models_to_configmappo(data, source_format, None)


def convert_to_vibe(data: dict, source_format: str) -> str:
    """Convert to Vibe format (TOML string output)."""
    # 1. MCP conversion
    mcp_generic = {}
    if source_format == "gemini" and "mcpServers" in data:
        mcp_generic = mcp_converters.gemini.from_gemini(data.get("mcpServers", {}))
    elif source_format == "opencode" and "mcp" in data:
        mcp_generic = mcp_converters.opencode.from_opencode(data.get("mcp", {}))
    elif source_format == "kilo" and "mcp" in data:
        mcp_generic = mcp_converters.kilo.from_kilo(data.get("mcp", {}))
    elif source_format == "qwen" and "mcpServers" in data:
        mcp_generic = mcp_converters.qwen.from_qwen(data.get("mcpServers", {}))

    mcp_vibe = mcp_converters.vibe.to_vibe(mcp_generic)

    # 2. Models & Providers conversion
    provider_data = {}
    if source_format == "opencode" and "provider" in data:
        provider_data = data.get("provider", {})
    elif source_format == "kilo" and "provider" in data:
        provider_data = data.get("provider", {})
    elif source_format == "qwen" and "modelProviders" in data:
        model_providers = data.get("modelProviders", {})
        provider_dict = {}
        for provider_key, models_list in model_providers.items():
            # If Qwen modelProviders list is a direct array or {models: [...]}:
            if isinstance(models_list, dict):
                models_list = models_list.get("models", [])
            provider_dict[provider_key] = {"models": {m.get("id", ""): m for m in models_list if isinstance(m, dict)}}
        provider_data = provider_dict

    models_vibe = model_converters.vibe.to_vibe(provider_data)

    # 3. Build top-level and general settings
    result = {}
    if mcp_vibe:
        result["mcp_servers"] = mcp_vibe

    if models_vibe:
        result["providers"] = models_vibe.get("providers", [])
        result["models"] = models_vibe.get("models", [])
        if "active_model" in models_vibe:
            result["active_model"] = models_vibe["active_model"]

    # Set default agent
    result["default_agent"] = "plan"

    # Map settings from source formats
    if source_format in ["opencode", "kilo"] and "autoupdate" in data:
        result["enable_auto_update"] = data["autoupdate"]

    # Map general settings from Gemini or Qwen if present
    general = data.get("general", {})
    if isinstance(general, dict):
        if "enable_auto_update" in general:
            result["enable_auto_update"] = general["enable_auto_update"]
        if "enable_notifications" in general:
            result["enable_notifications"] = general["enable_notifications"]
        if "enable_telemetry" in general:
            result["enable_telemetry"] = general["enable_telemetry"]

    # Return as TOML string
    return model_converters.vibe.to_vibe_toml(result)


def convert_section_only(
    data: dict,
    source_format: str,
    target_format: str,
    section: str,
    specific_item: str | None = None
) -> dict:
    """Convert only a specific section (mcp or models) with optional item filter."""
    if section == "mcp":
        return convert_mcp_section(data, source_format, target_format, specific_item)
    elif section == "models":
        return convert_models_section(data, source_format, target_format, specific_item)
    else:
        raise ValueError(f"Unknown section: {section}. Use 'mcp' or 'models'.")


def convert_mcp_section(
    data: dict,
    source_format: str,
    target_format: str,
    specific_server: str | None = None
) -> dict:
    """Convert only the MCP section."""
    if source_format == "gemini":
        mcp_data = data.get("mcpServers", {})
    elif source_format == "opencode":
        mcp_data = data.get("mcp", {})
    elif source_format == "kilo":
        mcp_data = data.get("mcp", {})
    elif source_format == "qwen":
        mcp_data = data.get("mcpServers", {})
    else:
        mcp_data = {}
    
    mcp_data = filter_mcp_servers(mcp_data, specific_server)

    if target_format == "nanobot":
        return mcp_converters.nanobot.to_nanobot(mcp_data)
    elif target_format == "hermes":
        # Hermes MCP format uses mcp_servers dict with full configurations
        return mcp_converters.hermes.to_hermes(mcp_data)
    elif target_format == "vibe":
        if source_format == "gemini":
            generic_mcp = mcp_converters.gemini.from_gemini(mcp_data)
        elif source_format == "opencode":
            generic_mcp = mcp_converters.opencode.from_opencode(mcp_data)
        elif source_format == "kilo":
            generic_mcp = mcp_converters.kilo.from_kilo(mcp_data)
        elif source_format == "qwen":
            generic_mcp = mcp_converters.qwen.from_qwen(mcp_data)
        else:
            generic_mcp = mcp_data
        mcp_vibe = mcp_converters.vibe.to_vibe(generic_mcp)
        return model_converters.vibe.to_vibe_toml({"mcp_servers": mcp_vibe})
    elif target_format == "gemini":
        if source_format == "gemini":
            return {"mcpServers": mcp_data}
        elif source_format == "opencode":
            return {"mcpServers": mcp_converters.opencode.from_opencode(mcp_data)}
        elif source_format == "kilo":
            return {"mcpServers": mcp_converters.kilo.from_kilo(mcp_data)}
        elif source_format == "qwen":
            return {"mcpServers": mcp_converters.qwen.from_qwen(mcp_data)}
    elif target_format == "opencode":
        if source_format == "gemini":
            # Gemini to generic, then generic to opencode
            generic_mcp = mcp_converters.gemini.from_gemini(mcp_data)
            return {"mcp": mcp_converters.opencode.to_opencode(generic_mcp)}
        elif source_format == "opencode":
            return {"mcp": mcp_data}
        elif source_format == "kilo":
            # Kilo to generic, then generic to opencode
            generic_mcp = mcp_converters.kilo.from_kilo(mcp_data)
            return {"mcp": mcp_converters.opencode.to_opencode(generic_mcp)}
        elif source_format == "qwen":
            # Qwen to generic, then generic to opencode
            generic_mcp = mcp_converters.qwen.from_qwen(mcp_data)
            return {"mcp": mcp_converters.opencode.to_opencode(generic_mcp)}
    elif target_format == "qwen":
        if source_format == "gemini":
            return {"mcpServers": mcp_converters.gemini.from_gemini(mcp_data)}
        elif source_format == "opencode":
            return {"mcpServers": mcp_converters.opencode.from_opencode(mcp_data)}
        elif source_format == "kilo":
            return {"mcpServers": mcp_converters.kilo.from_kilo(mcp_data)}
        elif source_format == "qwen":
            return {"mcpServers": mcp_data}
    elif target_format == "kilo":
        if source_format == "gemini":
            return {"mcp": mcp_converters.gemini.from_gemini(mcp_data)}
        elif source_format == "opencode":
            return {"mcp": mcp_converters.opencode.from_opencode(mcp_data)}
        elif source_format == "kilo":
            return {"mcp": mcp_data}
        elif source_format == "qwen":
            return {"mcp": mcp_converters.qwen.from_qwen(mcp_data)}
    elif target_format == "kilo":
        if source_format == "gemini":
            # Gemini to generic, then generic to kilo
            generic_mcp = mcp_converters.gemini.from_gemini(mcp_data)
            return {"mcp": mcp_converters.kilo.to_kilo(generic_mcp)}
        elif source_format == "opencode":
            # Opencode to generic, then generic to kilo
            generic_mcp = mcp_converters.opencode.from_opencode(mcp_data)
            return {"mcp": mcp_converters.kilo.to_kilo(generic_mcp)}
        elif source_format == "kilo":
            return {"mcp": mcp_data}
        elif source_format == "qwen":
            # Qwen to generic, then generic to kilo
            generic_mcp = mcp_converters.qwen.from_qwen(mcp_data)
            return {"mcp": mcp_converters.kilo.to_kilo(generic_mcp)}

    return {}


def convert_models_section(
    data: dict,
    source_format: str,
    target_format: str,
    specific_model: str | None = None
) -> dict:
    """Convert only the models section."""
    if target_format == "nanobot":
        return convert_models_to_nanobot(data, source_format, specific_model)
    elif target_format == "hermes":
        return convert_models_to_hermes(data, source_format, specific_model)
    elif target_format == "configmappo":
        return convert_models_to_configmappo(data, source_format, specific_model)
    elif target_format == "vibe":
        return convert_models_to_vibe(data, source_format, specific_model)

    if source_format == "gemini":
        return {}
    elif source_format == "opencode":
        models_data = data.get("provider", {})
        models_data = filter_opencode_models_by_id(models_data, specific_model)

        if target_format == "gemini":
            return {}
        elif target_format == "opencode":
            return {"provider": models_data}
        elif target_format == "kilo":
            return {"provider": models_data}
        elif target_format == "qwen":
            model_providers, env_vars = model_converters.opencode.from_opencode({"provider": models_data})
            result = {"modelProviders": model_providers}
            if env_vars:
                result["env"] = env_vars
            return result
    elif source_format == "kilo":
        models_data = data.get("provider", {})
        models_data = filter_opencode_models_by_id(models_data, specific_model)

        if target_format == "gemini":
            return {}
        elif target_format == "opencode":
            return {"provider": models_data}
        elif target_format == "kilo":
            return {"provider": models_data}
        elif target_format == "qwen":
            model_providers, env_vars = model_converters.opencode.from_opencode({"provider": models_data})
            result = {"modelProviders": model_providers}
            if env_vars:
                result["env"] = env_vars
            return result
    elif source_format == "qwen":
        model_providers = data.get("modelProviders", {})
        # Note: filter_models_by_provider is not used here as it filters by provider_key, not model ID
        # Keep all providers for now

        if target_format == "gemini":
            return {}
        elif target_format == "opencode":
            provider = model_converters.qwen.from_qwen({"modelProviders": model_providers, "env": data.get("env", {})})
            return {"provider": provider}
        elif target_format == "kilo":
            provider = model_converters.qwen.from_qwen({"modelProviders": model_providers, "env": data.get("env", {})})
            return {"provider": provider}
        elif target_format == "qwen":
            return {"modelProviders": model_providers}

    return {}


def convert_models_to_nanobot(
    data: dict,
    source_format: str,
    specific_model: str | None = None
) -> dict:
    """Convert models section to Nanobot format."""
    # Get provider data based on source format
    if source_format == "opencode":
        provider_data = data.get("provider", {})
        provider_data = filter_opencode_models_by_id(provider_data, specific_model)
        nanobot_providers = model_converters.nanobot.to_nanobot(provider_data)
    elif source_format == "kilo":
        provider_data = data.get("provider", {})
        provider_data = filter_opencode_models_by_id(provider_data, specific_model)
        nanobot_providers = model_converters.nanobot.to_nanobot(provider_data)
    elif source_format == "qwen":
        model_providers = data.get("modelProviders", {})
        # Reconstruct provider dict for conversion
        provider_dict = {}
        for provider_key, models_list in model_providers.items():
            provider_dict[provider_key] = {"models": {m.get("id", ""): m for m in models_list}}
        nanobot_providers = model_converters.nanobot.to_nanobot(provider_dict)
    else:
        nanobot_providers = {}
    
    # Return as providers structure with defaults
    result = {"providers": nanobot_providers}
    
    # Add default agent settings
    if nanobot_providers:
        result["agents"] = {
            "defaults": {
                "workspace": "~/.nanobot/workspace",
                "model": list(nanobot_providers.keys())[0] + "/default",
                "maxTokens": 110000,
                "temperature": 0.7,
                "maxToolIterations": 20,
                "memoryWindow": 50
            }
        }
    
    return result


def convert_models_to_hermes(
    data: dict,
    source_format: str,
    specific_model: str | None = None
) -> dict:
    """Convert models section to Hermes format."""
    # Get provider data based on source format
    if source_format == "opencode":
        provider_data = data.get("provider", {})
        provider_data = filter_opencode_models_by_id(provider_data, specific_model)
        hermes_models = model_converters.hermes.to_hermes(provider_data)
    elif source_format == "kilo":
        provider_data = data.get("provider", {})
        provider_data = filter_opencode_models_by_id(provider_data, specific_model)
        hermes_models = model_converters.hermes.to_hermes(provider_data)
    elif source_format == "qwen":
        model_providers = data.get("modelProviders", {})
        # Reconstruct provider dict for conversion
        provider_dict = {}
        for provider_key, models_list in model_providers.items():
            provider_dict[provider_key] = {"models": {m.get("id", ""): m for m in models_list}}
        hermes_models = model_converters.hermes.to_hermes(provider_dict)
    else:
        hermes_models = {"model": {}, "provider": {}}
    
    # Return as model structure with defaults
    result = {
        "model": hermes_models.get("model", {}),
        "provider": hermes_models.get("provider", ""),
        "toolsets": ["all"],
        "agent": {
            "max_turns": 60,
            "verbose": False,
            "reasoning_effort": "medium"
        }
    }

    return result


def convert_models_to_configmappo(
    data: dict,
    source_format: str,
    specific_model: str | None = None
) -> str:
    """Convert models section to LiteLLM ConfigMap YAML format (one-way only)."""
    # Get provider data based on source format
    if source_format == "opencode":
        provider_data = data.get("provider", {})
        provider_data = filter_opencode_models_by_id(provider_data, specific_model)
    elif source_format == "kilo":
        provider_data = data.get("provider", {})
        provider_data = filter_opencode_models_by_id(provider_data, specific_model)
    elif source_format == "qwen":
        model_providers = data.get("modelProviders", {})
        # Qwen format: {provider_key: {models: [model_obj, ...]}}
        # Group models by baseUrl for ConfigMap
        providers_by_url = {}
        for provider_key, provider_data_item in model_providers.items():
            # Handle both {models: [...]} and direct list formats
            if isinstance(provider_data_item, dict):
                models_list = provider_data_item.get("models", [])
            else:
                models_list = provider_data_item
            for model in models_list:
                if not isinstance(model, dict):
                    continue
                base_url = model.get("baseUrl", "")
                if not base_url:
                    continue
                if base_url not in providers_by_url:
                    providers_by_url[base_url] = {"models": {}, "npm": "@ai-sdk/openai-compatible"}
                model_id = model.get("id", "")
                if specific_model and model_id != specific_model:
                    continue
                providers_by_url[base_url]["models"][model_id] = model
        # Convert to provider dict format
        provider_dict = {}
        for idx, (base_url, info) in enumerate(providers_by_url.items()):
            provider_name = f"provider_{idx}"
            provider_dict[provider_name] = {
                "models": info["models"],
                "options": {"baseURL": base_url},
                "npm": info["npm"]
            }
        provider_data = provider_dict
    else:
        provider_data = {}

    # Convert to ConfigMap YAML format
    yaml_output = model_converters.configmappo.to_configmappo({"provider": provider_data})
    return yaml_output


def convert_models_to_vibe(
    data: dict,
    source_format: str,
    specific_model: str | None = None
) -> str:
    """Convert models section to Vibe format."""
    # Get provider data based on source format
    if source_format == "opencode":
        provider_data = data.get("provider", {})
        provider_data = filter_opencode_models_by_id(provider_data, specific_model)
    elif source_format == "kilo":
        provider_data = data.get("provider", {})
        provider_data = filter_opencode_models_by_id(provider_data, specific_model)
    elif source_format == "qwen":
        model_providers = data.get("modelProviders", {})
        # Reconstruct provider dict for conversion
        provider_dict = {}
        for provider_key, models_list in model_providers.items():
            if isinstance(models_list, dict):
                models_list = models_list.get("models", [])
            provider_dict[provider_key] = {"models": {m.get("id", ""): m for m in models_list if isinstance(m, dict)}}
        provider_data = provider_dict
    else:
        provider_data = {}

    models_vibe = model_converters.vibe.to_vibe(provider_data)

    # We want only the providers, models, and active_model in the TOML output
    result = {}
    if models_vibe:
        result["providers"] = models_vibe.get("providers", [])
        result["models"] = models_vibe.get("models", [])
        if "active_model" in models_vibe:
            result["active_model"] = models_vibe["active_model"]

    return model_converters.vibe.to_vibe_toml(result)
