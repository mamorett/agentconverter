"""
Model conversion functions for Kilo format.

Kilo format is identical to OpenCode format.
"""

from typing import Any


def to_kilo(provider_data: dict) -> dict:
    """
    Convert generic provider data to Kilo format (identical to OpenCode).
    
    Args:
        provider_data: Generic provider data
    
    Returns:
        Dict in Kilo format (same as OpenCode)
    """
    # Kilo is identical to OpenCode
    from . import opencode
    return opencode.to_opencode(provider_data)


def from_kilo(kilo_data: dict) -> dict:
    """
    Convert Kilo provider format to generic format (identical to OpenCode).
    
    Args:
        kilo_data: Dict with provider key containing models
    
    Returns:
        Generic provider dict
    """
    # Kilo is identical to OpenCode
    return dict(kilo_data)
