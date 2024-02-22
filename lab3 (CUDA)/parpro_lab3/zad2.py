import numpy as np
from numba import cuda

N = 100000000
M = 1000
L = 128

@cuda.jit
def calculate_pi(n, h, num_tasks, tasks, results):
    thread_id = cuda.threadIdx.x
    thread_stride = cuda.blockDim.x
    block_id = cuda.blockIdx.x

    for task_id in range(thread_id, num_tasks, thread_stride):
        task_start = tasks[task_id]
        task_end = min(task_start + M, n)
        
        task_sum = 0.0
        for i in range(task_start, task_end):
            x = h * (i + 0.5)
            task_sum += 4.0 / (1.0 + x*x)
        
        results[block_id, task_id] = h * task_sum

def main():
    h = 1.0 / N
    num_tasks = (N + M - 1) // M
    
    tasks = np.arange(0, N, M).astype(np.int32)
    results = np.zeros((L, num_tasks), dtype=np.float64)
    
    d_tasks = cuda.to_device(tasks)
    d_results = cuda.to_device(results)
    
    threads_per_block = L
    blocks_per_grid = 1
    
    calculate_pi[blocks_per_grid, threads_per_block](N, h, num_tasks, d_tasks, d_results)
    
    d_results.copy_to_host(results)
    
    pi = np.sum(results)
    pi_approx = np.pi
    error = np.abs(pi - pi_approx)
    
    print("pi je približno %.16f, greška je %.16f" % (pi, error))

if __name__ == '__main__':
    main()