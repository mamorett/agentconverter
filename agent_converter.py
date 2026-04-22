#!/usr/bin/env python3
"""
Agent Configuration Converter

Converts between Gemini, OpenCode, and Qwen configuration formats.
Supports full file conversion or selective conversion of MCP servers or models.
"""

import argparse
import json
import sys
from copy import deepcopy
from typing import Any


# ============================================================================
# Format Detection
# ============================================================================

def detect_format(data: dict) -> str:
    """Detect the configuration format from the data structure."""
    # Nanobot detection: has "agents" and "providers" and "gateway"
    if "agents" in data and "providers" in data and "gateway" in data:
        return "nanobot"
    # Hermes detection: has "model" with "default" and "toolsets" array
    if "model" in data and isinstance(data.get("model"), dict) and "toolsets" in data:
        return "hermes"
    if "provider" in data and "mcp" in data:
        # Distinguish between opencode and kilo by checking for "permission" key
        if "permission" in data:
            return "kilo"
        return "opencode"
    elif "modelProviders" in data:
        return "qwen"
    elif "mcpServers" in data and "provider" not in data and "modelProviders" not in data:
        return "gemini"
    else:
        # Fallback detection
        if "mcpServers" in data:
            return "gemini"
        elif "mcp" in data and "provider" in data:
            if "permission" in data:
                return "kilo"
            return "opencode"
        elif "modelProviders" in data:
            return "qwen"
    return "unknown"


# ============================================================================
# MCP Conversion Functions
# ============================================================================

def mcp_gemini_to_opencode(gemini_mcp: dict) -> dict:
    """Convert Gemini MCP format to OpenCode format."""
    result = {}
    for name, config in gemini_mcp.items():
        # Handle disabled servers (remove _disabled suffix)
        clean_name = name.replace("_disabled", "")
        
        # Build command array: command + args
        command = []
        if isinstance(config.get("command"), str):
            command.append(config["command"])
        if isinstance(config.get("args"), list):
            command.extend(config["args"])
        
        entry = {
            "command": command,
            "type": "local"
        }
        
        # Add environment if present
        if config.get("env"):
            entry["environment"] = dict(config["env"])
        
        result[clean_name] = entry
    
    return result


def mcp_opencode_to_gemini(opencode_mcp: dict) -> dict:
    """Convert OpenCode MCP format to Gemini format."""
    result = {}
    for name, config in opencode_mcp.items():
        command = config.get("command", [])
        
        # Split command into command (first element) and args (rest)
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
        
        # Add environment if present (OpenCode uses 'environment', Gemini uses 'env')
        if config.get("environment"):
            entry["env"] = dict(config["environment"])
        
        result[name] = entry
    
    return result


def mcp_gemini_to_qwen(gemini_mcp: dict) -> dict:
    """Convert Gemini MCP format to Qwen format."""
    # Qwen format for MCP is the same as Gemini
    result = {}
    for name, config in gemini_mcp.items():
        entry = {
            "command": config.get("command", ""),
            "args": list(config.get("args", []))
        }
        
        if config.get("env"):
            entry["env"] = dict(config["env"])
        
        result[name] = entry
    
    return result


def mcp_qwen_to_gemini(qwen_mcp: dict) -> dict:
    """Convert Qwen MCP format to Gemini format."""
    # Qwen format for MCP is the same as Gemini
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


def mcp_opencode_to_qwen(opencode_mcp: dict) -> dict:
    """Convert OpenCode MCP format to Qwen format."""
    result = {}
    for name, config in opencode_mcp.items():
        command = config.get("command", [])
        
        # Split command into command (first element) and args (rest)
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
        
        if config.get("environment"):
            entry["env"] = dict(config["environment"])
        
        result[name] = entry
    
    return result


def mcp_qwen_to_opencode(qwen_mcp: dict) -> dict:
    """Convert Qwen MCP format to OpenCode format."""
    result = {}
    for name, config in qwen_mcp.items():
        # Build command array: command + args
        command = []
        if isinstance(config.get("command"), str):
            command.append(config["command"])
        if isinstance(config.get("args"), list):
            command.extend(config["args"])

        entry = {
            "command": command,
            "type": "local"
        }

        if config.get("env"):
            entry["environment"] = dict(config["env"])

        result[name] = entry

    return result


# ============================================================================
# Kilo MCP Conversion Functions (Kilo format is identical to OpenCode)
# ============================================================================

def mcp_opencode_to_kilo(opencode_mcp: dict) -> dict:
    """Convert OpenCode MCP format to Kilo format (identical)."""
    return dict(opencode_mcp)


def mcp_kilo_to_opencode(kilo_mcp: dict) -> dict:
    """Convert Kilo MCP format to OpenCode format (identical)."""
    return dict(kilo_mcp)


def mcp_gemini_to_kilo(gemini_mcp: dict) -> dict:
    """Convert Gemini MCP format to Kilo format."""
    return mcp_gemini_to_opencode(gemini_mcp)


def mcp_kilo_to_gemini(kilo_mcp: dict) -> dict:
    """Convert Kilo MCP format to Gemini format."""
    return mcp_opencode_to_gemini(kilo_mcp)


def mcp_qwen_to_kilo(qwen_mcp: dict) -> dict:
    """Convert Qwen MCP format to Kilo format."""
    return mcp_qwen_to_opencode(qwen_mcp)


def mcp_kilo_to_qwen(kilo_mcp: dict) -> dict:
    """Convert Kilo MCP format to Qwen format."""
    return mcp_opencode_to_qwen(kilo_mcp)


# ============================================================================
# Nanobot MCP Conversion Functions
# ============================================================================

def mcp_to_nanobot(mcp_data: dict) -> dict:
    """
    Convert generic MCP format to Nanobot mcpServers structure.
    Nanobot uses mcpServers under tools section with command, args, env.
    """
    result = {}
    for name, config in mcp_data.items():
        command = config.get("command", [])
        
        # Split command into command (first element) and args (rest)
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
        if config.get("env"):
            entry["env"] = dict(config["env"])
        elif config.get("environment"):
            entry["env"] = dict(config["environment"])

        result[name] = entry

    return result


def mcp_gemini_to_nanobot(gemini_mcp: dict) -> dict:
    """Convert Gemini MCP format to Nanobot format."""
    return mcp_to_nanobot(gemini_mcp)


def mcp_opencode_to_nanobot(opencode_mcp: dict) -> dict:
    """Convert OpenCode MCP format to Nanobot format."""
    return mcp_to_nanobot(opencode_mcp)


def mcp_qwen_to_nanobot(qwen_mcp: dict) -> dict:
    """Convert Qwen MCP format to Nanobot format."""
    return mcp_to_nanobot(qwen_mcp)


def mcp_kilo_to_nanobot(kilo_mcp: dict) -> dict:
    """Convert Kilo MCP format to Nanobot format."""
    return mcp_to_nanobot(kilo_mcp)


# ============================================================================
# Hermes MCP Conversion Functions
# ============================================================================

def mcp_to_hermes(mcp_data: dict) -> list:
    """
    Convert generic MCP format to Hermes MCP server list.
    Hermes stores MCP servers as a flat list of server names in tools.mcpServers.
    """
    # Hermes format is a simple list of enabled MCP server names
    return list(mcp_data.keys())


def mcp_gemini_to_hermes(gemini_mcp: dict) -> list:
    """Convert Gemini MCP format to Hermes format (list of server names)."""
    return mcp_to_hermes(gemini_mcp)


def mcp_opencode_to_hermes(opencode_mcp: dict) -> list:
    """Convert OpenCode MCP format to Hermes format."""
    return mcp_to_hermes(opencode_mcp)


def mcp_qwen_to_hermes(qwen_mcp: dict) -> list:
    """Convert Qwen MCP format to Hermes format."""
    return mcp_to_hermes(qwen_mcp)


def mcp_kilo_to_hermes(kilo_mcp: dict) -> list:
    """Convert Kilo MCP format to Hermes format."""
    return mcp_to_hermes(kilo_mcp)


# ============================================================================
# Model Conversion Functions
# ============================================================================

def extract_baseurl_from_opencode_provider(provider_data: dict) -> str:
    """Extract baseURL from OpenCode provider data."""
    return provider_data.get("options", {}).get("baseURL", "")


def extract_envkey_from_provider_name(provider_name: str) -> str:
    """Generate env key from provider name."""
    normalized = provider_name.upper().replace(" ", "_").replace("-", "_")
    return f"{normalized}_API_KEY"


def models_opencode_to_qwen(opencode_data: dict) -> tuple[dict, dict]:
    """
    Convert OpenCode provider/models format to Qwen modelProviders format.
    Returns (modelProviders dict, env dict).
    """
    model_providers = {"openai": []}
    env_vars = {}
    
    providers = opencode_data.get("provider", {})
    
    for provider_name, provider_data in providers.items():
        base_url = extract_baseurl_from_opencode_provider(provider_data)
        env_key = extract_envkey_from_provider_name(provider_name)
        
        # Add env var with default value
        env_vars[env_key] = "not-needed"
        
        models_dict = provider_data.get("models", {})
        for model_id, model_data in models_dict.items():
            model_entry = {
                "id": model_id,
                "name": model_data.get("name", model_id),
                "envKey": env_key,
                "baseUrl": base_url
            }
            
            # Handle modalities (OpenCode: input/output arrays -> Qwen: image boolean)
            modalities = model_data.get("modalities", {})
            if modalities:
                input_modalities = modalities.get("input", [])
                has_image_input = "image" in input_modalities
                if has_image_input:
                    model_entry["generationConfig"] = {
                        "modalities": {"image": True}
                    }
            
            model_providers["openai"].append(model_entry)
    
    return model_providers, env_vars


def models_qwen_to_opencode(qwen_data: dict) -> dict:
    """Convert Qwen modelProviders format to OpenCode provider format."""
    provider = {}
    
    model_providers = qwen_data.get("modelProviders", {})
    
    # Group models by baseUrl to create providers
    providers_by_url = {}
    
    for provider_key, models_list in model_providers.items():
        for model in models_list:
            base_url = model.get("baseUrl", "")
            if not base_url:
                continue
            if base_url not in providers_by_url:
                providers_by_url[base_url] = {
                    "models": {},
                    "envKey": model.get("envKey", ""),
                    "image_models": set()
                }
            
            model_id = model.get("id", "")
            model_name = model.get("name", model_id)
            
            providers_by_url[base_url]["models"][model_id] = {
                "name": model_name
            }
            
            # Check for image modalities
            gen_config = model.get("generationConfig", {})
            modalities = gen_config.get("modalities", {})
            if modalities.get("image", False):
                providers_by_url[base_url]["image_models"].add(model_id)
    
    # Convert to OpenCode format
    for idx, (base_url, data) in enumerate(providers_by_url.items()):
        # Generate provider name from URL
        provider_name = f"provider_{idx}"
        
        provider[provider_name] = {
            "name": provider_name,
            "npm": "@ai-sdk/openai-compatible",
            "options": {
                "baseURL": base_url
            },
            "models": {}
        }
        
        for model_id, model_info in data["models"].items():
            model_entry = {"name": model_info["name"]}
            
            # Add modalities if this is an image model
            if model_id in data["image_models"]:
                model_entry["modalities"] = {
                    "input": ["text", "image"],
                    "output": ["text"]
                }
            
            provider[provider_name]["models"][model_id] = model_entry
    
    return provider


def models_gemini_to_opencode(gemini_data: dict) -> dict:
    """
    Convert Gemini format to OpenCode models.
    Gemini has no models, so returns empty provider dict.
    """
    return {}


def models_gemini_to_qwen(gemini_data: dict) -> tuple[dict, dict]:
    """
    Convert Gemini format to Qwen models.
    Gemini has no models, so returns empty dicts.
    """
    return {}, {}


def models_opencode_to_gemini(opencode_data: dict) -> dict:
    """
    Convert OpenCode models to Gemini format.
    Gemini has no models section, so returns empty dict.
    """
    return {}


def models_qwen_to_gemini(qwen_data: dict) -> dict:
    """
    Convert Qwen models to Gemini format.
    Gemini has no models section, so returns empty dict.
    """
    return {}


# ============================================================================
# Kilo Model Conversion Functions (Kilo format is identical to OpenCode)
# ============================================================================

def models_opencode_to_kilo(opencode_data: dict) -> dict:
    """Convert OpenCode provider format to Kilo format (identical)."""
    return dict(opencode_data)


def models_kilo_to_opencode(kilo_data: dict) -> dict:
    """Convert Kilo provider format to OpenCode format (identical)."""
    return dict(kilo_data)


def models_gemini_to_kilo(gemini_data: dict) -> dict:
    """
    Convert Gemini format to Kilo models.
    Gemini has no models, so returns empty dict.
    """
    return {}


def models_kilo_to_gemini(kilo_data: dict) -> dict:
    """
    Convert Kilo models to Gemini format.
    Gemini has no models section, so returns empty dict.
    """
    return {}


def models_qwen_to_kilo(qwen_data: dict) -> dict:
    """Convert Qwen modelProviders format to Kilo provider format."""
    return models_qwen_to_opencode(qwen_data)


def models_kilo_to_qwen(kilo_data: dict) -> tuple[dict, dict]:
    """Convert Kilo provider format to Qwen modelProviders format."""
    return models_opencode_to_qwen({"provider": kilo_data})


# ============================================================================
# Nanobot Model Conversion Functions
# ============================================================================

def models_to_nanobot(provider_data: dict) -> dict:
    """
    Convert generic provider format to Nanobot providers structure.
    Nanobot has providers as a dict with apiKey, apiBase, extraHeaders.
    """
    result = {}
    
    # Handle OpenCode/Kilo format (provider dict with models inside)
    for provider_name, provider_info in provider_data.items():
        # Extract base URL
        base_url = ""
        if isinstance(provider_info, dict):
            base_url = provider_info.get("options", {}).get("baseURL", "")
            models_dict = provider_info.get("models", {})
        else:
            models_dict = {}

        # Build Nanobot provider entry
        nanobot_entry = {
            "apiKey": "",  # Placeholder - user needs to fill
            "apiBase": base_url if base_url else None,
            "extraHeaders": None
        }

        # Use provider name as key, normalize to lowercase
        key = provider_name.lower().replace("_", "")
        result[key] = nanobot_entry

    return result


def models_opencode_to_nanobot(opencode_data: dict) -> dict:
    """Convert OpenCode provider format to Nanobot format."""
    return models_to_nanobot(opencode_data)


def models_kilo_to_nanobot(kilo_data: dict) -> dict:
    """Convert Kilo provider format to Nanobot format."""
    return models_to_nanobot(kilo_data)


def models_qwen_to_nanobot(qwen_data: dict) -> dict:
    """Convert Qwen modelProviders format to Nanobot format."""
    # Qwen format is different - need to extract from modelProviders
    result = {}
    model_providers = qwen_data.get("modelProviders", {})
    
    for provider_key, models_list in model_providers.items():
        if not models_list:
            continue
        
        # Get base URL from first model
        base_url = models_list[0].get("baseUrl", "") if models_list else ""
        
        nanobot_entry = {
            "apiKey": "",  # Placeholder - user needs to fill
            "apiBase": base_url if base_url else None,
            "extraHeaders": None
        }
        
        key = provider_key.lower().replace("_", "")
        result[key] = nanobot_entry

    return result


def models_gemini_to_nanobot(gemini_data: dict) -> dict:
    """
    Convert Gemini format to Nanobot models.
    Gemini has no models section, so returns empty dict.
    """
    return {}


# ============================================================================
# Hermes Model Conversion Functions
# ============================================================================

def models_to_hermes(provider_data: dict) -> dict:
    """
    Convert generic provider format to Hermes model structure.
    Hermes uses model.default for the default model and provider for provider name.
    Returns a dict with 'model' and 'provider' keys.
    """
    result = {
        "model": {},
        "provider": {}
    }
    
    if not provider_data:
        return result
    
    # Get the first available model as default
    for provider_name, provider_info in provider_data.items():
        if isinstance(provider_info, dict):
            models_dict = provider_info.get("models", {})
            if models_dict:
                # Get first model ID as default
                first_model_id = next(iter(models_dict.keys()), None)
                if first_model_id:
                    result["model"]["default"] = f"{provider_name}/{first_model_id}"
                    result["provider"] = provider_name
                    break
    
    return result


def models_opencode_to_hermes(opencode_data: dict) -> dict:
    """Convert OpenCode provider format to Hermes format."""
    return models_to_hermes(opencode_data)


def models_kilo_to_hermes(kilo_data: dict) -> dict:
    """Convert Kilo provider format to Hermes format."""
    return models_to_hermes(kilo_data)


def models_qwen_to_hermes(qwen_data: dict) -> dict:
    """Convert Qwen modelProviders format to Hermes format."""
    result = {
        "model": {},
        "provider": {}
    }
    
    model_providers = qwen_data.get("modelProviders", {})
    
    for provider_key, models_list in model_providers.items():
        if models_list:
            # Get first model ID as default
            first_model = models_list[0]
            first_model_id = first_model.get("id", "")
            if first_model_id:
                result["model"]["default"] = f"{provider_key}:{first_model_id}"
                result["provider"] = provider_key
                break
    
    return result


def models_gemini_to_hermes(gemini_data: dict) -> dict:
    """
    Convert Gemini format to Hermes models.
    Gemini has no models section, so returns empty dict.
    """
    return {
        "model": {},
        "provider": {}
    }


# ============================================================================
# Section Selection Helpers
# ============================================================================

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


# ============================================================================
# Main Conversion Logic
# ============================================================================

def convert_full_file(data: dict, source_format: str, target_format: str) -> dict:
    """Convert a full configuration file from source to target format."""
    result = {}

    if target_format == "gemini":
        result = convert_to_gemini(data, source_format)
    elif target_format == "opencode":
        result = convert_to_opencode(data, source_format)
    elif target_format == "qwen":
        result = convert_to_qwen(data, source_format)
    elif target_format == "kilo":
        result = convert_to_kilo(data, source_format)
    elif target_format == "nanobot":
        result = convert_to_nanobot(data, source_format)
    elif target_format == "hermes":
        result = convert_to_hermes(data, source_format)
    else:
        raise ValueError(f"Unknown target format: {target_format}")

    return result


def convert_to_gemini(data: dict, source_format: str) -> dict:
    """Convert to Gemini format."""
    result = {}

    # MCP conversion
    if source_format == "gemini" and "mcpServers" in data:
        result["mcpServers"] = data["mcpServers"]
    elif source_format == "opencode" and "mcp" in data:
        result["mcpServers"] = mcp_opencode_to_gemini(data.get("mcp", {}))
    elif source_format == "kilo" and "mcp" in data:
        result["mcpServers"] = mcp_kilo_to_gemini(data.get("mcp", {}))
    elif source_format == "qwen" and "mcpServers" in data:
        result["mcpServers"] = mcp_qwen_to_gemini(data.get("mcpServers", {}))

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
        result["mcp"] = mcp_kilo_to_opencode(data.get("mcp", {}))
    elif source_format == "gemini" and "mcpServers" in data:
        result["mcp"] = mcp_gemini_to_opencode(data.get("mcpServers", {}))
    elif source_format == "qwen" and "mcpServers" in data:
        result["mcp"] = mcp_qwen_to_opencode(data.get("mcpServers", {}))

    # Models conversion
    if "provider" in data:
        if source_format == "opencode":
            result["provider"] = data["provider"]
        elif source_format == "kilo":
            result["provider"] = models_kilo_to_opencode(data.get("provider", {}))
        elif source_format == "gemini":
            result["provider"] = models_gemini_to_opencode(data)
        elif source_format == "qwen":
            result["provider"] = models_qwen_to_opencode(data)
    else:
        # Even if no provider in source, try to convert from Qwen modelProviders
        if source_format == "qwen" and "modelProviders" in data:
            result["provider"] = models_qwen_to_opencode(data)

    return result


def convert_to_qwen(data: dict, source_format: str) -> dict:
    """Convert to Qwen format."""
    result = {
        "$version": 3
    }

    # MCP conversion
    if "mcpServers" in data:
        if source_format == "qwen":
            result["mcpServers"] = data["mcpServers"]
        elif source_format == "gemini":
            result["mcpServers"] = mcp_gemini_to_qwen(data.get("mcpServers", {}))
        elif source_format == "opencode":
            result["mcpServers"] = mcp_opencode_to_qwen(data.get("mcp", {}))
        elif source_format == "kilo":
            result["mcpServers"] = mcp_kilo_to_qwen(data.get("mcp", {}))

    # Models conversion
    if "modelProviders" in data or "provider" in data:
        if source_format == "qwen":
            result["modelProviders"] = data.get("modelProviders", {})
            result["env"] = data.get("env", {})
        elif source_format == "gemini":
            model_providers, env_vars = models_gemini_to_qwen(data)
            result["modelProviders"] = model_providers
            result["env"] = env_vars
        elif source_format == "opencode":
            model_providers, env_vars = models_opencode_to_qwen(data)
            result["modelProviders"] = model_providers
            result["env"] = env_vars
        elif source_format == "kilo":
            model_providers, env_vars = models_kilo_to_qwen(data.get("provider", {}))
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
        result["mcp"] = mcp_opencode_to_kilo(data.get("mcp", {}))
    elif source_format == "gemini" and "mcpServers" in data:
        result["mcp"] = mcp_gemini_to_kilo(data.get("mcpServers", {}))
    elif source_format == "qwen" and "mcpServers" in data:
        result["mcp"] = mcp_qwen_to_kilo(data.get("mcpServers", {}))

    # Models conversion
    if "provider" in data:
        if source_format == "kilo":
            result["provider"] = data["provider"]
        elif source_format == "opencode":
            result["provider"] = models_opencode_to_kilo(data.get("provider", {}))
        elif source_format == "gemini":
            result["provider"] = models_gemini_to_kilo(data)
        elif source_format == "qwen":
            result["provider"] = models_qwen_to_kilo(data)
    else:
        # Even if no provider in source, try to convert from Qwen modelProviders
        if source_format == "qwen" and "modelProviders" in data:
            result["provider"] = models_qwen_to_kilo(data)

    return result


def convert_to_nanobot(data: dict, source_format: str) -> dict:
    """Convert to Nanobot format (MCP + models only as per user requirement)."""
    result = {}

    # MCP conversion
    if source_format == "nanobot" and "tools" in data and "mcpServers" in data.get("tools", {}):
        result["tools"] = {"mcpServers": data["tools"]["mcpServers"]}
    elif source_format == "opencode" and "mcp" in data:
        result["tools"] = {"mcpServers": mcp_opencode_to_nanobot(data.get("mcp", {}))}
    elif source_format == "kilo" and "mcp" in data:
        result["tools"] = {"mcpServers": mcp_kilo_to_nanobot(data.get("mcp", {}))}
    elif source_format == "gemini" and "mcpServers" in data:
        result["tools"] = {"mcpServers": mcp_gemini_to_nanobot(data.get("mcpServers", {}))}
    elif source_format == "qwen" and "mcpServers" in data:
        result["tools"] = {"mcpServers": mcp_qwen_to_nanobot(data.get("mcpServers", {}))}

    # Models conversion
    if source_format == "opencode" and "provider" in data:
        provider_data = data.get("provider", {})
        nanobot_providers = models_opencode_to_nanobot(provider_data)
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
        nanobot_providers = models_kilo_to_nanobot(provider_data)
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
        nanobot_providers = models_to_nanobot(provider_dict)
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

    # MCP conversion
    if source_format == "hermes" and "tools" in data and "mcpServers" in data.get("tools", {}):
        result["tools"] = {"mcpServers": data["tools"]["mcpServers"]}
    elif source_format == "opencode" and "mcp" in data:
        result["tools"] = {"mcpServers": mcp_opencode_to_hermes(data.get("mcp", {}))}
    elif source_format == "kilo" and "mcp" in data:
        result["tools"] = {"mcpServers": mcp_kilo_to_hermes(data.get("mcp", {}))}
    elif source_format == "gemini" and "mcpServers" in data:
        result["tools"] = {"mcpServers": mcp_gemini_to_hermes(data.get("mcpServers", {}))}
    elif source_format == "qwen" and "mcpServers" in data:
        result["tools"] = {"mcpServers": mcp_qwen_to_hermes(data.get("mcpServers", {}))}

    # Models conversion
    if source_format == "opencode" and "provider" in data:
        provider_data = data.get("provider", {})
        hermes_models = models_opencode_to_hermes(provider_data)
        if hermes_models.get("model"):
            result["model"] = hermes_models["model"]
            result["provider"] = hermes_models["provider"]
    elif source_format == "kilo" and "provider" in data:
        provider_data = data.get("provider", {})
        hermes_models = models_kilo_to_hermes(provider_data)
        if hermes_models.get("model"):
            result["model"] = hermes_models["model"]
            result["provider"] = hermes_models["provider"]
    elif source_format == "qwen" and "modelProviders" in data:
        model_providers = data.get("modelProviders", {})
        provider_dict = {}
        for provider_key, models_list in model_providers.items():
            provider_dict[provider_key] = {"models": {m.get("id", ""): m for m in models_list}}
        hermes_models = models_to_hermes(provider_dict)
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
        return convert_mcp_to_nanobot(data, source_format, specific_server)
    elif target_format == "hermes":
        return convert_mcp_to_hermes(data, source_format, specific_server)
    elif target_format == "gemini":
        if source_format == "gemini":
            return {"mcpServers": mcp_data}
        elif source_format == "opencode":
            return {"mcpServers": mcp_opencode_to_gemini(mcp_data)}
        elif source_format == "kilo":
            return {"mcpServers": mcp_kilo_to_gemini(mcp_data)}
        elif source_format == "qwen":
            return {"mcpServers": mcp_qwen_to_gemini(mcp_data)}
    elif target_format == "opencode":
        if source_format == "gemini":
            return {"mcp": mcp_gemini_to_opencode(mcp_data)}
        elif source_format == "opencode":
            return {"mcp": mcp_data}
        elif source_format == "kilo":
            return {"mcp": mcp_kilo_to_opencode(mcp_data)}
        elif source_format == "qwen":
            return {"mcp": mcp_qwen_to_opencode(mcp_data)}
    elif target_format == "qwen":
        if source_format == "gemini":
            return {"mcpServers": mcp_gemini_to_qwen(mcp_data)}
        elif source_format == "opencode":
            return {"mcpServers": mcp_opencode_to_qwen(mcp_data)}
        elif source_format == "kilo":
            return {"mcpServers": mcp_kilo_to_qwen(mcp_data)}
        elif source_format == "qwen":
            return {"mcpServers": mcp_data}
    elif target_format == "kilo":
        if source_format == "gemini":
            return {"mcp": mcp_gemini_to_kilo(mcp_data)}
        elif source_format == "opencode":
            return {"mcp": mcp_opencode_to_kilo(mcp_data)}
        elif source_format == "kilo":
            return {"mcp": mcp_data}
        elif source_format == "qwen":
            return {"mcp": mcp_qwen_to_kilo(mcp_data)}

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
            return {"provider": models_opencode_to_kilo(models_data)}
        elif target_format == "qwen":
            model_providers, env_vars = models_opencode_to_qwen({"provider": models_data})
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
            return {"provider": models_kilo_to_opencode(models_data)}
        elif target_format == "kilo":
            return {"provider": models_data}
        elif target_format == "qwen":
            model_providers, env_vars = models_kilo_to_qwen(models_data)
            result = {"modelProviders": model_providers}
            if env_vars:
                result["env"] = env_vars
            return result
    elif source_format == "qwen":
        model_providers = data.get("modelProviders", {})
        model_providers = filter_models_by_provider(model_providers, specific_model)

        if target_format == "gemini":
            return {}
        elif target_format == "opencode":
            provider = models_qwen_to_opencode({"modelProviders": model_providers, "env": data.get("env", {})})
            return {"provider": provider}
        elif target_format == "kilo":
            provider = models_qwen_to_kilo({"modelProviders": model_providers, "env": data.get("env", {})})
            return {"provider": provider}
        elif target_format == "qwen":
            return {"modelProviders": model_providers}

    return {}


# ============================================================================
# Nanobot Section Conversion Functions
# ============================================================================

def convert_mcp_to_nanobot(
    data: dict,
    source_format: str,
    specific_server: str | None = None
) -> dict:
    """Convert MCP section to Nanobot format."""
    # Get MCP data based on source format
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
    
    # Convert to Nanobot format
    nanobot_mcp = mcp_to_nanobot(mcp_data)
    
    # Return as tools.mcpServers structure
    return {"tools": {"mcpServers": nanobot_mcp}}


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
        nanobot_providers = models_opencode_to_nanobot(provider_data)
    elif source_format == "kilo":
        provider_data = data.get("provider", {})
        provider_data = filter_opencode_models_by_id(provider_data, specific_model)
        nanobot_providers = models_kilo_to_nanobot(provider_data)
    elif source_format == "qwen":
        model_providers = data.get("modelProviders", {})
        model_providers = filter_models_by_provider(model_providers, specific_model)
        # Reconstruct provider dict for conversion
        provider_dict = {}
        for provider_key, models_list in model_providers.items():
            provider_dict[provider_key] = {"models": {m.get("id", ""): m for m in models_list}}
        nanobot_providers = models_to_nanobot(provider_dict)
    else:
        nanobot_providers = {}

    # Return as providers structure with defaults
    result = {"providers": nanobot_providers}
    
    # Add default agent settings from nanobot_config.json reference
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


# ============================================================================
# Hermes Section Conversion Functions
# ============================================================================

def convert_mcp_to_hermes(
    data: dict,
    source_format: str,
    specific_server: str | None = None
) -> dict:
    """Convert MCP section to Hermes format."""
    # Get MCP data based on source format
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
    
    # Convert to Hermes format (list of server names)
    hermes_mcp = mcp_to_hermes(mcp_data)
    
    # Return as tools.mcpServers structure
    return {"tools": {"mcpServers": hermes_mcp}}


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
        hermes_models = models_opencode_to_hermes(provider_data)
    elif source_format == "kilo":
        provider_data = data.get("provider", {})
        provider_data = filter_opencode_models_by_id(provider_data, specific_model)
        hermes_models = models_kilo_to_hermes(provider_data)
    elif source_format == "qwen":
        model_providers = data.get("modelProviders", {})
        model_providers = filter_models_by_provider(model_providers, specific_model)
        # Reconstruct provider dict for conversion
        provider_dict = {}
        for provider_key, models_list in model_providers.items():
            provider_dict[provider_key] = {"models": {m.get("id", ""): m for m in models_list}}
        hermes_models = models_to_hermes(provider_dict)
    else:
        hermes_models = {"model": {}, "provider": {}}

    # Return as model structure with defaults from hermes_config.yaml reference
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


# ============================================================================
# Diff Functions for Same-Format Comparison
# ============================================================================

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


# ============================================================================
# File I/O
# ============================================================================

def load_json_file(filepath: str) -> dict:
    """Load and parse a JSON file."""
    with open(filepath, "r") as f:
        return json.load(f)


def save_json_file(data: dict, filepath: str) -> None:
    """Save data to a JSON file."""
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


# ============================================================================
# CLI Argument Parser
# ============================================================================

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert agent configuration between Gemini, OpenCode, Qwen, and Kilo formats.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Convert full file:
    %(prog)s -i gemini_settings.json -o output.json -t qwen

  Convert only MCP section:
    %(prog)s -i gemini_settings.json -o output.json -t opencode --section mcp

  Convert specific MCP server:
    %(prog)s -i gemini_settings.json -o output.json -t qwen --mcp github

  Convert specific model:
    %(prog)s -i opencode.json -o output.json -t qwen --model qwen3:14b

  Auto-detect source format:
    %(prog)s -i config.json -o output.json -t gemini

  Specify source format explicitly:
    %(prog)s -i config.json -o output.json -t qwen -s opencode

  Diff mode - compare two files of same format:
    %(prog)s -i file1.json --target-input file2.json --diff -s qwen -o diff_report.txt

  Diff mode with auto-detection:
    %(prog)s -i opencode.json --target-input opencode_backup.json --diff
        """
    )
    
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Input configuration file path"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output file path (optional - defaults to stdout)"
    )
    
    parser.add_argument(
        "-t", "--target",
        choices=["gemini", "opencode", "qwen", "kilo", "nanobot", "hermes"],
        help="Target format (required unless using --diff)"
    )

    parser.add_argument(
        "-s", "--source",
        choices=["gemini", "opencode", "qwen", "kilo", "nanobot", "hermes", "auto"],
        default="auto",
        help="Source format (default: auto-detect)"
    )

    parser.add_argument(
        "--section",
        choices=["mcp", "models"],
        help="Convert only a specific section (mcp or models)"
    )

    parser.add_argument(
        "--mcp",
        help="Convert only a specific MCP server by name"
    )

    parser.add_argument(
        "--model",
        help="Convert only models matching this model ID"
    )

    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Output to stdout instead of file"
    )

    parser.add_argument(
        "--target-input",
        help="For diff mode: second input file to compare against (source vs target)"
    )

    parser.add_argument(
        "--diff",
        action="store_true",
        help="Diff mode: compare source with target input file (when formats are the same)"
    )

    return parser.parse_args()


# ============================================================================
# Main Entry Point
# ============================================================================

def main() -> int:
    """Main entry point."""
    args = parse_args()
    
    # Load input file
    try:
        data = load_json_file(args.input)
    except FileNotFoundError:
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {e}", file=sys.stderr)
        return 1

    # Diff mode: compare source with target file
    if args.diff:
        if not args.target_input:
            print("Error: --diff requires --target-input to specify the comparison file", file=sys.stderr)
            return 1
        
        try:
            target_data = load_json_file(args.target_input)
        except FileNotFoundError:
            print(f"Error: Target input file not found: {args.target_input}", file=sys.stderr)
            return 1
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in target input file: {e}", file=sys.stderr)
            return 1
        
        # Detect formats
        source_format = args.source if args.source != "auto" else detect_format(data)
        if source_format == "unknown":
            print("Error: Could not detect source format. Use -s to specify explicitly.", file=sys.stderr)
            return 1
        
        target_file_format = detect_format(target_data)
        if target_file_format == "unknown":
            print("Error: Could not detect target file format.", file=sys.stderr)
            return 1
        
        # Compute diffs - get full missing sections
        mcp_missing = compute_mcp_diff_full(data, target_data, source_format, target_file_format)
        model_missing = compute_model_diff_full(data, target_data, source_format, target_file_format)
        
        # Build output based on source format
        if source_format == "gemini":
            result = {}
            if mcp_missing:
                result["mcpServers"] = mcp_missing
        elif source_format == "opencode":
            result = {}
            if mcp_missing:
                result["mcp"] = mcp_missing
            if model_missing:
                # Reconstruct provider structure with only missing models
                result["provider"] = {}
                for provider_name, models_dict in model_missing.items():
                    result["provider"][provider_name] = {"models": models_dict}
        elif source_format == "kilo":
            result = {}
            if mcp_missing:
                result["mcp"] = mcp_missing
            if model_missing:
                # Reconstruct provider structure with only missing models
                result["provider"] = {}
                for provider_name, models_dict in model_missing.items():
                    result["provider"][provider_name] = {"models": models_dict}
        elif source_format == "qwen":
            result = {}
            if mcp_missing:
                result["mcpServers"] = mcp_missing
            if model_missing:
                result["modelProviders"] = model_missing
        
        # Output result
        output_json = json.dumps(result, indent=2)
        
        # Default to stdout, write to file only if -o is specified
        if args.stdout or not args.output:
            print(output_json)
        else:
            try:
                with open(args.output, "w") as f:
                    f.write(output_json)
                print(f"Diff output written to: {args.output}", file=sys.stderr)
            except Exception as e:
                print(f"Error writing output file: {e}", file=sys.stderr)
                return 1
        
        return 0

    # Conversion mode: require -t/--target
    if not args.target:
        print("Error: -t/--target is required for conversion mode", file=sys.stderr)
        return 1

    target_format = args.target

    # Detect or use specified source format
    source_format = args.source
    if source_format == "auto":
        source_format = detect_format(data)
        if source_format == "unknown":
            print("Error: Could not detect source format. Use -s to specify explicitly.", file=sys.stderr)
            return 1
        print(f"Detected source format: {source_format}", file=sys.stderr)

    # Perform conversion
    try:
        if args.section or args.mcp or args.model:
            # Section-specific conversion
            if args.mcp:
                args.section = "mcp"
            if args.model:
                args.section = "models"

            result = convert_section_only(
                data, source_format, target_format,
                args.section,
                args.mcp or args.model
            )
        else:
            # Full file conversion
            result = convert_full_file(data, source_format, target_format)
    except Exception as e:
        print(f"Error during conversion: {e}", file=sys.stderr)
        return 1

    # Output result
    output_json = json.dumps(result, indent=2)

    # Default to stdout, write to file only if -o is specified
    if args.stdout or not args.output:
        print(output_json)
    else:
        try:
            save_json_file(result, args.output)
            print(f"Conversion complete. Output written to: {args.output}", file=sys.stderr)
        except Exception as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
