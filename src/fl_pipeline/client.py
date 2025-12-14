import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import time

from src.algorithms import (
    BLSSignature, LHSSignature, WatersHomomorphicSignature,
    BonehBoyenHomomorphicSignature, RSASignature, EdDSASignature,
    AdditiveHMAC, LinearHMAC, PolynomialHMAC, LatticeHMAC
)
from src.algorithms.homomorphic_encryption import HomomorphicEncryption
from src.fl_pipeline.aggregation import Aggregator

class FLClient:
    def __init__(self, client_id: int, model_dim: int = 1000,
                 auth_scheme: str = "BLS", use_encryption: bool = False):
        self.client_id = client_id
        self.model_dim = model_dim
        self.auth_scheme = auth_scheme
        self.use_encryption = use_encryption
        self.local_model = np.random.randn(model_dim).astype(np.float32)
        self.auth_handler = None
        self.auth_keys = {}
        self.he_handler = None
        self._init_auth_scheme()
        if use_encryption:
            self.he_handler = HomomorphicEncryption()
            self.he_handler.key_generation()
    
    def _init_auth_scheme(self):
        scheme = self.auth_scheme
        if scheme == "BLS":
            self.auth_handler = BLSSignature()
            priv_key, pub_key = self.auth_handler.key_generation()
            self.auth_keys = {"private": priv_key, "public": pub_key}
        elif scheme == "LHS":
            self.auth_handler = LHSSignature(vector_dim=self.model_dim)
            priv_key, pub_key = self.auth_handler.key_generation()
            self.auth_keys = {"private": priv_key, "public": pub_key}
        elif scheme == "Waters":
            self.auth_handler = WatersHomomorphicSignature()
            priv_key, pub_key = self.auth_handler.key_generation()
            self.auth_keys = {"private": priv_key, "public": pub_key}
        elif scheme == "BonehBoyen":
            self.auth_handler = BonehBoyenHomomorphicSignature()
            priv_key, pub_key = self.auth_handler.key_generation()
            self.auth_keys = {"private": priv_key, "public": pub_key}
        elif scheme == "RSA":
            self.auth_handler = RSASignature()
            priv_key, pub_key = self.auth_handler.key_generation()
            self.auth_keys = {"private": priv_key, "public": pub_key}
        elif scheme == "EdDSA":
            self.auth_handler = EdDSASignature()
            priv_key, pub_key = self.auth_handler.key_generation()
            self.auth_keys = {"private": priv_key, "public": pub_key}
        elif scheme == "Additive_HMAC":
            self.auth_handler = AdditiveHMAC()
            secret_key = self.auth_handler.key_generation()
            self.auth_keys = {"secret": secret_key}
        elif scheme == "Linear_HMAC":
            self.auth_handler = LinearHMAC(vector_dim=self.model_dim)
            secret_key = self.auth_handler.key_generation()
            self.auth_keys = {"secret": secret_key}
        elif scheme == "Polynomial_HMAC":
            self.auth_handler = PolynomialHMAC()
            secret_key = self.auth_handler.key_generation()
            self.auth_keys = {"secret": secret_key}
        elif scheme == "Lattice_HMAC":
            self.auth_handler = LatticeHMAC()
            secret_key = self.auth_handler.key_generation()
            self.auth_keys = {"secret": secret_key}
    def compute_local_update(self, global_model: Optional[np.ndarray] = None) -> np.ndarray:
        update = np.random.randn(self.model_dim).astype(np.float32) * 0.1
        if global_model is not None:
            update = global_model + update
        return update
    
    def prepare_update(self, global_model: Optional[np.ndarray] = None) -> Dict[str, Any]:
        update = self.compute_local_update(global_model)
        auth_data = self.authenticate_update(update)
        result = {
            "update": update,
            "client_id": self.client_id,
            "auth_tag": auth_data.get("tag"),
            "auth_metadata": auth_data.get("metadata", {})
        }
        if self.use_encryption and self.he_handler:
            encrypted, _ = self.he_handler.encrypt(update)
            result["update"] = encrypted
            result["encrypted"] = True
        return result
    
    def authenticate_update(self, update: np.ndarray) -> Dict[str, Any]:
        if not self.auth_handler:
            return {"tag": b"", "metadata": {}}
        update_bytes = update.tobytes()
        if hasattr(self.auth_handler, 'sign'):
            sig, sign_time = self.auth_handler.sign(update_bytes)
            metadata = {
                "public_key": self.auth_keys.get("public"),
                "sign_time": sign_time
            }
            return {"tag": sig, "metadata": metadata}
        elif hasattr(self.auth_handler, 'generate_tag'):
            identifier = f"client_{self.client_id}".encode()
            tag, gen_time = self.auth_handler.generate_tag(update_bytes, identifier)
            metadata = {
                "identifier": identifier,
                "gen_time": gen_time
            }
            return {"tag": tag, "metadata": metadata}
        return {"tag": b"", "metadata": {}}