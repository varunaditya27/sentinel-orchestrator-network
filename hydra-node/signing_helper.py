#!/usr/bin/env python3
"""
Signing Helper for SON Hydra Settlement Layer
Generates ED25519 keypairs and signs canonical JSON messages.
"""

import json
import base64
import nacl.signing
import nacl.encoding
import os
import argparse

def generate_keypair():
    """Generate a new ED25519 keypair"""
    # Generate private key
    signing_key = nacl.signing.SigningKey.generate()

    # Get public key
    verify_key = signing_key.verify_key

    # Encode as base64
    private_key_b64 = base64.b64encode(signing_key.encode()).decode()
    public_key_b64 = base64.b64encode(verify_key.encode()).decode()

    return private_key_b64, public_key_b64

def sign_message(private_key_b64: str, message: bytes) -> str:
    """Sign a message using ED25519 private key"""
    # Decode private key
    private_key_bytes = base64.b64decode(private_key_b64)
    signing_key = nacl.signing.SigningKey(private_key_bytes)

    # Sign message
    signed = signing_key.sign(message)

    # Return signature as base64
    return base64.b64encode(signed.signature).decode()

def load_canonical_message(filepath: str) -> bytes:
    """Load and canonicalize JSON message for signing"""
    with open(filepath, 'r') as f:
        data = json.load(f)

    # Create canonical JSON (sorted keys, no extra whitespace)
    canonical_json = json.dumps(data, sort_keys=True, separators=(',', ':'))
    return canonical_json.encode()

def main():
    parser = argparse.ArgumentParser(description='Signing Helper for SON Settlement')
    parser.add_argument('--generate-keys', action='store_true', help='Generate new ED25519 keypair')
    parser.add_argument('--sign', action='store_true', help='Sign a message')
    parser.add_argument('--private-key', help='Base64 encoded private key for signing')
    parser.add_argument('--message-file', help='Path to JSON message file to sign')
    parser.add_argument('--output-keys', help='Output file for generated keys (JSON)')

    args = parser.parse_args()

    if args.generate_keys:
        print("Generating new ED25519 keypair...")
        private_key, public_key = generate_keypair()

        keys_data = {
            "private_key": private_key,
            "public_key": public_key
        }

        if args.output_keys:
            with open(args.output_keys, 'w') as f:
                json.dump(keys_data, f, indent=2)
            print(f"Keys saved to {args.output_keys}")
        else:
            print("Private Key (base64):", private_key)
            print("Public Key (base64):", public_key)

    elif args.sign:
        if not args.private_key or not args.message_file:
            parser.error("--private-key and --message-file required for signing")

        # Load and canonicalize message
        message_bytes = load_canonical_message(args.message_file)

        # Sign message
        signature_b64 = sign_message(args.private_key, message_bytes)

        print("Message signed successfully!")
        print("Signature (base64):", signature_b64)
        print("Message hash (for reference):", base64.b64encode(message_bytes).decode()[:32] + "...")

    else:
        # Generate keys for all agents
        agents = ['sentinel', 'oracle', 'midnight']
        all_keys = {}

        print("Generating ED25519 keypairs for all SON agents...")
        for agent in agents:
            private_key, public_key = generate_keypair()
            all_keys[agent] = {
                'public_key': public_key,
                'private_key': private_key
            }
            print(f"\n{agent.upper()}:")
            print(f"  Public Key:  {public_key}")
            print(f"  Private Key: {private_key}")

        # Save to file
        output_file = "test_vectors/agent_keys.json"
        os.makedirs("test_vectors", exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(all_keys, f, indent=2)
        print(f"\nAll agent keys saved to {output_file}")

        # Generate a sample signature
        sample_msg = {"test": "message", "timestamp": "2025-01-01T00:00:00Z"}
        sample_bytes = json.dumps(sample_msg, sort_keys=True, separators=(',', ':')).encode()

        print("\nSample signature test:")
        signature = sign_message(all_keys['sentinel']['private_key'], sample_bytes)
        print(f"Sample signature: {signature}")

if __name__ == '__main__':
    main()
