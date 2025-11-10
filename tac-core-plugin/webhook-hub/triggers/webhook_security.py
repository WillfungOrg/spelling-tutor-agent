"""GitHub webhook security utilities.

Provides HMAC-SHA256 signature verification for GitHub webhooks to prevent
unauthorized requests and spoofing attacks.
"""

import hmac
import hashlib
from typing import Optional


def verify_github_signature(
    payload_body: bytes,
    signature_header: str,
    secret: str
) -> bool:
    """Verify GitHub webhook HMAC-SHA256 signature.

    Uses constant-time comparison to prevent timing attacks.

    Args:
        payload_body: Raw request body bytes
        signature_header: X-Hub-Signature-256 header value
        secret: Webhook secret from environment

    Returns:
        True if signature is valid, False otherwise

    Example:
        >>> body = b'{"action":"opened"}'
        >>> signature = "sha256=abc123..."
        >>> secret = "my-webhook-secret"
        >>> verify_github_signature(body, signature, secret)
        True
    """
    if not signature_header or not signature_header.startswith("sha256="):
        return False

    # Create HMAC hash of payload
    hash_object = hmac.new(
        secret.encode('utf-8'),
        msg=payload_body,
        digestmod=hashlib.sha256
    )
    expected_signature = "sha256=" + hash_object.hexdigest()

    # CRITICAL: Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(expected_signature, signature_header)
