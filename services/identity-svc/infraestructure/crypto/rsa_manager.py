"""
Infrastructure layer - RSA Key Management for JWT signing
Generates and manages RSA key pairs for OAuth/OIDC JWT tokens
"""
import os
import json
from pathlib import Path
from typing import Dict, Tuple
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import base64


class RSAKeyManager:
    """Manages RSA key pairs for JWT signing and JWKS endpoint"""
    
    def __init__(self, keys_dir: str = "keys"):
        self.keys_dir = Path(keys_dir)
        self.keys_dir.mkdir(exist_ok=True)
        self.private_key_path = self.keys_dir / "private_key.pem"
        self.public_key_path = self.keys_dir / "public_key.pem"
        
    def generate_keys(self, key_size: int = 2048) -> None:
        """Generate new RSA key pair"""
        print(f"🔑 Generating RSA-{key_size} key pair...")
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        
        # Serialize private key
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        # Get public key and serialize
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # Save to files
        with open(self.private_key_path, 'wb') as f:
            f.write(private_pem)
        with open(self.public_key_path, 'wb') as f:
            f.write(public_pem)
            
        print(f"✅ Keys saved to {self.keys_dir}/")
    
    def load_private_key(self) -> str:
        """Load private key in PEM format"""
        if not self.private_key_path.exists():
            self.generate_keys()
        
        with open(self.private_key_path, 'r') as f:
            return f.read()
    
    def load_public_key(self) -> str:
        """Load public key in PEM format"""
        if not self.public_key_path.exists():
            self.generate_keys()
        
        with open(self.public_key_path, 'r') as f:
            return f.read()
    
    def get_jwks(self) -> Dict:
        """
        Generate JWKS (JSON Web Key Set) for OpenID Connect discovery
        Returns the public key in JWK format
        """
        if not self.public_key_path.exists():
            self.generate_keys()
        
        # Load public key
        with open(self.public_key_path, 'rb') as f:
            public_key = serialization.load_pem_public_key(
                f.read(),
                backend=default_backend()
            )
        
        # Extract public numbers
        public_numbers = public_key.public_numbers()
        
        # Convert to base64url encoding (without padding)
        def int_to_base64url(n: int) -> str:
            byte_length = (n.bit_length() + 7) // 8
            n_bytes = n.to_bytes(byte_length, byteorder='big')
            return base64.urlsafe_b64encode(n_bytes).rstrip(b'=').decode('utf-8')
        
        # Build JWK
        jwk = {
            "kty": "RSA",
            "use": "sig",
            "kid": "identity-svc-key-1",  # Key ID
            "alg": "RS256",
            "n": int_to_base64url(public_numbers.n),  # Modulus
            "e": int_to_base64url(public_numbers.e),  # Exponent
        }
        
        return {
            "keys": [jwk]
        }
    
    def ensure_keys_exist(self) -> None:
        """Ensure RSA keys exist, generate if they don't"""
        if not self.private_key_path.exists() or not self.public_key_path.exists():
            self.generate_keys()
