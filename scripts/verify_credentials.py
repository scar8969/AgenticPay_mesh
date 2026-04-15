#!/usr/bin/env python3
"""
AgentPay Mesh - Credential Verification Script

This script validates all API credentials and connections before running demos.
Tests Circle API, Anthropic API, Arc blockchain connectivity, and configuration.

Usage:
    python scripts/verify_credentials.py

Exit codes:
    0 - All checks passed (system ready for real mode)
    1 - Some checks failed (system will use mock mode)
    2 - Critical configuration errors
"""

import os
import sys
import asyncio
import httpx
from pathlib import Path
from typing import Dict, List, Tuple

# Color codes for terminal output
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"

def print_success(message: str):
    print(f"{Colors.GREEN}✓{Colors.END} {message}")

def print_error(message: str):
    print(f"{Colors.RED}✗{Colors.END} {message}")

def print_warning(message: str):
    print(f"{Colors.YELLOW}⚠{Colors.END} {message}")

def print_info(message: str):
    print(f"{Colors.BLUE}ℹ{Colors.END} {message}")

def print_header(message: str):
    print(f"\n{Colors.BOLD}{message}{Colors.END}")
    print("─" * len(message))

class CredentialVerifier:
    def __init__(self):
        self.results: Dict[str, bool] = {}
        self.env_path = Path(__file__).parent.parent / ".env"

    def check_env_file(self) -> bool:
        """Check if .env file exists"""
        print_header("Environment Configuration")

        if not self.env_path.exists():
            print_error(".env file not found (copy from .env.example)")
            print_info("System will run in mock mode")
            return False

        print_success(f".env file found: {self.env_path}")
        return True

    def load_env_vars(self) -> Dict[str, str]:
        """Load environment variables from .env file"""
        env_vars = {}
        try:
            with open(self.env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
        except Exception as e:
            print_error(f"Failed to read .env file: {e}")
            return {}

        return env_vars

    def check_circle_credentials(self, env_vars: Dict[str, str]) -> bool:
        """Check Circle API credentials"""
        print_header("Circle API Credentials")

        api_key = env_vars.get('CIRCLE_API_KEY')
        entity_secret = env_vars.get('CIRCLE_ENTITY_SECRET_CIPHERTEXT')

        if not api_key or api_key == 'your_circle_api_key_here':
            print_warning("CIRCLE_API_KEY not configured")
            print_info("Nanopayments will use mock mode")
            return False

        print_success("CIRCLE_API_KEY is configured")

        if not entity_secret or entity_secret == 'your_encrypted_entity_secret_here':
            print_warning("CIRCLE_ENTITY_SECRET_CIPHERTEXT not configured")
            print_info("Wallet operations will use mock mode")
            return False

        print_success("CIRCLE_ENTITY_SECRET_CIPHERTEXT is configured")
        return True

    def check_anthropic_credentials(self, env_vars: Dict[str, str]) -> bool:
        """Check Anthropic API credentials"""
        print_header("Anthropic API Credentials")

        api_key = env_vars.get('ANTHROPIC_API_KEY')

        if not api_key or api_key == 'your_anthropic_api_key':
            print_warning("ANTHROPIC_API_KEY not configured")
            print_info("AI agents will use mock responses")
            return False

        print_success("ANTHROPIC_API_KEY is configured")
        return True

    def check_agent_wallets(self, env_vars: Dict[str, str]) -> bool:
        """Check agent wallet configuration"""
        print_header("Agent Wallet Configuration")

        required_wallets = [
            'WALLET_ADDR_COORDINATOR',
            'WALLET_ADDR_SEARCHAGENT',
            'WALLET_ADDR_REVIEWAGENT',
            'WALLET_ADDR_SUMMARYAGENT'
        ]

        required_keys = [
            'PRIVKEY_COORDINATOR',
            'PRIVKEY_SEARCHAGENT',
            'PRIVKEY_REVIEWAGENT',
            'PRIVKEY_SUMMARYAGENT'
        ]

        wallets_configured = 0
        for wallet in required_wallets:
            addr = env_vars.get(wallet)
            if addr and addr != '0x...' and len(addr) > 10:
                print_success(f"{wallet}: {addr[:10]}...{addr[-6:]}")
                wallets_configured += 1
            else:
                print_warning(f"{wallet}: not configured")

        keys_configured = 0
        for key in required_keys:
            privkey = env_vars.get(key)
            if privkey and privkey != '0x...' and len(privkey) > 10:
                keys_configured += 1

        if keys_configured > 0:
            print_success(f"Private keys: {keys_configured}/{len(required_keys)} configured")
        else:
            print_warning("No private keys configured")

        return wallets_configured == len(required_wallets) and keys_configured == len(required_keys)

    async def test_circle_api_connection(self, env_vars: Dict[str, str]) -> bool:
        """Test Circle API connectivity"""
        print_header("Circle API Connectivity")

        api_key = env_vars.get('CIRCLE_API_KEY')
        if not api_key or api_key == 'your_circle_api_key_here':
            print_warning("Skipping - API key not configured")
            return False

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Test Circle configuration endpoint
                headers = {'Authorization': f'Bearer {api_key}'}
                response = await client.get(
                    'https://api.circle.com/v1/w3s/config',
                    headers=headers
                )

                if response.status_code == 200:
                    print_success("Circle API is reachable")
                    data = response.json()
                    if 'data' in data:
                        print_success(f"Circle environment: {data['data'].get('blockchain', 'unknown')}")
                    return True
                else:
                    print_error(f"Circle API returned status {response.status_code}")
                    return False

        except Exception as e:
            print_error(f"Circle API connection failed: {e}")
            return False

    async def test_anthropic_api_connection(self, env_vars: Dict[str, str]) -> bool:
        """Test Anthropic API connectivity"""
        print_header("Anthropic API Connectivity")

        api_key = env_vars.get('ANTHROPIC_API_KEY')
        if not api_key or api_key == 'your_anthropic_api_key':
            print_warning("Skipping - API key not configured")
            return False

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {
                    'x-api-key': api_key,
                    'anthropic-version': '2023-06-01',
                    'content-type': 'application/json'
                }

                # Minimal test request
                test_payload = {
                    'model': 'claude-haiku-3.5-20241022',
                    'max_tokens': 10,
                    'messages': [{'role': 'user', 'content': 'test'}]
                }

                response = await client.post(
                    'https://api.anthropic.com/v1/messages',
                    headers=headers,
                    json=test_payload
                )

                if response.status_code == 200:
                    print_success("Anthropic API is reachable")
                    return True
                elif response.status_code == 401:
                    print_error("Anthropic API key is invalid")
                    return False
                else:
                    print_warning(f"Anthropic API returned status {response.status_code}")
                    return False

        except Exception as e:
            print_error(f"Anthropic API connection failed: {e}")
            return False

    async def test_arc_blockchain_connection(self, env_vars: Dict[str, str]) -> bool:
        """Test Arc blockchain RPC connectivity"""
        print_header("Arc Blockchain Connectivity")

        rpc_url = env_vars.get('ARC_RPC_URL', 'https://rpc.arc-testnet.circle.com')

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Test with a simple JSON-RPC request
                payload = {
                    'jsonrpc': '2.0',
                    'method': 'eth_chainId',
                    'params': [],
                    'id': 1
                }

                response = await client.post(rpc_url, json=payload)

                if response.status_code == 200:
                    data = response.json()
                    if 'result' in data:
                        chain_id = int(data['result'], 16)
                        print_success(f"Arc RPC is reachable (Chain ID: {chain_id})")
                        return True
                    else:
                        print_error("Unexpected RPC response")
                        return False
                else:
                    print_error(f"Arc RPC returned status {response.status_code}")
                    return False

        except Exception as e:
            print_error(f"Arc RPC connection failed: {e}")
            return False

    def check_backend_dependencies(self) -> bool:
        """Check if required Python packages are installed"""
        print_header("Python Dependencies")

        required_packages = [
            'fastapi',
            'uvicorn',
            'httpx',
            'anthropic',
            'web3'
        ]

        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
                print_success(f"{package} is installed")
            except ImportError:
                print_error(f"{package} is missing")
                missing_packages.append(package)

        if missing_packages:
            print_warning(f"Missing packages: {', '.join(missing_packages)}")
            print_info("Run: pip install -r requirements.txt")
            return False

        return True

    def generate_summary(self, results: Dict[str, bool]) -> Tuple[int, str]:
        """Generate verification summary and recommendation"""
        print_header("Verification Summary")

        passed = sum(1 for v in results.values() if v)
        total = len(results)

        print(f"Tests passed: {passed}/{total}")

        # Determine system mode capability
        if results.get('circle_credentials') and results.get('anthropic_credentials'):
            mode = "REAL MODE - Full nanopayments and AI capabilities"
            exit_code = 0
        elif results.get('circle_credentials') or results.get('anthropic_credentials'):
            mode = "HYBRID MODE - Partial capabilities, some mock fallbacks"
            exit_code = 1
        else:
            mode = "MOCK MODE - Demo with simulated payments and responses"
            exit_code = 1

        print(f"\nSystem mode: {Colors.BOLD}{mode}{Colors.END}")

        # Provide recommendations
        print_header("Recommendations")

        if not results.get('env_file'):
            print_info("1. Copy .env.example to .env")
            print_info("2. Edit .env with your credentials")
        elif not results.get('circle_credentials'):
            print_info("1. Get Circle API key: https://developers.circle.com/")
            print_info("2. Add CIRCLE_API_KEY to .env")
        elif not results.get('anthropic_credentials'):
            print_info("1. Get Anthropic API key: https://console.anthropic.com/")
            print_info("2. Add ANTHROPIC_API_KEY to .env")
        elif not results.get('agent_wallets'):
            print_info("1. Start backend: python run.py")
            print_info("2. Create wallets: curl -X POST http://localhost:8000/setup/wallets")
            print_info("3. Update .env with wallet addresses and keys")
            print_info("4. Fund wallets: https://faucet.circle.com")
        else:
            print_success("All credentials configured! System ready for demo.")

        return exit_code, mode

    async def run_verification(self) -> Tuple[int, str]:
        """Run complete verification sequence"""
        print(f"{Colors.BOLD}AgentPay Mesh - Credential Verification{Colors.END}")
        print("=" * 50)

        # Check environment file
        env_exists = self.check_env_file()
        self.results['env_file'] = env_exists

        if not env_exists:
            return self.generate_summary(self.results)

        # Load environment variables
        env_vars = self.load_env_vars()
        if not env_vars:
            return self.generate_summary(self.results)

        # Check credentials
        self.results['circle_credentials'] = self.check_circle_credentials(env_vars)
        self.results['anthropic_credentials'] = self.check_anthropic_credentials(env_vars)
        self.results['agent_wallets'] = self.check_agent_wallets(env_vars)

        # Test connectivity
        self.results['circle_api'] = await self.test_circle_api_connection(env_vars)
        self.results['anthropic_api'] = await self.test_anthropic_api_connection(env_vars)
        self.results['arc_blockchain'] = await self.test_arc_blockchain_connection(env_vars)

        # Check dependencies
        self.results['dependencies'] = self.check_backend_dependencies()

        # Generate summary
        return self.generate_summary(self.results)

async def main():
    """Main entry point"""
    verifier = CredentialVerifier()
    exit_code, mode = await verifier.run_verification()

    print(f"\n{Colors.BOLD}{'=' * 50}{Colors.END}")
    print(f"{Colors.BOLD}Exit code: {exit_code}{Colors.END}")

    sys.exit(exit_code)

if __name__ == "__main__":
    asyncio.run(main())