"""
Model conversion functions for Hermes format.

Hermes uses model.default for the default model and provider for provider name.
"""

from typing import Any


def to_hermes(provider_data: dict) -> dict:
    """
    Convert generic provider data to Hermes format.
    
    Hermes uses model.default for the default model and provider for provider name.
    
    Args:
        provider_data: Generic provider data with models
    
    Returns:
        Dict with 'model' and 'provider' keys
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


def from_hermes(hermes_data: dict) -> dict:
    """
    Convert Hermes model format to generic provider format.
    
    Args:
        hermes_data: Dict with model and provider keys
    
    Returns:
        Generic provider dict
    """
    result = {}
    
    provider_name = hermes_data.get("provider", "")
    model_default = hermes_data.get("model", {}).get("default", "")
    
    if provider_name and model_default:
        # Extract model ID from default (format: provider/model_id)
        if "/" in model_default:
            model_id = model_default.split("/")[-1]
            result[provider_name] = {
                "models": {
                    model_id: {
                        "name": model_id
                    }
                }
            }
    
    return result
