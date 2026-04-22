"""
Model conversion functions for Gemini format.

Gemini has no models section - returns empty dicts.
"""

from typing import Any


def to_gemini(provider_data: dict) -> dict:
    """
    Convert generic provider data to Gemini format.
    
    Gemini has no models section, so returns empty dict.
    
    Args:
        provider_data: Generic provider data
    
    Returns:
        Empty dict (Gemini has no models)
    """
    return {}


def from_gemini(gemini_data: dict) -> dict:
    """
    Convert Gemini format to generic provider format.
    
    Gemini has no models section, so returns empty dict.
    
    Args:
        gemini_data: Gemini config data
    
    Returns:
        Empty dict (Gemini has no models)
    """
    return {}
