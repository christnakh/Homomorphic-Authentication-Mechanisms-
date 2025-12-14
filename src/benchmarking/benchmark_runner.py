import time
import yaml
import numpy as np
from typing import Dict, List, Any
from tqdm import tqdm

from src.algorithms import (
    BLSSignature, LHSSignature, WatersHomomorphicSignature,
    BonehBoyenHomomorphicSignature, RSASignature, EdDSASignature,
    AdditiveHMAC, LinearHMAC, PolynomialHMAC, LatticeHMAC
)
from src.benchmarking.metrics_collector import MetricsCollector
from src.benchmarking.security_benchmarks import SecurityBenchmark

class BenchmarkRunner:
    def __init__(self, config_path: str = "config/benchmark_config.yaml"):
        self.config = self._load_config(config_path)
        self.algorithms = {}
        self.metrics_collector = MetricsCollector()
        self.security_benchmark = SecurityBenchmark()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    def initialize_algorithms(self):
        if self.config.get("algorithms", {}).get("homomorphic_signatures"):
            for algo_config in self.config["algorithms"]["homomorphic_signatures"]:
                if algo_config.get("enabled", True):
                    name = algo_config["name"]
                    if name == "BLS":
                        self.algorithms[name] = BLSSignature()
                    elif name == "LHS":
                        vector_dim = self.config.get("benchmark", {}).get("vector_dimensions", [100])[0]
                        self.algorithms[name] = LHSSignature(vector_dim=vector_dim)
                    elif name == "Waters":
                        self.algorithms[name] = WatersHomomorphicSignature()
                    elif name == "BonehBoyen":
                        self.algorithms[name] = BonehBoyenHomomorphicSignature()
                    elif name == "RSA":
                        self.algorithms[name] = RSASignature()
                    elif name == "EdDSA":
                        self.algorithms[name] = EdDSASignature()
        if self.config.get("algorithms", {}).get("homomorphic_mac"):
            for algo_config in self.config["algorithms"]["homomorphic_mac"]:
                if algo_config.get("enabled", True):
                    name = algo_config["name"]
                    if name == "Additive_HMAC":
                        self.algorithms[name] = AdditiveHMAC()
                    elif name == "Linear_HMAC":
                        vector_dim = self.config.get("benchmark", {}).get("vector_dimensions", [100])[0]
                        self.algorithms[name] = LinearHMAC(vector_dim=vector_dim)
                    elif name == "Polynomial_HMAC":
                        self.algorithms[name] = PolynomialHMAC()
                    elif name == "Lattice_HMAC":
                        self.algorithms[name] = LatticeHMAC()
    def benchmark_key_generation(self, algorithm_name: str, iterations: int = 10) -> Dict[str, Any]:
        algo = self.algorithms.get(algorithm_name)
        if not algo:
            return {}
        times = []
        memory_peaks = []
        for _ in range(iterations):
            self.metrics_collector.start_memory_monitoring()
            self.metrics_collector.sample_memory()
            start = time.time()
            if hasattr(algo, 'key_generation'):
                algo.key_generation()
            times.append(time.time() - start)
            self.metrics_collector.sample_memory()
            memory_stats = self.metrics_collector.stop_memory_monitoring()
            memory_peaks.append(memory_stats["peak_mb"])
        avg_time = np.mean(times)
        std_time = np.std(times)
        avg_memory = np.mean(memory_peaks) if memory_peaks else 0.0
        self.metrics_collector.record_performance(
            algorithm=algorithm_name,
            operation="key_generation",
            key_gen_time=avg_time,
            memory_peak_mb=avg_memory
        )
        return {
            "algorithm": algorithm_name,
            "avg_time": avg_time,
            "std_time": std_time,
            "avg_memory_mb": avg_memory,
            "iterations": iterations
        }
    def benchmark_signing(self, algorithm_name: str, message_sizes: List[int], 
                         iterations: int = 10) -> Dict[str, Any]:
        algo = self.algorithms.get(algorithm_name)
        if not algo:
            return {}
        results = {}
        for msg_size in message_sizes:
            times = []
            memory_peaks = []
            for _ in range(iterations):
                self.metrics_collector.start_memory_monitoring()
                self.metrics_collector.sample_memory()
                message = np.random.bytes(msg_size)
                if hasattr(algo, 'sign'):
                    _, sign_time = algo.sign(message)
                    times.append(sign_time)
                elif hasattr(algo, 'generate_tag'):
                    _, gen_time = algo.generate_tag(message, b"test_id")
                    times.append(gen_time)
                self.metrics_collector.sample_memory()
                memory_stats = self.metrics_collector.stop_memory_monitoring()
                memory_peaks.append(memory_stats["peak_mb"])
            avg_time = np.mean(times)
            avg_memory = np.mean(memory_peaks) if memory_peaks else 0.0
            results[msg_size] = {
                "avg_time": avg_time,
                "std_time": np.std(times),
                "avg_memory_mb": avg_memory
            }
            self.metrics_collector.record_performance(
                algorithm=algorithm_name,
                operation=f"signing_{msg_size}",
                sign_time=avg_time,
                memory_peak_mb=avg_memory
            )
        return results
    def benchmark_verification(self, algorithm_name: str, message_sizes: List[int],
                              iterations: int = 10) -> Dict[str, Any]:
        algo = self.algorithms.get(algorithm_name)
        if not algo:
            return {}
        results = {}
        for msg_size in message_sizes:
            times = []
            for _ in range(iterations):
                message = np.random.bytes(msg_size)
                if hasattr(algo, 'sign'):
                    sig, _ = algo.sign(message)
                    _, verify_time = algo.verify(message, sig)
                    times.append(verify_time)
                elif hasattr(algo, 'generate_tag'):
                    tag, _ = algo.generate_tag(message, b"test_id")
                    _, verify_time = algo.verify_tag(message, tag, b"test_id")
                    times.append(verify_time)
            results[msg_size] = {
                "avg_time": np.mean(times),
                "std_time": np.std(times)
            }
            self.metrics_collector.record_performance(
                algorithm=algorithm_name,
                operation=f"verification_{msg_size}",
                verify_time=np.mean(times)
            )
        return results
    def benchmark_aggregation(self, algorithm_name: str, num_clients: List[int],
                            message_size: int = 4096, iterations: int = 5) -> Dict[str, Any]:
        algo = self.algorithms.get(algorithm_name)
        if not algo:
            return {}
        results = {}
        for n_clients in num_clients:
            times = []
            memory_peaks = []
            for _ in range(iterations):
                self.metrics_collector.start_memory_monitoring()
                self.metrics_collector.sample_memory()
                signatures = []
                messages = []
                for _ in range(n_clients):
                    message = np.random.bytes(message_size)
                    messages.append(message)
                    if hasattr(algo, 'sign'):
                        sig, _ = algo.sign(message)
                        signatures.append(sig)
                    elif hasattr(algo, 'generate_tag'):
                        tag, _ = algo.generate_tag(message, b"test_id")
                        signatures.append(tag)
                start = time.time()
                if hasattr(algo, 'aggregate_signatures'):
                    _, agg_time = algo.aggregate_signatures(signatures)
                    times.append(agg_time)
                elif hasattr(algo, 'combine_tags'):
                    _, combine_time = algo.combine_tags(signatures)
                    times.append(combine_time)
                else:
                    times.append(0.0)
                self.metrics_collector.sample_memory()
                memory_stats = self.metrics_collector.stop_memory_monitoring()
                memory_peaks.append(memory_stats["peak_mb"])
            avg_time = np.mean(times)
            avg_memory = np.mean(memory_peaks) if memory_peaks else 0.0
            results[n_clients] = {
                "avg_time": avg_time,
                "std_time": np.std(times),
                "avg_memory_mb": avg_memory
            }
            self.metrics_collector.record_performance(
                algorithm=algorithm_name,
                operation=f"aggregation_{n_clients}",
                aggregate_time=avg_time,
                memory_peak_mb=avg_memory
            )
        return results
    def benchmark_communication_overhead(self, algorithm_name: str) -> Dict[str, Any]:
        algo = self.algorithms.get(algorithm_name)
        if not algo:
            return {}
        sig_size = 0
        pub_key_size = 0
        priv_key_size = 0
        if hasattr(algo, 'get_signature_size'):
            sig_size = algo.get_signature_size()
        elif hasattr(algo, 'get_tag_size'):
            sig_size = algo.get_tag_size()
        if hasattr(algo, 'get_public_key_size'):
            pub_key_size = algo.get_public_key_size()
        if hasattr(algo, 'get_key_size'):
            priv_key_size = algo.get_key_size()
        nonce_size = 16
        message_commitment_size = 32
        proof_of_possession_size = 0
        aggregate_sig_size = sig_size
        if algorithm_name == "BLS":
            aggregate_sig_size = sig_size
        elif algorithm_name in ["Additive_HMAC", "Linear_HMAC"]:
            aggregate_sig_size = sig_size
        metadata_per_round = pub_key_size + nonce_size + message_commitment_size + proof_of_possession_size
        self.metrics_collector.record_communication(
            algorithm=algorithm_name,
            signature_size=sig_size,
            public_key_size=pub_key_size,
            private_key_size=priv_key_size,
            tag_size=sig_size,
            aggregate_signature_size=aggregate_sig_size,
            nonce_size=nonce_size,
            message_commitment_size=message_commitment_size,
            proof_of_possession_size=proof_of_possession_size,
            metadata_per_round=metadata_per_round,
            compression_ratio=1.0 if aggregate_sig_size == sig_size else sig_size / aggregate_sig_size
        )
        return {
            "algorithm": algorithm_name,
            "signature_size": sig_size,
            "public_key_size": pub_key_size,
            "private_key_size": priv_key_size,
            "nonce_size": nonce_size,
            "message_commitment_size": message_commitment_size,
            "proof_of_possession_size": proof_of_possession_size,
            "metadata_per_round": metadata_per_round,
            "aggregate_signature_size": aggregate_sig_size
        }
    def run_full_benchmark(self) -> Dict[str, Any]:
        print("Initializing algorithms...")
        self.initialize_algorithms()
        benchmark_config = self.config.get("benchmark", {})
        num_clients = benchmark_config.get("num_clients", [10, 50, 100])
        message_sizes = benchmark_config.get("message_sizes", [1024, 4096, 16384])
        iterations = benchmark_config.get("iterations", 10)
        results = {}
        for algo_name in tqdm(self.algorithms.keys(), desc="Benchmarking algorithms"):
            print(f"\nBenchmarking {algo_name}...")
            algo_results = {}
            print(f"  Key generation...")
            algo_results["key_generation"] = self.benchmark_key_generation(algo_name, iterations)
            print(f"  Signing...")
            algo_results["signing"] = self.benchmark_signing(algo_name, message_sizes, iterations)
            print(f"  Verification...")
            algo_results["verification"] = self.benchmark_verification(algo_name, message_sizes, iterations)
            print(f"  Aggregation...")
            algo_results["aggregation"] = self.benchmark_aggregation(
                algo_name, num_clients, message_sizes[1], iterations // 2
            )
            print(f"  Communication overhead...")
            algo_results["communication"] = self.benchmark_communication_overhead(algo_name)
            print(f"  Security benchmarks...")
            algo_results["security"] = self.security_benchmark.run_security_suite(
                self.algorithms[algo_name], algo_name
            )
            results[algo_name] = algo_results
        return results
    def export_results(self, output_dir: str = "results/"):
        import os
        os.makedirs(output_dir, exist_ok=True)
        self.metrics_collector.export_to_json(f"{output_dir}/metrics.json")
        self.metrics_collector.export_to_csv(f"{output_dir}/metrics")