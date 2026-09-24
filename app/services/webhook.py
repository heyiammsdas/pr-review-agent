import os
import hmac
import hashlib

def verify_github_signature(payload_body: bytes, signature_header: str) -> bool:
    """
    Verifies the GitHub webhook signature using HMAC SHA-256.
    """
    secret = os.getenv("GITHUB_WEBHOOK_SECRET")
    if not secret:
        # Fail securely if the secret is not configured
        return False
        
    if not signature_header or not signature_header.startswith("sha256="):
        return False
        
    # Calculate the expected HMAC SHA-256 hash
    expected_hash = hmac.new(
        secret.encode('utf-8'),
        payload_body,
        hashlib.sha256
    ).hexdigest()
    
    expected_signature = f"sha256={expected_hash}"
    
    # Use compare_digest to prevent timing attacks
    return hmac.compare_digest(expected_signature, signature_header)

def generate_test_signature(payload_body: bytes, secret: str) -> str:
    """
    Utility for tests to generate a valid signature.
    """
    hash_value = hmac.new(
        secret.encode('utf-8'),
        payload_body,
        hashlib.sha256
    ).hexdigest()
    return f"sha256={hash_value}"
