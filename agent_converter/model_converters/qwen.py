"""
Model conversion functions for Qwen format.

Qwen uses modelProviders with env vars.
"""

from typing import Any


def to_qwen(provider_data: dict) -> tuple[dict, dict]:
    """
    Convert generic provider data to Qwen modelProviders format.
    
    Args:
        provider_data: Generic provider data
    
    Returns:
        Tuple of (modelProviders dict, env dict)
    """
    # Delegate to opencode converter since formats are similar
    from . import opencode
    return opencode.from_opencode({"provider": provider_data})


def from_qwen(qwen_data: dict) -> dict:
    """
    Convert Qwen modelProviders format to OpenCode provider format.
    
    Args:
        qwen_data: Dict with modelProviders and env keys
    
    Returns:
        Dict in OpenCode provider format
    """
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
