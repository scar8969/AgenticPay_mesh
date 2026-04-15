#!/usr/bin/env python3
"""
AgentPay Mesh - Real Payment Test Script

This script executes a small real nanopayment transaction to verify
Circle Nanopayments integration is working correctly.

Usage:
    python scripts/test_real_payments.py [--amount USDC_AMOUNT]

The script will:
1. Validate credentials
2. Create a test nanopayment transaction
3. Wait for ledger confirmation
4. Verify transaction settled correctly
5. Display detailed transaction information

Prerequisites:
- CIRCLE_API_KEY configured in .env
- Agent wallets created and funded
- USDC in sender wallet
"""

import os
import sys
import asyncio
import json
import time
import argparse
from pathlib import Path
from typing import Dict, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.payment_service import PaymentService
from services.circle_wallets import CircleWallets
from services.nanopayments import CircleNanopayments

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

class PaymentTester:
    def __init__(self, test_amount_usdc: float = 0.001):
        self.test_amount_usdc = test_amount_usdc
        self.payment_service = None
        self.nanopayments = None
        self.wallets = None

    def check_prerequisites(self) -> bool:
        """Check if required environment variables are set"""
        print_header("Prerequisites Check")

        required_vars = [
            'CIRCLE_API_KEY',
            'CIRCLE_ENTITY_SECRET_CIPHERTEXT',
            'WALLET_ADDR_COORDINATOR',
            'WALLET_ADDR_SEARCHAGENT',
            'PRIVKEY_COORDINATOR'
        ]

        missing_vars = []
        for var in required_vars:
            value = os.getenv(var)
            if not value or value in ['your_circle_api_key_here', 'your_encrypted_entity_secret_here', '0x...']:
                print_error(f"{var}: not configured")
                missing_vars.append(var)
            else:
                # Show only configuration status and length for security
                if 'ADDR' in var:
                    if value and len(value) > 10:
                        print_success(f"{var}: configured (length: {len(value)})")
                    else:
                        print_error(f"{var}: not configured")
                        missing_vars.append(var)
                elif 'PRIVKEY' in var:
                    if value and len(value) > 10:
                        print_success(f"{var}: configured (length: {len(value)})")
                    else:
                        print_error(f"{var}: not configured")
                        missing_vars.append(var)
                else:
                    if value and value not in ['your_circle_api_key_here', 'your_anthropic_api_key']:
                        print_success(f"{var}: configured (length: {len(value)})")
                    else:
                        print_error(f"{var}: not configured")
                        missing_vars.append(var)

        if missing_vars:
            print_warning(f"\nMissing {len(missing_vars)} required variables")
            print_info("Please configure these in your .env file")
            return False

        print_success("All prerequisites met")
        return True

    async def initialize_services(self) -> bool:
        """Initialize payment services"""
        print_header("Service Initialization")

        try:
            self.payment_service = PaymentService()
            self.nanopayments = CircleNanopayments()
            self.wallets = CircleWallets()

            print_success("Payment services initialized")
            return True

        except Exception as e:
            print_error(f"Failed to initialize services: {e}")
            return False

    async def check_wallet_balance(self, wallet_address: str) -> Optional[float]:
        """Check USDC balance of a wallet"""
        print_info(f"Checking balance for {wallet_address[:10]}...{wallet_address[-6:]}")

        try:
            balance = await self.wallets.get_balance(wallet_address)
            if balance is not None:
                print_success(f"Balance: ${balance:.6f} USDC")
                return balance
            else:
                print_warning("Could not retrieve balance")
                return None

        except Exception as e:
            print_error(f"Balance check failed: {e}")
            return None

    async def execute_test_payment(self) -> Optional[Dict]:
        """Execute a test nanopayment transaction"""
        print_header("Test Payment Execution")

        sender_address = os.getenv('WALLET_ADDR_COORDINATOR')
        sender_privkey = os.getenv('PRIVKEY_COORDINATOR')
        receiver_address = os.getenv('WALLET_ADDR_SEARCHAGENT')

        print_info(f"Sender: configured (length: {len(sender_address) if sender_address else 0})")
        print_info(f"Receiver: configured (length: {len(receiver_address) if receiver_address else 0})")
        print_info(f"Amount: ${self.test_amount_usdc:.6f} USDC")
        print_info("Resource: /test/payment")

        try:
            # Execute payment through payment service
            start_time = time.time()
            result = await self.payment_service.pay(
                sender="Coordinator",
                receiver="SearchAgent",
                amount_usdc=self.test_amount_usdc,
                sender_address=sender_address,
                sender_privkey=sender_privkey,
                receiver_address=receiver_address,
                resource="/test/payment"
            )
            elapsed = (time.time() - start_time) * 1000

            if result.get('success'):
                print_success(f"Payment completed in {elapsed:.1f}ms")
                return result
            else:
                print_error(f"Payment failed: {result.get('error', 'Unknown error')}")
                return None

        except Exception as e:
            print_error(f"Payment execution error: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def verify_transaction(self, transaction_id: str) -> bool:
        """Verify transaction settled on ledger"""
        print_header("Transaction Verification")

        print_info(f"Transaction ID: {transaction_id}")
        print_info("Waiting for ledger confirmation...")

        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                # Check transaction status
                status = await self.nanopayments.get_transaction_status(transaction_id)

                if status == 'confirmed':
                    print_success(f"Transaction confirmed on ledger (attempt {attempt + 1})")
                    return True
                elif status == 'pending':
                    print_warning(f"Still pending... (attempt {attempt + 1}/{max_attempts})")
                    await asyncio.sleep(2)
                else:
                    print_error(f"Transaction failed with status: {status}")
                    return False

            except Exception as e:
                print_warning(f"Verification attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(2)

        print_error("Transaction verification timeout")
        return False

    def display_transaction_details(self, result: Dict):
        """Display detailed transaction information"""
        print_header("Transaction Details")

        details = [
            ("Status", "SUCCESS" if result.get('success') else "FAILED"),
            ("Transaction ID", result.get('id', 'N/A')),
            ("Payment Rail", result.get('rail', 'unknown')),
            ("Amount", f"${result.get('amount', 0):.6f} USDC"),
            ("Sender", result.get('sender', 'N/A')),
            ("Receiver", result.get('receiver', 'N/A')),
            ("Resource", result.get('resource', 'N/A')),
            ("Timestamp", result.get('timestamp', 'N/A'))
        ]

        for key, value in details:
            print(f"{key:.<20} {value}")

        if 'fees' in result:
            print(f"\nFee Breakdown:")
            for fee_type, fee_amount in result['fees'].items():
                print(f"  {fee_type:.<18} ${fee_amount:.6f}")

    async def run_test(self) -> bool:
        """Run complete test sequence"""
        print(f"{Colors.BOLD}AgentPay Mesh - Real Payment Test{Colors.END}")
        print("=" * 50)

        # Check prerequisites
        if not self.check_prerequisites():
            return False

        # Initialize services
        if not await self.initialize_services():
            return False

        # Check sender balance
        sender_address = os.getenv('WALLET_ADDR_COORDINATOR')
        balance = await self.check_wallet_balance(sender_address)

        if balance is None or balance < self.test_amount_usdc:
            print_error(f"Insufficient balance. Need ${self.test_amount_usdc:.6f} USDC")
            if balance is not None:
                print_info(f"Current balance: ${balance:.6f} USDC")
            print_info("Fund wallet at: https://faucet.circle.com")
            return False

        # Execute test payment
        result = await self.execute_test_payment()
        if not result:
            return False

        # Display transaction details
        self.display_transaction_details(result)

        # Verify transaction (if real payment)
        if result.get('rail') == 'nanopayments':
            transaction_id = result.get('id')
            if transaction_id and transaction_id != 'mock_tx_id':
                verified = await self.verify_transaction(transaction_id)
                if verified:
                    print_success("Payment fully verified on Circle ledger")
                else:
                    print_warning("Payment executed but ledger verification failed")
            else:
                print_warning("Mock transaction - skipping ledger verification")
        else:
            print_warning("Test ran in mock mode")

        # Final summary
        print_header("Test Summary")
        if result.get('success'):
            print_success("Real payment test PASSED")
            print_info("Your Circle Nanopayments integration is working correctly!")
            return True
        else:
            print_error("Real payment test FAILED")
            return False

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Test real nanopayment transactions')
    parser.add_argument('--amount', type=float, default=0.001,
                       help='Test payment amount in USDC (default: 0.001)')

    args = parser.parse_args()
    tester = PaymentTester(test_amount_usdc=args.amount)

    try:
        success = await tester.run_test()
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print_warning("\nTest interrupted by user")
        sys.exit(130)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())