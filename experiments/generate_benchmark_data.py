#!/usr/bin/env python3
import json
import time
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.algorithms import (
    BLSSignature, LHSSignature, WatersHomomorphicSignature,
    BonehBoyenHomomorphicSignature, RSASignature, EdDSASignature,
    AdditiveHMAC, LinearHMAC
)

def benchmark_algorithm(algo, name, message_sizes=[1024, 4096, 16384], num_clients=[10, 50, 100]):
    results = {
        "name": name,
        "key_gen_time": [],
        "sign_times": {},
        "verify_times": {},
        "aggregate_times": {},
        "signature_sizes": [],
        "public_key_sizes": []
    }
    if hasattr(algo, 'key_generation'):
        for _ in range(5):
            start = time.time()
            if name in ["Additive_HMAC", "Linear_HMAC"]:
                key = algo.key_generation()
            else:
                priv, pub = algo.key_generation()
            key_time = time.time() - start
            results["key_gen_time"].append(key_time)
    for msg_size in message_sizes:
        message = b'x' * msg_size
        times = []
        for _ in range(10):
            if name in ["Additive_HMAC", "Linear_HMAC"]:
                if name == "Linear_HMAC":
                    vector = np.random.randn(100).astype(np.float32)
                    tag, t = algo.generate_tag(vector, b"test")
                else:
                    tag, t = algo.generate_tag(message, b"test")
            else:
                sig, t = algo.sign(message)
            times.append(t)
        results["sign_times"][msg_size] = {
            "mean": np.mean(times),
            "std": np.std(times)
        }
    if hasattr(algo, 'get_signature_size'):
        results["signature_sizes"].append(algo.get_signature_size())
    if hasattr(algo, 'get_public_key_size'):
        results["public_key_sizes"].append(algo.get_public_key_size())
    for n in num_clients:
        if hasattr(algo, 'aggregate_signatures'):
            signatures = []
            for _ in range(n):
                if name in ["Additive_HMAC", "Linear_HMAC"]:
                    if name == "Linear_HMAC":
                        vector = np.random.randn(100).astype(np.float32)
                        tag, _ = algo.generate_tag(vector, b"test")
                    else:
                        tag, _ = algo.generate_tag(b"test_msg", b"test")
                    signatures.append(tag)
                else:
                    sig, _ = algo.sign(b"test_message")
                    signatures.append(sig)
            times = []
            for _ in range(5):
                if hasattr(algo, 'aggregate_signatures'):
                    agg_sig, t = algo.aggregate_signatures(signatures)
                elif hasattr(algo, 'combine_tags'):
                    agg_sig, t = algo.combine_tags(signatures)
                else:
                    t = 0.0
                times.append(t)
            results["aggregate_times"][n] = {
                "mean": np.mean(times),
                "std": np.std(times)
            }
    return results

def main():
    print("Generating benchmark data...")
    algorithms = {
        "BLS": BLSSignature(),
        "LHS": LHSSignature(vector_dim=100),
        "Waters": WatersHomomorphicSignature(),
        "BonehBoyen": BonehBoyenHomomorphicSignature(),
        "RSA": RSASignature(),
        "EdDSA": EdDSASignature(),
        "Additive_HMAC": AdditiveHMAC(),
        "Linear_HMAC": LinearHMAC(vector_dim=100)
    }
    all_results = {}
    for name, algo in algorithms.items():
        print(f"Benchmarking {name}...")
        try:
            results = benchmark_algorithm(algo, name)
            all_results[name] = results
        except Exception as e:
            print(f"Error benchmarking {name}: {e}")
            continue
    output_file = Path("results/benchmark_summary.json")
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"\nResults saved to {output_file}")
    print("\nSummary:")
    for name, results in all_results.items():
        avg_key_gen = np.mean(results["key_gen_time"]) if results["key_gen_time"] else 0
        print(f"{name}: Key gen={avg_key_gen*1000:.2f}ms, Sign={np.mean(list(results['sign_times'].values())[0]['mean'])*1000:.3f}ms")

if __name__ == "__main__":
    main()
