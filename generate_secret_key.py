#!/usr/bin/env python3
"""
Generate a secure SECRET_KEY for PackOptima deployment
"""
import secrets

def generate_secret_key():
    """Generate a cryptographically secure random key"""
    return secrets.token_urlsafe(32)

if __name__ == "__main__":
    key = generate_secret_key()
    print("=" * 60)
    print("🔐 Your Secure SECRET_KEY for PackOptima")
    print("=" * 60)
    print()
    print(key)
    print()
    print("=" * 60)
    print("Copy this key and use it in Render.com environment variables")
    print("=" * 60)
