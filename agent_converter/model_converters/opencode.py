"""
Model conversion functions for OpenCode format.

OpenCode uses provider dict with models inside each provider.
"""

from typing import Any


def extract_baseurl_from_opencode_provider(provider_data: dict) -> str:
    """Extract baseURL from OpenCode provider data."""
    return provider_data.get("options", {}).get("baseURL", "")


def extract_envkey_from_provider_name(provider_name: str) -> str:
    """Generate env key from provider name."""
    normalized = provider_name.upper().replace(" ", "_").replace("-", "_")
    return f"{normalized}_API_KEY"


def to_opencode(provider_data: dict) -> dict:
    """
    Convert generic provider data to OpenCode format.
    
    Args:
        provider_data: Generic provider data with models
    
    Returns:
        Dict in OpenCode format {provider_name: {name, npm, options, models}}
    """
    return dict(provider_data)


def from_opencode(opencode_data: dict) -> tuple[dict, dict]:
    """
    Convert OpenCode provider format to Qwen modelProviders format.
    
    Args:
        opencode_data: Dict with provider key containing {name, npm, options, models}
    
    Returns:
        Tuple of (modelProviders dict, env dict)
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
