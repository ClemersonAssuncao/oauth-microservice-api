"""
OpenID Connect Discovery endpoints
"""
from fastapi import APIRouter
from interfaces.api.container import Container

router = APIRouter()
container = Container()


@router.get("/.well-known/openid-configuration")
async def openid_configuration():
    """OpenID Connect Discovery endpoint"""
    settings = container.settings
    return {
        "issuer": settings.issuer,
        "authorization_endpoint": f"{settings.issuer}/oauth/authorize",
        "token_endpoint": f"{settings.issuer}/api/v1/auth/token",
        "userinfo_endpoint": f"{settings.issuer}/api/v1/auth/userinfo",
        "jwks_uri": f"{settings.issuer}/.well-known/jwks.json",
        "introspection_endpoint": f"{settings.issuer}/api/v1/auth/introspect",
        "response_types_supported": ["code", "token"],
        "grant_types_supported": ["authorization_code", "password", "refresh_token"],
        "subject_types_supported": ["public"],
        "id_token_signing_alg_values_supported": ["RS256"],
        "scopes_supported": ["openid", "profile", "email"],
        "token_endpoint_auth_methods_supported": ["client_secret_basic", "client_secret_post"],
        "claims_supported": ["sub", "iss", "aud", "exp", "iat", "username", "email", "roles"]
    }


@router.get("/.well-known/jwks.json")
async def jwks():
    """JSON Web Key Set endpoint"""
    return container.rsa_manager.get_jwks()
