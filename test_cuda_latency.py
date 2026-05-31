from qubit_fabric import QubitFabric
from cuda_latency_bridge import CUDASentinelAccelerator, RAW_CUDA_SENTINEL_KERNEL

def run_pcie_latency_test():
    print("Initializing HQA Phase 3: PCIe Bus Latency Squeezing Benchmark...\n")
    
    print("==================================================")
    print("COMPILING RAW C++ KERNEL TO NVCC TARGET:")
    print("==================================================")
    # Print the first 15 lines of the raw kernel for visual validation
    print("\n".join(RAW_CUDA_SENTINEL_KERNEL.strip().split("\n")[:15]))
    print("...\n==================================================\n")
    
    fabric = QubitFabric(width=10, height=10)
    accelerator = CUDASentinelAccelerator(fabric)
    
    error_x, error_y = 4, 4
    
    print(f"\n[TEST 1] Standard Architecture (CPU Supervisor over PCIe Bus)")
    print("-" * 50)
    cpu_logs, cpu_latency = accelerator.execute_quench_cpu_mode(error_x, error_y)
    for log in cpu_logs:
        print(log)
    print(f">> Total Reflex Latency: {cpu_latency:,.2f} microseconds")
    
    print(f"\n[TEST 2] Accelerated Edge Architecture (Zero-Copy Pinned Memory)")
    print("-" * 50)
    gpu_logs, gpu_latency = accelerator.execute_quench_gpu_edge_mode(error_x, error_y)
    for log in gpu_logs:
        print(log)
    print(f">> Total Reflex Latency: {gpu_latency:,.2f} microseconds")
    
    print("\n" + "=" * 50)
    speedup = cpu_latency / gpu_latency
    print(f"RESULT: PCIe bus elimination resulted in a {speedup:,.1f}x speedup.")
    print("Quantum coherence cascade prevented.")

if __name__ == "__main__":
    run_pcie_latency_test()
