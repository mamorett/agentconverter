"""
Model conversion functions for Nanobot format.

Nanobot uses providers dict with apiKey, apiBase, extraHeaders.
"""

from typing import Any


def to_nanobot(provider_data: dict) -> dict:
    """
    Convert generic provider data to Nanobot format.
    
    Nanobot has providers as a dict with apiKey, apiBase, extraHeaders.
    
    Args:
        provider_data: Generic provider data with models
    
    Returns:
        Dict in Nanobot format {provider_name: {apiKey, apiBase, extraHeaders}}
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


def from_nanobot(nanobot_data: dict) -> dict:
    """
    Convert Nanobot provider format to generic format.
    
    Args:
        nanobot_data: Dict with providers structure
    
    Returns:
        Generic provider dict
    """
    # Nanobot format is different - we can only extract basic info
    result = {}
    providers = nanobot_data.get("providers", {})
    
    for provider_key, provider_info in providers.items():
        base_url = provider_info.get("apiBase", "")
        
        result[provider_key] = {
            "options": {"baseURL": base_url},
            "models": {}
        }
    
    return result
