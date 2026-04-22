"""
Model conversion functions for LiteLLM ConfigMap format.

This is a one-way conversion only (to ConfigMap format).
Output is YAML suitable for Kubernetes ConfigMap.
"""

import yaml
from typing import Any


def to_configmappo(provider_data: dict) -> str:
    """
    Convert provider data to LiteLLM ConfigMap YAML format.

    Args:
        provider_data: Provider data in generic/OpenCode format with {provider_name: {models}}

    Returns:
        YAML string suitable for Kubernetes ConfigMap data.config.yaml
    """
    # Build model_list from provider data
    model_list = []

    providers = provider_data.get("provider", {})

    for provider_name, provider_data_item in providers.items():
        models_dict = provider_data_item.get("models", {})
        base_url = provider_data_item.get("options", {}).get("baseURL", "")
        npm_package = provider_data_item.get("npm", "")

        # Determine model prefix based on npm package
        if "openai-compatible" in npm_package or "openai" in npm_package.lower():
            model_prefix = "openai"
        else:
            model_prefix = "openai"  # Default to openai for compatibility

        for model_id, model_data in models_dict.items():
            # Build litellm_params
            litellm_params = {
                "model": f"{model_prefix}/{model_id}",
                "api_base": base_url,
                "api_key": "ollama",  # Default placeholder
                "proxy_url": "http://localhost:1056"  # Default placeholder
            }

            # Build model entry
            model_entry = {
                "model_name": model_id,
                "litellm_params": litellm_params
            }

            # Add comments from _launch or other metadata if present
            if model_data.get("_launch"):
                # Could add comment here if needed
                pass

            model_list.append(model_entry)

    # Build final ConfigMap structure
    config = {
        "model_list": model_list,
        "litellm_settings": {
            "success_callback": ["langfuse", "prometheus"],
            "failure_callback": ["langfuse", "prometheus"]
        }
    }

    # Generate YAML output
    yaml_output = yaml.dump(
        config,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True
    )

    return yaml_output


def from_configmappo(configmappo_yaml: str) -> dict:
    """
    Parse ConfigMap YAML format (not implemented - one-way conversion only).

    Args:
        configmappo_yaml: YAML string from ConfigMap

    Returns:
        Empty dict (this function is a placeholder)
    """
    raise NotImplementedError("ConfigMap format is one-way conversion only (to ConfigMap)")
