#!/usr/bin/env python3
import argparse
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.benchmarking.benchmark_runner import BenchmarkRunner
from src.benchmarking.visualization import Visualizer

def main():
    parser = argparse.ArgumentParser(description="Run homomorphic authentication benchmarks")
    parser.add_argument("--config", type=str, default="config/benchmark_config.yaml",
                       help="Path to benchmark configuration file")
    parser.add_argument("--output", type=str, default="results/",
                       help="Output directory for results")
    parser.add_argument("--plots", action="store_true",
                       help="Generate plots")
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("Homomorphic Authentication Benchmark Suite")
    print("=" * 80)
    print()
    
    runner = BenchmarkRunner(config_path=args.config)
    
    print("Starting benchmark execution...")
    results = runner.run_full_benchmark()
    
    print("\nExporting results...")
    runner.export_results(output_dir=args.output)
    
    if args.plots:
        print("\nGenerating visualizations...")
        visualizer = Visualizer(output_dir=os.path.join(args.output, "plots"))
        
        visualizer.plot_performance_comparison(results)
        
        visualizer.plot_scalability(results)
        
        visualizer.plot_communication_overhead(results)
        
        visualizer.plot_message_size_impact(results)
        
        visualizer.create_summary_table(results)
        
        print(f"Plots saved to {visualizer.output_dir}")
    
    print("\n" + "=" * 80)
    print("Benchmark execution completed!")
    print(f"Results saved to {args.output}")
    print("=" * 80)

if __name__ == "__main__":
    main()

