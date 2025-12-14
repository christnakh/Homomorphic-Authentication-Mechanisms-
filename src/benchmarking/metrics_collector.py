import json
import numpy as np
import psutil
import os
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional

@dataclass
class PerformanceMetrics:
    operation: str
    algorithm: str
    key_gen_time: float = 0.0
    sign_time: float = 0.0
    verify_time: float = 0.0
    aggregate_time: float = 0.0
    aggregate_verify_time: float = 0.0
    encrypt_time: float = 0.0
    decrypt_time: float = 0.0
    total_time: float = 0.0
    memory_peak_mb: float = 0.0
    memory_avg_mb: float = 0.0

    operation: str
    algorithm: str
    key_gen_time: float = 0.0
    sign_time: float = 0.0
    verify_time: float = 0.0
    aggregate_time: float = 0.0
    aggregate_verify_time: float = 0.0
    encrypt_time: float = 0.0
    decrypt_time: float = 0.0
    total_time: float = 0.0
    memory_peak_mb: float = 0.0
    memory_avg_mb: float = 0.0
@dataclass
class CommunicationMetrics:
    algorithm: str
    signature_size: int = 0
    public_key_size: int = 0
    private_key_size: int = 0
    tag_size: int = 0
    ciphertext_size: int = 0
    total_message_size: int = 0
    aggregate_signature_size: int = 0
    compression_ratio: float = 1.0
    nonce_size: int = 0
    proof_of_possession_size: int = 0
    message_commitment_size: int = 0
    metadata_per_round: int = 0
@dataclass
class SecurityMetrics:
    algorithm: str
    security_notion: str = ""
    public_verifiability: bool = False
    homomorphic_operations: List[str] = None
    limitations: List[str] = None
    key_distribution: str = ""

class MetricsCollector:
    def __init__(self):
        self.performance_metrics = []
        self.communication_metrics = []
        self.security_metrics = []
        self.process = psutil.Process(os.getpid())
        self.memory_samples = []
    
    def start_memory_monitoring(self):
        self.memory_samples = []
    def sample_memory(self):
        try:
            memory_mb = self.process.memory_info().rss / 1024 / 1024
            self.memory_samples.append(memory_mb)
        except:
            pass
    def stop_memory_monitoring(self) -> Dict[str, float]:
        if not self.memory_samples:
            return {"peak_mb": 0.0, "avg_mb": 0.0}
        return {
            "peak_mb": max(self.memory_samples),
            "avg_mb": np.mean(self.memory_samples)
        }
    def record_performance(self, algorithm: str, operation: str, **kwargs):
        metrics_data = {
            "operation": operation,
            "algorithm": algorithm
        }
        valid_fields = ['key_gen_time', 'sign_time', 'verify_time', 'agg_time', 
                       'memory_peak_mb', 'memory_avg_mb']
        for field in valid_fields:
            if field in kwargs:
                metrics_data[field] = kwargs[field]
        metrics = PerformanceMetrics(
            operation=operation,
            algorithm=algorithm
        )
        for key, value in kwargs.items():
            setattr(metrics, key, value)
        self.performance_metrics.append(metrics)
    def record_communication(self, algorithm: str, **kwargs):
        metrics = CommunicationMetrics(
            algorithm=algorithm,
            **kwargs
        )
        self.communication_metrics.append(metrics)
    def record_security(self, algorithm: str, **kwargs):
        metrics = SecurityMetrics(
            algorithm=algorithm,
            **kwargs
        )
        self.security_metrics.append(metrics)
    def get_summary_statistics(self) -> Dict[str, Any]:
        summary = {
            "performance": {},
            "communication": {},
            "security": {}
        }
        if self.performance_metrics:
            algorithms = set(m.algorithm for m in self.performance_metrics)
            for algo in algorithms:
                algo_metrics = [m for m in self.performance_metrics if m.algorithm == algo]
                summary["performance"][algo] = {
                    "avg_key_gen_time": np.mean([m.key_gen_time for m in algo_metrics]),
                    "avg_sign_time": np.mean([m.sign_time for m in algo_metrics]),
                    "avg_verify_time": np.mean([m.verify_time for m in algo_metrics]),
                    "avg_aggregate_time": np.mean([m.aggregate_time for m in algo_metrics]),
                    "avg_total_time": np.mean([m.total_time for m in algo_metrics]),
                    "avg_memory_peak": np.mean([m.memory_peak_mb for m in algo_metrics])
                }
        if self.communication_metrics:
            algorithms = set(m.algorithm for m in self.communication_metrics)
            for algo in algorithms:
                algo_metrics = [m for m in self.communication_metrics if m.algorithm == algo]
                summary["communication"][algo] = {
                    "avg_signature_size": np.mean([m.signature_size for m in algo_metrics]),
                    "avg_public_key_size": np.mean([m.public_key_size for m in algo_metrics]),
                    "avg_total_message_size": np.mean([m.total_message_size for m in algo_metrics])
                }
        return summary
    def export_to_json(self, filepath: str):
        data = {
            "performance": [asdict(m) for m in self.performance_metrics],
            "communication": [asdict(m) for m in self.communication_metrics],
            "security": [asdict(m) for m in self.security_metrics],
            "summary": self.get_summary_statistics()
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    def export_to_csv(self, filepath_prefix: str):
        import pandas as pd
        if self.performance_metrics:
            df_perf = pd.DataFrame([asdict(m) for m in self.performance_metrics])
            df_perf.to_csv(f"{filepath_prefix}_performance.csv", index=False)
        if self.communication_metrics:
            df_comm = pd.DataFrame([asdict(m) for m in self.communication_metrics])
            df_comm.to_csv(f"{filepath_prefix}_communication.csv", index=False)
        if self.security_metrics:
            df_sec = pd.DataFrame([asdict(m) for m in self.security_metrics])
            df_sec.to_csv(f"{filepath_prefix}_security.csv", index=False)