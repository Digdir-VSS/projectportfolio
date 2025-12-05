import requests
import jwt
from jwt.algorithms import RSAAlgorithm
import os 
from dotenv import load_dotenv

load_dotenv()

def _get_tenant_public_key_for_key_id(key_id, tenant_name):
    """
    Obtain the public key used by Azure AD to sign tokens.

    Note that this method obtains all public keys on every call. This could be optimised by caching these keys and/or by
    only obtaining keys that are not yet present in the cache.
    """
    jwks_url = f"https://login.microsoftonline.com/{tenant_name}/discovery/v2.0/keys"
    response = requests.get(jwks_url)
    jwks = response.json()

    # Find the correct key from the available keys
    key = next((key for key in jwks["keys"] if key["kid"] == key_id), None)

    # Attempt to extract the actual public key
    if key:
        public_key = RSAAlgorithm.from_jwk(key)
    else:
        raise Exception("Public key not found")

    return public_key


def validate_token(jwt_token, tenant_name):
    """Validate the JWT token using the public key from Azure AD."""

    # Obtain relevant specifications from the JWT token
    header = jwt.get_unverified_header(jwt_token)
    algorithm = header["alg"]
    key_id = header["kid"]

    # Obtain the Azure public key corresponding to our tenant and the given `key_id` that was included in the JWT token.
    tenant_public_key = _get_tenant_public_key_for_key_id(key_id, tenant_name)

    try:
        # Decode the token, verifying the signature and claims
        decoded_token = jwt.decode(jwt_token, tenant_public_key, algorithms=[algorithm], audience=os.getenv("CLIENT_ID"))
        return decoded_token
    except jwt.PyJWTError as e:
        print(f"Token validation error: {e}")
        return None
