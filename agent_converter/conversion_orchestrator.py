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
        result["mcp"] = mcp_converters.kilo.from_kilo(data.get("mcp", {}))
    elif source_format == "gemini" and "mcpServers" in data:
        result["mcp"] = mcp_converters.gemini.from_gemini(data.get("mcpServers", {}))
    elif source_format == "qwen" and "mcpServers" in data:
        result["mcp"] = mcp_converters.qwen.from_qwen(data.get("mcpServers", {}))
    
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
        result["mcp"] = mcp_converters.opencode.from_opencode(data.get("mcp", {}))
    elif source_format == "gemini" and "mcpServers" in data:
        result["mcp"] = mcp_converters.gemini.from_gemini(data.get("mcpServers", {}))
    elif source_format == "qwen" and "mcpServers" in data:
        result["mcp"] = mcp_converters.qwen.from_qwen(data.get("mcpServers", {}))
    
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

    # MCP conversion - Hermes uses a list of server names
    if source_format == "hermes" and "tools" in data and "mcpServers" in data.get("tools", {}):
        result["tools"] = {"mcpServers": data["tools"]["mcpServers"]}
    elif source_format == "opencode" and "mcp" in data:
        result["tools"] = mcp_converters.hermes.to_hermes(data.get("mcp", {}))
    elif source_format == "kilo" and "mcp" in data:
        result["tools"] = mcp_converters.hermes.to_hermes(data.get("mcp", {}))
    elif source_format == "gemini" and "mcpServers" in data:
        result["tools"] = mcp_converters.hermes.to_hermes(data.get("mcpServers", {}))
    elif source_format == "qwen" and "mcpServers" in data:
        result["tools"] = mcp_converters.hermes.to_hermes(data.get("mcpServers", {}))
    
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
        # Hermes MCP format is a list, wrap it in tools structure
        return {"tools": {"mcpServers": mcp_converters.hermes.to_hermes(mcp_data)}}
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
            return {"mcp": mcp_converters.gemini.from_gemini(mcp_data)}
        elif source_format == "opencode":
            return {"mcp": mcp_data}
        elif source_format == "kilo":
            return {"mcp": mcp_converters.kilo.from_kilo(mcp_data)}
        elif source_format == "qwen":
            return {"mcp": mcp_converters.qwen.from_qwen(mcp_data)}
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
