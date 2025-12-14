"""
Homomorphic Encryption Integration

This module provides integration with homomorphic encryption libraries
for encrypted aggregation in Federated Learning.
"""

import time
from typing import Tuple, Optional, List, Any
import numpy as np

try:
    import tenseal as ts
    TENSEAL_AVAILABLE = True
except ImportError:
    TENSEAL_AVAILABLE = False
    print("Warning: tenseal not available. Using fallback implementation.")

try:
    from Pyfhel import Pyfhel
    PYFHEL_AVAILABLE = True
except ImportError:
    PYFHEL_AVAILABLE = False
    print("Warning: Pyfhel not available. Using fallback implementation.")


class HomomorphicEncryption:
    """
    Homomorphic Encryption Wrapper
    
    Supports encrypted aggregation for FL:
    - Clients encrypt their updates
    - Server aggregates encrypted updates
    - Result can be decrypted (or used for further computation)
    
    Uses Microsoft SEAL (via tenseal) for CKKS scheme
    """
    
    def __init__(self, scheme: str = "CKKS", poly_modulus_degree: int = 8192):
        self.scheme = scheme
        self.poly_modulus_degree = poly_modulus_degree
        self.context: Optional[Any] = None
        self.public_key: Optional[Any] = None
        self.secret_key: Optional[Any] = None
        self.key_gen_time = 0.0
        
    def key_generation(self) -> Tuple[Any, Any]:
        """Generate HE key pair using Microsoft SEAL (via tenseal)"""
        start = time.time()
        if TENSEAL_AVAILABLE and self.scheme == "CKKS":
            # Generate CKKS context and keys using Microsoft SEAL
            # Library: tenseal (Python wrapper for Microsoft SEAL)
            # Source: https://github.com/OpenMined/TenSEAL
            # Microsoft SEAL: https://github.com/microsoft/SEAL
            self.context = ts.context(
                ts.SCHEME_TYPE.CKKS,
                poly_modulus_degree=self.poly_modulus_degree,
                coeff_mod_bit_sizes=[60, 40, 40, 60]
            )
            self.context.generate_galois_keys()
            self.context.global_scale = 2**40
            self.public_key = self.context
            self.secret_key = self.context.secret_key()
            self._using_real_he = True
        else:
            # Fallback: mock keys (only if tenseal not available)
            if not TENSEAL_AVAILABLE:
                print("WARNING: tenseal not available. Using fallback implementation.")
                print("Install with: pip install tenseal")
            self.public_key = "mock_public_key"
            self.secret_key = "mock_secret_key"
            self._using_real_he = False
        
        self.key_gen_time = time.time() - start
        return self.public_key, self.secret_key
    
    def is_using_real_he(self) -> bool:
        """Check if using real HE library or fallback"""
        return getattr(self, '_using_real_he', False)
    
    def encrypt(self, data: np.ndarray) -> Tuple[Any, float]:
        """Encrypt data vector"""
        start = time.time()
        if TENSEAL_AVAILABLE and self.context:
            encrypted = ts.ckks_vector(self.context, data.tolist())
            encrypt_time = time.time() - start
            return encrypted, encrypt_time
        else:
            # Fallback: return data as-is (no encryption)
            encrypt_time = time.time() - start
            return data, encrypt_time
    
    def decrypt(self, encrypted_data: Any) -> Tuple[np.ndarray, float]:
        """Decrypt encrypted data"""
        start = time.time()
        if TENSEAL_AVAILABLE and hasattr(encrypted_data, 'decrypt'):
            decrypted = np.array(encrypted_data.decrypt())
            decrypt_time = time.time() - start
            return decrypted, decrypt_time
        else:
            # Fallback: return as-is
            if isinstance(encrypted_data, np.ndarray):
                decrypt_time = time.time() - start
                return encrypted_data, decrypt_time
            else:
                decrypt_time = time.time() - start
                return np.array([]), decrypt_time
    
    def aggregate_encrypted(self, encrypted_updates: List[Any]) -> Tuple[Any, float]:
        """Aggregate encrypted updates"""
        start = time.time()
        if TENSEAL_AVAILABLE and len(encrypted_updates) > 0:
            if hasattr(encrypted_updates[0], '__add__'):
                # Homomorphic addition
                result = encrypted_updates[0]
                for update in encrypted_updates[1:]:
                    result = result + update
                agg_time = time.time() - start
                return result, agg_time
        
        # Fallback: aggregate as numpy arrays
        if isinstance(encrypted_updates[0], np.ndarray):
            result = sum(encrypted_updates)
            agg_time = time.time() - start
            return result, agg_time
        else:
            agg_time = time.time() - start
            return encrypted_updates[0] if encrypted_updates else None, agg_time
    
    def get_ciphertext_size(self, encrypted_data: Any) -> int:
        """Estimate ciphertext size in bytes"""
        if TENSEAL_AVAILABLE and hasattr(encrypted_data, 'serialize'):
            try:
                serialized = encrypted_data.serialize()
                return len(serialized)
            except:
                pass
        # Fallback estimate
        return self.poly_modulus_degree * 8  # Rough estimate
    
    def get_public_key_size(self) -> int:
        """Estimate public key size in bytes"""
        if TENSEAL_AVAILABLE and self.context:
            try:
                serialized = self.context.serialize()
                return len(serialized)
            except:
                pass
        return self.poly_modulus_degree * 16  # Rough estimate

