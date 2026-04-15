"""
Credential validation utilities for AgentPay Mesh
Provides safe credential handling without exposing values

This module ensures that credentials are never exposed in logs, API responses,
or console output while maintaining full functionality for validation and status checking.
"""
import os
import re
from typing import Optional, Tuple, Dict, Any

# Credential format patterns for validation
CIRCLE_API_KEY_PATTERN = r'^[a-zA-Z0-9_-]{20,}$'
ETH_ADDRESS_PATTERN = r'^0x[a-fA-F0-9]{40}$'
ETH_PRIVATE_KEY_PATTERN = r'^0x[a-fA-F0-9]{64}$'
ANTHROPIC_API_KEY_PATTERN = r'^sk-ant-[a-zA-Z0-9_-]{20,}$'

# Placeholder values that indicate unconfigured credentials
PLACEHOLDERS = {
    'your_circle_api_key_here',
    'your_encrypted_entity_secret_here',
    'your_anthropic_api_key',
    '0x...',
    '0x_FILL_FROM_ARC_DOCS',
    'USDC-ARC-TESTNET',
    'not configured'
}

class CredentialError(Exception):
    """Raised when credential validation fails"""
    pass

def is_placeholder(value: str) -> bool:
    """
    Check if a value is a placeholder or empty string

    Args:
        value: The credential value to check

    Returns:
        True if the value is a placeholder or empty, False otherwise
    """
    if not value:
        return True
    return value in PLACEHOLDERS or (isinstance(value, str) and value.strip() == '')

def validate_credential_type(credential_type: str, value: str) -> Tuple[bool, str]:
    """
    Validate credential format without exposing the actual value

    Args:
        credential_type: Type of credential ('circle_api_key', 'anthropic_api_key', etc.)
        value: The credential value to validate

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if format is valid, False otherwise
        - error_message: Empty string if valid, error description if invalid
    """
    if is_placeholder(value):
        return False, "Credential is placeholder value"

    if credential_type == 'circle_api_key':
        if len(value) < 20:
            return False, "Circle API key too short (min 20 chars)"
        if not re.match(CIRCLE_API_KEY_PATTERN, value):
            return False, "Circle API key format invalid"
        return True, ""

    elif credential_type == 'anthropic_api_key':
        if not value.startswith('sk-ant-'):
            return False, "Anthropic API key must start with 'sk-ant-'"
        if len(value) < 30:
            return False, "Anthropic API key too short"
        return True, ""

    elif credential_type == 'eth_address':
        if not re.match(ETH_ADDRESS_PATTERN, value):
            return False, "Invalid Ethereum address format"
        return True, ""

    elif credential_type == 'eth_private_key':
        if not re.match(ETH_PRIVATE_KEY_PATTERN, value):
            return False, "Invalid Ethereum private key format"
        if len(value) != 66:
            return False, "Private key must be 66 characters (0x + 64 hex)"
        return True, ""

    elif credential_type == 'entity_secret':
        if len(value) < 10:
            return False, "Entity secret too short"
        return True, ""

    return False, f"Unknown credential type: {credential_type}"

def get_credential_status(credential_type: str, env_var: str) -> Dict[str, Any]:
    """
    Get credential status without exposing the actual value

    Args:
        credential_type: Type of credential for validation
        env_var: Environment variable name to check

    Returns:
        Dictionary with keys:
        - 'configured': bool - whether credential is set and not a placeholder
        - 'valid_format': bool - whether credential format is valid
        - 'length': int - length of credential value (0 if not configured)
        - 'error': str or None - error message if validation fails
    """
    value = os.getenv(env_var, '')

    status = {
        'configured': not is_placeholder(value) and len(value) > 0,
        'valid_format': False,
        'length': len(value),
        'error': None
    }

    if status['configured']:
        is_valid, error = validate_credential_type(credential_type, value)
        status['valid_format'] = is_valid
        status['error'] = error if not is_valid else None

    return status

def sanitize_credential(value: str, cred_type: str = "credential") -> str:
    """
    Sanitize credentials for display by showing only type and length

    Args:
        value: The credential value to sanitize
        cred_type: Type description for display

    Returns:
        Safe string representation without exposing the actual value
    """
    if not value:
        return f"{cred_type}(not configured)"
    if is_placeholder(value):
        return f"{cred_type}(placeholder)"
    return f"{cred_type}(configured, length={len(value)})"

def sanitize_log_message(message: str, credentials: Dict[str, str]) -> str:
    """
    Sanitize credentials from log messages

    Args:
        message: Original log message
        credentials: Dict of credential_name -> credential_value pairs

    Returns:
        Sanitized message with credentials replaced
    """
    sanitized = message
    for name, value in credentials.items():
        if value and not is_placeholder(value):
            # Replace with placeholder
            sanitized = sanitized.replace(value, f"***{name}***")
    return sanitized

def get_secure_credential(env_var: str, default: str = "") -> str:
    """
    Get credential from environment with placeholder detection

    Args:
        env_var: Environment variable name
        default: Default value if not found

    Returns:
        Credential value or empty string if placeholder/default
    """
    value = os.getenv(env_var, default)
    if is_placeholder(value):
        return ""
    return value

def check_credentials_configured(required_vars: list) -> Tuple[bool, list]:
    """
    Check if multiple credentials are properly configured

    Args:
        required_vars: List of environment variable names to check

    Returns:
        Tuple of (all_configured, missing_vars)
        - all_configured: True if all credentials are configured
        - missing_vars: List of variable names that are not configured
    """
    missing = []
    for var in required_vars:
        value = os.getenv(var, '')
        if is_placeholder(value):
            missing.append(var)

    return len(missing) == 0, missing

def get_wallet_display_info(address: Optional[str], privkey: Optional[str] = None) -> Dict[str, Any]:
    """
    Get wallet information without exposing sensitive data

    Args:
        address: Wallet address
        privkey: Private key (optional)

    Returns:
        Dictionary with safe wallet information
    """
    info = {
        'address_configured': bool(address and not is_placeholder(address) and len(address) > 10),
        'address_length': len(address) if address else 0,
        'privkey_configured': bool(privkey and not is_placeholder(privkey) and len(privkey) > 10),
        'privkey_length': len(privkey) if privkey else 0,
    }

    return info

def validate_environment() -> Dict[str, Any]:
    """
    Validate entire environment configuration for security readiness

    Returns:
        Dictionary with overall security status and detailed credential checks
    """
    credentials_to_check = [
        ('circle_api_key', 'CIRCLE_API_KEY'),
        ('entity_secret', 'CIRCLE_ENTITY_SECRET_CIPHERTEXT'),
        ('anthropic_api_key', 'ANTHROPIC_API_KEY'),
    ]

    wallet_credentials = [
        'WALLET_ADDR_COORDINATOR',
        'WALLET_ADDR_SEARCHAGENT',
        'WALLET_ADDR_REVIEWAGENT',
        'WALLET_ADDR_SUMMARYAGENT',
        'PRIVKEY_COORDINATOR',
        'PRIVKEY_SEARCHAGENT',
        'PRIVKEY_REVIEWAGENT',
        'PRIVKEY_SUMMARYAGENT',
    ]

    results = {
        'credentials': {},
        'wallets': {},
        'overall_status': 'unknown'
    }

    # Check API credentials
    configured_count = 0
    for cred_type, env_var in credentials_to_check:
        status = get_credential_status(cred_type, env_var)
        results['credentials'][env_var] = status
        if status['configured']:
            configured_count += 1

    # Check wallet credentials
    wallets_configured = 0
    for wallet_var in wallet_credentials:
        value = os.getenv(wallet_var, '')
        configured = not is_placeholder(value) and len(value) > 10
        results['wallets'][wallet_var] = {
            'configured': configured,
            'length': len(value) if value else 0
        }
        if configured:
            wallets_configured += 1

    # Determine overall status
    if configured_count == len(credentials_to_check) and wallets_configured == len(wallet_credentials):
        results['overall_status'] = 'fully_configured'
    elif configured_count > 0 or wallets_configured > 0:
        results['overall_status'] = 'partially_configured'
    else:
        results['overall_status'] = 'mock_mode'

    return results