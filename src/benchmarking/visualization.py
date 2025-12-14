import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import os

class Visualizer:
    def __init__(self, output_dir: str = "results/plots"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 8)
    
    def plot_performance_comparison(self, metrics_data: Dict[str, Any], 
                                   output_file: str = "performance_comparison.png"):
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        algorithms = list(metrics_data.keys())
        
        key_gen_times = [metrics_data[algo].get("key_generation", {}).get("avg_time", 0) 
                        for algo in algorithms]
        axes[0, 0].bar(algorithms, key_gen_times)
        axes[0, 0].set_title("Key Generation Time")
        axes[0, 0].set_ylabel("Time (seconds)")
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        sign_times = []
        for algo in algorithms:
            signing_data = metrics_data[algo].get("signing", {})
            if signing_data:
                times = [v.get("avg_time", 0) for k, v in signing_data.items() if isinstance(k, int)]
                sign_times.append(times[1] if len(times) > 1 else times[0] if times else 0)
            else:
                sign_times.append(0)
        axes[0, 1].bar(algorithms, sign_times)
        axes[0, 1].set_title("Signing Time (4KB message)")
        axes[0, 1].set_ylabel("Time (seconds)")
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        verify_times = []
        for algo in algorithms:
            verify_data = metrics_data[algo].get("verification", {})
            if verify_data:
                times = [v.get("avg_time", 0) for k, v in verify_data.items() if isinstance(k, int)]
                verify_times.append(times[1] if len(times) > 1 else times[0] if times else 0)
            else:
                verify_times.append(0)
        axes[1, 0].bar(algorithms, verify_times)
        axes[1, 0].set_title("Verification Time (4KB message)")
        axes[1, 0].set_ylabel("Time (seconds)")
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        agg_times = []
        for algo in algorithms:
            agg_data = metrics_data[algo].get("aggregation", {})
            if agg_data:
                times = [v.get("avg_time", 0) for k, v in agg_data.items() if isinstance(k, int)]
                agg_times.append(times[-1] if times else 0)
            else:
                agg_times.append(0)
        axes[1, 1].bar(algorithms, agg_times)
        axes[1, 1].set_title("Aggregation Time (100 clients)")
        axes[1, 1].set_ylabel("Time (seconds)")
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, output_file), dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_scalability(self, metrics_data: Dict[str, Any],
                        output_file: str = "scalability.png"):
        fig, ax = plt.subplots(figsize=(12, 8))
        
        algorithms = list(metrics_data.keys())
        
        for algo in algorithms:
            agg_data = metrics_data[algo].get("aggregation", {})
            if agg_data:
                num_clients = sorted([k for k in agg_data.keys() if isinstance(k, int)])
                times = [agg_data[n].get("avg_time", 0) for n in num_clients]
                ax.plot(num_clients, times, marker='o', label=algo, linewidth=2)
        
        ax.set_xlabel("Number of Clients")
        ax.set_ylabel("Aggregation Time (seconds)")
        ax.set_title("Scalability: Aggregation Time vs Number of Clients")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, output_file), dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_communication_overhead(self, metrics_data: Dict[str, Any],
                                   output_file: str = "communication_overhead.png"):
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        algorithms = list(metrics_data.keys())
        
        sig_sizes = []
        for algo in algorithms:
            comm_data = metrics_data[algo].get("communication", {})
            sig_sizes.append(comm_data.get("signature_size", 0))
        
        axes[0].bar(algorithms, sig_sizes)
        axes[0].set_title("Signature/Tag Size")
        axes[0].set_ylabel("Size (bytes)")
        axes[0].tick_params(axis='x', rotation=45)
        
        pub_key_sizes = []
        for algo in algorithms:
            comm_data = metrics_data[algo].get("communication", {})
            pub_key_sizes.append(comm_data.get("public_key_size", 0))
        
        axes[1].bar(algorithms, pub_key_sizes)
        axes[1].set_title("Public Key Size")
        axes[1].set_ylabel("Size (bytes)")
        axes[1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, output_file), dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_message_size_impact(self, metrics_data: Dict[str, Any],
                                output_file: str = "message_size_impact.png"):
        fig, ax = plt.subplots(figsize=(12, 8))
        
        algorithms = list(metrics_data.keys())
        message_sizes = [1024, 4096, 16384]
        
        for algo in algorithms:
            signing_data = metrics_data[algo].get("signing", {})
            if signing_data:
                times = [signing_data.get(size, {}).get("avg_time", 0) for size in message_sizes]
                ax.plot(message_sizes, times, marker='o', label=algo, linewidth=2)
        
        ax.set_xlabel("Message Size (bytes)")
        ax.set_ylabel("Signing Time (seconds)")
        ax.set_title("Message Size Impact on Signing Time")
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xscale('log')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, output_file), dpi=300, bbox_inches='tight')
        plt.close()
    
    def create_summary_table(self, metrics_data: Dict[str, Any],
                           output_file: str = "summary_table.txt"):
        try:
            from tabulate import tabulate
        except ImportError:
            tabulate = None
        
        algorithms = list(metrics_data.keys())
        table_data = []
        
        for algo in algorithms:
            perf = metrics_data[algo]
            comm = perf.get("communication", {})
            
            key_gen = perf.get("key_generation", {}).get("avg_time", 0)
            sign = perf.get("signing", {}).get(4096, {}).get("avg_time", 0)
            verify = perf.get("verification", {}).get(4096, {}).get("avg_time", 0)
            sig_size = comm.get("signature_size", 0)
            pub_key_size = comm.get("public_key_size", 0)
            
            table_data.append([
                algo,
                f"{key_gen:.4f}",
                f"{sign:.6f}",
                f"{verify:.6f}",
                sig_size,
                pub_key_size
            ])
        
        headers = ["Algorithm", "Key Gen (s)", "Sign (s)", "Verify (s)", 
                  "Sig Size (B)", "Pub Key (B)"]
        
        if tabulate:
            table = tabulate(table_data, headers=headers, tablefmt="grid")
        else:
            table_lines = [" | ".join(headers)]
            table_lines.append("-" * len(table_lines[0]))
            for row in table_data:
                table_lines.append(" | ".join([str(cell) for cell in row]))
            table = "\n".join(table_lines)
        
        with open(os.path.join(self.output_dir, output_file), 'w') as f:
            f.write("Benchmark Summary Table\n")
            f.write("=" * 80 + "\n\n")
            f.write(table)
        
        print(table)
