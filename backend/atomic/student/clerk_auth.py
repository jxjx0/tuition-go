import os
import time
import jwt
import requests
from functools import wraps
from flask import request, jsonify

# Cache for JWKS keys
_jwks_cache = {
    "keys": None,
    "fetched_at": 0,
}
_CACHE_TTL = 300  # 5 minutes


def _get_jwks_url():
    """Get the Clerk JWKS URL from environment."""
    url = os.environ.get("CLERK_JWKS_URL")
    if not url:
        raise RuntimeError("CLERK_JWKS_URL environment variable is not set")
    return url


def _fetch_jwks():
    """Fetch and cache JWKS keys from Clerk."""
    now = time.time()
    if _jwks_cache["keys"] and (now - _jwks_cache["fetched_at"]) < _CACHE_TTL:
        return _jwks_cache["keys"]

    jwks_url = _get_jwks_url()
    response = requests.get(jwks_url, timeout=5)
    response.raise_for_status()
    jwks = response.json()

    _jwks_cache["keys"] = jwks
    _jwks_cache["fetched_at"] = now
    return jwks


def _get_signing_key(token):
    """Find the correct signing key from JWKS for the given token."""
    jwks = _fetch_jwks()
    unverified_header = jwt.get_unverified_header(token)
    kid = unverified_header.get("kid")

    for key_data in jwks.get("keys", []):
        if key_data.get("kid") == kid:
            return jwt.algorithms.RSAAlgorithm.from_jwk(key_data)

    raise jwt.exceptions.InvalidKeyError(
        f"No matching key found for kid: {kid}"
    )


def verify_clerk_token(token):
    """
    Verify a Clerk JWT token and return the decoded claims.
    Raises jwt.exceptions on failure.
    """
    signing_key = _get_signing_key(token)
    decoded = jwt.decode(
        token,
        signing_key,
        algorithms=["RS256"],
        options={
            "verify_exp": True,
            "verify_aud": False,  # Clerk tokens may not have aud
        },
    )
    return decoded


def require_auth(f):
    """
    Flask route decorator that requires a valid Clerk JWT.
    Sets request.clerk_user_id and request.clerk_claims on success.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return {"error": "Missing or invalid Authorization header"}, 401

        token = auth_header[7:]  # Strip "Bearer "

        try:
            claims = verify_clerk_token(token)
        except jwt.ExpiredSignatureError:
            return {"error": "Token has expired"}, 401
        except jwt.InvalidTokenError as e:
            return {"error": f"Invalid token: {str(e)}"}, 401
        except Exception as e:
            return {"error": f"Authentication failed: {str(e)}"}, 500

        # Attach user info to request context
        request.clerk_user_id = claims.get("sub")
        request.clerk_claims = claims
        return f(*args, **kwargs)

    return decorated
